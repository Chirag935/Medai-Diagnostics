@echo off
REM ==========================================
REM MedAI Health Companion - Start Script
REM Starts Backend + Frontend
REM ==========================================

echo.
echo  ==========================================
echo   MedAI Health Companion - Starting...
echo  ==========================================
echo.

REM --- Check Python 3.11 ---
echo [1/6] Checking Python 3.11...
py -3.11 --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python 3.11 not found!
    pause
    exit /b 1
)
echo       OK

REM --- Check Node ---
echo [2/6] Checking Node.js...
node --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Node.js not found!
    pause
    exit /b 1
)
echo       OK

REM --- Setup Python 3.11 venv ---
echo [3/6] Setting up backend...
if not exist ".venv311\Scripts\python.exe" (
    echo       Creating Python 3.11 virtual environment...
    py -3.11 -m venv .venv311
    call .venv311\Scripts\activate.bat
    python -m pip install --upgrade pip setuptools wheel >nul 2>&1
    pip install -r backend\requirements.txt
    if errorlevel 1 (
        echo [ERROR] Backend install failed!
        pause
        exit /b 1
    )
) else (
    call .venv311\Scripts\activate.bat
)
echo       Backend ready

REM --- Train new AI Health Companion models if missing ---
echo [4/6] Checking AI Health Companion models...
if not exist "backend\models\symptom_disease_model.pkl" (
    echo       Training Smart Symptom Checker model...
    echo       Downloading datasets and generating Random Forest classifier...
    pushd backend
    python train_symptom_model.py
    popd
)
if not exist "backend\models\skin_disease_model.h5" (
    echo       Generating Skin Infection CNN model...
    pushd backend
    python train_skin_model.py
    popd
)
echo       Health Companion models ready

REM --- Setup frontend ---
echo [5/6] Setting up frontend...
if not exist "frontend\node_modules\next\package.json" (
    echo       Installing frontend packages...
    pushd frontend
    call npm install
    popd
)
echo       Frontend ready

REM --- Launch services ---
echo [6/6] Launching services...
echo.

start "MedAI Backend" cmd /k "cd /d %~dp0 && call .venv311\Scripts\activate.bat && cd backend && python main.py"
echo       Backend starting on http://localhost:8000 ...
timeout /t 5 /nobreak >nul

start "MedAI Frontend" cmd /k "cd /d %~dp0frontend && npm run dev"
echo       Frontend starting on http://localhost:3000 ...
timeout /t 10 /nobreak >nul

echo.
echo  ==========================================
echo   MedAI Health Companion is RUNNING!
echo  ==========================================
echo.
echo   Frontend:  http://localhost:3000
echo   Backend:   http://localhost:8000
echo   API Docs:  http://localhost:8000/docs
echo.

start http://localhost:3000
pause
