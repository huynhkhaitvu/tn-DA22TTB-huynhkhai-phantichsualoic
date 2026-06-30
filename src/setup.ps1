#!/bin/bash
# SETUP SCRIPT - Windows PowerShell

echo "===================================="
echo "Setup C Code Analyzer System"
echo "===================================="

# Check Python
echo ""
echo "[1/4] Checking Python..."
python --version
if ($LASTEXITCODE -ne 0) {
    echo "❌ Python not found. Please install Python 3.12+"
    exit 1
}
echo "✅ Python found"

# Check GCC
echo ""
echo "[2/4] Checking GCC..."
gcc --version
if ($LASTEXITCODE -ne 0) {
    echo "❌ GCC not found. Please install MinGW-w64"
    echo "   See INSTALL_GCC.md for instructions"
    exit 1
}
echo "✅ GCC found"

# Setup Virtual Environment
echo ""
echo "[3/4] Setting up Python virtual environment..."
cd backend
if (!(Test-Path "venv")) {
    python -m venv venv
    echo "✅ Virtual environment created"
} else {
    echo "✅ Virtual environment already exists"
}

# Activate venv
.\venv\Scripts\Activate.ps1

# Install dependencies
echo ""
echo "[4/4] Installing Python packages..."
pip install -r requirements.txt
echo "✅ Packages installed"

# Setup .env
if (!(Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    echo ""
    echo "⚠️  .env file created. Please add your Gemini API key:"
    echo "   1. Open backend\.env"
    echo "   2. Replace 'your_api_key_here' with your actual API key"
    echo "   3. Get API key from https://aistudio.google.com/app/apikey"
} else {
    echo "✅ .env already exists"
}

echo ""
echo "===================================="
echo "Setup Complete! ✅"
echo "===================================="
echo ""
echo "Next steps:"
echo "1. Add Gemini API key to backend\.env"
echo "2. Run: python app.py (from backend folder with venv activated)"
echo "3. Open frontend\index.html in browser"
echo ""
