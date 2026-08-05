"""Génère la Figure 6 du rapport : diagramme en barres comparant violations,
code smells et dette technique par modèle générateur (analyse SonarQube).

Par défaut, les données sont lues directement dans le tableau SonarQube de
``docs/etat-de-lart-outils-ia.md`` (source unique de vérité, mise à jour par
``scripts/compare_metrics.py`` / relevé manuel) --- aucune valeur n'est
dupliquée en dur dans ce script.

Avec ``--live``, récupère les métriques en direct depuis l'API SonarQube
(``http://localhost:9000`` par défaut) pour les quatre projets variant-a-*.

Usage :
    python scripts/generate_fig6_chart.py
    make fig6
    python scripts/generate_fig6_chart.py --live --sonar-token $env:SONAR_TOKEN
    python scripts/generate_fig6_chart.py --output fig6.png
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_OUTPUT = ROOT / "fig6.png"
DEFAULT_ETAT_ART = ROOT / "docs" / "etat-de-lart-outils-ia.md"

MODEL_LABELS = ["nano", "codex", "sol", "terra"]
MODEL_NAMES = {
    "nano": "gpt-5.4-nano",
    "codex": "gpt-5.3-codex",
    "sol": "gpt-5.6-sol",
    "terra": "gpt-5.6-terra",
}

PROJECT_KEYS = {
    "nano": "8inf950-variant-a-nano",
    "codex": "8inf950-variant-a-codex",
    "sol": "8inf950-variant-a-sol",
    "terra": "8inf950-variant-a-terra",
}

SONAR_METRIC_KEYS = {
    "Violations (total)": "violations",
    "Code smells": "code_smells",
    "Dette technique (min)": "sqale_index",
}


def _parse_markdown_table(md_text: str, header_prefix: str) -> dict[str, dict[str, float]]:
    """Parse un tableau Markdown ``| Métrique | \\`modèle\\` | ... |`` en
    ``{métrique: {label_modèle: valeur}}``, où ``label_modèle`` est déduit de
    ``MODEL_NAMES`` (ex. \\`gpt-5.4-nano\\` -> ``nano``)."""
    lines = md_text.splitlines()
    header_idx = next(
        (i for i, line in enumerate(lines) if line.strip().startswith(header_prefix)), None
    )
    if header_idx is None:
        raise ValueError(f"Tableau '{header_prefix}' introuvable")

    header_cells = [c.strip() for c in lines[header_idx].strip().strip("|").split("|")]
    name_to_label = {v: k for k, v in MODEL_NAMES.items()}
    model_order = [name_to_label.get(cell.strip("`").strip()) for cell in header_cells[1:]]

    table: dict[str, dict[str, float]] = {}
    row_idx = header_idx + 2  # ligne d'en-tête + ligne de séparation "---"
    while row_idx < len(lines) and lines[row_idx].strip().startswith("|"):
        cells = [c.strip() for c in lines[row_idx].strip().strip("|").split("|")]
        metric_name, raw_values = cells[0], cells[1:]
        values: dict[str, float] = {}
        for label, raw in zip(model_order, raw_values):
            if label is None:
                continue
            match = re.search(r"-?\d+(?:[.,]\d+)?", raw)
            if match:
                values[label] = float(match.group(0).replace(",", "."))
        table[metric_name] = values
        row_idx += 1
    return table


def load_metrics_from_etat_art(md_path: Path) -> dict[str, dict[str, int]]:
    """Lit les métriques Violations/Bugs/Vulnérabilités/Dette technique du
    tableau SonarQube de ``docs/etat-de-lart-outils-ia.md`` et en déduit les
    trois séries de la Figure~6 (Code smells n'y figure pas explicitement,
    mais violations = bugs + vulnérabilités + code smells sous SonarQube)."""
    table = _parse_markdown_table(md_path.read_text(encoding="utf-8"), "| Métrique SonarQube")

    violations = table["Violations (total)"]
    bugs = table["Bugs"]
    vulnerabilities = table["Vulnérabilités"]
    debt = table["Dette technique (min)"]

    return {
        "Violations (total)": {m: int(violations[m]) for m in MODEL_LABELS},
        "Code smells": {
            m: int(violations[m] - bugs[m] - vulnerabilities[m]) for m in MODEL_LABELS
        },
        "Dette technique (min)": {m: int(debt[m]) for m in MODEL_LABELS},
    }


def fetch_live_metrics(sonar_url: str, sonar_token: str) -> dict[str, dict[str, int]]:
    """Récupère les métriques en direct depuis l'API SonarQube pour les 4 projets."""
    import requests

    metrics: dict[str, dict[str, int]] = {label: {} for label in SONAR_METRIC_KEYS}
    for model, project_key in PROJECT_KEYS.items():
        response = requests.get(
            f"{sonar_url}/api/measures/component",
            params={"component": project_key, "metricKeys": ",".join(SONAR_METRIC_KEYS.values())},
            auth=(sonar_token, ""),
            timeout=10,
        )
        response.raise_for_status()
        measures = {m["metric"]: m["value"] for m in response.json()["component"].get("measures", [])}
        for label, metric_key in SONAR_METRIC_KEYS.items():
            metrics[label][model] = int(float(measures.get(metric_key, 0)))
    return metrics


def build_chart(metrics: dict[str, dict[str, int]], output: Path) -> None:
    labels = list(metrics.keys())
    x = np.arange(len(MODEL_LABELS))
    width = 0.25
    colors = ["#4C72B0", "#DD8452", "#55A868"]

    fig, ax = plt.subplots(figsize=(9, 5.5))

    for i, label in enumerate(labels):
        values = [metrics[label][model] for model in MODEL_LABELS]
        offset = (i - (len(labels) - 1) / 2) * width
        bars = ax.bar(x + offset, values, width, label=label, color=colors[i % len(colors)])
        ax.bar_label(bars, padding=2, fontsize=8)

    ax.set_xlabel("Modèle générateur")
    ax.set_ylabel("Valeur (nombre / minutes)")
    ax.set_title("Comparaison SonarQube par modèle générateur (analyse SonarQube)")
    ax.set_xticks(x)
    ax.set_xticklabels([MODEL_NAMES[m] for m in MODEL_LABELS], rotation=10)
    ax.legend(title="Métrique")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.yaxis.grid(True, linestyle="--", alpha=0.4)
    ax.set_axisbelow(True)

    fig.tight_layout()
    fig.savefig(output, dpi=200)
    print(f"Figure enregistrée : {output}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--live", action="store_true", help="Récupérer les métriques depuis SonarQube")
    parser.add_argument("--sonar-url", default="http://localhost:9000")
    parser.add_argument("--sonar-token", default="", help="Jeton SonarQube (Administration > Security)")
    parser.add_argument(
        "--etat-art",
        type=Path,
        default=DEFAULT_ETAT_ART,
        help="Fichier Markdown source des métriques (par défaut docs/etat-de-lart-outils-ia.md)",
    )
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="Chemin de sortie PNG")
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    if args.live:
        if not args.sonar_token:
            raise SystemExit("--live nécessite --sonar-token (ou $env:SONAR_TOKEN)")
        metrics = fetch_live_metrics(args.sonar_url, args.sonar_token)
    else:
        metrics = load_metrics_from_etat_art(args.etat_art)

    build_chart(metrics, args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
