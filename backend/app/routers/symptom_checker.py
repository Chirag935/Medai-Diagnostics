from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import pandas as pd
import joblib
import json
import os
import traceback

router = APIRouter()

MODEL_PATH = "models/symptom_disease_model.pkl"
META_PATH = "models/symptom_disease_metadata.json"

class SymptomRequest(BaseModel):
    symptoms: list[str]

@router.post("/predict")
async def predict_disease(request: SymptomRequest):
    try:
        # For demo purposes, we will return a mock prediction if the model is not trained yet
        if not os.path.exists(MODEL_PATH) or not os.path.exists(META_PATH):
            print("Model not found, returning mock response for demo.")
            # Basic fallback logic for common symptoms
            symptoms = [s.lower() for s in request.symptoms]
            
            if "cough" in symptoms and "fever" in symptoms:
                return {
                    "prediction": "Respiratory Infection (Possible TB/Pneumonia)",
                    "confidence": 0.85,
                    "severity": "High - Consult a doctor",
                    "recommendation": "Please get a chest X-ray and consult a physician immediately."
                }
            elif "rash" in symptoms or "itching" in symptoms:
                return {
                    "prediction": "Fungal Infection / Allergic Reaction",
                    "confidence": 0.78,
                    "severity": "Low - Monitor",
                    "recommendation": "Use topical cream. If it persists, consult a dermatologist."
                }
            else:
                return {
                    "prediction": "Common Viral Pathogen",
                    "confidence": 0.65,
                    "severity": "Moderate",
                    "recommendation": "Rest and stay hydrated. Monitor symptoms."
                }
        
        # Load the model
        model = joblib.load(MODEL_PATH)
        with open(META_PATH, "r") as f:
            metadata = json.load(f)
            
        all_symptoms = metadata["symptoms"]
        
        # Create input array
        input_data = [0] * len(all_symptoms)
        for s in request.symptoms:
            # Map user symptoms to model symptoms
            for i, model_symp in enumerate(all_symptoms):
                if s.lower().replace(" ", "_") in model_symp.lower():
                    input_data[i] = 1
        
        # Predict
        prediction = model.predict([input_data])[0]
        probabilities = model.predict_proba([input_data])[0]
        confidence = float(max(probabilities))
        
        return {
            "prediction": prediction,
            "confidence": confidence,
            "severity": "Consult a physician based on these findings."
        }
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
