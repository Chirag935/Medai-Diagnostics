#!/usr/bin/env python3
"""
Train Breast Cancer Prediction Model using Real Wisconsin Diagnostic Breast Cancer Dataset
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, confusion_matrix, classification_report
)
import joblib
import json
import os
from datetime import datetime

class BreastCancerModelTrainer:
    def __init__(self, data_path="data/breast_cancer_wdbc.csv"):
        self.data_path = data_path
        self.model = None
        self.scaler = None
        self.metrics = {}
        
    def load_and_preprocess_data(self):
        """Load and preprocess the Wisconsin Diagnostic Breast Cancer dataset"""
        print("Loading Wisconsin Diagnostic Breast Cancer Dataset...")
        
        if not os.path.exists(self.data_path):
            # Try to download from sklearn if file doesn't exist
            print("Dataset not found, downloading from sklearn...")
            from sklearn.datasets import load_breast_cancer
            
            data = load_breast_cancer()
            df = pd.DataFrame(data.data, columns=data.feature_names)
            df['target'] = data.target
            df['diagnosis'] = df['target'].map({0: 'benign', 1: 'malignant'})
            
            # Save for future use
            os.makedirs(os.path.dirname(self.data_path), exist_ok=True)
            df.to_csv(self.data_path, index=False)
        else:
            df = pd.read_csv(self.data_path)
        
        print(f"Dataset loaded: {len(df)} records")
        print(f"Features: {len([col for col in df.columns if col not in ['target', 'diagnosis']])}")
        
        # Check for missing values
        print(f"Missing values: {df.isnull().sum().sum()}")
        
        # Separate features and target
        feature_columns = [col for col in df.columns if col not in ['target', 'diagnosis']]
        X = df[feature_columns]
        y = df['target']
        
        print(f"Malignant cases: {y.sum()} ({y.sum()/len(y)*100:.1f}%)")
        print(f"Benign cases: {len(y)-y.sum()} ({(len(y)-y.sum())/len(y)*100:.1f}%)")
        
        return X, y
    
    def find_best_model(self, X, y):
        """Find the best model using cross-validation"""
        print("\nFinding the best model...")
        
        # Define models to test
        models = {
            'RandomForest': RandomForestClassifier(random_state=42, class_weight='balanced'),
            'GradientBoosting': GradientBoostingClassifier(random_state=42),
            'LogisticRegression': LogisticRegression(random_state=42, max_iter=1000, class_weight='balanced'),
            'SVM': SVC(random_state=42, probability=True, class_weight='balanced')
        }
        
        # Scale features for models that need it
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        results = {}
        
        for name, model in models.items():
            print(f"\nTesting {name}...")
            
            # Use cross-validation for more reliable evaluation
            if name in ['LogisticRegression', 'SVM']:
                cv_scores = cross_val_score(model, X_scaled, y, cv=5, scoring='accuracy')
            else:
                cv_scores = cross_val_score(model, X, y, cv=5, scoring='accuracy')
            
            results[name] = {
                'cv_mean': cv_scores.mean(),
                'cv_std': cv_scores.std(),
                'cv_scores': cv_scores.tolist()
            }
            
            print(f"  CV Accuracy: {cv_scores.mean():.4f} (+/- {cv_scores.std() * 2:.4f})")
        
        # Select best model
        best_model_name = max(results.keys(), key=lambda k: results[k]['cv_mean'])
        print(f"\nBest model: {best_model_name}")
        print(f"Best CV accuracy: {results[best_model_name]['cv_mean']:.4f}")
        
        return best_model_name, results
    
    def train_final_model(self, X, y, model_name):
        """Train the final model with hyperparameter tuning"""
        print(f"\nTraining final {model_name} model...")
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        # Scale features
        self.scaler = StandardScaler()
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Define hyperparameter grids
        param_grids = {
            'RandomForest': {
                'n_estimators': [100, 200, 300],
                'max_depth': [10, 15, 20, None],
                'min_samples_split': [2, 5, 10],
                'min_samples_leaf': [1, 2, 4]
            },
            'GradientBoosting': {
                'n_estimators': [100, 200],
                'learning_rate': [0.01, 0.1, 0.2],
                'max_depth': [3, 5, 7]
            },
            'LogisticRegression': {
                'C': [0.1, 1, 10, 100],
                'penalty': ['l2']
            },
            'SVM': {
                'C': [0.1, 1, 10],
                'kernel': ['rbf', 'linear'],
                'gamma': ['scale', 'auto']
            }
        }
        
        # Select model
        models = {
            'RandomForest': RandomForestClassifier(random_state=42, class_weight='balanced'),
            'GradientBoosting': GradientBoostingClassifier(random_state=42),
            'LogisticRegression': LogisticRegression(random_state=42, max_iter=1000, class_weight='balanced'),
            'SVM': SVC(random_state=42, probability=True, class_weight='balanced')
        }
        
        base_model = models[model_name]
        param_grid = param_grids[model_name]
        
        # Use appropriate data for training
        if model_name in ['LogisticRegression', 'SVM']:
            X_train_data = X_train_scaled
            X_test_data = X_test_scaled
        else:
            X_train_data = X_train
            X_test_data = X_test_scaled  # Still scale for consistency
        
        # Grid search with cross-validation
        grid_search = GridSearchCV(
            base_model, param_grid, cv=5, scoring='accuracy', n_jobs=-1, verbose=1
        )
        
        grid_search.fit(X_train_data, y_train)
        
        # Best model
        self.model = grid_search.best_estimator_
        
        print(f"Best parameters: {grid_search.best_params_}")
        print(f"Best CV score: {grid_search.best_score_:.4f}")
        
        # Evaluate on test set
        y_pred = self.model.predict(X_test_data)
        y_pred_proba = self.model.predict_proba(X_test_data)[:, 1]
        
        # Calculate comprehensive metrics
        self.metrics = {
            'accuracy': accuracy_score(y_test, y_pred),
            'precision': precision_score(y_test, y_pred),
            'recall': recall_score(y_test, y_pred),
            'f1_score': f1_score(y_test, y_pred),
            'roc_auc': roc_auc_score(y_test, y_pred_proba),
            'confusion_matrix': confusion_matrix(y_test, y_pred).tolist(),
            'classification_report': classification_report(y_test, y_pred, output_dict=True),
            'best_params': grid_search.best_params_,
            'cv_score': grid_search.best_score_,
            'model_type': model_name,
            'training_samples': len(X_train),
            'test_samples': len(X_test),
            'feature_names': X.columns.tolist()
        }
        
        # Feature importance (for tree-based models)
        if hasattr(self.model, 'feature_importances_'):
            feature_importance = dict(zip(X.columns, self.model.feature_importances_))
            self.metrics['feature_importance'] = feature_importance
            
            # Show top 10 features
            top_features = sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)[:10]
            print("\nTop 10 Feature Importance:")
            for feature, importance in top_features:
                print(f"  {feature}: {importance:.4f}")
        
        # Print detailed metrics
        print(f"\nTest Set Performance:")
        print(f"  Accuracy: {self.metrics['accuracy']:.4f}")
        print(f"  Precision: {self.metrics['precision']:.4f}")
        print(f"  Recall: {self.metrics['recall']:.4f}")
        print(f"  F1-Score: {self.metrics['f1_score']:.4f}")
        print(f"  ROC-AUC: {self.metrics['roc_auc']:.4f}")
        
        print(f"\nConfusion Matrix:")
        cm = self.metrics['confusion_matrix']
        print(f"  True Negative (Benign): {cm[0][0]}")
        print(f"  False Positive: {cm[0][1]}")
        print(f"  False Negative: {cm[1][0]}")
        print(f"  True Positive (Malignant): {cm[1][1]}")
        
        return self.metrics
    
    def save_model(self):
        """Save the trained model and metadata"""
        print("\nSaving model and metadata...")
        
        # Create models directory
        os.makedirs('models', exist_ok=True)
        
        # Save model
        joblib.dump(self.model, 'models/breast_cancer_model.pkl')
        
        # Save scaler
        joblib.dump(self.scaler, 'models/breast_cancer_scaler.pkl')
        
        # Save metadata with timestamp
        metadata = {
            **self.metrics,
            'training_date': datetime.now().isoformat(),
            'dataset': 'Wisconsin Diagnostic Breast Cancer (WDBC)',
            'total_samples': self.metrics['training_samples'] + self.metrics['test_samples'],
            'target_classes': ['Benign', 'Malignant'],
            'model_purpose': 'Breast cancer malignancy prediction based on tumor characteristics'
        }
        
        with open('models/breast_cancer_metadata.json', 'w') as f:
            json.dump(metadata, f, indent=2)
        
        print("Model saved successfully!")
        print(f"  Model: models/breast_cancer_model.pkl")
        print(f"  Scaler: models/breast_cancer_scaler.pkl")
        print(f"  Metadata: models/breast_cancer_metadata.json")
        
        return metadata

def main():
    """Main training pipeline"""
    print("=" * 80)
    print("BREAST CANCER PREDICTION MODEL TRAINING")
    print("Using Real Wisconsin Diagnostic Breast Cancer Dataset")
    print("=" * 80)
    
    try:
        # Initialize trainer
        trainer = BreastCancerModelTrainer()
        
        # Load and preprocess data
        X, y = trainer.load_and_preprocess_data()
        
        # Find best model
        best_model_name, cv_results = trainer.find_best_model(X, y)
        
        # Train final model
        metrics = trainer.train_final_model(X, y, best_model_name)
        
        # Save model
        metadata = trainer.save_model()
        
        print("\n" + "=" * 80)
        print("TRAINING COMPLETED SUCCESSFULLY!")
        print("=" * 80)
        print(f"Model: {best_model_name}")
        print(f"Test Accuracy: {metrics['accuracy']:.4f} ({metrics['accuracy']*100:.1f}%)")
        print(f"ROC-AUC: {metrics['roc_auc']:.4f}")
        print(f"F1-Score: {metrics['f1_score']:.4f}")
        print(f"Model saved and ready for deployment!")
        
        return True
        
    except Exception as e:
        print(f"\nTraining failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
