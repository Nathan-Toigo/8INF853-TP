"""Extrait des fichiers de code depuis une réponse Markdown générée par un LLM.

La réponse doit suivre la convention imposée par
docs/prompts/redaction-projet-medical.md : chaque fichier est précédé d'un marqueur
`===FILE: chemin/relatif===` sur sa propre ligne, immédiatement suivi d'un bloc de code
Markdown (```lang ... ```) contenant le contenu intégral du fichier.

Ce module permet de transformer la sortie "vibe coding" (un seul gros document Markdown)
en un vrai projet exécutable, sans révision manuelle du contenu généré.
"""

from __future__ import annotations

import re
from pathlib import Path

FILE_BLOCK_RE = re.compile(
    r"^===FILE:\s*(?P<path>.+?)\s*===\s*\n```[^\n]*\n(?P<code>.*?)\n```",
    re.MULTILINE | re.DOTALL,
)


def extract_files(markdown_text: str) -> list[tuple[str, str]]:
    """Retourne une liste de (chemin_relatif, contenu) trouvés dans le texte."""
    return [
        (match.group("path").strip(), match.group("code"))
        for match in FILE_BLOCK_RE.finditer(markdown_text)
    ]


def _is_safe_relative_path(relative_path: str) -> bool:
    path = Path(relative_path)
    return not path.is_absolute() and ".." not in path.parts


def write_files(files: list[tuple[str, str]], base_dir: Path) -> list[Path]:
    """Écrit chaque (chemin, contenu) sous base_dir. Retourne les chemins écrits.

    Les chemins absolus ou contenant ".." sont ignorés par sécurité (le LLM ne doit
    jamais pouvoir écrire en dehors du dossier cible).
    """
    written: list[Path] = []
    for relative_path, content in files:
        if not _is_safe_relative_path(relative_path):
            print(f"  [ignoré, chemin non sûr] {relative_path}")
            continue
        target = base_dir / relative_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        written.append(target)
    return written
