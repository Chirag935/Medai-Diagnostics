import os
import json
from fastapi import APIRouter, HTTPException
from typing import Dict, Any

router = APIRouter()

DISEASE_CONFIG = {
    "symptoms": {
        "name": "General Symptom Predictor (Random Forest)",
        "meta": "models/symptom_disease_metadata.json",
    },
    "skin": {
        "name": "Skin Infection Classifier (CNN)",
        "meta": "models/skin_disease_metadata.json",
    }
}

def _load_metadata(model_key: str) -> dict:
    cfg = DISEASE_CONFIG.get(model_key)
    if not cfg:
        return {}
    path = cfg.get("meta")
    if path and os.path.exists(path):
        try:
            with open(path, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return {}

@router.get("/{model_key}")
async def get_metrics(model_key: str):
    if model_key not in DISEASE_CONFIG:
        raise HTTPException(status_code=404, detail="Model not found")
        
    meta = _load_metadata(model_key)
    return {
        "model_name": DISEASE_CONFIG[model_key]["name"],
        "accuracy": meta.get("accuracy", 0.0),
        "classes": len(meta.get("diseases", meta.get("classes", []))),
        "status": "active" if meta else "not_trained"
    }

@router.get("/")
async def get_all_metrics():
    res = {}
    for key in DISEASE_CONFIG:
        meta = _load_metadata(key)
        res[key] = {
            "model_name": DISEASE_CONFIG[key]["name"],
            "accuracy": meta.get("accuracy", 0.0),
            "status": "active" if meta else "not_trained"
        }
    return res
