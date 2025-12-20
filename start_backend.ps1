# EarlyCare Gateway - Backend Startup Script (from root)
# Run: .\start_backend.ps1

$backendPath = "$PSScriptRoot\backend"
$pythonScript = "$backendPath\run_webapp.py"

Write-Host "================================" -ForegroundColor Cyan
Write-Host "🏥 EarlyCare Gateway Backend" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# Check if backend folder exists
if (-not (Test-Path $backendPath)) {
    Write-Host "❌ Backend folder not found: $backendPath" -ForegroundColor Red
    exit 1
}

Write-Host "📁 Backend path: $backendPath" -ForegroundColor Green
Write-Host "🚀 Starting Flask server..." -ForegroundColor Yellow
Write-Host ""

# Run Python from backend directory
Push-Location $backendPath
try {
    python run_webapp.py
} finally {
    Pop-Location
}
