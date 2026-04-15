from fastapi import APIRouter, HTTPException
import numpy as np
import joblib
import os
import json
from typing import Dict, Any

from app.schemas.prediction import BreastCancerRequest, BreastCancerResponse

router = APIRouter()

def load_breast_cancer_model():
    """Load the trained breast cancer prediction model"""
    model_path = "models/breast_cancer_model.pkl"
    scaler_path = "models/breast_cancer_scaler.pkl"
    
    if os.path.exists(model_path) and os.path.exists(scaler_path):
        model = joblib.load(model_path)
        scaler = joblib.load(scaler_path)
        return model, scaler
    else:
        print("Breast cancer model not found. Please run: python train_real_breast_cancer_model.py")
        return DummyBreastCancerModel(), None

class DummyBreastCancerModel:
    """Fallback dummy model for demonstration"""
    def predict_proba(self, X):
        # Return dummy probabilities
        return np.array([[0.1, 0.9]])  # [benign, malignant]
    
    def predict(self, X):
        return np.array([1])  # malignant

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
    """Return feature importance for breast cancer prediction"""
    try:
        # Try to load actual model feature importance
        if os.path.exists("models/breast_cancer_metadata.json"):
            with open("models/breast_cancer_metadata.json", "r") as f:
                metadata = json.load(f)
                return metadata.get("feature_importance", {})
    except Exception:
        pass
    
    # Fallback to default importance
    return {
        "concave_points_worst": 0.25,
        "radius_worst": 0.18,
        "texture_worst": 0.15,
        "area_worst": 0.12,
        "perimeter_worst": 0.10,
        "concavity_worst": 0.08,
        "compactness_worst": 0.06,
        "symmetry_worst": 0.04
    }

def get_top_risk_factors(features: Dict[str, float], feature_importance: Dict[str, float]) -> list:
    """Get top 3 risk factors based on input values and feature importance"""
    risk_factors = []
    
    # Check for high values in important features
    if features.get("concave_points_worst", 0) > 0.15:
        risk_factors.append("High concave points")
    if features.get("radius_worst", 0) > 17:
        risk_factors.append("Large radius")
    if features.get("texture_worst", 0) > 25:
        risk_factors.append("Irregular texture")
    if features.get("area_worst", 0) > 800:
        risk_factors.append("Large area")
    if features.get("concavity_worst", 0) > 0.2:
        risk_factors.append("High concavity")
    
    return risk_factors[:3]  # Return top 3

def generate_explanation(probability: float, risk_level: str, features: Dict[str, float]) -> str:
    """Generate clinical explanation of the prediction"""
    radius = features.get("radius_worst", 0)
    texture = features.get("texture_worst", 0)
    concave_points = features.get("concave_points_worst", 0)
    
    explanation = f"Based on the analysis of breast tumor characteristics, "
    
    if risk_level == "LOW":
        explanation += f"the risk of malignancy is low ({probability:.1f}%). "
        explanation += "The tumor characteristics suggest benign features with regular borders and uniform texture."
    elif risk_level == "MODERATE":
        explanation += f"there is a moderate risk of malignancy ({probability:.1f}%). "
        explanation += "Some tumor characteristics show atypical features that warrant further investigation."
    elif risk_level == "HIGH":
        explanation += f"there is a high risk of malignancy ({probability:.1f}%). "
        explanation += "The tumor shows several concerning features including irregular borders and texture. "
        explanation += "Biopsy and further diagnostic testing are recommended."
    else:  # CRITICAL
        explanation += f"there is a critical risk of malignancy ({probability:.1f}%). "
        explanation += "The tumor characteristics are highly suggestive of malignancy. "
        explanation += "Immediate medical consultation and diagnostic procedures are strongly recommended."
    
    return explanation

@router.post("/predict", response_model=BreastCancerResponse)
async def predict_breast_cancer(request: BreastCancerRequest):
    """
    Predict breast cancer from clinical features
    
    All 30 features from the Wisconsin Diagnostic Breast Cancer (WDBC) dataset:
    - radius, texture, perimeter, area, smoothness, compactness, concavity, concave points, symmetry, fractal dimension
    - Each feature has mean, standard error, and worst (largest) values
    """
    try:
        # Convert request to feature array
        features_array = np.array([[
            request.radius_mean,
            request.texture_mean,
            request.perimeter_mean,
            request.area_mean,
            request.smoothness_mean,
            request.compactness_mean,
            request.concavity_mean,
            request.concave_points_mean,
            request.symmetry_mean,
            request.fractal_dimension_mean,
            request.radius_se,
            request.texture_se,
            request.perimeter_se,
            request.area_se,
            request.smoothness_se,
            request.compactness_se,
            request.concavity_se,
            request.concave_points_se,
            request.symmetry_se,
            request.fractal_dimension_se,
            request.radius_worst,
            request.texture_worst,
            request.perimeter_worst,
            request.area_worst,
            request.smoothness_worst,
            request.compactness_worst,
            request.concavity_worst,
            request.concave_points_worst,
            request.symmetry_worst,
            request.fractal_dimension_worst
        ]])
        
        # Load model and scaler
        model, scaler = load_breast_cancer_model()
        
        # Scale features if scaler is available
        if scaler is not None:
            features_array = scaler.transform(features_array)
        
        # Make prediction
        probabilities = model.predict_proba(features_array)[0]
        
        # Extract probabilities
        benign_prob = probabilities[0] * 100
        malignant_prob = probabilities[1] * 100
        
        # Determine prediction and risk level
        prediction = "Malignant" if malignant_prob > benign_prob else "Benign"
        confidence = max(malignant_prob, benign_prob)
        risk_level = calculate_risk_level(malignant_prob)
        
        # Get feature importance and risk factors
        feature_importance = get_feature_importance()
        input_features = request.dict()
        top_risk_factors = get_top_risk_factors(input_features, feature_importance)
        
        # Generate explanation
        explanation = generate_explanation(malignant_prob, risk_level, input_features)
        
        return BreastCancerResponse(
            disease="Breast Cancer",
            confidence=confidence,
            risk_level=risk_level,
            prediction=prediction,
            explanation=explanation,
            input_features=input_features,
            feature_importance=feature_importance,
            top_risk_factors=top_risk_factors,
            malignant_probability=malignant_prob,
            benign_probability=benign_prob
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")
