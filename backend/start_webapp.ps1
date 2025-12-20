# EarlyCare Gateway - Avvio Web App
# PowerShell script per avviare l'applicazione web

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  🏥 EarlyCare Gateway - Medical Access & Vision" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Check if Python is installed
$pythonCmd = $null
try {
    if (Get-Command python -ErrorAction SilentlyContinue) {
        $pythonCmd = "python"
    } elseif (Get-Command python3 -ErrorAction SilentlyContinue) {
        $pythonCmd = "python3"
    }
} catch {
    Write-Host "❌ Python non trovato. Installare Python 3.8 o superiore." -ForegroundColor Red
    exit 1
}

Write-Host "✅ Python trovato: $pythonCmd" -ForegroundColor Green
Write-Host ""

# Check if virtual environment exists
if (Test-Path "venv\Scripts\Activate.ps1") {
    Write-Host "📦 Attivazione ambiente virtuale..." -ForegroundColor Yellow
    & "venv\Scripts\Activate.ps1"
} else {
    Write-Host "⚠️  Nessun ambiente virtuale trovato. Creazione in corso..." -ForegroundColor Yellow
    & $pythonCmd -m venv venv
    & "venv\Scripts\Activate.ps1"
    Write-Host "✅ Ambiente virtuale creato" -ForegroundColor Green
}

Write-Host ""

# Install/update requirements
Write-Host "📦 Installazione dipendenze..." -ForegroundColor Yellow
& $pythonCmd -m pip install --upgrade pip -q
& $pythonCmd -m pip install -r requirements.txt -q

Write-Host "✅ Dipendenze installate" -ForegroundColor Green
Write-Host ""

# Start the web application
Write-Host "🚀 Avvio applicazione web..." -ForegroundColor Cyan
Write-Host ""
Write-Host "L'applicazione sarà disponibile su:" -ForegroundColor Green
Write-Host "  → http://localhost:5000" -ForegroundColor White
Write-Host "  → http://127.0.0.1:5000" -ForegroundColor White
Write-Host ""
Write-Host "Premi CTRL+C per terminare l'applicazione" -ForegroundColor Yellow
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

& $pythonCmd run_webapp.py
