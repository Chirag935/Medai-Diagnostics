from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import pandas as pd
import joblib
import json
import os
import traceback
import numpy as np
from datetime import datetime

router = APIRouter()

MODELS_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "models")
MODEL_PATH = os.path.join(MODELS_DIR, "symptom_disease_model.pkl")
META_PATH = os.path.join(MODELS_DIR, "symptom_disease_metadata.json")

# Supabase client for logging
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")
_sb_client = None

def _get_supabase():
    global _sb_client
    if _sb_client is None and SUPABASE_URL and SUPABASE_KEY:
        from supabase import create_client
        _sb_client = create_client(SUPABASE_URL, SUPABASE_KEY)
    return _sb_client

def _log_prediction(module: str, prediction: str, confidence: float, features: str = None):
    """Auto-log prediction to Supabase predictions table."""
    try:
        sb = _get_supabase()
        if sb:
            sb.table("predictions").insert({
                "module": module,
                "prediction": prediction,
                "confidence": confidence,
                "timestamp": datetime.now().isoformat(),
                "features": features
            }).execute()
    except Exception:
        pass  # Don't break predictions if logging fails

# Load model and metadata once at startup for faster predictions
_model = None
_metadata = None

def _get_model():
    global _model, _metadata
    if _model is None:
        if not os.path.exists(MODEL_PATH) or not os.path.exists(META_PATH):
            raise HTTPException(
                status_code=503,
                detail="Symptom prediction model not trained yet. Run train_symptom_model.py first."
            )
        _model = joblib.load(MODEL_PATH)
        with open(META_PATH, "r") as f:
            _metadata = json.load(f)
        print(f"[Symptom Checker] Model loaded: {len(_metadata['symptoms'])} symptoms, {len(_metadata['diseases'])} diseases")
    return _model, _metadata

class SymptomRequest(BaseModel):
    symptoms: list[str]

@router.post("/predict")
async def predict_disease(request: SymptomRequest):
    try:
        model, metadata = _get_model()
        all_symptoms = metadata["symptoms"]
        all_diseases = metadata["diseases"]
        
        # Create input vector — exact matching against model's symptom list
        input_data = [0] * len(all_symptoms)
        matched_count = 0
        
        for user_symptom in request.symptoms:
            # Normalize: lowercase, replace spaces with underscores
            normalized = user_symptom.lower().strip().replace(" ", "_")
            
            # Try exact match first
            for i, model_symptom in enumerate(all_symptoms):
                model_normalized = model_symptom.lower().strip()
                if normalized == model_normalized:
                    input_data[i] = 1
                    matched_count += 1
                    break
            else:
                # Try partial match as fallback (e.g., "fever" matches "high_fever")
                for i, model_symptom in enumerate(all_symptoms):
                    model_normalized = model_symptom.lower().strip()
                    if normalized in model_normalized or model_normalized in normalized:
                        input_data[i] = 1
                        matched_count += 1
                        break
        
        if matched_count == 0:
            return {
                "prediction": "Unable to match symptoms",
                "confidence": 0.0,
                "severity": "Unknown",
                "recommendation": "Please select symptoms from the provided list for accurate prediction.",
                "matched_symptoms": 0,
                "total_submitted": len(request.symptoms)
            }
        
        # Real ML prediction
        prediction = model.predict([input_data])[0]
        probabilities = model.predict_proba([input_data])[0]
        confidence = float(max(probabilities))
        
        # Get top 3 predictions for transparency
        top_indices = np.argsort(probabilities)[::-1][:3]
        top_predictions = []
        for idx in top_indices:
            if probabilities[idx] > 0.01:
                top_predictions.append({
                    "disease": all_diseases[idx] if idx < len(all_diseases) else f"Class {idx}",
                    "probability": round(float(probabilities[idx]) * 100, 1)
                })
        
        # Determine severity based on confidence
        if confidence >= 0.8:
            severity = "High - Strong prediction. Consult a physician."
        elif confidence >= 0.5:
            severity = "Moderate - Likely match. Medical consultation recommended."
        else:
            severity = "Low - Uncertain prediction. Consider adding more symptoms."
        
        # Auto-log to MLOps dashboard
        _log_prediction("symptoms", prediction, confidence, json.dumps(request.symptoms))
        
        return {
            "prediction": prediction,
            "confidence": round(confidence, 3),
            "severity": severity,
            "recommendation": f"AI identified {matched_count} symptom(s). Top match: {prediction} ({round(confidence*100,1)}%). Please consult a healthcare professional for confirmation.",
            "matched_symptoms": matched_count,
            "total_submitted": len(request.symptoms),
            "top_predictions": top_predictions
        }
    except HTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")
