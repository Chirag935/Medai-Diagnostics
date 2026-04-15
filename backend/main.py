from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn
import os

from app.routers import pneumonia, malaria, breast_cancer, diabetes, alzheimer, liver_disease, kidney_disease, heart_disease, metrics

app = FastAPI(
    title="MedAI Diagnostics API",
    description="Advanced AI-powered medical diagnostics platform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001", 
        "http://localhost:3002",
        "http://localhost:3003",
        "http://localhost:3004",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
        "http://127.0.0.1:3002",
        "http://127.0.0.1:3003",
        "http://127.0.0.1:3004",
        "https://medaidiagnostics.netlify.app",
        "https://*.netlify.app",
        "*"  # Allow all origins for now (restrict in production)
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for model uploads
if not os.path.exists("static"):
    os.makedirs("static")
app.mount("/static", StaticFiles(directory="static"), name="static")

# Include routers
app.include_router(pneumonia.router, prefix="/api/pneumonia", tags=["Pneumonia"])
app.include_router(malaria.router, prefix="/api/malaria", tags=["Malaria"])
app.include_router(breast_cancer.router, prefix="/api/breast-cancer", tags=["Breast Cancer"])
app.include_router(diabetes.router, prefix="/api/diabetes", tags=["Diabetes"])
app.include_router(alzheimer.router, prefix="/api/alzheimer", tags=["Alzheimer"])
app.include_router(liver_disease.router, prefix="/api/liver-disease", tags=["Liver Disease"])
app.include_router(kidney_disease.router, prefix="/api/kidney-disease", tags=["Kidney Disease"])
app.include_router(heart_disease.router, prefix="/api/heart-disease", tags=["Heart Disease"])
app.include_router(metrics.router, prefix="/api/metrics", tags=["Metrics"])

@app.get("/")
async def root():
    return {
        "message": "MedAI Diagnostics API",
        "version": "1.0.0",
        "status": "active",
        "endpoints": {
            "pneumonia": "/api/pneumonia",
            "malaria": "/api/malaria",
            "breast_cancer": "/api/breast-cancer",
            "diabetes": "/api/diabetes",
            "alzheimer": "/api/alzheimer",
            "liver_disease": "/api/liver-disease",
            "kidney_disease": "/api/kidney-disease",
            "heart_disease": "/api/heart-disease",
            "metrics": "/api/metrics"
        }
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "MedAI Diagnostics API"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
