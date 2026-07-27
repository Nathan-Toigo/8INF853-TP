# État de l'art — Modèles générateurs de code IA

Comparatif à compléter en vue de justifier le(s) choix d'outil(s) utilisé(s) pour la
variante A (`variant-a-vibe-coding`) de l'étude de cas.

## Grille comparative

| Critère | Cursor | GitHub Copilot | Claude Code | (autre : Windsurf/Cody) |
|---|---|---|---|---|
| Mode agentique (édition multi-fichiers, exécution de commandes) | | | | |
| Gestion du contexte (taille, indexation du repo) | | | | |
| Génération de tests automatique | | | | |
| Explicabilité des suggestions | | | | |
| Exécution locale / on-prem possible (pertinent pour données de santé) | | | | |
| Intégration CI/CD | | | | |
| Modèle(s) sous-jacent(s) | | | | |
| Coût | | | | |
| Adoption en industrie (sources) | | | | |

## Considérations spécifiques au domaine de la santé

- Traitement des données sensibles : les prompts/contexte envoyés à un service cloud
  peuvent-ils contenir des données de patients réelles ? (Réponse attendue : non — utiliser
  uniquement des données fictives/synthétiques dans ce projet.)
- Conformité réglementaire (Loi 25 au Québec, HIPAA aux É.-U.) — pertinence pour un futur
  déploiement réel, même si hors périmètre direct du projet.

## Sources à consulter

- Documentation officielle de chaque outil
- Études industrielles (GitHub Octoverse, Stack Overflow Developer Survey, rapports
  GitClear/DX sur la qualité du code généré par IA)
- Articles académiques (IEEE, ACM) sur l'impact de l'IA générative sur la qualité logicielle

> À compléter avec les références précises (auteurs, année, lien) dans la section
> Références du rapport final.
