"""
Malaria Detection Router — Production version
Uses 31-feature extraction (24 histogram + 6 statistical + 1 brightness)
matching the malaria_real.pkl Ensemble (RF+ET) model.
"""
import os
import io
import numpy as np
import cv2
from PIL import Image
from fastapi import APIRouter, File, UploadFile, HTTPException
import joblib
import json
from datetime import datetime

router = APIRouter()

# Cached model objects (loaded once on first request)
_model = None
_scaler = None
_metadata = None


def _load_model():
    """Load model and cache for subsequent requests."""
    global _model, _scaler, _metadata
    if _model is not None:
        return _model, _scaler, _metadata

    model_path = "models/malaria_real.pkl"
    scaler_path = "models/malaria_real_scaler.pkl"
    meta_path = "models/malaria_real_metadata.json"

    if not os.path.exists(model_path):
        raise HTTPException(503, "Malaria model file not found. Please train the model first.")

    _model = joblib.load(model_path)
    _scaler = joblib.load(scaler_path) if os.path.exists(scaler_path) else None

    if os.path.exists(meta_path):
        with open(meta_path) as f:
            _metadata = json.load(f)
    else:
        _metadata = {}

    return _model, _scaler, _metadata


def _extract_features(img_array: np.ndarray) -> np.ndarray:
    """
    Extract exactly 31 features from an RGB image.
    24 colour-histogram bins (8 per channel) + 6 channel statistics + 1 brightness.
    """
    img_array = cv2.resize(img_array, (64, 64))
    features = []

    # 1. Colour histogram — 8 bins × 3 channels = 24 features
    for ch in range(3):
        hist = cv2.calcHist([img_array], [ch], None, [8], [0, 256]).flatten()
        hist = hist / (np.sum(hist) + 1e-7)
        features.extend(hist.tolist())

    # 2. Per-channel mean & std — 3 × 2 = 6 features
    for ch in range(3):
        channel = img_array[:, :, ch].astype(np.float32) / 255.0
        features.append(float(np.mean(channel)))
        features.append(float(np.std(channel)))

    # 3. Overall brightness — 1 feature
    gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
    features.append(float(np.mean(gray) / 255.0))

    assert len(features) == 31, f"Expected 31 features, got {len(features)}"
    return np.array(features, dtype=np.float32).reshape(1, -1)


@router.post("/predict")
async def predict_malaria(file: UploadFile = File(...)):
    """Predict malaria from a blood-smear image."""
    try:
        model, scaler, metadata = _load_model()

        # Read & decode image
        contents = await file.read()
        img = Image.open(io.BytesIO(contents))
        if img.mode != "RGB":
            img = img.convert("RGB")
        img_array = np.array(img)

        # Feature extraction
        features = _extract_features(img_array)

        # Validate feature count against model
        if hasattr(model, "n_features_in_") and model.n_features_in_ != features.shape[1]:
            raise HTTPException(
                500,
                f"Feature mismatch: model expects {model.n_features_in_}, got {features.shape[1]}",
            )

        # Scale only if scaler matches feature count
        if scaler and hasattr(scaler, 'n_features_in_') and scaler.n_features_in_ == features.shape[1]:
            features = scaler.transform(features)
        elif scaler:
            print(f"WARNING: Skipping scaler (expects {getattr(scaler, 'n_features_in_', '?')} features, got {features.shape[1]})")

        # Predict
        probs = model.predict_proba(features)[0]
        prediction = model.predict(features)[0]

        is_infected = int(prediction) == 1
        confidence = round(float(probs[int(prediction)]) * 100, 1)
        infected_prob = round(float(probs[1]) * 100, 1)
        uninfected_prob = round(float(probs[0]) * 100, 1)

        # Determine risk level
        if infected_prob >= 80:
            risk_level = "CRITICAL"
        elif infected_prob >= 60:
            risk_level = "HIGH"
        elif infected_prob >= 40:
            risk_level = "MODERATE"
        else:
            risk_level = "LOW"

        # Generate explanation
        if is_infected:
            explanation = f"The AI model detected parasitic patterns in the blood smear consistent with malaria infection with {confidence}% confidence."
        else:
            explanation = f"The blood smear analysis shows no malaria parasites detected with {confidence}% confidence. The cell morphology appears normal."

        return {
            "prediction": "Malaria Detected" if is_infected else "No Malaria - Uninfected",
            "confidence": confidence,
            "risk_level": risk_level,
            "explanation": explanation,
            "infected_probability": infected_prob,
            "uninfected_probability": uninfected_prob,
            "probabilities": {
                "infected": infected_prob,
                "uninfected": uninfected_prob,
            },
            "model_accuracy": metadata.get("accuracy", 0),
            "model_info": {
                "type": metadata.get("model", "Ensemble"),
                "features": metadata.get("n_features", 31),
            },
            "timestamp": datetime.now().isoformat(),
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Prediction failed: {str(e)}")
