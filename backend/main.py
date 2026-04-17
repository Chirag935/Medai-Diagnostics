from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn
import os

from app.routers import malaria, pneumonia, breast_cancer, diabetes, alzheimer, liver_disease, kidney_disease, heart_disease, metrics
from app.demo_values import DEMO_VALUES

app = FastAPI(
    title="MedAI Diagnostics API",
    description="Advanced AI-powered medical diagnostics platform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS - FIXED: Allow all origins for Netlify frontend
# CORS must have allow_credentials=False when using wildcard origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins including Netlify
    allow_credentials=False,  # Required to be False for wildcard
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600,
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
    return {"status": "healthy", "service": "MedAI Diagnostics API", "cors": "enabled"}

@app.options("/{path:path}")
async def handle_options(path: str):
    """Handle CORS preflight requests"""
    return {"message": "OK"}

@app.get("/cors-test")
async def cors_test():
    """Test CORS is working"""
    return {"cors": "working", "timestamp": "2024"}

@app.get("/demo-values")
async def get_demo_values():
    """Get demo values for all diseases"""
    return DEMO_VALUES

@app.get("/demo-values/{disease}")
async def get_demo_value(disease: str):
    """Get demo values for specific disease"""
    if disease in DEMO_VALUES:
        return DEMO_VALUES[disease]
    return {"error": "Disease not found"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False, workers=1)
