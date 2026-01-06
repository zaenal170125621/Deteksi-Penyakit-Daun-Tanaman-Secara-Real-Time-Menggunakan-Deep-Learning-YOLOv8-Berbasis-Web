# Quick Setup Script for Windows PowerShell
# Run this script to set up the project quickly

Write-Host "🌿 Plant Leaf Disease Detector - Setup Script" -ForegroundColor Green
Write-Host "=============================================" -ForegroundColor Green
Write-Host ""

# Check Python version
Write-Host "📌 Checking Python version..." -ForegroundColor Yellow
$pythonVersion = python --version 2>&1
if ($pythonVersion -match "Python 3\.([0-9]+)") {
    $minorVersion = [int]$matches[1]
    if ($minorVersion -ge 10) {
        Write-Host "✓ Python version: $pythonVersion" -ForegroundColor Green
    } else {
        Write-Host "✗ Python 3.10+ required, found: $pythonVersion" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "✗ Python not found or version check failed" -ForegroundColor Red
    exit 1
}

# Create virtual environment
Write-Host ""
Write-Host "📌 Creating virtual environment..." -ForegroundColor Yellow
if (Test-Path "venv") {
    Write-Host "⚠ Virtual environment already exists, skipping..." -ForegroundColor Yellow
} else {
    python -m venv venv
    Write-Host "✓ Virtual environment created" -ForegroundColor Green
}

# Activate virtual environment
Write-Host ""
Write-Host "📌 Activating virtual environment..." -ForegroundColor Yellow
& ".\venv\Scripts\Activate.ps1"
Write-Host "✓ Virtual environment activated" -ForegroundColor Green

# Upgrade pip
Write-Host ""
Write-Host "📌 Upgrading pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip --quiet
Write-Host "✓ Pip upgraded" -ForegroundColor Green

# Install requirements
Write-Host ""
Write-Host "📌 Installing dependencies (this may take a few minutes)..." -ForegroundColor Yellow
pip install -r requirements.txt
Write-Host "✓ Dependencies installed" -ForegroundColor Green

# Check for model
Write-Host ""
Write-Host "📌 Checking for trained model..." -ForegroundColor Yellow
if (Test-Path "models\best.pt") {
    Write-Host "✓ Model found at models\best.pt" -ForegroundColor Green
} else {
    Write-Host "⚠ No model found at models\best.pt" -ForegroundColor Yellow
    Write-Host "  You need to train a model or place a pre-trained model in models\" -ForegroundColor Yellow
    Write-Host "  See README.md for training instructions" -ForegroundColor Yellow
}

# Get IP address
Write-Host ""
Write-Host "📌 Your network information:" -ForegroundColor Yellow
$ipAddress = (Get-NetIPAddress -AddressFamily IPv4 -InterfaceAlias "Wi-Fi" -ErrorAction SilentlyContinue).IPAddress
if ($ipAddress) {
    Write-Host "  Local IP: $ipAddress" -ForegroundColor Cyan
    Write-Host "  Access from phone: http://$ipAddress:8000" -ForegroundColor Cyan
} else {
    # Try to get any IPv4 address
    $ipAddress = (Get-NetIPAddress -AddressFamily IPv4 | Where-Object {$_.IPAddress -notlike "127.*"} | Select-Object -First 1).IPAddress
    if ($ipAddress) {
        Write-Host "  Local IP: $ipAddress" -ForegroundColor Cyan
        Write-Host "  Access from phone: http://$ipAddress:8000" -ForegroundColor Cyan
    } else {
        Write-Host "  Could not detect IP address automatically" -ForegroundColor Yellow
        Write-Host "  Run 'ipconfig' to find your IPv4 address" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "=============================================" -ForegroundColor Green
Write-Host "✓ Setup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Train model (if not done): See README.md" -ForegroundColor White
Write-Host "2. Start server: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload" -ForegroundColor White
Write-Host "3. Open browser: http://localhost:8000 (laptop) or http://<IP>:8000 (phone)" -ForegroundColor White
Write-Host ""
Write-Host "For firewall issues, run as Administrator:" -ForegroundColor Yellow
Write-Host "New-NetFirewallRule -DisplayName 'Plant Detector' -Direction Inbound -LocalPort 8000 -Protocol TCP -Action Allow" -ForegroundColor White
Write-Host ""
