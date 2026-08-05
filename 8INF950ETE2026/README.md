# 8INF950 — Sujets spéciaux : Vibe Coding & Qualité Logicielle en Santé

Projet réalisé dans le cadre du cours 8INF950 (Été 2026, UQAC), sous la supervision du
professeur Hamid Mcheick.

## Objectif

Le projet se concentre sur deux objectifs :

1. **Étudier l'impact du *vibe coding* (génération de code par IA, sans révision
   approfondie) sur la qualité logicielle**, à travers une étude de cas dans le domaine de
   la santé : un système de **gestion de rendez-vous médicaux**.
2. **Analyser les résultats de cette étude de cas** au moyen de deux analyses
   complémentaires appliquées aux mêmes projets générés :
   - une **analyse SonarQube** (statique — bugs, vulnérabilités, dette technique, notes) ;
   - une **analyse étendue** (quality gate CI — lint, couverture de tests, audit de
     dépendances) qui va au-delà du scan SonarQube.

Quatre modèles générateurs (tous **OpenAI**, déployés via **Azure AI Foundry** —
contrainte pratique de l'abonnement *Azure for Students*, voir `main.tex` §1.4) reçoivent
la **même spécification fonctionnelle** (`docs/cahier-des-charges.md`) et génèrent chacun
une implémentation, sans révision humaine (« vibe coding pur »). Les résultats sont
comparés à l'aide de métriques de qualité basées sur la norme **ISO/IEC 25010**
(`docs/grille-qualite-iso25010.md`).

| Modèle          | Dossier                          | Clé SonarQube              |
| --------------- | --------------------------------- | -------------------------- |
| `gpt-5.4-nano`  | `case-study/variant-a-nano/`      | `8inf950-variant-a-nano`   |
| `gpt-5.3-codex` | `case-study/variant-a-codex/`     | `8inf950-variant-a-codex`  |
| `gpt-5.6-sol`   | `case-study/variant-a-sol/`       | `8inf950-variant-a-sol`    |
| `gpt-5.6-terra` | `case-study/variant-a-terra/`     | `8inf950-variant-a-terra`  |

Le dossier `case-study/variant-b-hybrid/` ne contient **pas** une cinquième
implémentation : c'est uniquement la **configuration de référence** du pipeline de
l'analyse étendue (workflow GitHub Actions, dépendances de dev), appliquée aux quatre
projets ci-dessus.

## Prérequis

| Outil | Version / notes | Utilisé pour |
| --- | --- | --- |
| **Python** | 3.11+ | Génération LLM, extraction de code, scripts d'analyse |
| **Docker** (+ Docker Compose) | — | Démarrer SonarQube Community en local |
| **Java** | 17+ (fourni avec `sonar-scanner`) | Requis par `sonar-scanner` |
| **sonar-scanner CLI** | — | Lancer une analyse SonarQube par projet |
| **make** | WSL/Linux/macOS (WSL recommandé sous Windows) | Cibles `ci-variants-a`, `fig6` |
| **LaTeX** (`pdflatex`/TeX Live) | — | Compiler `main.tex` (rapport final) |
| Accès **Azure AI Foundry** *(optionnel)* | déploiement OpenAI (ex. abonnement Azure for Students) | Régénérer un projet via `generate_with_llm.py` |
| **Ollama** *(optionnel)* | LLM local compatible OpenAI | Génération sans dépendance cloud |

Sous **WSL/Debian**, `pip install` système est bloqué par défaut (PEP 668). Les scripts de
ce dépôt (`run_ci_local.py`, cible `make fig6`) créent et utilisent automatiquement un
environnement virtuel `.venv/` à la racine pour contourner cette contrainte. Si la création
du venv échoue (`ensurepip is not available`), installez le paquet manquant :

```bash
make setup-wsl
# équivalent à : sudo apt update && sudo apt install -y python3-venv python3-pip
```

## Structure du dépôt

```
8INF950ETE2026/
├── main.tex                        # Rapport final (LaTeX)
├── Makefile                        # make ci-variants-a, make fig6, make setup-wsl
├── plan8INF950ETE2026.pdf          # Plan de cours officiel
├── .env.example                    # Modèle de configuration pour les LLM externes (Azure/local)
├── docs/
│   ├── cahier-des-charges.md       # Spécification fonctionnelle commune aux 4 modèles
│   ├── grille-qualite-iso25010.md  # Attributs qualité retenus + métriques + outils
│   ├── etat-de-lart-outils-ia.md   # Tableaux SonarQube + pipeline CI local (4 modèles)
│   ├── risques-vibe-coding.md      # Hallucinations, vulnérabilités, absence de tests
│   ├── prompts/
│   │   └── redaction-projet-medical.md  # Prompt utilisé pour générer un projet médical via LLM
│   └── rapports-avancement/        # Rapports mensuels remis au professeur
├── case-study/
│   ├── variant-a-nano/             # Généré par gpt-5.4-nano
│   ├── variant-a-codex/            # Généré par gpt-5.3-codex
│   ├── variant-a-sol/              # Généré par gpt-5.6-sol
│   ├── variant-a-terra/            # Généré par gpt-5.6-terra
│   ├── variant-b-hybrid/           # Config. de référence de l'analyse étendue (pas un 5e projet)
│   └── docker-compose.sonarqube.yml
├── scripts/
│   ├── generate_with_llm.py        # CLI : génère un projet médical via Azure OpenAI ou LLM local
│   ├── llm_client.py               # Abstraction d'appel LLM (Azure OpenAI / LLM local)
│   ├── extract_code_blocks.py      # Extrait les fichiers balisés d'un GENERATED_DRAFT.md
│   ├── compare_metrics.py          # Extraction & comparaison des métriques SonarQube (API)
│   ├── run_ci_local.py             # Pipeline CI local (Ruff, pytest, pip-audit) sur les 4 modèles
│   ├── generate_fig6_chart.py      # Diagramme en barres (Figure 6 du rapport) depuis etat-de-lart-outils-ia.md
│   └── requirements.txt            # Dépendances des scripts (openai, requests, matplotlib, ...)
├── .github/workflows/
│   └── variant-b-hybrid-ci.yml     # CI GitHub Actions (Ruff, pytest ≥80 %, pip-audit)
└── README.md
```

## Démarche

| Étape | Description | Livrable / commande |
| --- | --- | --- |
| 1. Cadre d'analyse | Définir les attributs ISO 25010 et les outils de mesure | `docs/grille-qualite-iso25010.md` |
| 2. Génération (vibe coding pur) | Générer un projet par modèle à partir du même prompt, sans révision | `scripts/generate_with_llm.py` → `GENERATED_DRAFT.md` → `scripts/extract_code_blocks.py` |
| 3. Analyse SonarQube | Scanner chaque projet généré | `sonar-scanner` (voir ci-dessous) |
| 4. Analyse étendue | Appliquer le quality gate (lint, tests, dépendances) aux mêmes projets | `make ci-variants-a` |
| 5. Analyse des résultats | Comparer les métriques et interpréter les écarts | `docs/etat-de-lart-outils-ia.md`, `main.tex` |

## Étapes pour reproduire un résultat similaire

### 1. Cloner et installer les dépendances des scripts

```powershell
git clone https://github.com/Nathan-Toigo/8INF853-TP.git
cd 8INF950ETE2026
pip install -r scripts/requirements.txt
```

### 2. (Optionnel) Générer un nouveau projet via un LLM externe

```powershell
Copy-Item .env.example .env
# éditer .env avec l'endpoint/clé Azure AI Foundry, ou l'URL du LLM local (Ollama, etc.)

python scripts/generate_with_llm.py --provider azure `
  --project-name "Gestion de rendez-vous médicaux" `
  --output case-study/variant-a-terra/GENERATED_DRAFT.md `
  --code-dir case-study/variant-a-terra
```

`--code-dir` matérialise directement les fichiers balisés `===FILE: chemin===` de la
réponse sur disque (voir `scripts/extract_code_blocks.py`), sans révision du contenu généré.

### 3. Démarrer SonarQube localement

```powershell
docker compose -f case-study/docker-compose.sonarqube.yml up -d
# interface : http://localhost:9000 (identifiants par défaut admin/admin, à changer)
```

### 4. Lancer une analyse SonarQube par projet généré

```powershell
cd case-study/variant-a-terra   # ou variant-a-nano, -codex, -sol
sonar-scanner -D project.settings=sonar-project.properties -D sonar.host.url=http://localhost:9000 -D sonar.token=$env:SONAR_TOKEN
```

Répéter pour chaque modèle, puis consulter `http://localhost:9000` ou extraire les
métriques par API :

```powershell
python scripts/compare_metrics.py
```

### 5. Lancer l'analyse étendue (quality gate CI) sur les 4 projets

```bash
# WSL / Linux / macOS
make ci-variants-a
# équivalent direct : python scripts/run_ci_local.py
```

Exécute Ruff (lint), Pytest (`--cov-fail-under=80`) et `pip-audit` sur les quatre projets
`variant-a-*`, puis met automatiquement à jour le tableau « Pipeline CI local » dans
`docs/etat-de-lart-outils-ia.md`. Crée et utilise un `.venv/` local pour contourner PEP 668
sous WSL/Debian (voir `make setup-wsl` si la création du venv échoue).

### 6. Démarrer une application générée (test manuel / Swagger)

```powershell
cd case-study/variant-a-terra
pip install -r requirements.txt
python -m hypercorn app.main:app --reload --bind 127.0.0.1:8001
# Swagger UI : http://127.0.0.1:8001/docs
```

### 7. Régénérer la Figure 6 du rapport (diagramme comparatif)

```bash
make fig6
# équivalent direct : python scripts/generate_fig6_chart.py
```

Lit directement les valeurs du tableau SonarQube dans `docs/etat-de-lart-outils-ia.md`
(source unique de vérité) et produit `fig6.png`. Option `--live --sonar-token $env:SONAR_TOKEN`
pour récupérer les métriques en direct depuis l'API SonarQube plutôt que depuis le Markdown.

### 8. Compiler le rapport final

```bash
pdflatex main.tex
pdflatex main.tex   # 2 passes pour la table des matières / liste des figures
```

## Outils utilisés

### SonarQube

Plateforme d'analyse statique qui inspecte le code source sans l'exécuter et produit des
indicateurs de qualité : **bugs potentiels**, **vulnérabilités de sécurité**, **code
smells**, **complexité cyclomatique**, **duplication de code** et **dette technique**
(temps estimé pour corriger les problèmes détectés).

Démarré localement via `case-study/docker-compose.sonarqube.yml`, alimenté par
`sonar-scanner` (configuration `sonar-project.properties` dans chaque dossier
`variant-a-*`).

### Ruff, Pytest (+ coverage), pip-audit — analyse étendue

Le quality gate de l'**analyse étendue** (`make ci-variants-a` /
`scripts/run_ci_local.py`) combine :
- **Ruff** — lint (style, erreurs courantes) ;
- **Pytest** + `pytest-cov` — exécution des tests et couverture minimale (≥ 80 %) ;
- **pip-audit** — audit des vulnérabilités connues des dépendances (`requirements.txt`).

