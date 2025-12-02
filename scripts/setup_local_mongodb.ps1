# Setup MongoDB Community Edition Locale
# Scarica e installa MongoDB da: https://www.mongodb.com/try/download/community

Write-Host "=== Setup MongoDB Locale per EarlyCare ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "PROBLEMA RILEVATO:" -ForegroundColor Yellow
Write-Host "Python 3.14 (development version) ha problemi SSL/TLS con MongoDB Atlas"
Write-Host ""
Write-Host "SOLUZIONI:" -ForegroundColor Green
Write-Host ""
Write-Host "1. SOLUZIONE RACCOMANDATA - Usa Python 3.12:" -ForegroundColor Cyan
Write-Host "   - Scarica Python 3.12 da https://www.python.org/downloads/"
Write-Host "   - Installa e usa quello per questo progetto"
Write-Host "   - Python 3.14 è ancora in beta (release ottobre 2025)"
Write-Host ""
Write-Host "2. SOLUZIONE ALTERNATIVA - MongoDB Locale:" -ForegroundColor Cyan
Write-Host "   - Scarica MongoDB Community da https://www.mongodb.com/try/download/community"
Write-Host "   - Installa e avvia: mongod --dbpath C:\data\db"
Write-Host "   - Modifica gateway_config.yaml:"
Write-Host '     connection_string: "mongodb://localhost:27017/"'
Write-Host ""
Write-Host "3. WORKAROUND TEMPORANEO - Bypass SSL:" -ForegroundColor Cyan
Write-Host "   - Uso solo per sviluppo, non per produzione!"
Write-Host ""

# Chiedi all'utente quale soluzione preferisce
Write-Host "Vuoi applicare il workaround temporaneo per bypassare SSL? (y/n): " -NoNewline
$risposta = Read-Host

if ($risposta -eq 'y') {
    Write-Host ""
    Write-Host "Applicando workaround..." -ForegroundColor Yellow
    
    # Backup del config
    Copy-Item "config\gateway_config.yaml" "config\gateway_config.yaml.backup"
    
    # Modifica config per usare parametri SSL meno restrittivi
    $configContent = @"
# Database Configuration
database:
  mongodb:
    enabled: true
    connection_string: "mongodb+srv://angelospeed2003:kjhwoP4rXR3UsnaV@mav.0zz64yh.mongodb.net/?retryWrites=true&w=majority&ssl=true&ssl_cert_reqs=CERT_NONE"
    database_name: "earlycare"
    # Workaround per Python 3.14 - NON USARE IN PRODUZIONE
    use_ssl: true
    ssl_allow_invalid_certificates: true
    server_selection_timeout_ms: 10000
"@
    
    Write-Host "✓ Backup creato: config\gateway_config.yaml.backup" -ForegroundColor Green
    Write-Host ""
    Write-Host "IMPORTANTE:" -ForegroundColor Red
    Write-Host "Questo è solo un workaround temporaneo!"
    Write-Host "Per un uso produttivo, installa Python 3.12" -ForegroundColor Yellow
}
else {
    Write-Host ""
    Write-Host "OK. Installa Python 3.12 da:" -ForegroundColor Cyan
    Write-Host "https://www.python.org/downloads/" -ForegroundColor White
}
