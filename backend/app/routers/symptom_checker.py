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

# Simple disease descriptions for common people
DISEASE_INFO: dict[str, str] = {
    "Fungal infection": "A skin condition caused by fungi. Common symptoms include itching, rash, and skin peeling. Usually treatable with antifungal creams.",
    "Allergy": "Your body's immune system overreacts to something harmless like pollen, food, or dust. Causes sneezing, itching, or rashes.",
    "GERD": "Stomach acid flows back into your food pipe, causing heartburn and chest discomfort. Managed with diet changes and antacids.",
    "Chronic cholestasis": "A liver condition where bile flow is reduced. Causes itching and yellowing of skin. Needs medical evaluation.",
    "Drug Reaction": "An unwanted side effect from medication. Can cause rashes, fever, or nausea. Stop the medication and see a doctor.",
    "Peptic ulcer disease": "Open sores in the stomach lining causing burning stomach pain, especially when hungry. Treatable with medication.",
    "AIDS": "A serious immune system disease caused by HIV. Requires medical diagnosis with blood tests — symptom checkers alone cannot diagnose this. Many common symptoms overlap with less serious conditions.",
    "Diabetes": "Your body has trouble managing blood sugar levels. Causes frequent urination, thirst, and fatigue. Managed with diet, exercise, and medication.",
    "Gastroenteritis": "Stomach flu — an infection causing vomiting, diarrhea, and stomach cramps. Usually resolves in a few days with rest and fluids.",
    "Bronchial Asthma": "Airways in your lungs get narrow, making breathing difficult. Triggers include dust, cold air, and exercise. Managed with inhalers.",
    "Hypertension": "High blood pressure — often has no symptoms but increases risk of heart disease. Managed with lifestyle changes and medication.",
    "Migraine": "Severe throbbing headache, often on one side, with nausea and light sensitivity. Can last hours to days.",
    "Cervical spondylosis": "Wear and tear of neck bones and discs causing neck pain and stiffness. Common with aging.",
    "Paralysis (brain hemorrhage)": "Loss of movement in part of the body due to bleeding in the brain. This is a medical emergency — call 911 immediately.",
    "Jaundice": "Yellowing of skin and eyes due to excess bilirubin. Often signals a liver problem. Needs medical evaluation.",
    "Malaria": "A mosquito-borne infection causing high fever, chills, and sweating. Treatable with antimalarial drugs.",
    "Chicken pox": "A viral infection causing itchy, blister-like rash all over the body. Common in children. Usually mild and self-resolving.",
    "Dengue": "A mosquito-borne viral fever causing high fever, severe headache, and body pain. Needs medical monitoring.",
    "Typhoid": "A bacterial infection from contaminated food/water causing prolonged fever, weakness, and stomach pain. Treatable with antibiotics.",
    "Hepatitis A": "A liver infection from contaminated food/water. Causes fatigue, nausea, and jaundice. Usually resolves on its own.",
    "Hepatitis B": "A serious liver infection spread through blood/body fluids. Can become chronic. Vaccine available for prevention.",
    "Hepatitis C": "A liver infection spread through blood contact. Often has no early symptoms. Curable with modern medications.",
    "Hepatitis D": "A liver infection that only occurs with Hepatitis B. Makes liver disease more severe.",
    "Hepatitis E": "A liver infection from contaminated water. Similar to Hepatitis A. Usually self-resolving.",
    "Alcoholic hepatitis": "Liver inflammation from heavy alcohol use. Causes jaundice, fever, and abdominal pain. Requires stopping alcohol.",
    "Tuberculosis": "A bacterial lung infection causing persistent cough, weight loss, and night sweats. Treatable with a course of antibiotics.",
    "Common Cold": "A mild viral infection of the nose and throat. Causes runny nose, sneezing, and sore throat. Resolves in 7-10 days.",
    "Pneumonia": "A lung infection causing cough with phlegm, fever, and difficulty breathing. May need antibiotics.",
    "Dimorphic hemorrhoids (piles)": "Swollen blood vessels in the rectum causing pain and bleeding during bowel movements. Treatable with diet changes and medication.",
    "Heart attack": "Blood flow to the heart is blocked. Causes chest pain, shortness of breath. This is a medical emergency — call 911.",
    "Varicose veins": "Swollen, twisted veins visible under the skin, usually in legs. Caused by weakened valves. Manageable with compression stockings.",
    "Hypothyroidism": "Your thyroid gland doesn't produce enough hormones, causing fatigue, weight gain, and cold sensitivity. Managed with daily medication.",
    "Hyperthyroidism": "Your thyroid produces too much hormone, causing weight loss, rapid heartbeat, and anxiety. Treatable with medication.",
    "Hypoglycemia": "Blood sugar drops too low, causing shakiness, sweating, and confusion. Eat something sugary immediately.",
    "Osteoarthritis": "Joint cartilage wears down over time causing pain and stiffness, especially in knees and hips. Common with aging.",
    "Arthritis": "Inflammation of joints causing pain, swelling, and reduced movement. Multiple types exist. Managed with medication and exercise.",
    "(vertigo) Paroxysmal Positional Vertigo": "Brief episodes of dizziness triggered by head position changes. Not dangerous but uncomfortable. Treatable with head exercises.",
    "Acne": "Clogged skin pores causing pimples, blackheads, and bumps. Very common in teenagers. Treatable with skincare products.",
    "Urinary tract infection": "Bacterial infection in the urinary system causing burning urination and frequent urge to pee. Treatable with antibiotics.",
    "Psoriasis": "An immune condition causing thick, scaly patches on skin. Chronic but manageable with creams and medication.",
    "Impetigo": "A contagious skin infection causing red sores that rupture and form crusts. Common in children. Treatable with antibiotics.",
}

def get_disease_description(disease: str) -> str:
    return DISEASE_INFO.get(disease, f"{disease} — Please consult a healthcare professional for detailed information about this condition.")

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
                disease_name = all_diseases[idx] if idx < len(all_diseases) else f"Class {idx}"
                top_predictions.append({
                    "disease": disease_name,
                    "probability": round(float(probabilities[idx]) * 100, 1),
                    "description": get_disease_description(disease_name)
                })
        
        # Determine severity based on confidence
        if confidence >= 0.8:
            severity = "High - Strong prediction. Consult a physician."
        elif confidence >= 0.5:
            severity = "Moderate - Likely match. Medical consultation recommended."
        else:
            severity = "Low - Uncertain prediction. Consider adding more symptoms for better accuracy."
        
        # Confidence warning
        confidence_warning = ""
        if confidence < 0.6:
            confidence_warning = "⚠️ Low confidence — these symptoms match multiple conditions. Please add more symptoms or consult a doctor for proper diagnosis."
        
        # Auto-log to MLOps dashboard
        _log_prediction("symptoms", prediction, confidence, json.dumps(request.symptoms))
        
        return {
            "prediction": prediction,
            "description": get_disease_description(prediction),
            "confidence": round(confidence, 3),
            "severity": severity,
            "confidence_warning": confidence_warning,
            "recommendation": f"AI identified {matched_count} symptom(s). Top match: {prediction} ({round(confidence*100,1)}%). Please consult a healthcare professional for confirmation.",
            "disclaimer": "⚕️ This AI prediction is for informational purposes only. It is NOT a medical diagnosis. Many symptoms overlap between common and serious conditions. Always consult a qualified healthcare professional.",
            "matched_symptoms": matched_count,
            "total_submitted": len(request.symptoms),
            "top_predictions": top_predictions
        }
    except HTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")
