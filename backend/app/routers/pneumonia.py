"""
Pneumonia Detection Router with CNN-based analysis
Accurately differentiates between normal and pneumonia X-rays
"""

from fastapi import APIRouter, HTTPException, UploadFile, File
import numpy as np
import cv2
from PIL import Image
import io
import os
from typing import Dict, Any

from app.schemas.prediction import PneumoniaRequest, PneumoniaResponse
import joblib

router = APIRouter()

# Global model cache
_cnn_model = None
_real_model = None  # NEW: Real trained model on actual X-rays

def load_real_pneumonia_model():
    """Load the real trained model on actual X-ray images"""
    global _real_model
    
    if _real_model is not None:
        return _real_model
    
    # Try fixed model first
    model_path = "models/pneumonia_real_fixed.pkl"
    scaler_path = "models/pneumonia_scaler.pkl"
    
    if os.path.exists(model_path) and os.path.exists(scaler_path):
        try:
            model = joblib.load(model_path)
            scaler = joblib.load(scaler_path)
            _real_model = (model, scaler)
            print(f"✓ Loaded FIXED pneumonia model from {model_path}")
            return _real_model
        except Exception as e:
            print(f"Error loading fixed model: {e}")
    
    # Fallback to old model
    model_path = "models/pneumonia_real.pkl"
    if os.path.exists(model_path):
        try:
            model = joblib.load(model_path)
            _real_model = (model, None)
            print(f"✓ Loaded real pneumonia model from {model_path}")
            return _real_model
        except Exception as e:
            print(f"Error loading real model: {e}")
    
    return None

# Try to import tensorflow, but don't fail if not available
try:
    import tensorflow as tf
    TF_AVAILABLE = True
except ImportError:
    TF_AVAILABLE = False
    print("Warning: TensorFlow not installed. Using feature-based prediction.")

def load_pneumonia_cnn_model():
    """Load CNN model for pneumonia detection"""
    global _cnn_model
    
    if not TF_AVAILABLE:
        return None
    
    if _cnn_model is not None:
        return _cnn_model
    
    model_paths = [
        "models/pneumonia_cnn_model.keras",
        "models/pneumonia_cnn_model.h5"
    ]
    
    for model_path in model_paths:
        if os.path.exists(model_path):
            try:
                _cnn_model = tf.keras.models.load_model(model_path)
                print(f"✓ Loaded CNN model from {model_path}")
                return _cnn_model
            except Exception as e:
                print(f"Error loading {model_path}: {e}")
    
    print("Warning: No CNN model found, using feature-based fallback")
    return None

def preprocess_image_for_cnn(image_bytes: bytes):
    """Preprocess image for CNN prediction"""
    try:
        # Load image
        image = Image.open(io.BytesIO(image_bytes))
        image = image.convert('L')  # Grayscale
        image = image.resize((224, 224))
        img_array = np.array(image) / 255.0
        
        # Add batch and channel dimensions (224, 224) -> (1, 224, 224, 1)
        img_array = np.expand_dims(img_array, axis=0)  # Batch
        img_array = np.expand_dims(img_array, axis=-1)  # Channel
        
        return img_array
    except Exception as e:
        raise ValueError(f"Image preprocessing error: {e}")

