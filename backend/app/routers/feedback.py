"""
MLOps Feedback & Continuous Learning Router
Implements a feedback loop where users can verify predictions,
storing results in SQLite for model performance tracking and retraining.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import sqlite3
import os
import json
from datetime import datetime, timedelta
from typing import Optional

router = APIRouter()

MODELS_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "models")
DB_PATH = os.path.join(MODELS_DIR, "mlops_feedback.db")


def init_db():
    """Initialize the SQLite database for feedback storage."""
    os.makedirs(MODELS_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            module TEXT NOT NULL,
            prediction TEXT NOT NULL,
            confidence REAL NOT NULL,
            user_feedback TEXT DEFAULT NULL,
            is_correct INTEGER DEFAULT NULL,
            timestamp TEXT NOT NULL,
            features TEXT DEFAULT NULL
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS model_versions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            module TEXT NOT NULL,
            version TEXT NOT NULL,
            accuracy REAL NOT NULL,
            samples_trained INTEGER NOT NULL,
            timestamp TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


# Initialize DB on module load
init_db()


class PredictionLog(BaseModel):
    module: str  # "symptoms" or "skin"
    prediction: str
    confidence: float
    features: Optional[str] = None


class FeedbackSubmission(BaseModel):
    prediction_id: int
    is_correct: bool
    user_feedback: str = ""


@router.post("/log")
async def log_prediction(log: PredictionLog):
    """Log a prediction for future feedback collection."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO predictions (module, prediction, confidence, timestamp, features) VALUES (?, ?, ?, ?, ?)",
            (log.module, log.prediction, log.confidence, datetime.now().isoformat(), log.features)
        )
        prediction_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return {"prediction_id": prediction_id, "status": "logged"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/submit")
async def submit_feedback(feedback: FeedbackSubmission):
    """Submit user feedback on a prediction's accuracy."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE predictions SET is_correct = ?, user_feedback = ? WHERE id = ?",
            (1 if feedback.is_correct else 0, feedback.user_feedback, feedback.prediction_id)
        )
        if cursor.rowcount == 0:
            conn.close()
            raise HTTPException(status_code=404, detail="Prediction ID not found")
        conn.commit()
        conn.close()
        return {"status": "feedback_recorded", "prediction_id": feedback.prediction_id}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/dashboard")
async def get_mlops_dashboard():
    """Get comprehensive MLOps metrics for the dashboard."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Total predictions
        cursor.execute("SELECT COUNT(*) FROM predictions")
        total_predictions = cursor.fetchone()[0]

        # Predictions with feedback
        cursor.execute("SELECT COUNT(*) FROM predictions WHERE is_correct IS NOT NULL")
        total_feedback = cursor.fetchone()[0]

        # Accuracy from feedback
        cursor.execute("SELECT COUNT(*) FROM predictions WHERE is_correct = 1")
        correct_count = cursor.fetchone()[0]
        feedback_accuracy = (correct_count / total_feedback * 100) if total_feedback > 0 else 0

        # Per-module stats
        modules = {}
        for module in ["symptoms", "skin"]:
            cursor.execute("SELECT COUNT(*) FROM predictions WHERE module = ?", (module,))
            mod_total = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM predictions WHERE module = ? AND is_correct IS NOT NULL", (module,))
            mod_feedback = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM predictions WHERE module = ? AND is_correct = 1", (module,))
            mod_correct = cursor.fetchone()[0]

            cursor.execute("SELECT AVG(confidence) FROM predictions WHERE module = ?", (module,))
            avg_conf = cursor.fetchone()[0] or 0

            modules[module] = {
                "total_predictions": mod_total,
                "total_feedback": mod_feedback,
                "correct": mod_correct,
                "accuracy": round((mod_correct / mod_feedback * 100) if mod_feedback > 0 else 0, 1),
                "avg_confidence": round(avg_conf * 100, 1),
            }

        # Time-series data (predictions per day, last 7 days)
        daily_stats = []
        for i in range(6, -1, -1):
            day = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
            cursor.execute(
                "SELECT COUNT(*) FROM predictions WHERE timestamp LIKE ?",
                (f"{day}%",)
            )
            count = cursor.fetchone()[0]
            cursor.execute(
                "SELECT COUNT(*) FROM predictions WHERE timestamp LIKE ? AND is_correct = 1",
                (f"{day}%",)
            )
            correct = cursor.fetchone()[0]
            cursor.execute(
                "SELECT COUNT(*) FROM predictions WHERE timestamp LIKE ? AND is_correct IS NOT NULL",
                (f"{day}%",)
            )
            reviewed = cursor.fetchone()[0]
            daily_stats.append({
                "date": day,
                "predictions": count,
                "correct": correct,
                "reviewed": reviewed,
            })

        # Recent predictions
        cursor.execute(
            "SELECT id, module, prediction, confidence, is_correct, user_feedback, timestamp FROM predictions ORDER BY id DESC LIMIT 10"
        )
        recent = []
        for row in cursor.fetchall():
            recent.append({
                "id": row[0],
                "module": row[1],
                "prediction": row[2],
                "confidence": row[3],
                "is_correct": row[4],
                "user_feedback": row[5],
                "timestamp": row[6],
            })

        # Model version history
        cursor.execute("SELECT * FROM model_versions ORDER BY id DESC LIMIT 5")
        versions = []
        for row in cursor.fetchall():
            versions.append({
                "id": row[0],
                "module": row[1],
                "version": row[2],
                "accuracy": row[3],
                "samples_trained": row[4],
                "timestamp": row[5],
            })

        conn.close()

        return {
            "total_predictions": total_predictions,
            "total_feedback": total_feedback,
            "feedback_accuracy": round(feedback_accuracy, 1),
            "modules": modules,
            "daily_stats": daily_stats,
            "recent_predictions": recent,
            "model_versions": versions,
            "data_drift_status": "stable" if feedback_accuracy > 70 or total_feedback == 0 else "warning",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
