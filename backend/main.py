from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from app.routers import symptom_checker, skin_analyzer, metrics, chat, feedback, patients

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
    allow_origins=["*"],
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
app.include_router(symptom_checker.router, prefix="/api/symptoms", tags=["Symptom Checker"])
app.include_router(skin_analyzer.router, prefix="/api/skin", tags=["Skin Analyzer"])
app.include_router(metrics.router, prefix="/api/metrics", tags=["Metrics"])
app.include_router(chat.router, prefix="/api/chat", tags=["AI Assistant"])
app.include_router(feedback.router, prefix="/api/feedback", tags=["MLOps Feedback"])
app.include_router(patients.router, prefix="/api/patients", tags=["Patient Management"])

@app.get("/")
async def root():
    return {
        "message": "MedAI Diagnostics API",
        "version": "1.0.0",
        "status": "active",
        "endpoints": {
            "symptom_checker": "/api/symptoms",
            "skin_analyzer": "/api/skin",
            "metrics": "/api/metrics",
            "ai_assistant": "/api/chat",
            "mlops_feedback": "/api/feedback"
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



if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False, workers=1)
