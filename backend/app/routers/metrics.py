from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from datetime import datetime

from app.schemas.prediction import ModelMetrics, AllMetricsResponse

router = APIRouter()

def get_dummy_metrics(model_name: str) -> ModelMetrics:
    """Generate dummy metrics for demonstration"""
    return ModelMetrics(
        model_name=model_name,
        accuracy=0.92,
        precision=0.91,
        recall=0.93,
        f1_score=0.92,
        specificity=0.89,
        sensitivity=0.93,
        auc_roc=0.95,
        mcc=0.84,
        confusion_matrix=[[85, 5], [3, 82]],
        training_accuracy=0.94,
        validation_accuracy=0.92,
        test_accuracy=0.92,
        dataset_info={
            "source": "Public Medical Dataset",
            "samples": 1000,
            "split_ratio": "70/15/15",
            "class_distribution": "Balanced",
            "preprocessing": ["Normalization", "Feature Engineering"]
        }
    )

@router.get("/{disease}", response_model=ModelMetrics)
async def get_disease_metrics(disease: str):
    """Get performance metrics for a specific disease model"""
    disease_models = {
        "pneumonia": "Pneumonia Detection CNN",
        "malaria": "Malaria Detection CNN",
        "breast-cancer": "Breast Cancer Random Forest",
        "diabetes": "Diabetes Prediction XGBoost",
        "alzheimer": "Alzheimer's Detection CNN",
        "liver-disease": "Liver Disease Random Forest",
        "kidney-disease": "Kidney Disease XGBoost",
        "heart-disease": "Heart Disease Random Forest"
    }
    
    if disease not in disease_models:
        raise HTTPException(status_code=404, detail=f"Disease model '{disease}' not found")
    
    return get_dummy_metrics(disease_models[disease])

@router.get("/all", response_model=AllMetricsResponse)
async def get_all_metrics():
    """Get performance metrics for all disease models"""
    diseases = [
        "pneumonia", "malaria", "breast-cancer", "diabetes",
        "alzheimer", "liver-disease", "kidney-disease", "heart-disease"
    ]
    
    metrics = {}
    for disease in diseases:
        model_name = f"{disease.replace('-', ' ').title()} Model"
        metrics[disease] = get_dummy_metrics(model_name)
    
    # Generate comparison chart data
    comparison_data = {
        "accuracy_comparison": {
            "labels": [d.replace('-', ' ').title() for d in diseases],
            "datasets": [{
                "label": "Accuracy",
                "data": [0.92, 0.89, 0.94, 0.91, 0.88, 0.90, 0.93, 0.92]
            }]
        },
        "auc_roc_comparison": {
            "labels": [d.replace('-', ' ').title() for d in diseases],
            "datasets": [{
                "label": "AUC-ROC",
                "data": [0.95, 0.92, 0.96, 0.94, 0.91, 0.93, 0.95, 0.94]
            }]
        }
    }
    
    return AllMetricsResponse(
        metrics=metrics,
        comparison_chart_data=comparison_data
    )
