"""Extrait et compare les métriques SonarQube des deux variantes de l'étude de cas.

Usage :
    python scripts/compare_metrics.py

Prérequis : une instance SonarQube démarrée (voir case-study/docker-compose.sonarqube.yml)
avec les deux projets déjà analysés (sonar-scanner exécuté dans chaque variante).

Nécessite : pip install requests tabulate
"""

from __future__ import annotations

import requests
from tabulate import tabulate

SONAR_URL = "http://localhost:9000"
SONAR_TOKEN = ""  # à renseigner : jeton généré dans SonarQube (Administration > Security)

PROJECT_KEYS = {
    "Variante A (vibe coding)": "8inf950-variant-a-vibe-coding",
    "Variante B (hybride)": "8inf950-variant-b-hybrid",
}

METRICS = [
    "bugs",
    "vulnerabilities",
    "code_smells",
    "coverage",
    "duplicated_lines_density",
    "complexity",
    "sqale_index",  # dette technique, en minutes
    "security_hotspots",
]


def fetch_metrics(project_key: str) -> dict[str, str]:
    response = requests.get(
        f"{SONAR_URL}/api/measures/component",
        params={"component": project_key, "metricKeys": ",".join(METRICS)},
        auth=(SONAR_TOKEN, ""),
        timeout=10,
    )
    response.raise_for_status()
    measures = response.json()["component"].get("measures", [])
    return {m["metric"]: m["value"] for m in measures}


def main() -> None:
    rows = []
    for label, project_key in PROJECT_KEYS.items():
        metrics = fetch_metrics(project_key)
        rows.append([label] + [metrics.get(metric, "N/A") for metric in METRICS])

    headers = ["Variante"] + METRICS
    print(tabulate(rows, headers=headers, tablefmt="github"))


if __name__ == "__main__":
    main()