Ce pipeline est aussi outillé en CI GitHub Actions
(`.github/workflows/variant-b-hybrid-ci.yml`) pour le dossier `variant-b-hybrid`.

### matplotlib — visualisation

`scripts/generate_fig6_chart.py` génère un diagramme en barres comparant violations, code
smells et dette technique par modèle, à partir des données de
`docs/etat-de-lart-outils-ia.md`.

## Génération via un LLM externe (hors Cursor)

Pour rendre la méthodologie « vibe coding » reproductible et indépendante de l'IDE,
`scripts/generate_with_llm.py` envoie directement un prompt à un LLM externe — un modèle
déployé sur **Azure AI Foundry** (cloud, endpoint unifié compatible OpenAI) ou un **LLM
local** (ex. Ollama, on-prem) — et enregistre sa réponse telle quelle, sans révision
humaine.

Le prompt utilisé est défini dans
[`docs/prompts/redaction-projet-medical.md`](docs/prompts/redaction-projet-medical.md)
(modifiable) et demande au LLM de rédiger : problème/utilisateurs, modèle de données,
fonctionnalités, architecture, code source et limites connues, avec chaque fichier balisé
`===FILE: chemin/relatif===` suivi d'un bloc de code.

```powershell
# Via Azure AI Foundry
python scripts/generate_with_llm.py --provider azure `
  --project-name "Gestion de rendez-vous médicaux" `
  --output case-study/variant-a-terra/GENERATED_DRAFT.md `
  --code-dir case-study/variant-a-terra

