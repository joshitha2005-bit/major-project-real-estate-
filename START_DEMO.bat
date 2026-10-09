@echo off
REM ============================================================================
REM GEOSMART PRICE AI -- 1-CLICK CLEAN MACHINE REPRODUCIBLE DEMO LAUNCHER
REM ============================================================================
REM This script automates reproducible setup on a clean Windows machine:
REM   1. Checks Python and Node.js prerequisites
REM   2. Initializes local .env from .env.example if missing
REM   3. Installs Python dependencies (PyTorch, XGBoost, SHAP, FastAPI)
REM   4. Installs Frontend dependencies (React, Vite, Leaflet, Lucide)
REM   5. Initializes local demo SQLite database and seeds golden records
REM   6. Concurrently starts Backend (port 8000) and Frontend (port 5173)
REM ============================================================================

title GeoSmart Price AI - Demo Launcher
echo ============================================================================
echo   GEOSMART PRICE AI: MULTIMODAL REAL ESTATE VALUATION PLATFORM
echo ============================================================================
echo.

REM 1. Verify Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in system PATH.
    echo Please install Python 3.10+ (Recommended: 3.11 or 3.13) from https://www.python.org/
    pause
    exit /b 1
)
echo [OK] Python detected:
python --version

REM 2. Verify Node.js
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Node.js is not installed or not in system PATH.
    echo Please install Node.js 18+ (Recommended: 20 or 22) from https://nodejs.org/
    pause
    exit /b 1
)
echo [OK] Node.js detected:
node --version

REM 3. Setup .env from .env.example if missing
if not exist ".env" (
    if exist ".env.example" (
        echo [INFO] Creating local .env from .env.example...
        copy ".env.example" ".env" >nul
        echo [OK] .env created with safe defaults.
    )
)

if not exist "backend\.env" (
    if exist "backend\.env.example" (
        copy "backend\.env.example" "backend\.env" >nul
    )
)

REM 4. Install Python Dependencies
echo.
echo [INFO] Installing / verifying backend dependencies...
pip install -r backend\requirements.txt --quiet
if %errorlevel% neq 0 (
    echo [WARNING] Encountered warnings during pip install. Continuing...
)

REM 5. Install Frontend Dependencies
echo.
echo [INFO] Installing / verifying frontend npm dependencies...
cd frontend
call npm install --quiet
cd ..

REM 6. Initialize Demo Database & Verify Golden ML Artifacts
echo.
echo [INFO] Initializing reproducible demo database...
python backend\init_demo_db.py
if %errorlevel% neq 0 (
    echo [ERROR] Database initialization failed.
    pause
    exit /b 1
)

REM 7. Launch Backend API Server
echo.
echo [INFO] Launching FastAPI Backend Server on http://localhost:8000 ...
start "GeoSmart AI - Backend API" cmd /k "cd backend && uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload"

REM 8. Launch Frontend Vite Dev Server
echo [INFO] Launching Frontend UI on http://localhost:5173 ...
start "GeoSmart AI - Frontend UI" cmd /k "cd frontend && npm run dev"

REM 9. Wait briefly and open browser
echo.
echo [INFO] Waiting for servers to initialize...
timeout /t 5 /nobreak >nul
start http://localhost:5173

echo.
echo ============================================================================
echo   DEMO LAUNCHED SUCCESSFULLY!
echo   Frontend UI : http://localhost:5173
echo   Backend API : http://localhost:8000
echo   API Docs    : http://localhost:8000/docs
echo ============================================================================
echo.
echo Press any key to close this launcher window (servers will remain running).
pause >nul
