# EarlyCare Gateway - Full Application Startup (Backend + Frontend)
# Run: .\start_webapp.ps1

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  🏥 EarlyCare Gateway - Medical Access & Vision" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

$backendPath = "$PSScriptRoot\backend"
$frontendPath = "$PSScriptRoot\frontend"

# Check paths
if (-not (Test-Path $backendPath)) {
    Write-Host "❌ Backend folder not found" -ForegroundColor Red
    exit 1
}

if (-not (Test-Path $frontendPath)) {
    Write-Host "❌ Frontend folder not found" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Backend path: $backendPath" -ForegroundColor Green
Write-Host "✅ Frontend path: $frontendPath" -ForegroundColor Green
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

Write-Host "🚀 Starting Backend (Flask)..." -ForegroundColor Cyan
$backendProcess = Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$backendPath'; python run_webapp.py" -PassThru

Write-Sleep -Seconds 3

Write-Host "🚀 Starting Frontend (Vite)..." -ForegroundColor Cyan
$frontendProcess = Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$frontendPath'; npm run dev" -PassThru

Write-Host ""
Write-Host "============================================================" -ForegroundColor Green
Write-Host "✅ Application Started!" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Green
Write-Host ""
Write-Host "Backend:  http://localhost:5000" -ForegroundColor Cyan
Write-Host "Frontend: http://localhost:5173" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press CTRL+C to stop" -ForegroundColor Yellow
