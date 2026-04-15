# MedAI Backend Deployment Helper
# This script prepares the backend for deployment to Render

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "MedAI Backend Deployment Helper" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Check if git is initialized
if (-not (Test-Path .git)) {
    Write-Host "Initializing Git repository..." -ForegroundColor Yellow
    git init
    git add .
    git commit -m "Initial commit for deployment"
    Write-Host "Git repository initialized!" -ForegroundColor Green
} else {
    Write-Host "Git repository already exists" -ForegroundColor Green
}

# Check for large files (models)
$modelSize = (Get-ChildItem backend/models -Recurse | Measure-Object -Property Length -Sum).Sum / 1MB
Write-Host ""
Write-Host "Model files size: $([math]::Round($modelSize, 2)) MB" -ForegroundColor Cyan

if ($modelSize -gt 100) {
    Write-Host "WARNING: Model files are large ($([math]::Round($modelSize, 2)) MB)" -ForegroundColor Red
    Write-Host "Free deployment services may have limits. Consider:" -ForegroundColor Yellow
    Write-Host "  1. Using Git LFS for large files" -ForegroundColor Yellow
    Write-Host "  2. Training models on the server after deploy" -ForegroundColor Yellow
    Write-Host "  3. Using a paid plan with higher limits" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "DEPLOYMENT INSTRUCTIONS:" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Option 1: Deploy to Render (Recommended)" -ForegroundColor Green
Write-Host "----------------------------------------" -ForegroundColor Green
Write-Host "1. Push code to GitHub:"
Write-Host "   git remote add origin https://github.com/YOUR_USERNAME/medai-diagnostics.git"
Write-Host "   git push -u origin main"
Write-Host ""
Write-Host "2. Go to https://render.com and sign up"
Write-Host "3. Click 'New +' → 'Web Service'"
Write-Host "4. Connect your GitHub repo"
Write-Host "5. Settings:"
Write-Host "   - Root Directory: backend"
Write-Host "   - Build Command: pip install -r requirements.txt"
Write-Host "   - Start Command: uvicorn main:app --host 0.0.0.0 --port 10000"
Write-Host "6. Click 'Create Web Service'"
Write-Host ""
Write-Host "Option 2: Deploy to Railway" -ForegroundColor Green
Write-Host "----------------------------------------" -ForegroundColor Green
Write-Host "1. Go to https://railway.app"
Write-Host "2. New Project → Deploy from GitHub"
Write-Host "3. Set environment variable: PORT=8000"
Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "AFTER BACKEND DEPLOYMENT:" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "1. Copy your backend URL (e.g., https://medai-backend.onrender.com)"
Write-Host "2. Update frontend/src/lib/api-config.ts with new URL"
Write-Host "3. Rebuild: cd frontend && npm run build"
Write-Host "4. Redeploy: netlify deploy --prod --dir=dist"
Write-Host ""
Write-Host "Full guide: DEPLOYMENT_GUIDE.md" -ForegroundColor Yellow
