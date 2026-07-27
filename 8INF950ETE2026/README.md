# 8INF950 — Sujets spéciaux : Vibe Coding & Qualité Logicielle en Santé

Projet réalisé dans le cadre du cours 8INF950 (Été 2026, UQAC), sous la supervision du
professeur Hamid Mcheick.

## Objectif

Le projet se concentre sur deux objectifs :

1. **Proposer et implémenter un modèle, ou faire une étude comparative de modèles générateurs de code par IA (« vibe coding »), selon des attributs/critères de qualité logicielle** — ici, à travers une étude de cas dans le domaine de la santé : un système
  de **gestion de rendez-vous médicaux**.
2. **Analyser les résultats de cette étude de cas.**

La même spécification fonctionnelle (voir `[docs/cahier-des-charges.md](docs/cahier-des-charges.md)`)
est implémentée selon deux approches de développement, puis comparée à l'aide de métriques
de qualité basées sur la norme **ISO/IEC 25010** (voir `[docs/grille-qualite-iso25010.md](docs/grille-qualite-iso25010.md)`).


| Variante | Approche                                                                      | Dossier                                                                |
| -------- | ----------------------------------------------------------------------------- | ---------------------------------------------------------------------- |
| A        | Vibe coding pur : prompts IA, suggestions acceptées sans révision approfondie | `[case-study/variant-a-vibe-coding](case-study/variant-a-vibe-coding)` |
| B        | Modèle hybride : IA + revue humaine, TDD, quality gate obligatoire            | `[case-study/variant-b-hybrid](case-study/variant-b-hybrid)`           |


## Structure du dépôt

```
8INF950ETE2026/
├── plan8INF950ETE2026.pdf          # Plan de cours officiel
├── .env.example                    # Modèle de configuration pour les LLM externes (Azure/local)
├── docs/
│   ├── cahier-des-charges.md       # Spécification fonctionnelle commune aux 2 variantes
│   ├── grille-qualite-iso25010.md  # Attributs qualité retenus + métriques + outils
│   ├── etat-de-lart-outils-ia.md   # Comparatif Cursor / Copilot / Claude Code
│   ├── risques-vibe-coding.md      # Hallucinations, vulnérabilités, absence de tests
│   ├── prompts/
│   │   └── redaction-projet-medical.md  # Prompt utilisé pour générer un projet médical via LLM
│   └── rapports-avancement/        # Rapports mensuels remis au professeur
├── case-study/
│   ├── variant-a-vibe-coding/      # Implémentation "vibe coding pur"
│   ├── variant-b-hybrid/           # Implémentation "hybride IA + humain"
│   └── docker-compose.sonarqube.yml
├── scripts/
│   ├── compare_metrics.py          # Extraction & comparaison des métriques SonarQube
│   ├── generate_with_llm.py        # CLI : génère un projet médical via Azure OpenAI ou LLM local
│   └── llm_client.py               # Abstraction d'appel LLM (Azure OpenAI / LLM local)
└── README.md
```

## Démarche


| Étape                              | Description                                                                                              | Livrable dans ce dépôt                                         |
| ---------------------------------- | -------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------- |
| Cadre d'analyse                    | Définir les attributs/critères de qualité retenus (ISO 25010) et les outils de mesure                    | `docs/grille-qualite-iso25010.md`                              |
| Étude comparative / implémentation | Implémenter la même spécification fonctionnelle selon 2 approches (vibe coding pur vs modèle hybride)    | `case-study/`                                                  |
| Analyse des résultats              | Comparer les métriques obtenues (SonarQube, sécurité, couverture, performance) et interpréter les écarts | `docs/rapport-final.md` (à créer), `docs/rapports-avancement/` |


## Outils

Le projet s'appuie sur des outils spécialisés d'analyse de qualité et de sécurité, moins
connus que les outils génériques (FastAPI, pytest, Docker). Voici ce qu'ils font et
pourquoi ils sont utilisés ici.

### SonarQube

Plateforme d'analyse statique de code qui inspecte le code source sans l'exécuter et
produit des indicateurs de qualité : **bugs potentiels**, **vulnérabilités de sécurité**,
**code smells** (mauvaises pratiques), **complexité cyclomatique**, **duplication de
code** et **dette technique** (temps estimé pour corriger les problèmes détectés). Elle
applique aussi un **quality gate** : un ensemble de seuils (ex. couverture minimale,
0 vulnérabilité critique) qui doit être respecté pour qu'un projet soit considéré
« conforme ».

