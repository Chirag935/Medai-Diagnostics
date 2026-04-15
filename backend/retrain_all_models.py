"""
Retrain ALL models with proper validation and class balancing
Ensures accurate predictions for both positive and negative cases
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, confusion_matrix, classification_report
)
import joblib
import json
import os
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

class ModelRetrainer:
    def __init__(self):
        self.models_dir = "models"
        os.makedirs(self.models_dir, exist_ok=True)
        
    def train_diabetes_model(self):
        """Retrain diabetes model with proper class balancing"""
        print("\n" + "="*60)
        print("RETRAINING: Diabetes Model")
        print("="*60)
        
        # Load data
        df = pd.read_csv("data/pima_diabetes.csv")
        
        # Handle zero values
        zero_cols = ['glucose', 'blood_pressure', 'skin_thickness', 'insulin', 'bmi']
        for col in zero_cols:
            df[col] = df[col].replace(0, np.nan)
            df[col] = df[col].fillna(df[col].median())
        
        X = df.drop('outcome', axis=1)
        y = df['outcome']
        
        print(f"Dataset: {len(df)} samples")
        print(f"  No Diabetes: {sum(y==0)} ({sum(y==0)/len(y)*100:.1f}%)")
        print(f"  Diabetes: {sum(y==1)} ({sum(y==1)/len(y)*100:.1f}%)")
        
        # Split with stratification
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # Train with class balancing
        model = RandomForestClassifier(
            n_estimators=200,
            max_depth=10,
            min_samples_split=5,
            min_samples_leaf=2,
            class_weight='balanced_subsample',  # Critical for imbalanced data
            random_state=42
        )
        
        model.fit(X_train_scaled, y_train)
        
        # Evaluate
        y_pred = model.predict(X_test_scaled)
        y_prob = model.predict_proba(X_test_scaled)
        
        print("\nPerformance Metrics:")
        print(f"  Accuracy: {accuracy_score(y_test, y_pred):.3f}")
        print(f"  Precision: {precision_score(y_test, y_pred):.3f}")
        print(f"  Recall: {recall_score(y_test, y_pred):.3f}")
        print(f"  F1-Score: {f1_score(y_test, y_pred):.3f}")
        print(f"  ROC-AUC: {roc_auc_score(y_test, y_prob[:, 1]):.3f}")
        
        print("\nConfusion Matrix:")
        cm = confusion_matrix(y_test, y_pred)
        print(f"  TN={cm[0,0]}, FP={cm[0,1]}")
        print(f"  FN={cm[1,0]}, TP={cm[1,1]}")
        
        # Save model
        joblib.dump(model, f"{self.models_dir}/diabetes_model.pkl")
        joblib.dump(scaler, f"{self.models_dir}/diabetes_scaler.pkl")
        
        # Save metadata
        metadata = {
            "accuracy": float(accuracy_score(y_test, y_pred)),
            "precision": float(precision_score(y_test, y_pred)),
            "recall": float(recall_score(y_test, y_pred)),
            "f1_score": float(f1_score(y_test, y_pred)),
            "roc_auc": float(roc_auc_score(y_test, y_prob[:, 1])),
            "confusion_matrix": cm.tolist(),
            "training_date": datetime.now().isoformat(),
            "model_type": "RandomForest",
            "class_weight": "balanced_subsample"
        }
        
        with open(f"{self.models_dir}/diabetes_metadata.json", "w") as f:
            json.dump(metadata, f, indent=2)
        
        print("✓ Diabetes model retrained successfully")
        return True
    
    def train_heart_disease_model(self):
        """Retrain heart disease model"""
        print("\n" + "="*60)
        print("RETRAINING: Heart Disease Model")
        print("="*60)
        
        df = pd.read_csv("data/heart_disease_cleveland.csv")
        
        X = df.drop('target', axis=1)
        y = df['target']
        
        print(f"Dataset: {len(df)} samples")
        print(f"  No Disease: {sum(y==0)} ({sum(y==0)/len(y)*100:.1f}%)")
        print(f"  Disease: {sum(y==1)} ({sum(y==1)/len(y)*100:.1f}%)")
        
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        model = RandomForestClassifier(
            n_estimators=150,
            max_depth=8,
            class_weight='balanced',
            random_state=42
        )
        
        model.fit(X_train_scaled, y_train)
        
        y_pred = model.predict(X_test_scaled)
        y_prob = model.predict_proba(X_test_scaled)
        
        print(f"\nAccuracy: {accuracy_score(y_test, y_pred):.3f}")
        print(f"Precision: {precision_score(y_test, y_pred):.3f}")
        print(f"Recall: {recall_score(y_test, y_pred):.3f}")
        print(f"ROC-AUC: {roc_auc_score(y_test, y_prob[:, 1]):.3f}")
        
        cm = confusion_matrix(y_test, y_pred)
        print(f"Confusion Matrix: TN={cm[0,0]}, FP={cm[0,1]}, FN={cm[1,0]}, TP={cm[1,1]}")
        
        joblib.dump(model, f"{self.models_dir}/heart_disease_model.pkl")
        joblib.dump(scaler, f"{self.models_dir}/heart_disease_scaler.pkl")
        
        metadata = {
            "accuracy": float(accuracy_score(y_test, y_pred)),
            "precision": float(precision_score(y_test, y_pred)),
            "recall": float(recall_score(y_test, y_pred)),
            "roc_auc": float(roc_auc_score(y_test, y_prob[:, 1])),
            "confusion_matrix": cm.tolist(),
            "training_date": datetime.now().isoformat(),
            "model_type": "RandomForest"
        }
        
        with open(f"{self.models_dir}/heart_disease_metadata.json", "w") as f:
            json.dump(metadata, f, indent=2)
        
        print("✓ Heart disease model retrained successfully")
        return True
    
    def train_liver_disease_model(self):
        """Retrain liver disease model"""
        print("\n" + "="*60)
        print("RETRAINING: Liver Disease Model")
        print("="*60)
        
        df = pd.read_csv("data/liver_disease_indian.csv")
        
        # Column is named 'Dataset': 1 = disease, 0 = no disease (already correct)
        df['target'] = df['Dataset']
        
        X = df.drop(['Dataset', 'target'], axis=1)
        y = df['target']
        
        print(f"Dataset: {len(df)} samples")
        print(f"  No Disease: {sum(y==0)} ({sum(y==0)/len(y)*100:.1f}%)")
        print(f"  Disease: {sum(y==1)} ({sum(y==1)/len(y)*100:.1f}%)")
        
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        model = RandomForestClassifier(
            n_estimators=150,
            max_depth=10,
            class_weight='balanced',
            random_state=42
        )
        
        model.fit(X_train_scaled, y_train)
        
        y_pred = model.predict(X_test_scaled)
        y_prob = model.predict_proba(X_test_scaled)
        
        print(f"\nAccuracy: {accuracy_score(y_test, y_pred):.3f}")
        print(f"Precision: {precision_score(y_test, y_pred):.3f}")
        print(f"Recall: {recall_score(y_test, y_pred):.3f}")
        
        cm = confusion_matrix(y_test, y_pred)
        print(f"Confusion Matrix: TN={cm[0,0]}, FP={cm[0,1]}, FN={cm[1,0]}, TP={cm[1,1]}")
        
        joblib.dump(model, f"{self.models_dir}/liver_disease_model.pkl")
        joblib.dump(scaler, f"{self.models_dir}/liver_disease_scaler.pkl")
        
        metadata = {
            "accuracy": float(accuracy_score(y_test, y_pred)),
            "precision": float(precision_score(y_test, y_pred)),
            "recall": float(recall_score(y_test, y_pred)),
            "confusion_matrix": cm.tolist(),
            "training_date": datetime.now().isoformat()
        }
        
        with open(f"{self.models_dir}/liver_disease_metadata.json", "w") as f:
            json.dump(metadata, f, indent=2)
        
        print("✓ Liver disease model retrained successfully")
        return True
    
    def train_kidney_disease_model(self):
        """Retrain kidney disease model"""
        print("\n" + "="*60)
        print("RETRAINING: Kidney Disease Model")
        print("="*60)
        
        df = pd.read_csv("data/chronic_kidney_disease.csv")
        
        # Target column is 'classification' with values 0/1
        y = df['classification']
        
        # Select only numeric columns for features (exclude target)
        X = df.select_dtypes(include=[np.number]).drop('classification', axis=1, errors='ignore')
        
        # Handle missing values
        X = X.fillna(X.median())
        
        # If still no columns, use all non-target columns
        if X.shape[1] == 0:
            X = df.drop('classification', axis=1)
            # Convert all to numeric, coercing errors
            X = X.apply(pd.to_numeric, errors='coerce')
            X = X.fillna(X.median())
        
        print(f"Dataset: {len(df)} samples")
        print(f"  No CKD: {sum(y==0)} ({sum(y==0)/len(y)*100:.1f}%)")
        print(f"  CKD: {sum(y==1)} ({sum(y==1)/len(y)*100:.1f}%)")
        
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        model = RandomForestClassifier(
            n_estimators=150,
            max_depth=10,
            class_weight='balanced',
            random_state=42
        )
        
        model.fit(X_train_scaled, y_train)
        
        y_pred = model.predict(X_test_scaled)
        
        print(f"\nAccuracy: {accuracy_score(y_test, y_pred):.3f}")
        print(f"Precision: {precision_score(y_test, y_pred):.3f}")
        print(f"Recall: {recall_score(y_test, y_pred):.3f}")
        
        cm = confusion_matrix(y_test, y_pred)
        print(f"Confusion Matrix: TN={cm[0,0]}, FP={cm[0,1]}, FN={cm[1,0]}, TP={cm[1,1]}")
        
        joblib.dump(model, f"{self.models_dir}/kidney_disease_model.pkl")
        joblib.dump(scaler, f"{self.models_dir}/kidney_disease_scaler.pkl")
        
        metadata = {
            "accuracy": float(accuracy_score(y_test, y_pred)),
            "precision": float(precision_score(y_test, y_pred)),
            "recall": float(recall_score(y_test, y_pred)),
            "confusion_matrix": cm.tolist(),
            "training_date": datetime.now().isoformat()
        }
        
        with open(f"{self.models_dir}/kidney_disease_metadata.json", "w") as f:
            json.dump(metadata, f, indent=2)
        
        print("✓ Kidney disease model retrained successfully")
        return True
    
    def train_breast_cancer_model(self):
        """Retrain breast cancer model"""
        print("\n" + "="*60)
        print("RETRAINING: Breast Cancer Model")
        print("="*60)
        
        from sklearn.datasets import load_breast_cancer
        data = load_breast_cancer()
        
        X = pd.DataFrame(data.data, columns=data.feature_names)
        y = data.target  # 0 = malignant, 1 = benign
        
        print(f"Dataset: {len(y)} samples")
        print(f"  Malignant: {sum(y==0)} ({sum(y==0)/len(y)*100:.1f}%)")
        print(f"  Benign: {sum(y==1)} ({sum(y==1)/len(y)*100:.1f}%)")
        
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        model = RandomForestClassifier(
            n_estimators=200,
            max_depth=10,
            class_weight='balanced',
            random_state=42
        )
        
        model.fit(X_train_scaled, y_train)
        
        y_pred = model.predict(X_test_scaled)
        y_prob = model.predict_proba(X_test_scaled)
        
        print(f"\nAccuracy: {accuracy_score(y_test, y_pred):.3f}")
        print(f"Precision: {precision_score(y_test, y_pred):.3f}")
        print(f"Recall: {recall_score(y_test, y_pred):.3f}")
        print(f"ROC-AUC: {roc_auc_score(y_test, y_prob[:, 1]):.3f}")
        
        cm = confusion_matrix(y_test, y_pred)
        print(f"Confusion Matrix: TN={cm[0,0]}, FP={cm[0,1]}, FN={cm[1,0]}, TP={cm[1,1]}")
        
        joblib.dump(model, f"{self.models_dir}/breast_cancer_model.pkl")
        joblib.dump(scaler, f"{self.models_dir}/breast_cancer_scaler.pkl")
        
        metadata = {
            "accuracy": float(accuracy_score(y_test, y_pred)),
            "precision": float(precision_score(y_test, y_pred)),
            "recall": float(recall_score(y_test, y_pred)),
            "roc_auc": float(roc_auc_score(y_test, y_prob[:, 1])),
            "confusion_matrix": cm.tolist(),
            "training_date": datetime.now().isoformat()
        }
        
        with open(f"{self.models_dir}/breast_cancer_metadata.json", "w") as f:
            json.dump(metadata, f, indent=2)
        
        print("✓ Breast cancer model retrained successfully")
        return True
    
    def train_alzheimer_model(self):
        """Retrain Alzheimer's model"""
        print("\n" + "="*60)
        print("RETRAINING: Alzheimer's Model")
        print("="*60)
        
        df = pd.read_csv("data/alzheimer_dataset.csv")
        
        X = df.drop('target', axis=1)
        y = df['target']
        
        print(f"Dataset: {len(df)} samples")
        print(f"  No Alzheimer: {sum(y==0)} ({sum(y==0)/len(y)*100:.1f}%)")
        print(f"  Alzheimer: {sum(y==1)} ({sum(y==1)/len(y)*100:.1f}%)")
        
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        model = RandomForestClassifier(
            n_estimators=150,
            max_depth=8,
            class_weight='balanced',
            random_state=42
        )
        
        model.fit(X_train_scaled, y_train)
        
        y_pred = model.predict(X_test_scaled)
        
        print(f"\nAccuracy: {accuracy_score(y_test, y_pred):.3f}")
        print(f"Precision: {precision_score(y_test, y_pred):.3f}")
        print(f"Recall: {recall_score(y_test, y_pred):.3f}")
        
        cm = confusion_matrix(y_test, y_pred)
        print(f"Confusion Matrix: TN={cm[0,0]}, FP={cm[0,1]}, FN={cm[1,0]}, TP={cm[1,1]}")
        
        joblib.dump(model, f"{self.models_dir}/alzheimer_model.pkl")
        joblib.dump(scaler, f"{self.models_dir}/alzheimer_scaler.pkl")
        
        metadata = {
            "accuracy": float(accuracy_score(y_test, y_pred)),
            "precision": float(precision_score(y_test, y_pred)),
            "recall": float(recall_score(y_test, y_pred)),
            "confusion_matrix": cm.tolist(),
            "training_date": datetime.now().isoformat()
        }
        
        with open(f"{self.models_dir}/alzheimer_metadata.json", "w") as f:
            json.dump(metadata, f, indent=2)
        
        print("✓ Alzheimer's model retrained successfully")
        return True
    
    def retrain_all(self):
        """Retrain all models"""
        print("\n" + "="*60)
        print("STARTING COMPLETE MODEL RETRAINING")
        print("="*60)
        print("\nThis will retrain all 6 clinical models with:")
        print("  • Proper class balancing")
        print("  • Stratified train/test split")
        print("  • Performance validation")
        print("  • Confusion matrix reporting")
        print()
        
        results = {
            "diabetes": self.train_diabetes_model(),
            "heart_disease": self.train_heart_disease_model(),
            "liver_disease": self.train_liver_disease_model(),
            "kidney_disease": self.train_kidney_disease_model(),
            "breast_cancer": self.train_breast_cancer_model(),
            "alzheimer": self.train_alzheimer_model()
        }
        
        print("\n" + "="*60)
        print("RETRAINING COMPLETE")
        print("="*60)
        print("\nModel Status:")
        for model, success in results.items():
            status = "✓ SUCCESS" if success else "✗ FAILED"
            print(f"  {model}: {status}")
        
        print("\n" + "="*60)
        print("IMPORTANT: Restart the backend server to load new models!")
        print("="*60)
        print("\nCommand: cd backend && python main.py")
        print()

if __name__ == "__main__":
    retrainer = ModelRetrainer()
    retrainer.retrain_all()
