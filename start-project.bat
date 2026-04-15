@echo off
REM MedAI Diagnostics - Complete Start Script
REM Usage: Double-click or run in PowerShell with: .\start-project.bat

echo ==========================================
echo MedAI Diagnostics - Complete Startup
echo ==========================================
echo.

REM Check if models exist
if not exist "backend\models\diabetes_model.pkl" (
    echo [1/3] Training all models...
    echo This takes about 8-10 minutes on first run
    echo.
    cd backend
    python retrain_all_models.py
    python train_image_models.py
    cd ..
    echo.
    echo ✓ Models trained successfully!
) else (
    echo [1/3] Models already trained - skipping
)

echo.
echo [2/3] Starting Backend Server...
start "Backend Server" cmd /k "cd backend && echo Starting Backend... && python main.py && echo Backend stopped"

echo Waiting for backend (5 seconds)...
timeout /t 5 /nobreak >nul

echo.
echo [3/3] Starting Frontend...
start "Frontend Server" cmd /k "cd frontend && echo Installing dependencies (if needed)... && npm install && echo Starting Frontend... && npm run dev"

echo Waiting for frontend (5 seconds)...
timeout /t 5 /nobreak >nul

echo.
echo ==========================================
echo STARTUP COMPLETE!
echo ==========================================
echo.
echo Access the app:
echo   - Web App: http://localhost:3000
echo   - API Docs: http://localhost:8000/docs
echo.
echo To stop: Close the two terminal windows
echo.
pause

REM Open browser
start http://localhost:3000