# Via un LLM local (ex. Ollama démarré sur http://localhost:11434)
python scripts/generate_with_llm.py --provider local --model llama3.1 `
  --project-name "Suivi de patients chroniques" `
  --project-description "Suivi de la glycémie avec alertes en cas de valeur anormale" `
  --output docs/drafts/suivi-chronique.md
```

Le fournisseur `local` est particulièrement pertinent pour le domaine de la santé : il
garde les prompts (et d'éventuelles données) entièrement on-prem, ce qui évite les
préoccupations de confidentialité soulevées dans
[`docs/etat-de-lart-outils-ia.md`](docs/etat-de-lart-outils-ia.md).

## Limites connues

- Une seule étude de cas et un seul prompt par modèle.
- Couverture SonarQube non alimentée (pas de rapport `coverage.xml` importé dans les scans).
- L'analyse étendue (lint, tests, audit) n'est pas intégrée aux tableaux de bord
  SonarQube ; les deux analyses restent consultées séparément.
- `pip-audit` signale des vulnérabilités connues sur la version de Starlette imposée par
  FastAPI 0.115 (dépendance transitive) pour la plupart des projets.

## Prochaines étapes

1. Finaliser l'interprétation des résultats (`main.tex`, section Analyse).
2. Étendre `scripts/compare_metrics.py` pour agréger automatiquement les 4 clés SonarQube
   `8inf950-variant-a-*` (actuellement ciblé sur d'anciennes clés).
3. Documenter les écarts constatés dans `docs/rapports-avancement/`.
4. Compléter les figures manquantes du rapport (`fig1.png`, captures Swagger, etc.).
