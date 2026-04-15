@echo off
REM MedAI Diagnostics - Complete Start Script
REM ALWAYS retrains all models on every run, then starts backend and frontend

echo ==========================================
echo MedAI Diagnostics - Complete Startup
echo ==========================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found! Please install Python 3.11+
    pause
    exit /b 1
)

REM Check Node
node --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Node.js not found! Please install Node.js 20+
    pause
    exit /b 1
)

REM Always retrain clinical models (diabetes, heart, liver, kidney, breast cancer, alzheimer)
echo.
echo ==========================================
echo RETRAINING ALL CLINICAL MODELS (IMPROVED)
echo ==========================================
echo This will train: Diabetes, Heart Disease, Liver Disease,
echo                  Kidney Disease, Breast Cancer, Alzheimer's
echo Using: SMOTE, Balanced Random Forest, Ensemble methods
echo.
cd backend
python retrain_all_models_improved.py
if errorlevel 1 (
    echo ERROR: Clinical model training failed!
    pause
    exit /b 1
)
cd ..
echo ✓ Clinical models retrained successfully (high accuracy)

REM Always retrain image models (pneumonia and malaria)
echo.
echo ==========================================
echo RETRAINING IMAGE MODELS (AUGMENTED)
echo ==========================================
echo This will train: Pneumonia and Malaria detection
echo Using: 7x data augmentation, enhanced features
echo This may take 5-8 minutes...
echo.
cd backend
python train_images_augmented.py
if errorlevel 1 (
    echo ERROR: Image model training failed!
    pause
    exit /b 1
)
cd ..
echo ✓ Image models retrained successfully (high accuracy)

REM Start Backend in new window
echo.
echo Starting Backend Server...
start "MedAI Backend" cmd /k "cd backend && python main.py"

REM Wait for backend to start
echo Waiting for backend to initialize...
timeout /t 5 /nobreak >nul

REM Check if backend is running
curl -s http://localhost:8000/health >nul 2>&1
if %errorlevel% == 0 (
    echo ✓ Backend is running on http://localhost:8000
) else (
    echo ⚠ Backend may still be starting...
)

REM Start Frontend in new window
echo.
echo Starting Frontend...
echo Installing dependencies (if needed) and starting dev server...
start "MedAI Frontend" cmd /k "cd frontend && echo Installing npm packages... && npm install && echo Starting Next.js dev server... && npm run dev"

REM Wait longer for frontend to start (npm install can take time)
echo.
echo Waiting for frontend to initialize (15 seconds)...
timeout /t 15 /nobreak >nul

REM Verify frontend is running
curl -s http://localhost:3000 >nul 2>&1
if %errorlevel% == 0 (
    echo ✓ Frontend is running on http://localhost:3000
) else (
    echo ⚠ Frontend may still be starting... waiting 10 more seconds...
    timeout /t 10 /nobreak >nul
)

echo.
echo ==========================================
echo Startup Complete!
echo ==========================================
echo.
echo Access the application:
echo   Frontend: http://localhost:3000
echo   Backend:  http://localhost:8000
echo   API Docs: http://localhost:8000/docs
echo.
echo If browser doesn't open automatically, manually visit:
echo   http://localhost:3000
echo.
start http://localhost:3000

echo.
echo To stop:
echo   - Close the backend terminal window
echo   - Close the frontend terminal window
echo.
pause
