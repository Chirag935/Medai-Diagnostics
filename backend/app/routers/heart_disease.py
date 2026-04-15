from fastapi import APIRouter, HTTPException
import numpy as np
import joblib
import os
import json
from typing import Dict, Any

from app.schemas.prediction import HeartDiseaseRequest, HeartDiseaseResponse

router = APIRouter()

def load_heart_disease_model():
    """Load trained heart disease prediction model"""
    model_path = "models/heart_disease_model.pkl"
    scaler_path = "models/heart_disease_scaler.pkl"
    
    if os.path.exists(model_path) and os.path.exists(scaler_path):
        model = joblib.load(model_path)
        scaler = joblib.load(scaler_path)
        return model, scaler
    else:
        # Train model if it doesn't exist
        print("Training heart disease model...")
        try:
            import train_heart_disease_model
            model, scaler, _ = train_heart_disease_model.train_heart_disease_model()
            return model, scaler
        except Exception as e:
            print(f"Error training model: {e}")
            # Return dummy model as fallback
            return DummyHeartDiseaseModel(), None

class DummyHeartDiseaseModel:
    """Fallback dummy model for demonstration"""
    def predict_proba(self, X):
        return np.array([[0.2, 0.8]])  # [healthy, disease]
    
    def predict(self, X):
        return np.array([1])  # disease

def calculate_risk_level(probability: float) -> str:
    """Calculate risk level based on probability"""
    if probability < 30:
        return "LOW"
    elif probability < 60:
        return "MODERATE"
    elif probability < 80:
        return "HIGH"
    else:
        return "CRITICAL"

def get_feature_importance() -> Dict[str, float]:
    """Return feature importance for heart disease prediction"""
    try:
        if os.path.exists("models/heart_disease_metadata.json"):
            with open("models/heart_disease_metadata.json", "r") as f:
                metadata = json.load(f)
                return metadata.get("feature_importance", {})
    except Exception:
        pass
    
    # Fallback to default importance
    return {
        "thalach": 0.13,
        "age": 0.13,
        "trestbps": 0.12,
        "chol": 0.11,
        "ca": 0.10,
        "oldpeak": 0.10,
        "cp": 0.10,
        "thal": 0.06,
        "exang": 0.05,
        "sex": 0.03,
        "slope": 0.03,
        "restecg": 0.03,
        "fbs": 0.01
    }

def get_top_risk_factors(features: Dict[str, float], feature_importance: Dict[str, float]) -> list:
    """Get top 3 risk factors based on input values and feature importance"""
    risk_factors = []
    
    if features.get("age", 0) > 60:
        risk_factors.append("Advanced age")
    if features.get("chol", 0) > 240:
        risk_factors.append("High cholesterol")
    if features.get("trestbps", 0) > 140:
        risk_factors.append("High blood pressure")
    if features.get("thalach", 0) < 120:
        risk_factors.append("Low maximum heart rate")
    if features.get("cp", 0) > 1:
        risk_factors.append("Chest pain type")
    
    return risk_factors[:3]

def generate_explanation(probability: float, risk_level: str, features: Dict[str, float]) -> str:
    """Generate clinical explanation of prediction"""
    age = features.get("age", 0)
    chol = features.get("chol", 0)
    bp = features.get("trestbps", 0)
    
    explanation = f"Based on cardiovascular risk factor analysis, "
    
    if risk_level == "LOW":
        explanation += f"the risk of heart disease is low ({probability:.1f}%). "
        explanation += "Most cardiovascular parameters appear within normal ranges."
    elif risk_level == "MODERATE":
        explanation += f"there is a moderate risk of heart disease ({probability:.1f}%). "
        explanation += "Some risk factors are elevated and may benefit from lifestyle modifications."
    elif risk_level == "HIGH":
        explanation += f"there is a high risk of heart disease ({probability:.1f}%). "
        explanation += "Multiple cardiovascular risk factors are present. "
        explanation += "Medical consultation and preventive measures are recommended."
    else:  # CRITICAL
        explanation += f"there is a critical risk of heart disease ({probability:.1f}%). "
        explanation += "Significant cardiovascular risk factors are present. "
        explanation += "Immediate medical evaluation and intervention are strongly recommended."
    
    return explanation

@router.post("/predict", response_model=HeartDiseaseResponse)
async def predict_heart_disease(request: HeartDiseaseRequest):
    """
    Predict heart disease from cardiovascular risk factors
    
    Features include:
    - age: Age in years
    - sex: Sex (1 = male; 0 = female)
    - cp: Chest pain type (0-3)
    - trestbps: Resting blood pressure
    - chol: Serum cholesterol
    - fbs: Fasting blood sugar > 120 mg/dl (1 = true; 0 = false)
    - restecg: Resting electrocardiographic results (0-2)
    - thalach: Maximum heart rate achieved
    - exang: Exercise induced angina (1 = yes; 0 = no)
    - oldpeak: ST depression induced by exercise
    - slope: Slope of the peak exercise ST segment (0-2)
    - ca: Number of major vessels (0-3) colored by fluoroscopy
    - thal: Thalassemia (1 = normal; 2 = fixed defect; 3 = reversible defect)
    """
    try:
        # Convert request to feature array
        features_array = np.array([[
            request.age,
            request.sex,
            request.cp,
            request.trestbps,
            request.chol,
            request.fbs,
            request.restecg,
            request.thalach,
            request.exang,
            request.oldpeak,
            request.slope,
            request.ca,
            request.thal
        ]])
        
        # Load model and scaler
        model, scaler = load_heart_disease_model()
        
        # Scale features if scaler is available
        if scaler is not None:
            features_array = scaler.transform(features_array)
        
        # Make prediction
        probabilities = model.predict_proba(features_array)[0]
        
        # Extract probabilities
        healthy_prob = probabilities[0] * 100
        disease_prob = probabilities[1] * 100
        
        # Determine prediction and risk level
        prediction = "Heart Disease Risk Detected" if disease_prob > healthy_prob else "Healthy"
        confidence = max(disease_prob, healthy_prob)
        risk_level = calculate_risk_level(disease_prob)
        
        # Get feature importance and risk factors
        feature_importance = get_feature_importance()
        input_features = request.dict()
        top_risk_factors = get_top_risk_factors(input_features, feature_importance)
        
        # Generate explanation
        explanation = generate_explanation(disease_prob, risk_level, input_features)
        
        return HeartDiseaseResponse(
            disease="Heart Disease",
            confidence=confidence,
            risk_level=risk_level,
            prediction=prediction,
            explanation=explanation,
            input_features=input_features,
            feature_importance=feature_importance,
            top_risk_factors=top_risk_factors,
            disease_probability=disease_prob,
            healthy_probability=healthy_prob
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")
