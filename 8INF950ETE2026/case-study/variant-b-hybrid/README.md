# Variante B — Modèle hybride (IA + revue humaine)

## Règle du jeu

1. Utiliser le(s) même(s) outil(s) IA que la variante A pour générer une première
   proposition de code, fonctionnalité par fonctionnalité (mêmes prompts de départ que
   pour A, afin d'isoler l'effet de la méthode et non de l'outil).
2. **Toujours revoir le code généré avant de le committer** : corriger le style, la
   gestion d'erreurs, la sécurité (validation des entrées, pas de données sensibles en
   log), et refactorer si nécessaire.
3. Écrire (ou demander à l'IA de générer puis valider soi-même) les tests unitaires et
   d'intégration correspondants — TDD encouragé quand c'est pratique.
4. Respecter le quality gate CI (`.github/workflows/ci.yml`) avant toute fusion :
   - couverture de tests ≥ 80 %
   - 0 vulnérabilité haute/critique (Semgrep / `pip-audit`)
   - lint (ruff) sans erreur
5. Documenter les écarts constatés par rapport à la variante A dans
   `docs/rapports-avancement/`.

## Démarrage

```powershell
pip install -r requirements.txt -r requirements-dev.txt
python -m hypercorn app.main:app --reload --bind 127.0.0.1:8002
```

## Tests et couverture

```powershell
pytest --cov=app --cov-report=term-missing
```

## Lint

```powershell
ruff check app tests
```

## Analyse SonarQube

```powershell
sonar-scanner -Dproject.settings=sonar-project.properties
```
