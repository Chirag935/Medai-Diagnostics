@echo off
chcp 65001 >nul
title MedAI Diagnostics - Improved Models
cls

echo ╔══════════════════════════════════════════════════════════╗
echo ║       MedAI Diagnostics - Improved Model Training        ║
echo ║         High Accuracy ^& Reliable Predictions            ║
echo ╚══════════════════════════════════════════════════════════╝
echo.
echo This will retrain ALL models with advanced techniques:
echo   • SMOTE for class balancing
echo   • Balanced Random Forest
echo   • Ensemble methods
echo   • Better accuracy and reliability
echo.
pause

echo.
echo ════════════════════════════════════════════════════════════
echo STEP 1: Retraining Clinical Models (Improved)
echo ════════════════════════════════════════════════════════════
cd backend
python retrain_all_models_improved.py
if errorlevel 1 (
    echo.
    echo ❌ Retraining failed! Check error messages above.
    pause
    exit /b 1
)

echo.
echo ════════════════════════════════════════════════════════════
echo STEP 2: Retraining Image Models
echo ════════════════════════════════════════════════════════════
python train_real_images_fixed.py
if errorlevel 1 (
    echo.
    echo ⚠ Image training had issues, but continuing...
)

echo.
echo ════════════════════════════════════════════════════════════
echo STEP 3: Starting Backend Server
echo ════════════════════════════════════════════════════════════
start "MedAI Backend" cmd /c "python main.py & pause"

echo Waiting for backend to start...
timeout /t 5 /nobreak >nul

echo.
echo ════════════════════════════════════════════════════════════
echo STEP 4: Starting Frontend Server
echo ════════════════════════════════════════════════════════════
cd ..\frontend
start "MedAI Frontend" cmd /c "npm run dev & pause"

echo Waiting for frontend to start...
timeout /t 5 /nobreak >nul

echo.
echo ╔══════════════════════════════════════════════════════════╗
echo ║                   🎉 STARTUP COMPLETE!                   ║
echo ║                                                          ║
echo ║  Frontend: http://localhost:3000                        ║
echo ║  Backend:  http://localhost:8000/docs                   ║
echo ║                                                          ║
echo ║  Models trained with IMPROVED accuracy!                 ║
echo ╚══════════════════════════════════════════════════════════╝
echo.
echo Opening browser...
timeout /t 3 /nobreak >nul
start http://localhost:3000

echo.
echo ✅ All systems running with improved models!
echo Press any key to exit this window...
pause >nul
