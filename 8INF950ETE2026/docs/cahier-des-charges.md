# Cahier des charges — Système de gestion de rendez-vous médicaux

Cette spécification est **commune aux deux variantes** (A et B) afin de garantir une
comparaison équitable : seule la méthode de développement change, pas les exigences
fonctionnelles.

## Contexte

Une clinique souhaite un petit système permettant de gérer ses patients, ses médecins et
la prise de rendez-vous, avec des règles simples de disponibilité et de confidentialité
des données de santé.

## Entités du domaine

### Patient
- `id`, `nom`, `prénom`, `date_naissance`, `courriel`, `téléphone`
- `numéro_assurance_maladie` (donnée sensible — doit être masquée dans les logs et les
  réponses API non autorisées)

### Médecin
- `id`, `nom`, `prénom`, `spécialité`, `courriel`
- Disponibilités hebdomadaires (jours + plages horaires)

### RendezVous (Appointment)
- `id`, `patient_id`, `médecin_id`, `date_heure_début`, `durée_minutes`, `statut`
  (`planifié`, `confirmé`, `annulé`, `terminé`)
- `motif` (texte libre court)

## Exigences fonctionnelles (à implémenter identiquement dans les 2 variantes)

1. **CRUD Patients** : créer, lire, lister, mettre à jour, supprimer (soft delete).
2. **CRUD Médecins** : créer, lire, lister, mettre à jour, supprimer.
3. **Prise de rendez-vous** :
   - Un rendez-vous ne peut être créé que si le médecin est disponible au créneau demandé.
   - Impossible de créer deux rendez-vous qui se chevauchent pour le même médecin.
   - Impossible de créer un rendez-vous dans le passé.
4. **Annulation de rendez-vous** avec motif obligatoire.
5. **Recherche de créneaux disponibles** pour un médecin donné sur une période donnée.
6. **Endpoint de santé** (`/health`) pour le monitoring.
7. **Validation des données** : formats de courriel, téléphone, dates.
8. **Journalisation** : aucune donnée sensible (NAM, nom complet) en clair dans les logs.

## Exigences non fonctionnelles (servent de base à la grille qualité ISO 25010)

- **Sécurité** : authentification par jeton (JWT) sur les routes sensibles, validation
  stricte des entrées, pas de secrets en dur dans le code.
- **Performance** : temps de réponse < 200 ms pour les opérations CRUD simples (P95).
- **Maintenabilité** : couverture de tests ≥ 80 % pour la variante B (aucune cible
  imposée pour la variante A — c'est justement ce qui est mesuré).
- **Interopérabilité** : exposer une spécification OpenAPI complète et cohérente.
- **Portabilité** : l'application doit démarrer via Docker sans configuration manuelle.

## Hors périmètre (volontairement, pour garder l'étude gérable)

- Facturation / paiement
- Interface graphique riche (une API REST + documentation Swagger suffit)
- Intégration FHIR complète (peut être une piste d'extension si le temps le permet)

## Contrat d'API de référence

Voir `case-study/variant-b-hybrid/app` une fois complété pour le schéma OpenAPI de
référence — les deux variantes doivent exposer des routes équivalentes :

```
GET    /health
POST   /patients
GET    /patients
GET    /patients/{id}
PUT    /patients/{id}
DELETE /patients/{id}
POST   /medecins
GET    /medecins
GET    /medecins/{id}
GET    /medecins/{id}/creneaux-disponibles
POST   /rendez-vous
GET    /rendez-vous
GET    /rendez-vous/{id}
PATCH  /rendez-vous/{id}/annuler
```
