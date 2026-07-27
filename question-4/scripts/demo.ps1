$BaseUrl = "http://localhost:3000"

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  BanqueExpress - Demo Micro-services" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

function Wait-ForGateway {
    Write-Host "Attente du demarrage du gateway..." -ForegroundColor Yellow
    for ($i = 0; $i -lt 30; $i++) {
        try {
            $health = Invoke-RestMethod -Uri "$BaseUrl/health" -TimeoutSec 2
            if ($health.status -eq "ok") {
                Write-Host "Gateway pret!" -ForegroundColor Green
                return $true
            }
        } catch { }
        Start-Sleep -Seconds 2
    }
    Write-Host "ERREUR: Le gateway n'est pas accessible sur $BaseUrl" -ForegroundColor Red
    Write-Host "Lancez d'abord: docker compose up --build" -ForegroundColor Red
    exit 1
}

Wait-ForGateway

Write-Host ""
Write-Host "--- 1. Sante des services ---" -ForegroundColor White
$gateway = Invoke-RestMethod "$BaseUrl/health"
Write-Host "Gateway: $($gateway.status)"

Write-Host ""
Write-Host "--- 2. Liste des clients ---" -ForegroundColor White
$customers = Invoke-RestMethod "$BaseUrl/api/customers"
$customers | ForEach-Object { Write-Host "  [$($_.id)] $($_.first_name) $($_.last_name) - $($_.email)" }

Write-Host ""
Write-Host "--- 3. Liste des comptes ---" -ForegroundColor White
$accounts = Invoke-RestMethod "$BaseUrl/api/accounts"
$accounts | ForEach-Object { Write-Host "  [$($_.id)] $($_.account_number) - Solde: $($_.balance) $($_.currency)" }

Write-Host ""
Write-Host "--- 4. Depot de 500 EUR sur le compte 3 ---" -ForegroundColor White
$deposit = Invoke-RestMethod -Method POST -Uri "$BaseUrl/api/transactions/deposit" `
    -ContentType "application/json" `
    -Body '{"account_id": 3, "amount": 500, "description": "Depot demo"}'
Write-Host "  Transaction #$($deposit.transaction.id) - Nouveau solde: $($deposit.account.balance) EUR"

Write-Host ""
Write-Host "--- 5. Virement de 200 EUR (compte 1 -> compte 3) ---" -ForegroundColor White
$transfer = Invoke-RestMethod -Method POST -Uri "$BaseUrl/api/transactions/transfer" `
    -ContentType "application/json" `
    -Body '{"from_account_id": 1, "to_account_id": 3, "amount": 200, "description": "Virement demo"}'
Write-Host "  Transaction #$($transfer.transaction.id)"
Write-Host "  Compte source: $($transfer.from_account.balance) EUR"
Write-Host "  Compte dest:   $($transfer.to_account.balance) EUR"

Write-Host ""
Write-Host "--- 6. Retrait de 50 EUR du compte 2 ---" -ForegroundColor White
$withdraw = Invoke-RestMethod -Method POST -Uri "$BaseUrl/api/transactions/withdraw" `
    -ContentType "application/json" `
    -Body '{"account_id": 2, "amount": 50, "description": "Retrait demo"}'
Write-Host "  Transaction #$($withdraw.transaction.id) - Nouveau solde: $($withdraw.account.balance) EUR"

Write-Host ""
Write-Host "--- 7. Historique des transactions ---" -ForegroundColor White
$transactions = Invoke-RestMethod "$BaseUrl/api/transactions"
$transactions | Select-Object -First 5 | ForEach-Object {
    Write-Host "  [$($_.type)] $($_.amount) EUR - $($_.description)"
}

Write-Host ""
Write-Host "--- 8. Creation d'un nouveau client ---" -ForegroundColor White
$newCustomer = Invoke-RestMethod -Method POST -Uri "$BaseUrl/api/customers" `
    -ContentType "application/json" `
    -Body '{"first_name": "Claire", "last_name": "Bernard", "email": "claire.bernard@email.com"}'
Write-Host "  Client cree: [$($newCustomer.id)] $($newCustomer.first_name) $($newCustomer.last_name)"

Write-Host ""
Write-Host "============================================" -ForegroundColor Green
Write-Host "  DEMO TERMINEE AVEC SUCCES" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Green
Write-Host ""
