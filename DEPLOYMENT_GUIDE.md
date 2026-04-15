# MedAI Diagnostics - Deployment Guide

## 🚀 Quick Deploy to Render (Backend)

### Step 1: Deploy Backend to Render

1. **Push your code to GitHub** (if not already done)
   ```bash
   git init
   git add .
   git commit -m "Ready for deployment"
   git remote add origin https://github.com/yourusername/medai-diagnostics.git
   git push -u origin main
   ```

2. **Go to [render.com](https://render.com)**
   - Sign up/login with GitHub
   - Click "New +" → "Web Service"
   - Connect your GitHub repo
   - Select the `backend` folder as root
   - Settings:
     - **Name**: `medai-backend`
     - **Runtime**: Python 3
     - **Build Command**: `pip install -r requirements.txt`
     - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port 10000`
   - Click "Create Web Service"

3. **Get your backend URL**
   - Wait for deployment (5-10 minutes)
   - URL will be: `https://medai-backend.onrender.com`

### Step 2: Update Frontend API URL

1. Edit `frontend/src/lib/api-config.ts`:
   ```typescript
   export const API_BASE_URL = 'https://medai-backend.onrender.com'
   ```

2. **Rebuild and redeploy frontend**:
   ```bash
   cd frontend
   npm run build
   netlify deploy --prod --dir=dist
   ```

### Step 3: Test Deployment

- Frontend: `https://medaidiagnostics.netlify.app`
- Backend: `https://medai-backend.onrender.com`
- API Docs: `https://medai-backend.onrender.com/docs`

## 📋 Alternative: Deploy Backend to Railway

1. Go to [railway.app](https://railway.app)
2. New Project → Deploy from GitHub repo
3. Add environment variable: `PORT=8000`
4. Deploy!

## 🔧 Alternative: Deploy Backend to Heroku

```bash
# Install Heroku CLI and login
heroku login

# Create app
heroku create medai-backend

# Deploy
git subtree push --prefix backend heroku main
```

## ⚠️ Important Notes

1. **Render Free Tier**: Sleeps after 15 min inactivity (cold start = 30-60s delay)
2. **Model Files**: Ensure `/backend/models/` folder is in Git or retrain on deploy
3. **Image Datasets**: Pneumonia/Malaria need local datasets for training
4. **Custom Domain**: Add your `healthcare.app` domain in Netlify/Render settings

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| Predictions not working | Check backend URL in `api-config.ts` |
| CORS errors | Verify backend CORS includes Netlify URL |
| Slow responses | Render free tier has cold starts |
| Models missing | Retrain models or include in Git |

## 📞 Support

- Frontend URL: https://medaidiagnostics.netlify.app
- Backend Health: https://medai-backend.onrender.com/health
