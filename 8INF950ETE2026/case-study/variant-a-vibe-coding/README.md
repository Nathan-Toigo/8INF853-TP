# Variante A — Vibe coding pur

## Règle du jeu (important pour la validité de l'étude)

Cette variante doit être développée en suivant **strictement** cette méthode, sinon la
comparaison avec la variante B n'a plus de sens :

1. Utiliser un outil IA génératif (Cursor, Copilot ou Claude Code — choisir et le noter
   dans `docs/etat-de-lart-outils-ia.md`).
2. Décrire chaque fonctionnalité du [cahier des charges](../../docs/cahier-des-charges.md)
   par un prompt en langage naturel.
3. **Accepter les suggestions de code sans les corriger**, même si elles semblent
   imparfaites (sauf si le code ne compile/ne s'exécute pas du tout — dans ce cas,
   redemander à l'IA de corriger, mais ne pas corriger soi-même).
4. Ne pas écrire de tests manuellement. Si l'IA en génère spontanément, les garder tels
   quels.
5. Consigner chaque prompt utilisé et un résumé de ce qui a été généré dans
   `PROMPTS_LOG.md` (à créer) — ces traces serviront pour `docs/risques-vibe-coding.md`.

## Démarrage

```powershell
pip install -r requirements.txt
python -m hypercorn app.main:app --reload --bind 127.0.0.1:8001
```

L'application expose `/health` et sera enrichie au fil des prompts avec les routes du
cahier des charges (patients, médecins, rendez-vous).

## Analyse SonarQube

Prérequis : SonarQube démarré (`docker compose -f ../docker-compose.sonarqube.yml up -d`)
et un jeton généré sur http://localhost:9000 (My Account → Security).

```powershell
$env:SONAR_TOKEN = "votre_jeton"
sonar-scanner -D project.settings=sonar-project.properties -D sonar.host.url=http://localhost:9000 -D sonar.token=$env:SONAR_TOKEN
```

Sous PowerShell, l'espace après `-D` est obligatoire. Résultats :
http://localhost:9000/dashboard?id=8inf950-variant-a-vibe-coding