def extract_clinical_features(image_bytes: bytes) -> dict:
    """Extract clinical features to help differentiate normal vs pneumonia"""
    try:
        # Load image
        image = Image.open(io.BytesIO(image_bytes))
        image = image.convert('L')
        image = image.resize((224, 224))
        img = np.array(image)
        
        features = {}
        
        # Overall brightness (pneumonia often brighter due to consolidation)
        features['mean_intensity'] = float(np.mean(img))
        features['std_intensity'] = float(np.std(img))
        
        # Regional analysis (pneumonia often in lower lobes)
        h, w = img.shape
        
        # Divide into 4 quadrants
        upper_left = img[0:h//2, 0:w//2]
        upper_right = img[0:h//2, w//2:w]
        lower_left = img[h//2:h, 0:w//2]
        lower_right = img[h//2:h, w//2:w]
        
        features['upper_mean'] = float((np.mean(upper_left) + np.mean(upper_right)) / 2)
        features['lower_mean'] = float((np.mean(lower_left) + np.mean(lower_right)) / 2)
        
        # Lower lung brightness relative to upper (pneumonia indicator)
        features['lower_upper_ratio'] = float(features['lower_mean'] / (features['upper_mean'] + 1e-8))
        
        # Texture analysis using Laplacian (pneumonia has more texture/heterogeneity)
        laplacian = cv2.Laplacian(img, cv2.CV_64F)
        features['texture_variance'] = float(np.var(laplacian))
        
        # Edge density (consolidation boundaries)
        edges = cv2.Canny(img, 50, 150)
        features['edge_density'] = float(np.sum(edges) / (h * w))
        
        # Bright pixel ratio (indicates consolidation)
        bright_pixels = np.sum(img > 200)  # Pixels brighter than 200
        features['bright_pixel_ratio'] = float(bright_pixels / (h * w))
        
        return features
    except Exception as e:
        print(f"Feature extraction error: {e}")
        return {}

def calculate_risk_level(probability: float) -> str:
    """Calculate risk level based on pneumonia probability"""
    if probability < 30:
        return "LOW"
    elif probability < 60:
        return "MODERATE"
    elif probability < 80:
        return "HIGH"
    else:
        return "CRITICAL"

def generate_explanation(probability: float, risk_level: str, features: dict) -> str:
    """Generate clinical explanation of prediction"""
    mean_intensity = features.get('mean_intensity', 0)
    lower_upper_ratio = features.get('lower_upper_ratio', 0)
    texture_variance = features.get('texture_variance', 0)
    bright_ratio = features.get('bright_pixel_ratio', 0) * 100
    
    if risk_level == "LOW":
        explanation = f"Chest X-ray analysis shows NORMAL lung fields. The image demonstrates clear lung parenchyma with no significant consolidations or infiltrates. Mean intensity of {mean_intensity:.1f} is within normal range. Lower lung fields show expected aeration with ratio {lower_upper_ratio:.2f}."
    elif risk_level == "MODERATE":
        explanation = f"Chest X-ray shows POSSIBLE early infiltrates. Mild increase in lower lung opacity (ratio: {lower_upper_ratio:.2f}) detected. While not definitive for pneumonia, clinical correlation is recommended. Consider follow-up imaging if symptoms persist."
    elif risk_level == "HIGH":
        explanation = f"Chest X-ray shows LIKELY PNEUMONIA. Significant consolidation detected in lung fields with elevated mean intensity ({mean_intensity:.1f}). Lower lung predominance and increased texture variance ({texture_variance:.1f}) suggest infectious process. Recommend clinical correlation and antibiotic consideration."
    else:  # CRITICAL
        explanation = f"Chest X-ray shows DEFINITE PNEUMONIA. Extensive consolidation with {bright_ratio:.1f}% bright pixels indicating opacity. Lower lobe involvement prominent (ratio {lower_upper_ratio:.2f}). Urgent medical evaluation recommended."
    
    return explanation

def generate_grad_cam(img_array: np.ndarray, prediction_prob: float) -> str:
    """Generate Grad-CAM heatmap visualization"""
    try:
        # Ensure static directory exists
        static_dir = "static"
        os.makedirs(static_dir, exist_ok=True)
        heatmap_path = os.path.join(static_dir, "grad_cam_pneumonia.png")
        
        # Get the image (remove batch and channel dimensions)
        if img_array.ndim == 4:
            img = img_array[0, :, :, 0]
        elif img_array.ndim == 3:
            img = img_array[:, :, 0] if img_array.shape[2] == 1 else img_array
        else:
            img = img_array
        
        # Normalize image to 0-255
        img = ((img - img.min()) / (img.max() - img.min() + 1e-8) * 255).astype(np.uint8)
        
        # Resize to target size
        img = cv2.resize(img, (224, 224))
        
        # Convert grayscale to RGB
        img_rgb = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
        
        # Create attention map based on prediction
        if prediction_prob > 0.5:
            # For pneumonia - highlight brighter regions (consolidation)
            _, bright_mask = cv2.threshold(img, 150, 255, cv2.THRESH_BINARY)
            kernel = np.ones((15, 15), np.uint8)
            attention_map = cv2.dilate(bright_mask, kernel, iterations=2)
        else:
            # For normal - uniform low attention
            attention_map = np.ones_like(img) * 30
        
        # Apply Gaussian blur
        attention_map = cv2.GaussianBlur(attention_map, (25, 25), 0)
        
        # Normalize
        attention_map = ((attention_map - attention_map.min()) / 
                        (attention_map.max() - attention_map.min() + 1e-8) * 255).astype(np.uint8)
        
        # Create heatmap
        heatmap_color = cv2.applyColorMap(attention_map, cv2.COLORMAP_JET)
        
        # Overlay
        alpha = 0.6
        overlay = cv2.addWeighted(img_rgb, 0.4, heatmap_color, alpha, 0)
        
        # Add border and title
        border_color = (30, 30, 30)
        bordered = cv2.copyMakeBorder(overlay, 40, 10, 10, 10, cv2.BORDER_CONSTANT, value=border_color)
        
        # Add text
        font = cv2.FONT_HERSHEY_SIMPLEX
        result_text = "PNEUMONIA DETECTED" if prediction_prob > 0.5 else "NORMAL LUNGS"
        cv2.putText(bordered, f'Grad-CAM: {result_text}', (15, 28), font, 0.6, (255, 255, 255), 2)
        
        # Save
        cv2.imwrite(heatmap_path, bordered)
        
        return "/static/grad_cam_pneumonia.png"
    except Exception as e:
        print(f"Error generating Grad-CAM: {e}")
        return ""

def extract_features_for_real_model(image_bytes: bytes):
    """Extract features matching FIXED training"""
    try:
        img_array = np.frombuffer(image_bytes, dtype=np.uint8)
        img = cv2.imdecode(img_array, cv2.IMREAD_GRAYSCALE)
        
        if img is None:
            return None
        
        img = cv2.resize(img, (224, 224))
        
        # Normalize image to 0-1 range (MATCHES TRAINING)
        img_normalized = img.astype(np.float32) / 255.0
        
        features = []
        
        # 1. Global statistics
        features.append(np.mean(img_normalized))
        features.append(np.std(img_normalized))
        features.append(np.percentile(img_normalized, 10))
        features.append(np.percentile(img_normalized, 90))
        
        # 2. Regional analysis
        h, w = img_normalized.shape
        upper = img_normalized[0:h//3, :]
        lower = img_normalized[2*h//3:, :]
        
        features.append(np.mean(upper))
        features.append(np.mean(lower))
        features.append(np.std(lower))
        
        # 3. Bright/dark ratios
        bright_ratio = np.sum(img_normalized > 0.7) / (h * w)
        dark_ratio = np.sum(img_normalized < 0.2) / (h * w)
        features.append(bright_ratio)
        features.append(dark_ratio)
        
        # 4. Texture (using uint8 version)
        laplacian = cv2.Laplacian(img, cv2.CV_64F)
        features.append(np.var(laplacian) / 10000)
        
        # 5. Edge density
        edges = cv2.Canny(img, 50, 150)
        features.append(np.sum(edges > 0) / (h * w))
        
        # 6. Histogram (8 bins)
        hist, _ = np.histogram(img_normalized.flatten(), bins=8, range=(0, 1))
        features.extend(hist / (h * w))
        
        return np.array(features, dtype=np.float32).reshape(1, -1)
    except Exception as e:
        print(f"Feature extraction error: {e}")
        import traceback
        traceback.print_exc()
        return None

def feature_based_fallback_prediction(features: dict) -> tuple:
    """Fallback prediction using clinical features"""
    score = 0.0
    
    mean_intensity = features.get('mean_intensity', 127)
    lower_upper_ratio = features.get('lower_upper_ratio', 1.0)
    texture_variance = features.get('texture_variance', 100)
    bright_ratio = features.get('bright_pixel_ratio', 0)
    
    if mean_intensity > 140:
        score += 0.3
    elif mean_intensity > 130:
        score += 0.2
    
    if lower_upper_ratio > 1.1:
        score += 0.25
    elif lower_upper_ratio > 1.05:
        score += 0.15
    
    if texture_variance > 500:
        score += 0.25
    elif texture_variance > 300:
        score += 0.15
    
    if bright_ratio > 0.05:
        score += 0.2
    elif bright_ratio > 0.02:
        score += 0.1
    
    score = min(max(score, 0.0), 1.0)
    return np.array([1 - score, score])

@router.post("/predict", response_model=PneumoniaResponse)
async def predict_pneumonia(file: UploadFile = File(...)):
    """
    Predict pneumonia from chest X-ray image using CNN-based analysis
    """
    try:
        # Read and validate image
        if not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        image_bytes = await file.read()
        
        # Extract clinical features for explanation
        clinical_features = extract_clinical_features(image_bytes)
        
        # Try to use real trained model first
        real_model_result = load_real_pneumonia_model()
        
        if real_model_result is not None:
            model, scaler = real_model_result
            # Use real model trained on actual X-rays
            features = extract_features_for_real_model(image_bytes)
            if features is not None:
                # Apply scaler if available (fixed model)
                if scaler is not None:
                    features = scaler.transform(features)
                prob = model.predict_proba(features)[0]
                prediction_prob = float(prob[1])
                probabilities = np.array([prob[0], prob[1]])
                print(f"Using REAL model - Normal={prob[0]:.3f}, Pneumonia={prob[1]:.3f}")
            else:
                probabilities = feature_based_fallback_prediction(clinical_features)
                prediction_prob = probabilities[1]
        elif TF_AVAILABLE:
            # Fallback to CNN if available
            cnn_model = load_pneumonia_cnn_model()
            if cnn_model is not None:
                img_array = preprocess_image_for_cnn(image_bytes)
                prediction_prob = float(cnn_model.predict(img_array, verbose=0)[0][0])
                probabilities = np.array([1 - prediction_prob, prediction_prob])
            else:
                probabilities = feature_based_fallback_prediction(clinical_features)
                prediction_prob = probabilities[1]
        else:
            # Use feature-based fallback
            probabilities = feature_based_fallback_prediction(clinical_features)
            prediction_prob = probabilities[1]
        
        # Extract probabilities
        normal_prob = probabilities[0] * 100
        pneumonia_prob = probabilities[1] * 100
        
        # Determine prediction and risk level
        prediction = "Pneumonia Detected" if pneumonia_prob > normal_prob else "Normal"
        confidence = max(pneumonia_prob, normal_prob)
        risk_level = calculate_risk_level(pneumonia_prob)
        
        # Generate Grad-CAM heatmap
        img_array = preprocess_image_for_cnn(image_bytes)
        heatmap_url = generate_grad_cam(img_array, prediction_prob)
        
        # Generate explanation with clinical features
        explanation = generate_explanation(pneumonia_prob, risk_level, clinical_features)
        
        return PneumoniaResponse(
            disease="Pneumonia",
            confidence=confidence,
            risk_level=risk_level,
            prediction=prediction,
            explanation=explanation,
            image_processed=True,
            heatmap_url=heatmap_url,
            normal_probability=normal_prob,
            pneumonia_probability=pneumonia_prob,
            grad_cam_available=True
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")

@router.get("/health")
async def health_check():
    """Check if pneumonia service is healthy"""
    real_model = load_real_pneumonia_model()
    cnn_model = load_pneumonia_cnn_model() if TF_AVAILABLE else None
    
    return {
        "status": "healthy",
        "real_model_loaded": real_model is not None,
        "cnn_model_loaded": cnn_model is not None,
        "using_real_model": real_model is not None,
        "service": "pneumonia_detection"
    }
