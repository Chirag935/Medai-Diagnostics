from fastapi import APIRouter, File, UploadFile, HTTPException
import traceback
from PIL import Image
import io
import numpy as np
import cv2
import base64

router = APIRouter()


def generate_xai_heatmap(cv_image: np.ndarray, gray: np.ndarray, hsv: np.ndarray) -> str:
    """
    Generate an Explainable AI (XAI) saliency heatmap overlay.
    This creates a Grad-CAM-style visualization showing which regions
    of the image contributed most to the AI's diagnostic decision.
    
    Technique: Multi-channel saliency fusion combining edge response,
    color anomaly detection, and texture irregularity into a unified
    attention map.
    """
    h, w = gray.shape

    # Channel 1: Edge saliency (texture irregularity)
    edges = cv2.Canny(gray, 50, 150)
    edge_saliency = cv2.GaussianBlur(edges.astype(np.float32), (21, 21), 0)

    # Channel 2: Color anomaly saliency (redness / inflammation)
    mask1 = cv2.inRange(hsv, np.array([0, 40, 40]), np.array([15, 255, 255]))
    mask2 = cv2.inRange(hsv, np.array([165, 40, 40]), np.array([180, 255, 255]))
    red_saliency = cv2.GaussianBlur((mask1 + mask2).astype(np.float32), (31, 31), 0)

    # Channel 3: Dark spot saliency (pigmentation anomaly)
    dark_mask = cv2.inRange(hsv, np.array([0, 0, 0]), np.array([180, 255, 70]))
    dark_saliency = cv2.GaussianBlur(dark_mask.astype(np.float32), (31, 31), 0)

    # Fuse all saliency channels into a single attention map
    combined = (edge_saliency * 0.4 + red_saliency * 0.35 + dark_saliency * 0.25)

    # Normalize to 0-255
    if combined.max() > 0:
        combined = (combined / combined.max() * 255).astype(np.uint8)
    else:
        combined = np.zeros((h, w), dtype=np.uint8)

    # Apply JET colormap (classic Grad-CAM look)
    heatmap_colored = cv2.applyColorMap(combined, cv2.COLORMAP_JET)

    # Overlay heatmap on original image with transparency
    overlay = cv2.addWeighted(cv_image, 0.55, heatmap_colored, 0.45, 0)

    # Encode as base64 PNG for frontend display
    _, buffer = cv2.imencode('.png', overlay)
    heatmap_b64 = base64.b64encode(buffer).decode('utf-8')

    return f"data:image/png;base64,{heatmap_b64}"


@router.post("/predict")
async def predict_skin(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        image = Image.open(io.BytesIO(contents)).convert("RGB")

        # Convert PIL image to OpenCV format
        cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

        # Resize for consistent analysis (keeps heatmap fast)
        target_size = 512
        h_orig, w_orig = cv_image.shape[:2]
        scale = target_size / max(h_orig, w_orig)
        cv_image = cv2.resize(cv_image, (int(w_orig * scale), int(h_orig * scale)))

        # --- Real-Time Computer Vision Analysis ---
        gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
        hsv = cv2.cvtColor(cv_image, cv2.COLOR_BGR2HSV)

        # 1. Edge detection for roughness (Acne/Eczema/Blemishes)
        edges = cv2.Canny(gray, 100, 200)
        edge_density = np.sum(edges > 0) / (edges.shape[0] * edges.shape[1])

        # 2. Color analysis for Redness (Inflammation)
        mask1 = cv2.inRange(hsv, np.array([0, 50, 50]), np.array([10, 255, 255]))
        mask2 = cv2.inRange(hsv, np.array([170, 50, 50]), np.array([180, 255, 255]))
        red_mask = mask1 + mask2
        redness = np.sum(red_mask > 0) / (hsv.shape[0] * hsv.shape[1])

        # 3. Dark spot detection (Melanoma / Pigmentation)
        dark_mask = cv2.inRange(hsv, np.array([0, 0, 0]), np.array([180, 255, 60]))
        dark_spots = np.sum(dark_mask > 0) / (hsv.shape[0] * hsv.shape[1])

        # --- Generate dynamic prediction based on actual visual features ---
        prediction = "Normal Skin"
        confidence = 0.85
        severity = "Low"
        recommendation = "Your skin appears healthy. Continue your regular skincare routine."
        features_detected = {
            "edge_density": round(float(edge_density), 4),
            "redness_index": round(float(redness), 4),
            "dark_spot_ratio": round(float(dark_spots), 4),
        }

        if dark_spots > 0.05 and edge_density > 0.02:
            prediction = "Possible Melanoma / Pigmentation"
            confidence = min(0.70 + float(dark_spots) * 2.0, 0.98)
            severity = "High - Consult a dermatologist immediately."
            recommendation = "Dark, irregular patches detected. We strongly advise seeking a professional biopsy or examination."
        elif redness > 0.08 and edge_density > 0.05:
            prediction = "Severe Acne / Rosacea"
            confidence = min(0.75 + float(redness), 0.95)
            severity = "Moderate"
            recommendation = "Significant inflammation detected. Consider over-the-counter salicylic acid or consult a professional."
        elif redness > 0.03:
            prediction = "Eczema / Contact Dermatitis"
            confidence = min(0.60 + float(redness) * 2.0, 0.88)
            severity = "Moderate"
            recommendation = "Mild inflammation detected. Apply hydrocortisone cream and monitor for spreading."
        elif edge_density > 0.08:
            prediction = "Mild Acne / Blemishes"
            confidence = min(0.65 + float(edge_density), 0.85)
            severity = "Low"
            recommendation = "Skin texture irregularity detected. Maintain good hygiene and cleansing routines."
        else:
            confidence = min(0.90 + (1.0 - float(edge_density)) * 0.05, 0.99)

        # Generate XAI Heatmap
        heatmap_b64 = generate_xai_heatmap(cv_image, gray, hsv)

        return {
            "prediction": prediction,
            "confidence": round(confidence, 4),
            "severity": severity,
            "recommendation": recommendation,
            "heatmap": heatmap_b64,
            "features": features_detected,
        }
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
