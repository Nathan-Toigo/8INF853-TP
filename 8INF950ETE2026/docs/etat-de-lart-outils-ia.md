# État de l'art — Comparaison des modèles générateurs de code IA (métriques SonarQube)

Grille comparative alimentée par l'analyse statique **SonarQube** (`http://localhost:9000`),
une analyse `sonar-scanner` par variante, et l'API `/api/measures/component`.


| Métrique SonarQube      | `gpt-5.4-nano` | `gpt-5.3-codex` | `gpt-5.6-sol` | `gpt-5.6-terra` |
| ----------------------- | -------------- | --------------- | ------------- | --------------- |
| Bugs                    | 0              | 0               | 0             | 0               |
| Vulnérabilités          | 5              | 0               | 0             | 0               |
| Duplication (%)         | 0,0            | 0,0             | 0,0           | 0,0             |
| Complexité cyclomatique | 57             | 82              | 53            | 47              |
| Dette technique (min)   | 151            | 242             | 151           | 20              |
| Security hotspots       | 0              | 0               | 0             | 0               |
| Note fiabilité          | A              | A               | A             | A               |
| Note sécurité           | C              | A               | A             | A               |
| Note maintenabilité     | A              | A               | A             | A               |
| Lignes de code (NCLOC)  | 587            | 585             | 650           | 529             |
| Violations (total)      | 35             | 48              | 30            | 4               |




## Pipeline CI local (quality gate — variantes A)

Comparaison du pipeline qualité (identique à la variante B : Ruff, pytest >= 80 %, pip-audit)
appliqué aux projets vibe coding sans révision. Un **FAIL** est attendu pour la plupart
des variantes A (hypothèse H3). Lancer : `make ci-variants-a`.



Dernière exécution : `2026-08-05 08:08 UTC` via `make ci-variants-a` (Ruff, pytest --cov-fail-under=80, pip-audit).


| Métrique pipeline CI      | `gpt-5.4-nano`                 | `gpt-5.3-codex`                | `gpt-5.6-sol`                  | `gpt-5.6-terra`                |
| ------------------------- | ------------------------------ | ------------------------------ | ------------------------------ | ------------------------------ |
| Ruff (lint)               | échec                          | échec                          | échec                          | échec                          |
| Couverture Pytest (tests) | couverture insuffisante (10 %) | couverture insuffisante (33 %) | couverture insuffisante (60 %) | couverture insuffisante (66 %) |
| Seuil couverture >= 80 %  | non                            | non                            | non                            | non                            |
| pip-audit                 | 8 vuln.                        | 8 vuln.                        | 8 vuln.                        | 8 vuln.                        |
| Quality gate (3/3)        | FAIL                           | FAIL                           | FAIL                           | FAIL                           |




## Correspondance des projets SonarQube


| Modèle / variante | Dossier                      | Clé SonarQube             |
| ----------------- | ---------------------------- | ------------------------- |
| `gpt-5.4-nano`    | `case-study/variant-a-nano`  | `8inf950-variant-a-nano`  |
| `gpt-5.3-codex`   | `case-study/variant-a-codex` | `8inf950-variant-a-codex` |
| `gpt-5.6-sol`     | `case-study/variant-a-sol`   | `8inf950-variant-a-sol`   |
| `gpt-5.6-terra`   | `case-study/variant-a-terra` | `8inf950-variant-a-terra` |




## Méthode de collecte

1. Démarrer SonarQube : `docker compose -f case-study/docker-compose.sonarqube.yml up -d`
2. Analyser chaque variante :
  ```powershell
   cd case-study/variant-a-nano   # (ou codex, sol, terra)
   sonar-scanner -D project.settings=sonar-project.properties -D sonar.host.url=http://localhost:9000 -D sonar.token=$env:SONAR_TOKEN
  ```
3. Consulter les résultats sur [http://localhost:9000](http://localhost:9000) ou relancer l'extraction automatique :
  ```powershell
   python scripts/compare_metrics.py
  ```
4. Pipeline CI local (Ruff, pytest >= 80 %, pip-audit) sur les variantes A :
  ```powershell
   make ci-variants-a
   # ou : python scripts/run_ci_local.py
  ```
  Met à jour automatiquement le tableau « Pipeline CI local » ci-dessus dans ce fichier.

Les notes A–E correspondent aux échelles SonarQube (`1.0` = A, `2.0` = B, `3.0` = C, etc.).

## Synthèse préliminaire

- `gpt-5.6-terra` présente le moins de code smells (4) et la dette technique la plus faible (20 min).
- `gpt-5.3-codex` génère le code le plus complexe (82) et la dette la plus élevée (242 min), sans vulnérabilité détectée.
- `gpt-5.4-nano` est le seul avec des **vulnérabilités** signalées (5) et une note sécurité **C**.
- Aucune variante n'a de couverture de tests remontée dans SonarQube (0 % — attendu en vibe coding pur sans rapport `coverage.xml`).



## Considérations spécifiques au domaine de la santé

- Traitement des données sensibles : les prompts/contexte envoyés à un service cloud ne doivent pas contenir de données de patients réelles (données fictives/synthétiques uniquement).
- Conformité réglementaire (Loi 25 au Québec, HIPAA aux É.-U.) — pertinence pour un futur
déploiement réel, même si hors périmètre direct du projet.
- Les vulnérabilités SonarQube (ex. sur `gpt-5.4-nano`) doivent être analysées manuellement
dans l'onglet **Security** du dashboard avant toute conclusion définitive.



## Sources

- SonarQube Community — dashboard local [http://localhost:9000](http://localhost:9000)
- `docs/grille-qualite-iso25010.md` — cadre ISO/IEC 25010 et hypothèses H1–H4
- `scripts/compare_metrics.py` — extraction programmatique des métriques SonarQube
- `scripts/run_ci_local.py` / `Makefile` (`make ci-variants-a`) — pipeline CI local variantes A

