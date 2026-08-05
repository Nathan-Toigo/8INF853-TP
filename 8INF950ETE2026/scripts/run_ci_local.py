"""Exécute le pipeline CI (Ruff, pytest >= 80 %, pip-audit) sur toutes les variantes A.

Met à jour docs/etat-de-lart-outils-ia.md avec un tableau comparatif.

Usage :
    python scripts/run_ci_local.py
    make ci-variants-a
"""

from __future__ import annotations

import os
import re
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CASE_STUDY = ROOT / "case-study"
ETAT_ART = ROOT / "docs" / "etat-de-lart-outils-ia.md"
DEV_REQUIREMENTS = CASE_STUDY / "variant-b-hybrid" / "requirements-dev.txt"
VENV_DIR = ROOT / ".venv"

VARIANT_MODELS: dict[str, str] = {
    "variant-a-nano": "gpt-5.4-nano",
    "variant-a-codex": "gpt-5.3-codex",
    "variant-a-sol": "gpt-5.6-sol",
    "variant-a-terra": "gpt-5.6-terra",
}

MARKER_START = "<!-- CI_LOCAL_TABLE_START -->"
MARKER_END = "<!-- CI_LOCAL_TABLE_END -->"


@dataclass
class CiResult:
    variant: str
    model: str
    ruff_ok: bool
    ruff_detail: str
    tests_ok: bool
    tests_detail: str
    coverage_pct: str
    pip_audit_ok: bool
    pip_audit_detail: str
    quality_gate_ok: bool


def _run(cmd: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        cmd,
        cwd=cwd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )


def _venv_python_path() -> Path:
    if os.name == "nt":
        return VENV_DIR / "Scripts" / "python.exe"
    return VENV_DIR / "bin" / "python"


def _venv_setup_hint() -> str:
    minor = f"{sys.version_info.major}.{sys.version_info.minor}"
    return (
        "Sous Debian/Ubuntu (WSL), installez d'abord le module venv :\n"
        f"  sudo apt install python{minor}-venv\n"
        "  # ou : make setup-wsl\n"
        "Puis relancez : make ci-variants-a"
    )


def _ensure_venv() -> Path:
    """Crée .venv si besoin et y installe les outils CI (évite PEP 668 sous WSL/Debian)."""
    if not DEV_REQUIREMENTS.exists():
        raise FileNotFoundError(f"Dépendances CI introuvables : {DEV_REQUIREMENTS}")

    venv_python = _venv_python_path()
    if not venv_python.exists():
        print(f"Création de l'environnement virtuel {VENV_DIR}...")
        try:
            completed = subprocess.run(
                [sys.executable, "-m", "venv", str(VENV_DIR)],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
            )
        except FileNotFoundError as exc:
            raise RuntimeError(_venv_setup_hint()) from exc
        if completed.returncode != 0:
            detail = (completed.stderr or completed.stdout or "").strip()
            raise RuntimeError(
                f"Impossible de créer {VENV_DIR}.\n{detail}\n\n{_venv_setup_hint()}"
            )

    if not venv_python.exists():
        raise RuntimeError(
            f"Interpréteur introuvable après création du venv : {venv_python}\n\n{_venv_setup_hint()}"
        )

    print("Installation des outils CI (ruff, pytest-cov, pip-audit) dans .venv...")
    subprocess.run([str(venv_python), "-m", "pip", "install", "-q", "--upgrade", "pip"], check=True)
    subprocess.run(
        [str(venv_python), "-m", "pip", "install", "-q", "-r", str(DEV_REQUIREMENTS)],
        check=True,
    )
    return venv_python


def _lint_targets(variant_dir: Path) -> list[str]:
    targets = ["app"]
    if (variant_dir / "tests").is_dir():
        targets.append("tests")
    if (variant_dir / "app" / "tests").is_dir():
        targets.append("app/tests")
    return targets


def _pytest_targets(variant_dir: Path) -> list[str]:
    targets: list[str] = []
    if (variant_dir / "tests").is_dir():
        targets.append("tests")
    if (variant_dir / "app" / "tests").is_dir():
        targets.append("app/tests")
    return targets or ["."]


def _parse_coverage(output: str) -> str:
    match = re.search(r"TOTAL\s+\d+\s+\d+\s+(\d+(?:\.\d+)?)%", output)
    if match:
        return f"{match.group(1)} %"
    return "N/A"


def _parse_pip_audit_vulns(output: str) -> int:
    match = re.search(r"Found (\d+) known vulnerabilities", output)
    return int(match.group(1)) if match else 0


