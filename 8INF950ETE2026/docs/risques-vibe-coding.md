# Risques du vibe coding

Ce document recense les risques identifiés lors de la revue de littérature et observés
concrètement lors de l'implémentation de `variant-a-vibe-coding`.

## Catégories de risques

### 1. Hallucinations
- Appel à des fonctions/bibliothèques inexistantes ou mal nommées.
- Suggestions basées sur une version d'API obsolète.
- Logique métier plausible mais incorrecte (ex. règle de chevauchement de rendez-vous
  mal implémentée).

*Exemples concrets observés (à remplir pendant l'implémentation) :*

| # | Prompt utilisé | Suggestion générée | Problème constaté | Correction apportée |
|---|---|---|---|---|
| 1 | | | | |

### 2. Vulnérabilités de sécurité
- Injection (SQL, etc.) si les entrées ne sont pas paramétrées.
- Absence de validation des entrées.
- Secrets/clés en dur dans le code généré.
- Exposition de données sensibles (NAM, données de santé) dans les réponses API ou logs.

### 3. Absence de tests
- Le code généré par vibe coding n'inclut généralement pas de tests, sauf demande explicite.
- Risque de régressions silencieuses lors de modifications ultérieures.

### 4. Dette technique
- Duplication de code entre endpoints similaires générés indépendamment.
- Manque de cohérence architecturale (styles de code différents d'un prompt à l'autre).

## Méthode de mesure

- Vulnérabilités : SonarQube Security Hotspots + Semgrep + `pip-audit`.
- Hallucinations : journal manuel tenu pendant le développement (tableau ci-dessus).
- Absence de tests : couverture mesurée avec `coverage.py` (attendu proche de 0 % pour A).
- Dette technique : indicateur SonarQube "Technical Debt" (temps estimé de correction).

## Lien avec les garde-fous

Chaque risque identifié ici doit être associé à un garde-fou correspondant dans
`case-study/variant-b-hybrid` (ex. : quality gate SonarQube bloquant en cas de
vulnérabilité haute/critique, couverture minimale obligatoire en CI, revue de code
obligatoire avant fusion).
