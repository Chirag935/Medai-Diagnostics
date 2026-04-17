"""
Pneumonia Detection Router — Production version
Uses 37-feature extraction from grayscale chest X-rays
matching the pneumonia_real.pkl Ensemble (RF+ET) model.
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

# Cached model objects
_model = None
_scaler = None
_metadata = None


def _load_model():
    """Load model and cache for subsequent requests."""
    global _model, _scaler, _metadata
    if _model is not None:
        return _model, _scaler, _metadata

    model_path = "models/pneumonia_real.pkl"
    scaler_path = "models/pneumonia_real_scaler.pkl"
    meta_path = "models/pneumonia_real_metadata.json"

    if not os.path.exists(model_path):
        raise HTTPException(503, "Pneumonia model file not found. Please train the model first.")

    _model = joblib.load(model_path)
    _scaler = joblib.load(scaler_path) if os.path.exists(scaler_path) else None

    if os.path.exists(meta_path):
        with open(meta_path) as f:
            _metadata = json.load(f)
    else:
        _metadata = {}

    return _model, _scaler, _metadata


def _extract_features(image_bytes: bytes) -> np.ndarray:
    """
    Extract exactly 37 features from a chest X-ray image.
    6 global + 12 regional + 6 ratios + 4 texture + 9 histogram = 37.
    """
    # Decode image
    img_array = np.frombuffer(image_bytes, dtype=np.uint8)
    img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

    # PIL fallback
    if img is None:
        pil_img = Image.open(io.BytesIO(image_bytes))
        if pil_img.mode != "RGB":
            pil_img = pil_img.convert("RGB")
        img = np.array(pil_img)

    # Convert to grayscale
    if len(img.shape) == 3:
        img = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)

    img = cv2.resize(img, (128, 128))
    img_n = img.astype(np.float32) / 255.0
    h, w = img_n.shape
    total_pixels = h * w

    features = []

    # 1. Global statistics — 6 features
    features.extend([
        float(np.mean(img_n)),
        float(np.std(img_n)),
        float(np.percentile(img_n, 10)),
        float(np.percentile(img_n, 90)),
        float(np.min(img_n)),
        float(np.max(img_n)),
    ])

    # 2. Regional analysis — 6 regions × 2 = 12 features
    regions = [
        img_n[0 : h // 2, 0 : w // 2],
        img_n[0 : h // 2, w // 2 :],
        img_n[h // 2 :, 0 : w // 2],
        img_n[h // 2 :, w // 2 :],
        img_n[h // 4 : 3 * h // 4, :],
        img_n[:, w // 4 : 3 * w // 4],
    ]
    for r in regions:
        features.append(float(np.mean(r)))
        features.append(float(np.std(r)))

    # 3. Intensity ratios — 6 features
    features.append(float(np.sum(img_n < 0.2) / total_pixels))
    features.append(float(np.sum(img_n > 0.7) / total_pixels))
    features.append(float(np.sum((img_n >= 0.3) & (img_n <= 0.7)) / total_pixels))
    features.append(float(np.sum(img_n < 0.1) / total_pixels))
    features.append(float(np.sum(img_n > 0.9) / total_pixels))
    features.append(float(np.std(img_n) ** 2))

    # 4. Texture — 4 features
    laplacian = cv2.Laplacian(img, cv2.CV_64F)
    features.append(float(np.var(laplacian) / 10000))
    features.append(float(np.mean(np.abs(laplacian)) / 100))
    sobelx = cv2.Sobel(img, cv2.CV_64F, 1, 0, ksize=3)
    sobely = cv2.Sobel(img, cv2.CV_64F, 0, 1, ksize=3)
    features.append(float(np.mean(np.abs(sobelx))))
    features.append(float(np.mean(np.abs(sobely))))

    # 5. Histogram — 9 features
    hist, _ = np.histogram(img_n.flatten(), bins=9, range=(0, 1))
    features.extend((hist / total_pixels).tolist())

    assert len(features) == 37, f"Expected 37 features, got {len(features)}"
    return np.array(features, dtype=np.float32).reshape(1, -1)


@router.post("/predict")
async def predict_pneumonia(file: UploadFile = File(...)):
    """Predict pneumonia from a chest X-ray image."""
    try:
        model, scaler, metadata = _load_model()

        contents = await file.read()
        features = _extract_features(contents)

        # Validate feature count
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

        probs = model.predict_proba(features)[0]
        prediction = model.predict(features)[0]

        has_pneumonia = int(prediction) == 1
        confidence = round(float(probs[int(prediction)]) * 100, 1)
        pneumonia_prob = round(float(probs[1]) * 100, 1)
        normal_prob = round(float(probs[0]) * 100, 1)

        # Determine risk level based on pneumonia probability
        if pneumonia_prob >= 80:
            risk_level = "CRITICAL"
        elif pneumonia_prob >= 60:
            risk_level = "HIGH"
        elif pneumonia_prob >= 40:
            risk_level = "MODERATE"
        else:
            risk_level = "LOW"

        # Generate explanation
        if has_pneumonia:
            explanation = f"The AI model detected patterns consistent with pneumonia in the chest X-ray with {confidence}% confidence. The lung opacity patterns suggest possible infection."
        else:
            explanation = f"The chest X-ray analysis shows normal lung tissue with {confidence}% confidence. No significant pneumonia indicators were detected."

        return {
            "prediction": "Pneumonia Detected" if has_pneumonia else "Normal - No Pneumonia",
            "confidence": confidence,
            "risk_level": risk_level,
            "explanation": explanation,
            "pneumonia_probability": pneumonia_prob,
            "normal_probability": normal_prob,
            "probabilities": {
                "pneumonia": pneumonia_prob,
                "normal": normal_prob,
            },
            "model_accuracy": metadata.get("accuracy", 0),
            "model_info": {
                "type": metadata.get("model", "Ensemble"),
                "features": metadata.get("n_features", 37),
            },
            "timestamp": datetime.now().isoformat(),
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Prediction failed: {str(e)}")