def run_ci_for_variant(variant_dir: Path, model: str, ci_python: Path) -> CiResult:
    variant = variant_dir.name
    print(f"\n=== {variant} ({model}) ===")

    req = variant_dir / "requirements.txt"
    if not req.exists():
        print("  [ignoré] requirements.txt absent")
        return CiResult(
            variant=variant,
            model=model,
            ruff_ok=False,
            ruff_detail="N/A (pas de requirements.txt)",
            tests_ok=False,
            tests_detail="N/A",
            coverage_pct="N/A",
            pip_audit_ok=False,
            pip_audit_detail="N/A",
            quality_gate_ok=False,
        )

    subprocess.run(
        [str(ci_python), "-m", "pip", "install", "-q", "-r", str(req)],
        cwd=variant_dir,
        check=True,
    )

    lint_targets = _lint_targets(variant_dir)
    ruff = _run([str(ci_python), "-m", "ruff", "check", *lint_targets], variant_dir)
    ruff_ok = ruff.returncode == 0
    ruff_detail = "OK" if ruff_ok else "échec"
    print(f"  Ruff      : {ruff_detail}")

    pytest_targets = _pytest_targets(variant_dir)
    pytest_cmd = [
        str(ci_python),
        "-m",
        "pytest",
        *pytest_targets,
        "--cov=app",
        "--cov-report=term-missing",
        "--cov-fail-under=80",
    ]
    pytest_run = _run(pytest_cmd, variant_dir)
    tests_ok = pytest_run.returncode == 0
    combined_pytest = pytest_run.stdout + pytest_run.stderr
    coverage_pct = _parse_coverage(combined_pytest)
    if tests_ok:
        tests_detail = "OK"
    elif "coverage" in combined_pytest.lower() and coverage_pct != "N/A":
        tests_detail = f"couverture insuffisante ({coverage_pct})"
    else:
        tests_detail = "échec tests"
    print(f"  Pytest    : {tests_detail} (couverture {coverage_pct})")

    pip_audit = _run(
        [str(ci_python), "-m", "pip_audit", "-r", "requirements.txt"],
        variant_dir,
    )
    vuln_count = _parse_pip_audit_vulns(pip_audit.stdout + pip_audit.stderr)
    pip_audit_ok = pip_audit.returncode == 0
    pip_audit_detail = "OK" if pip_audit_ok else f"{vuln_count} vuln."
    print(f"  pip-audit : {pip_audit_detail}")

    quality_gate_ok = ruff_ok and tests_ok and pip_audit_ok
    print(f"  Quality gate : {'PASS' if quality_gate_ok else 'FAIL'}")

    return CiResult(
        variant=variant,
        model=model,
        ruff_ok=ruff_ok,
        ruff_detail=ruff_detail,
        tests_ok=tests_ok,
        tests_detail=tests_detail,
        coverage_pct=coverage_pct,
        pip_audit_ok=pip_audit_ok,
        pip_audit_detail=pip_audit_detail,
        quality_gate_ok=quality_gate_ok,
    )


def _build_table(results: list[CiResult]) -> str:
    models = [r.model for r in results]
    header = "| Métrique pipeline CI | " + " | ".join(f"`{m}`" for m in models) + " |"
    sep = "| --- | " + " | ".join("---" for _ in models) + " |"

    def row(label: str, values: list[str]) -> str:
        return "| " + label + " | " + " | ".join(values) + " |"

    rows = [
        row("Ruff (lint)", [r.ruff_detail for r in results]),
        row("Pytest (tests)", [r.tests_detail for r in results]),
        row("Couverture", [r.coverage_pct for r in results]),
        row("Seuil couverture >= 80 %", ["oui" if r.tests_ok else "non" for r in results]),
        row("pip-audit", [r.pip_audit_detail for r in results]),
        row("Quality gate (3/3)", ["PASS" if r.quality_gate_ok else "FAIL" for r in results]),
    ]

    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    intro = (
        f"Dernière exécution : `{timestamp}` via `make ci-variants-a` "
        f"(Ruff, pytest --cov-fail-under=80, pip-audit)."
    )

    return "\n".join(
        [
            MARKER_START,
            intro,
            "",
            header,
            sep,
            *rows,
            MARKER_END,
        ]
    )


def update_etat_art(results: list[CiResult]) -> None:
    table_block = _build_table(results)
    content = ETAT_ART.read_text(encoding="utf-8")

    section_title = "## Pipeline CI local (quality gate — variantes A)"
    if MARKER_START in content and MARKER_END in content:
        pattern = re.compile(
            re.escape(MARKER_START) + r".*?" + re.escape(MARKER_END),
            re.DOTALL,
        )
        content = pattern.sub(table_block, content)
    elif section_title in content:
        raise ValueError(
            f"Section trouvée sans marqueurs {MARKER_START}/{MARKER_END} dans {ETAT_ART}"
        )
    else:
        insert = (
            f"\n\n{section_title}\n\n"
            "Comparaison du pipeline qualité (identique à la variante B) appliqué aux "
            "projets vibe coding sans révision. Un **FAIL** est attendu pour la plupart "
            "des variantes A (hypothèse H3).\n\n"
            f"{table_block}\n"
        )
        # Insérer après le premier tableau SonarQube (après ligne 19 environ)
        sonar_end = content.find("## Correspondance des projets SonarQube")
        if sonar_end == -1:
            content = content.rstrip() + insert
        else:
            content = content[:sonar_end] + insert + "\n" + content[sonar_end:]

    ETAT_ART.write_text(content, encoding="utf-8")
    print(f"\nTableau CI mis à jour dans {ETAT_ART.relative_to(ROOT)}")


def main() -> int:
    print("Préparation de l'environnement CI (.venv)...")
    ci_python = _ensure_venv()

    results: list[CiResult] = []
    for folder_name, model in VARIANT_MODELS.items():
        variant_dir = CASE_STUDY / folder_name
        if not variant_dir.is_dir():
            print(f"  [ignoré] dossier absent : {variant_dir}")
            continue
        results.append(run_ci_for_variant(variant_dir, model, ci_python))

    if not results:
        print("Aucune variante A trouvée.", file=sys.stderr)
        return 1

    update_etat_art(results)

    failed = sum(1 for r in results if not r.quality_gate_ok)
    print(f"\nRésumé : {len(results) - failed}/{len(results)} quality gate PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
