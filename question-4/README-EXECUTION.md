# Question 4 — Exécution de BanqueExpress

Application bancaire micro-services avec Docker Compose.

## Prérequis

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installé et en cours d'exécution

## Lancer l'application

```powershell
cd question-4
docker compose up --build
```

Attendre que tous les services affichent « Service démarré » (~30 secondes au premier lancement).

## Tester avec le script de démonstration

Dans un **autre terminal** :

```powershell
cd question-4
.\scripts\demo.ps1
```

## Tester manuellement (curl / Invoke-RestMethod)

```powershell
# Santé du gateway
Invoke-RestMethod http://localhost:3000/health

# Lister les clients
Invoke-RestMethod http://localhost:3000/api/customers

# Lister les comptes
Invoke-RestMethod http://localhost:3000/api/accounts

# Virement de 200 EUR du compte 1 vers le compte 3
Invoke-RestMethod -Method POST -Uri http://localhost:3000/api/transactions/transfer `
  -ContentType "application/json" `
  -Body '{"from_account_id": 1, "to_account_id": 3, "amount": 200, "description": "Virement test"}'

# Historique des transactions
Invoke-RestMethod http://localhost:3000/api/transactions
```

## Arrêter l'application

```powershell
docker compose down
```

Pour supprimer aussi les données :

```powershell
docker compose down -v
```

## Documentation complète

Voir [RAPPORT.md](./RAPPORT.md) pour :
- Le rôle de DevOps et des micro-services (partie a)
- Les diagrammes d'architecture (partie b)
- Les avantages et inconvénients (partie c)
