# MedAI Diagnostics - Quick Command Reference

Copy-paste these commands to train models and run the project anytime.

---

## 🏋️ Step 1: Train All Models

### Option A: Train Everything at Once
```powershell
cd backend
python retrain_all_models.py
python train_image_models.py
```

### Option B: Train Individual Models
```powershell
cd backend

# Clinical models (fast - ~30 seconds each)
python -c "exec(open('retrain_all_models.py').read()); m=ModelRetrainer(); m.train_diabetes_model()"
python -c "exec(open('retrain_all_models.py').read()); m=ModelRetrainer(); m.train_heart_disease_model()"
python -c "exec(open('retrain_all_models.py').read()); m=ModelRetrainer(); m.train_liver_disease_model()"
python -c "exec(open('retrain_all_models.py').read()); m=ModelRetrainer(); m.train_kidney_disease_model()"
python -c "exec(open('retrain_all_models.py').read()); m=ModelRetrainer(); m.train_breast_cancer_model()"
python -c "exec(open('retrain_all_models.py').read()); m=ModelRetrainer(); m.train_alzheimer_model()"

# Image models (slow - ~2-3 minutes each)
python train_image_models.py
```

---

## 🖥️ Step 2: Run the Project

### Development Mode (Two Terminals)

**Terminal 1 - Backend:**
```powershell
cd backend
python main.py
```

**Terminal 2 - Frontend:**
```powershell
cd frontend
npm run dev
```

### Production Mode (Docker)
```powershell
# One command deploy
deploy.bat

# Or manually
docker-compose -f docker-compose.prod.yml up --build -d
```

---

## 🔍 Quick Checks

### Verify Models Exist
```powershell
dir backend\models\*.pkl
```
Should show 8+ model files.

### Check Backend Health
```powershell
curl http://localhost:8000/health
```

### Clear Old Predictions
```powershell
# Browser console (F12)
localStorage.removeItem('medai_predictions')
```

---

## 📁 Access Points

| Service | URL | Description |
|---------|-----|-------------|
| Web App | http://localhost:3000 | Main application |
| API Docs | http://localhost:8000/docs | Test endpoints |
| Backend | http://localhost:8000 | API server |

---

## 🛑 Stop Everything

```powershell
# Stop backend (in backend terminal)
Ctrl+C

# Stop frontend (in frontend terminal)
Ctrl+C

# Stop Docker
docker-compose -f docker-compose.prod.yml down

# Stop all Python processes
taskkill /F /IM python.exe

# Stop all Node processes
taskkill /F /IM node.exe
```

---

## 🔄 Full Restart Sequence

```powershell
# 1. Go to project folder
cd c:\Users\asus\CascadeProjects\medai-diagnostics

# 2. Train models (if needed)
cd backend
python retrain_all_models.py
python train_image_models.py

# 3. Start backend (Terminal 1)
python main.py

# 4. Start frontend (Terminal 2 - new window)
cd frontend
npm run dev

# 5. Open browser
start http://localhost:3000
```

---

## 🆘 Troubleshooting Commands

### Port Already in Use
```powershell
# Find what's using port 3000
netstat -ano | findstr :3000

# Kill the process
taskkill /PID <PID> /F
```

### Fix Frontend Issues
```powershell
cd frontend
rmdir /s /q node_modules
npm install
npm run dev
```

### Fix Backend Issues
```powershell
cd backend
pip install -r requirements.txt
python main.py
```

### Reset Everything
```powershell
# Delete models (to retrain)
del backend\models\*.pkl
del backend\models\*.json

# Delete frontend cache
cd frontend
rmdir /s /q node_modules
rmdir /s /q .next
```

---

## ☁️ Deploy to Cloud

### Railway (Free)
```powershell
# 1. Push to GitHub
git add .
git commit -m "Update"
git push origin main

# 2. Railway auto-deploys from GitHub
# Get URL from Railway dashboard
```

### Render (Free)
```powershell
# Same as above - push to GitHub
# Connect repo in Render dashboard
```

---

## 📱 Mobile Access (Same WiFi)

```powershell
# Find your computer's IP
ipconfig
# Look for "IPv4 Address"

# On phone/tablet browser:
# http://YOUR_IP:3000
```

---

## ⏱️ Time Estimates

| Task | Time |
|------|------|
| Train clinical models | ~3 minutes |
| Train image models | ~5 minutes |
| Start backend | ~10 seconds |
| Start frontend | ~30 seconds |
| Full restart | ~10 minutes |

---

## ✅ Complete Workflow

```powershell
# 1. Train models
cd backend && python retrain_all_models.py && python train_image_models.py

# 2. Start backend (new terminal)
cd backend && python main.py

# 3. Start frontend (another terminal)
cd frontend && npm run dev

# 4. Open browser
start http://localhost:3000
```

---

## 📞 Quick Reference Card

```
TRAIN:  cd backend; python retrain_all_models.py; python train_image_models.py
BACKEND: cd backend; python main.py
FRONTEND: cd frontend; npm run dev
DOCKER: deploy.bat
STOP: Ctrl+C or taskkill /F /IM python.exe
CLEAR: localStorage.removeItem('medai_predictions')
```

---

Save this file for future reference!
