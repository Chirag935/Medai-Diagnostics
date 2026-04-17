"""
Metrics Router — Production version
Reads real model performance data from *_metadata.json files
instead of returning hardcoded dummy values.
"""
import os
import json
from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from datetime import datetime

from app.schemas.prediction import ModelMetrics, AllMetricsResponse

router = APIRouter()

# Map disease slug → (metadata file, display name)
DISEASE_CONFIG: Dict[str, Dict[str, str]] = {
    "pneumonia": {
        "name": "Pneumonia Detection Ensemble",
        "meta": "models/pneumonia_real_metadata.json",
        "fallback_meta": "models/pneumonia_metadata.json",
    },
    "malaria": {
        "name": "Malaria Detection Ensemble",
        "meta": "models/malaria_real_metadata.json",
        "fallback_meta": "models/malaria_metadata.json",
    },
    "breast-cancer": {
        "name": "Breast Cancer Random Forest",
        "meta": "models/breast_cancer_metadata.json",
    },
    "diabetes": {
        "name": "Diabetes Prediction Model",
        "meta": "models/diabetes_metadata.json",
    },
    "alzheimer": {
        "name": "Alzheimer Detection Model",
        "meta": "models/alzheimer_metadata.json",
    },
    "liver-disease": {
        "name": "Liver Disease Random Forest",
        "meta": "models/liver_disease_metadata.json",
    },
    "kidney-disease": {
        "name": "Kidney Disease Model",
        "meta": "models/kidney_disease_metadata.json",
    },
    "heart-disease": {
        "name": "Heart Disease Random Forest",
        "meta": "models/heart_disease_metadata.json",
    },
}


def _load_metadata(disease: str) -> dict:
    """Load metadata JSON for a disease, trying primary then fallback path."""
    cfg = DISEASE_CONFIG.get(disease)
    if cfg is None:
        return {}

    for key in ("meta", "fallback_meta"):
        path = cfg.get(key)
        if path and os.path.exists(path):
            try:
                with open(path, "r") as f:
                    return json.load(f)
            except Exception:
                continue
    return {}


def _build_metrics(disease: str) -> ModelMetrics:
    """Build a ModelMetrics object from real metadata (or zeros if missing)."""
    cfg = DISEASE_CONFIG[disease]
    meta = _load_metadata(disease)

    accuracy = meta.get("accuracy", 0.0)
    precision = meta.get("precision", 0.0)
    recall = meta.get("recall", 0.0)
    f1 = meta.get("f1_score", 0.0)
    roc_auc = meta.get("roc_auc", 0.0)

    # Confusion matrix — expect list-of-lists or flat list
    cm = meta.get("confusion_matrix", [[0, 0], [0, 0]])
    if isinstance(cm, dict):
        cm = [[0, 0], [0, 0]]

    return ModelMetrics(
        model_name=cfg["name"],
        accuracy=accuracy,
        precision=precision,
        recall=recall,
        f1_score=f1,
        specificity=meta.get("specificity", 0.0),
        sensitivity=recall,  # sensitivity == recall
        auc_roc=roc_auc,
        mcc=meta.get("mcc", 0.0),
        confusion_matrix=cm,
        training_accuracy=meta.get("training_accuracy", accuracy),
        validation_accuracy=meta.get("validation_accuracy", accuracy),
        test_accuracy=meta.get("test_accuracy", accuracy),
        dataset_info=meta.get("dataset_info", {
            "source": "Trained model",
            "samples": meta.get("n_samples", 0),
            "features": meta.get("n_features", 0),
        }),
    )


@router.get("/{disease}", response_model=ModelMetrics)
async def get_disease_metrics(disease: str):
    """Get real performance metrics for a specific disease model."""
    if disease not in DISEASE_CONFIG:
        raise HTTPException(status_code=404, detail=f"Disease model '{disease}' not found")

    return _build_metrics(disease)


@router.get("/all", response_model=AllMetricsResponse)
async def get_all_metrics():
    """Get performance metrics for all disease models."""
    metrics = {}
    accuracy_vals = []
    auc_vals = []

    for disease in DISEASE_CONFIG:
        m = _build_metrics(disease)
        metrics[disease] = m
        accuracy_vals.append(m.accuracy)
        auc_vals.append(m.auc_roc)

    labels = [d.replace("-", " ").title() for d in DISEASE_CONFIG]

    comparison_data = {
        "accuracy_comparison": {
            "labels": labels,
            "datasets": [{"label": "Accuracy", "data": accuracy_vals}],
        },
        "auc_roc_comparison": {
            "labels": labels,
            "datasets": [{"label": "AUC-ROC", "data": auc_vals}],
        },
    }

    return AllMetricsResponse(
        metrics=metrics,
        comparison_chart_data=comparison_data,
    )
