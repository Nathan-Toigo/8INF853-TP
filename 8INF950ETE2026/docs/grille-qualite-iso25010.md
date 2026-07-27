# Grille d'analyse qualité — ISO/IEC 25010

Cette grille définit, pour chaque attribut retenu, la métrique mesurée, l'outil utilisé
et la méthode de collecte. Elle sert de base à la comparaison entre `variant-a-vibe-coding`
et `variant-b-hybrid`.

| Attribut ISO 25010 | Sous-caractéristique | Métrique | Outil | Cible / seuil |
|---|---|---|---|---|
| Adéquation fonctionnelle | Exhaustivité | % des exigences du cahier des charges implémentées | Revue manuelle | 100 % |
| Fiabilité | Maturité | Nombre de bugs trouvés en test manuel exploratoire | Revue manuelle | Le plus bas possible |
| Fiabilité | Tolérance aux fautes | Codes HTTP corrects sur entrées invalides | Tests d'intégration | 100 % des cas couverts |
| Performance | Comportement temporel | Latence P95 des endpoints CRUD | k6 / Locust | < 200 ms |
| Compatibilité | Interopérabilité | Conformité du schéma OpenAPI, cohérence des contrats | `openapi-spec-validator` | 0 erreur |
| Sécurité | Confidentialité | Nb de vulnérabilités (CWE) détectées | SonarQube Security, Semgrep | 0 vulnérabilité critique/haute |
| Sécurité | Confidentialité | Fuite de données sensibles dans les logs | Revue manuelle + grep | 0 occurrence |
| Compatibilité (dépendances) | — | Vulnérabilités connues dans les dépendances | `pip-audit` / Trivy | 0 CVE haute/critique |
| Maintenabilité | Modularité | Complexité cyclomatique moyenne | SonarQube | ≤ 10 par fonction |
| Maintenabilité | Testabilité | Couverture de tests (lignes/branches) | `coverage.py` | ≥ 80 % (cible B seulement) |
| Maintenabilité | — | Dette technique (temps estimé) | SonarQube | Comparaison relative A vs B |
| Maintenabilité | — | Nombre de "code smells" | SonarQube | Comparaison relative A vs B |
| Portabilité | Adaptabilité | Démarrage réussi via `docker compose up` sans configuration | Test manuel | Succès |

## Méthode de collecte

1. Lancer SonarQube (`case-study/docker-compose.sonarqube.yml`).
2. Exécuter l'analyse (`sonar-scanner`) dans chaque variante — voir les fichiers
   `sonar-project.properties` respectifs.
3. Exécuter `scripts/compare_metrics.py` pour extraire les métriques via l'API SonarQube
   et générer un tableau comparatif (CSV/Markdown) à insérer dans le rapport final.
4. Compléter les métriques non couvertes par SonarQube (performance, sécurité des
   dépendances, interopérabilité) manuellement ou via les outils listés ci-dessus.

## Hypothèses à tester (à ajuster au fil de la revue de littérature)

- H1 : la variante A (vibe coding pur) présente significativement plus de "code smells"
  et une dette technique plus élevée que la variante B.
- H2 : la variante A présente plus de vulnérabilités de sécurité détectées.
- H3 : la couverture de tests de la variante A est quasi nulle en l'absence de contrainte.
- H4 : le temps de développement perçu est plus court pour A, mais le temps total
  (développement + correction) converge vers B une fois les défauts corrigés.