Dans ce projet, SonarQube est l'outil central de comparaison entre `variant-a-vibe-coding`
et `variant-b-hybrid` : on lance une analyse sur chaque variante et on compare leurs
indicateurs (voir `docs/grille-qualite-iso25010.md` et `scripts/compare_metrics.py`).
Il est démarré localement via `case-study/docker-compose.sonarqube.yml` (interface web sur
`http://localhost:9000`) et alimenté par la commande `sonar-scanner`, configurée dans les
fichiers `sonar-project.properties` de chaque variante.

### Semgrep

Outil d'analyse statique orienté **sécurité**, basé sur des règles (patterns de code
vulnérable connus : injection, secrets en dur, désérialisation non sécurisée, etc.). Il
complète SonarQube pour la détection de vulnérabilités dans le code applicatif.

### coverage.py (via pytest-cov)

Mesure la **couverture de tests** : le pourcentage de lignes/branches du code réellement
exercées par les tests automatisés. Sert à quantifier objectivement la testabilité de
chaque variante (attendu proche de 0 % pour la variante A, ≥ 80 % exigé pour la variante B).

### k6 / Locust

Outils de **tests de charge/performance** qui simulent des requêtes HTTP pour mesurer la
latence et le débit d'une API sous charge. Utilisés pour comparer le comportement temporel
(ISO 25010 — Performance) des deux variantes.

### openapi-spec-validator

Valide qu'un schéma **OpenAPI** (généré automatiquement par FastAPI) est bien formé et
cohérent — utilisé comme proxy de mesure de l'attribut Interopérabilité.

## Génération via un LLM externe (hors Cursor)

Pour rendre la méthodologie « vibe coding » reproductible et indépendante de l'IDE,
`scripts/generate_with_llm.py` envoie directement un prompt à un LLM externe — un modèle
déployé sur **Azure AI Foundry** (cloud, via son endpoint unifié compatible OpenAI) ou un
**LLM local** (ex. Ollama, on-prem) — et enregistre sa réponse telle quelle, sans révision
humaine. Cela permet de générer la rédaction d'un projet médical (« projet X », ex. la
gestion de rendez-vous médicaux ou toute autre variante) en une seule commande, en dehors
de tout agent Cursor.

Le prompt utilisé est défini dans `[docs/prompts/redaction-projet-medical.md](docs/prompts/redaction-projet-medical.md)` (modifiable) et demande au LLM de rédiger : problème/utilisateurs, modèle de données, fonctionnalités, architecture, code source et limites connues.

### Configuration

```powershell
pip install -r scripts/requirements.txt
Copy-Item .env.example .env
# éditer .env avec l'endpoint/clé de votre projet Azure AI Foundry, ou l'URL de votre LLM local (Ollama, etc.)
```

### Utilisation

```powershell
# Via Azure AI Foundry
python scripts/generate_with_llm.py --provider azure `
  --project-name "Gestion de rendez-vous médicaux" `
  --output case-study/variant-a-vibe-coding/GENERATED_DRAFT.md

# Via un LLM local (ex. Ollama démarré sur http://localhost:11434)
python scripts/generate_with_llm.py --provider local --model llama3.1 `
  --project-name "Suivi de patients chroniques" `
  --project-description "Suivi de la glycémie avec alertes en cas de valeur anormale" `
  --output docs/drafts/suivi-chronique.md
```

Le fournisseur `local` est particulièrement pertinent pour le domaine de la santé : il
garde les prompts (et d'éventuelles données) entièrement on-prem, ce qui évite les
préoccupations de confidentialité soulevées dans
`[docs/etat-de-lart-outils-ia.md](docs/etat-de-lart-outils-ia.md)`.

## Démarrage rapide

```powershell
# Lancer SonarQube localement pour analyser les 2 variantes
docker compose -f case-study/docker-compose.sonarqube.yml up -d

# Variante A
cd case-study/variant-a-vibe-coding
pip install -r requirements.txt
python -m hypercorn app.main:app --reload --bind 127.0.0.1:8001

# Variante B (dans un autre terminal)
cd case-study/variant-b-hybrid
pip install -r requirements.txt -r requirements-dev.txt
python -m hypercorn app.main:app --reload --bind 127.0.0.1:8002
pytest --cov=app
```

## Prochaines étapes

1. Compléter `docs/etat-de-lart-outils-ia.md` avec le comparatif des outils.
2. Implémenter les fonctionnalités du cahier des charges dans `variant-a-vibe-coding`
  en utilisant volontairement une approche "prompt-only" (peu/pas de révision).
3. Implémenter les *mêmes* fonctionnalités dans `variant-b-hybrid` avec TDD, revue de
  code systématique et respect du quality gate SonarQube.
4. Lancer l'analyse comparative (`scripts/compare_metrics.py`) et documenter les résultats
  dans le rapport final.

