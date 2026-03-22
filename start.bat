@echo off
REM ===========================================
REM Startup Script untuk Google Maps Location API
REM Windows Batch Script
REM ===========================================

echo.
echo ╔════════════════════════════════════════════╗
echo ║  Google Maps Location API - Startup        ║
echo ╚════════════════════════════════════════════╝
echo.

REM Check if .env exists
if not exist ".env" (
    echo [WARNING] File .env tidak ditemukan!
    echo [INFO] Menyalin dari .env.example...
    copy .env.example .env
    echo [ACTION] Edit file .env dan isi API Keys sebelum melanjutkan
    echo.
    pause
    exit /b 1
)

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python tidak ditemukan!
    echo [INFO] Install Python 3.9+ dari python.org
    pause
    exit /b 1
)

REM Navigate to backend directory
cd backend

REM Check if virtual environment exists
if not exist "venv" (
    echo [INFO] Membuat virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo [INFO] Mengaktifkan virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo [INFO] Installing dependencies...
pip install -r requirements.txt -q

REM Start the server
echo.
echo ╔════════════════════════════════════════════╗
echo ║  Starting FastAPI Server...                ║
echo ║  API Docs: http://localhost:8000/docs      ║
echo ║  Health:   http://localhost:8000/health    ║
echo ╚════════════════════════════════════════════╝
echo.

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
