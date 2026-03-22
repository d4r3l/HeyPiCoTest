#!/bin/bash
# ===========================================
# Startup Script untuk Google Maps Location API
# Linux/Mac Bash Script
# ===========================================

echo ""
echo "╔════════════════════════════════════════════╗"
echo "║  Google Maps Location API - Startup        ║"
echo "╚════════════════════════════════════════════╝"
echo ""

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "[WARNING] File .env tidak ditemukan!"
    echo "[INFO] Menyalin dari .env.example..."
    cp .env.example .env
    echo "[ACTION] Edit file .env dan isi API Keys sebelum melanjutkan"
    echo ""
    exit 1
fi

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python tidak ditemukan!"
    echo "[INFO] Install Python 3.9+"
    exit 1
fi

# Navigate to backend directory
cd backend

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "[INFO] Membuat virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "[INFO] Mengaktifkan virtual environment..."
source venv/bin/activate

# Install dependencies
echo "[INFO] Installing dependencies..."
pip install -r requirements.txt -q

# Start the server
echo ""
echo "╔════════════════════════════════════════════╗"
echo "║  Starting FastAPI Server...                ║"
echo "║  API Docs: http://localhost:8000/docs      ║"
echo "║  Health:   http://localhost:8000/health    ║"
echo "╚════════════════════════════════════════════╝"
echo ""

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
