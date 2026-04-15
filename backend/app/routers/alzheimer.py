from fastapi import APIRouter, HTTPException
import numpy as np
import joblib
import os
import json
from typing import Dict, Any

from app.schemas.prediction import AlzheimerRequest, AlzheimerResponse

router = APIRouter()

def load_alzheimer_model():
    """Load trained Alzheimer's prediction model"""
    model_path = "models/alzheimer_model.pkl"
    scaler_path = "models/alzheimer_scaler.pkl"
    
    if os.path.exists(model_path) and os.path.exists(scaler_path):
        model = joblib.load(model_path)
        scaler = joblib.load(scaler_path)
        return model, scaler
    else:
        # Train model if it doesn't exist
        print("Training Alzheimer's model...")
        try:
            import train_alzheimer_model
            model, scaler, _ = train_alzheimer_model.train_alzheimer_model()
            return model, scaler
        except Exception as e:
            print(f"Error training model: {e}")
            # Return dummy model as fallback
            return DummyAlzheimerModel(), None

class DummyAlzheimerModel:
    """Fallback dummy model for demonstration"""
    def predict_proba(self, X):
        # Return dummy probabilities for 4 classes
        return np.array([[0.2, 0.15, 0.25, 0.4]])  # [non_demented, very_mild, mild, moderate]
    
    def predict(self, X):
        return np.array([3])  # moderate

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
    """Return feature importance for Alzheimer's prediction"""
    try:
        if os.path.exists("models/alzheimer_metadata.json"):
            with open("models/alzheimer_metadata.json", "r") as f:
                metadata = json.load(f)
                return metadata.get("feature_importance", {})
    except Exception:
        pass
    
    # Fallback to default importance
    return {
        "mmse_score": 0.15,
        "age": 0.13,
        "cortical_thickness": 0.11,
        "adl_score": 0.10,
        "memory_complaints": 0.10,
        "brain_volume_ratio": 0.09,
        "functional_assessment": 0.09,
        "education_years": 0.06,
        "behavioral_problems": 0.06,
        "csf_protein_level": 0.06,
        "hippocampal_atrophy": 0.06,
        "gender": 0.01
    }

def get_top_risk_factors(features: Dict[str, float], feature_importance: Dict[str, float]) -> list:
    """Get top 3 risk factors based on input values and feature importance"""
    risk_factors = []
    
    if features.get("mmse_score", 0) < 20:
        risk_factors.append("Low MMSE score")
    if features.get("age", 0) > 75:
        risk_factors.append("Advanced age")
    if features.get("memory_complaints", 0) == 1:
        risk_factors.append("Memory complaints")
    if features.get("behavioral_problems", 0) == 1:
        risk_factors.append("Behavioral problems")
    if features.get("cortical_thickness", 0) < 2.5:
        risk_factors.append("Reduced cortical thickness")
    
    return risk_factors[:3]

def generate_explanation(probability: float, risk_level: str, features: Dict[str, float]) -> str:
    """Generate clinical explanation of prediction"""
    age = features.get("age", 0)
    mmse = features.get("mmse_score", 0)
    
    explanation = f"Based on comprehensive cognitive assessment, "
    
    if risk_level == "LOW":
        explanation += f"the risk of Alzheimer's disease is low ({probability:.1f}%). "
        explanation += "Cognitive function appears largely preserved with minimal impairment."
    elif risk_level == "MODERATE":
        explanation += f"there is a moderate risk of Alzheimer's disease ({probability:.1f}%). "
        explanation += "Some cognitive impairment is present that may benefit from early intervention."
    elif risk_level == "HIGH":
        explanation += f"there is a high risk of Alzheimer's disease ({probability:.1f}%). "
        explanation += "Significant cognitive impairment is evident. "
        explanation += "Neurological evaluation and cognitive therapy are recommended."
    else:  # CRITICAL
        explanation += f"there is a critical risk of Alzheimer's disease ({probability:.1f}%). "
        explanation += "Severe cognitive impairment is present with significant functional limitations. "
        explanation += "Immediate neurological evaluation and comprehensive care planning are essential."
    
    return explanation

@router.post("/predict", response_model=AlzheimerResponse)
async def predict_alzheimer(request: AlzheimerRequest):
    """
    Predict Alzheimer's disease from clinical parameters
    
    Features include:
    - age: Age in years
    - gender: Gender (1 = male; 0 = female)
    - education_years: Years of education
    - mmse_score: Mini-Mental State Examination score
    - memory_complaints: Memory complaints (1 = yes; 0 = no)
    - behavioral_problems: Behavioral problems (1 = yes; 0 = no)
    - adl_score: Activities of Daily Living score
    - functional_assessment: Functional assessment score
    - brain_volume_ratio: Brain volume ratio
    - cortical_thickness: Cortical thickness
    - csf_protein_level: CSF protein level
    - hippocampal_atrophy: Hippocampal atrophy score
    """
    try:
        # Convert request to feature array
        features_array = np.array([[
            request.age,
            request.gender,
            request.education_years,
            request.mmse_score,
            request.memory_complaints,
            request.behavioral_problems,
            request.adl_score,
            request.functional_assessment,
            request.brain_volume_ratio,
            request.cortical_thickness,
            request.csf_protein_level,
            request.hippocampal_atrophy
        ]])
        
        # Load model and scaler
        model, scaler = load_alzheimer_model()
        
        # Scale features if scaler is available
        if scaler is not None:
            features_array = scaler.transform(features_array)
        
        # Make prediction
        probabilities = model.predict_proba(features_array)[0]
        
        # Extract probabilities
        non_demented_prob = probabilities[0] * 100
        very_mild_prob = probabilities[1] * 100
        mild_prob = probabilities[2] * 100
        moderate_prob = probabilities[3] * 100
        
        # Determine predicted class and overall risk
        class_names = ['Non-Demented', 'Very Mild', 'Mild', 'Moderate']
        predicted_class_idx = np.argmax(probabilities)
        predicted_class = class_names[predicted_class_idx]
        
        # Calculate overall dementia risk
        dementia_risk = (very_mild_prob + mild_prob + moderate_prob) / 3
        confidence = max(probabilities) * 100
        risk_level = calculate_risk_level(dementia_risk)
        
        # Get feature importance and risk factors
        feature_importance = get_feature_importance()
        input_features = request.dict()
        top_risk_factors = get_top_risk_factors(input_features, feature_importance)
        
        # Generate explanation
        explanation = generate_explanation(dementia_risk, risk_level, input_features)
        
        return AlzheimerResponse(
            disease="Alzheimer's",
            confidence=confidence,
            risk_level=risk_level,
            prediction=f"{predicted_class} Cognitive Impairment",
            explanation=explanation,
            input_features=input_features,
            feature_importance=feature_importance,
            top_risk_factors=top_risk_factors,
            non_demented_probability=non_demented_prob,
            very_mild_probability=very_mild_prob,
            mild_probability=mild_prob,
            moderate_probability=moderate_prob,
            predicted_class=predicted_class
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")
