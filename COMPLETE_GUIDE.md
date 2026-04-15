# MedAI Diagnostics - Complete Setup & Deployment Guide

Deploy and run MedAI on any device - desktop, tablet, or mobile!

---

## 📋 Prerequisites

### Required Software:
- **Python 3.11+** (https://python.org)
- **Node.js 20+** (https://nodejs.org)
- **Docker Desktop** (optional, for deployment)
- **Git** (for cloud deployment)

---

## 🚀 Quick Start (3 Steps)

### Step 1: Train All Models (One Command)
```powershell
cd backend
python train_all_real_models.py
```
**Time:** ~10-15 minutes  
**Output:** Trained models in `backend/models/`

### Step 2: Start Backend
```powershell
cd backend
python main.py
```
**Wait for:** `Application startup complete`  
**Access:** http://localhost:8000/docs

### Step 3: Start Frontend (New Terminal)
```powershell
cd frontend
npm install
npm run dev
```
**Wait for:** `Ready on http://localhost:3000`  
**Access:** http://localhost:3000

---

## 🏋️ Detailed Training Guide

### Option A: Train All Models at Once
```powershell
cd backend
python train_all_real_models.py
```

This trains:
- ✅ Diabetes (PIMA dataset)
- ✅ Breast Cancer (WDBC dataset)
- ✅ Heart Disease (Cleveland dataset)
- ✅ Liver Disease (Indian dataset)
- ✅ Kidney Disease (CKD dataset)
- ✅ Alzheimer's (OASIS dataset)
- ✅ Pneumonia (CNN on synthetic X-rays)
- ✅ Malaria (Synthetic blood smears)

### Option B: Train Individual Models
```powershell
cd backend

# Clinical models (fast)
python train_diabetes_model.py          # ~30 seconds
python train_breast_cancer_model.py     # ~30 seconds
python train_heart_disease_model.py     # ~30 seconds
python train_liver_disease_model.py     # ~30 seconds
python train_kidney_disease_model.py    # ~30 seconds
python train_alzheimer_model.py         # ~30 seconds

# Image models (slow)
python train_pneumonia_cnn.py           # ~5 minutes
python train_malaria_model.py           # ~2 minutes
```

### Verify Models Trained
```powershell
dir backend\models\*.pkl
```
Should show 8+ model files.

---

## 💻 Development Mode

### Terminal 1 - Backend
```powershell
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

### Terminal 2 - Frontend
```powershell
cd frontend
npm install
npm run dev
```

### Access Points
| Service | URL | Description |
|---------|-----|-------------|
| Web App | http://localhost:3000 | Frontend UI |
| API Docs | http://localhost:8000/docs | Swagger UI |
| API Base | http://localhost:8000/api | Backend API |

---

## 🌐 Deployment Options

### Option 1: Docker (Recommended for Local/Server)

#### One-Command Deploy (Windows)
```powershell
deploy.bat
```

#### Manual Docker Deploy
```powershell
# Build and start
docker-compose -f docker-compose.prod.yml up --build -d

# View logs
docker-compose -f docker-compose.prod.yml logs -f

# Stop
docker-compose -f docker-compose.prod.yml down
```

**Access:** http://localhost:8000

---

### Option 2: Railway (Free Cloud Hosting)

1. **Push to GitHub**
   ```powershell
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/YOUR_USERNAME/medai-diagnostics.git
   git push -u origin main
   ```

2. **Deploy on Railway**
   - Go to https://railway.app
   - Click "New Project" → "Deploy from GitHub repo"
   - Select your repository
   - Railway automatically detects `railway.toml`
   - Deploy!

3. **Access**
   - Railway provides a public URL
   - Access from any device with internet

---

### Option 3: Render (Free Cloud Hosting)

1. **Push to GitHub** (same as above)

2. **Deploy on Render**
   - Go to https://render.com
   - Click "New Web Service"
   - Connect your GitHub repo
   - Select "Docker" environment
   - Deploy!

3. **Access**
   - Render provides URL like `https://medai.onrender.com`
   - Use on any device

---

### Option 4: Vercel + Separate Backend

#### Deploy Frontend to Vercel
```powershell
cd frontend
npm install -g vercel
vercel
```

#### Deploy Backend to Railway/Render
Use Option 2 or 3 above for backend only.

#### Update API URL
Set environment variable in Vercel:
```
NEXT_PUBLIC_API_URL=https://your-backend-url.railway.app
```

---

## 📱 Mobile/Tablet Access

### Same WiFi (Local Network)
1. Find your computer's IP:
   ```powershell
   ipconfig
   # Look for "IPv4 Address" like 192.168.1.100
   ```

2. Access from phone/tablet:
   ```
   http://192.168.1.100:3000  # If using npm run dev
   http://192.168.1.100:8000  # If using Docker
   ```

### Cloud Deployed
- Use the provided URL (e.g., `https://medai.onrender.com`)
- Works on iOS Safari, Android Chrome, any browser
- Add to home screen for app-like experience

---

## 🔧 Environment Variables

### Backend (.env file in backend/)
```env
PORT=8000
ENVIRONMENT=production
PYTHONPATH=/app
```

### Frontend (optional)
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## 📊 Monitoring & Logs

### Backend Logs
```powershell
# Local
python main.py  # Logs in terminal

# Docker
docker-compose -f docker-compose.prod.yml logs -f
```

### Health Check
```
GET http://localhost:8000/health
```
Response:
```json
{
  "status": "healthy",
  "service": "MedAI Diagnostics API"
}
```

---

## 🔄 Updating After Deployment

### Local/Docker
```powershell
git pull  # Get latest code
docker-compose -f docker-compose.prod.yml up --build -d
```

### Cloud (Railway/Render)
- Auto-deploys on git push
- Or manual deploy from dashboard

---

## 🐛 Troubleshooting

### Port Already in Use
```powershell
# Find process using port 8000
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

### Model Not Found
```powershell
cd backend
python train_all_real_models.py
```

### Frontend Won't Start
```powershell
cd frontend
rm -rf node_modules
npm install
npm run dev
```

### CORS Errors
Update `backend/main.py`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For production, specify your domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## 📁 Project Structure

```
medai-diagnostics/
├── backend/
│   ├── app/              # FastAPI application
│   ├── models/           # Trained ML models
│   ├── data/             # Datasets
│   ├── main.py           # Entry point
│   └── requirements.txt  # Python dependencies
├── frontend/
│   ├── src/              # Next.js source
│   ├── public/           # Static assets
│   └── package.json      # Node dependencies
├── Dockerfile            # Container config
├── docker-compose.prod.yml
├── railway.toml          # Railway config
├── render.yaml           # Render config
└── deploy.bat            # Windows deploy script
```

---

## 🎯 Complete Workflow Summary

| Step | Local Dev | Docker Deploy | Cloud Deploy |
|------|-----------|---------------|--------------|
| **1. Train** | `python train_all_real_models.py` | Same | Same |
| **2. Start** | `python main.py` + `npm run dev` | `deploy.bat` | Git push |
| **3. Access** | localhost:3000 | localhost:8000 | Provided URL |
| **4. Mobile** | Same WiFi IP | Same WiFi IP | Any internet |

---

## 📞 Need Help?

- Check logs: `docker-compose logs -f`
- Verify models: `ls backend/models/`
- Test API: http://localhost:8000/docs
- Clear cache: Browser DevTools → Application → Clear Storage

---

## ✅ Pre-Deployment Checklist

- [ ] All models trained (`backend/models/` has .pkl files)
- [ ] Backend runs locally (`python main.py`)
- [ ] Frontend runs locally (`npm run dev`)
- [ ] API calls work (test at `/api/diabetes/predict`)
- [ ] Docker installed (for local deployment)
- [ ] Git repo created (for cloud deployment)
- [ ] Environment variables set (for cloud)

---

**Ready to deploy! 🚀**
