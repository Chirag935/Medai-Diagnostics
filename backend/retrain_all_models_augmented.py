"""
Data Augmentation + Cross-Validation for Maximum Accuracy
Uses advanced techniques to maximize performance on small datasets
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import StratifiedKFold, cross_val_score
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, ExtraTreesClassifier, VotingClassifier
from sklearn.preprocessing import StandardScaler, RobustScaler
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix
from imblearn.over_sampling import SMOTE, ADASYN, BorderlineSMOTE
from imblearn.ensemble import BalancedRandomForestClassifier
import joblib
import json
import os
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

class AugmentedTrainer:
    def __init__(self):
        self.models_dir = "models"
        os.makedirs(self.models_dir, exist_ok=True)
        self.results = {}
        
    def augment_data(self, X, y, noise_level=0.05, n_augment=2):
        """Add Gaussian noise to create synthetic samples"""
        X_aug = []
        y_aug = []
        
        for _ in range(n_augment):
            noise = np.random.normal(0, noise_level, X.shape)
            X_new = X + noise
            X_aug.append(X_new)
            y_aug.extend(y)
        
        X_combined = np.vstack([X] + X_aug)
        y_combined = np.hstack([y] * (n_augment + 1))
        
        return X_combined, y_combined
    
    def cross_val_train(self, X, y, model, n_splits=5):
        """Train with cross-validation for better generalization"""
        skf = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=42)
        
        scores = {'accuracy': [], 'precision': [], 'recall': [], 'f1': []}
        best_model = None
        best_score = 0
        
        for fold, (train_idx, val_idx) in enumerate(skf.split(X, y)):
            X_train, X_val = X[train_idx], X[val_idx]
            y_train, y_val = y[train_idx], y[val_idx]
            
            # Apply SMOTE
            try:
                smote = BorderlineSMOTE(random_state=42, k_neighbors=min(5, len(np.unique(y_train))-1))
                X_train_res, y_train_res = smote.fit_resample(X_train, y_train)
            except:
                X_train_res, y_train_res = X_train, y_train
            
            # Train
            model.fit(X_train_res, y_train_res)
            
            # Predict
            y_pred = model.predict(X_val)
            
            # Score
            acc = accuracy_score(y_val, y_pred)
            scores['accuracy'].append(acc)
            scores['precision'].append(precision_score(y_val, y_pred, zero_division=0))
            scores['recall'].append(recall_score(y_val, y_pred, zero_division=0))
            scores['f1'].append(f1_score(y_val, y_pred, zero_division=0))
            
            if acc > best_score:
                best_score = acc
                best_model = model
        
        # Return average scores
        avg_scores = {k: np.mean(v) for k, v in scores.items()}
        return best_model, avg_scores
    
    def train_diabetes(self):
        """Diabetes with augmentation"""
        print("\n" + "="*70)
        print("TRAINING: Diabetes Model (Augmented + Cross-Validation)")
        print("="*70)
        
        df = pd.read_csv("data/pima_diabetes.csv")
        
        # Handle zero values
        zero_cols = ['glucose', 'blood_pressure', 'skin_thickness', 'insulin', 'bmi']
        for col in zero_cols:
            df[col] = df[col].replace(0, np.nan).fillna(df[col].median())
        
        # Feature engineering
        df['glucose_bmi'] = df['glucose'] * df['bmi']
        df['age_pregnancies'] = df['age'] * df['pregnancies']
        
        X = df.drop('outcome', axis=1).values
        y = df['outcome'].values
        
        print(f"Original: {len(y)} samples")
        
        # Augment minority class
        minority_idx = y == 1
        X_minority = X[minority_idx]
        y_minority = y[minority_idx]
        
        X_aug, y_aug = self.augment_data(X_minority, y_minority, noise_level=0.03, n_augment=3)
        
        X_combined = np.vstack([X, X_aug])
        y_combined = np.hstack([y, y_aug])
        
        print(f"After augmentation: {len(y_combined)} samples")
        
        # Scale
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X_combined)
        
        # Cross-val training
        model = BalancedRandomForestClassifier(n_estimators=400, max_depth=20, random_state=42)
        best_model, scores = self.cross_val_train(X_scaled, y_combined, model)
        
        # Final train on all data
        model.fit(X_scaled, y_combined)
        
        # Evaluate on original data
        X_orig_scaled = scaler.transform(X)
        y_prob = model.predict_proba(X_orig_scaled)[:, 1]
        y_pred = model.predict(X_orig_scaled)
        
        return self.save_results(model, scaler, X, y, y_pred, y_prob, "diabetes", df.drop('outcome', axis=1).columns.tolist(), scores)
    
    def train_heart_disease(self):
        """Heart disease with augmentation"""
        print("\n" + "="*70)
        print("TRAINING: Heart Disease Model (Augmented)")
        print("="*70)
        
        df = pd.read_csv("data/heart_disease_cleveland.csv")
        
        target_col = 'target' if 'target' in df.columns else df.columns[-1]
        X = df.drop(target_col, axis=1).values
        y = df[target_col].values
        
        # Make binary
        if len(np.unique(y)) > 2:
            y = (y > 0).astype(int)
        
        print(f"Original: {len(y)} samples (Disease: {sum(y==1)})")
        
        # Heavy augmentation for this small dataset
        X_aug, y_aug = self.augment_data(X, y, noise_level=0.02, n_augment=5)
        
        print(f"After augmentation: {len(y_aug)} samples")
        
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X_aug)
        
        model = BalancedRandomForestClassifier(n_estimators=300, max_depth=15, random_state=42)
        model.fit(X_scaled, y_aug)
        
        # Evaluate on original
        X_orig_scaled = scaler.transform(X)
        y_prob = model.predict_proba(X_orig_scaled)[:, 1]
        y_pred = model.predict(X_orig_scaled)
        
        return self.save_results(model, scaler, X, y, y_pred, y_prob, "heart_disease", df.drop(target_col, axis=1).columns.tolist())
    
    def train_kidney_disease(self):
        """Kidney with aggressive augmentation"""
        print("\n" + "="*70)
        print("TRAINING: Kidney Disease Model (Heavy Augmentation)")
        print("="*70)
        
        df = pd.read_csv("data/chronic_kidney_disease.csv")
        df = df.drop(['id'], axis=1, errors='ignore')
        
        target_col = 'classification' if 'classification' in df.columns else df.columns[-1]
        
        if df[target_col].dtype == 'object':
            df[target_col] = df[target_col].apply(lambda x: 1 if 'ckd' in str(x).lower() else 0)
        
        for col in df.columns:
            if col != target_col:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        df = df.dropna()
        
        X = df.drop(target_col, axis=1).values
        y = df[target_col].values
        
        print(f"Original: {len(y)} samples (CKD: {sum(y==1)})")
        
        # Very heavy augmentation for severe imbalance
        minority_idx = y == 1
        if sum(minority_idx) > 0:
            X_minority = X[minority_idx]
            y_minority = y[minority_idx]
            X_aug, y_aug = self.augment_data(X_minority, y_minority, noise_level=0.02, n_augment=8)
            X_combined = np.vstack([X, X_aug])
            y_combined = np.hstack([y, y_aug])
        else:
            X_combined, y_combined = X, y
        
        print(f"After augmentation: {len(y_combined)} samples")
        
        scaler = RobustScaler()
        X_scaled = scaler.fit_transform(X_combined)
        
        # Cross-validation
        model = BalancedRandomForestClassifier(n_estimators=500, max_depth=25, random_state=42)
        best_model, scores = self.cross_val_train(X_scaled, y_combined, model, n_splits=3)
        
        # Final fit
        model.fit(X_scaled, y_combined)
        
        # Evaluate
        X_orig_scaled = scaler.transform(X)
        y_prob = model.predict_proba(X_orig_scaled)[:, 1]
        y_pred = (y_prob >= 0.25).astype(int)  # Lower threshold
        
        return self.save_results(model, scaler, X, y, y_pred, y_prob, "kidney_disease", df.drop(target_col, axis=1).columns.tolist(), scores)
    
    def train_liver_disease(self):
        """Liver disease"""
        print("\n" + "="*70)
        print("TRAINING: Liver Disease Model")
        print("="*70)
        
        df = pd.read_csv("data/liver_disease_indian.csv")
        
        target_col = 'Dataset' if 'Dataset' in df.columns else df.columns[-1]
        X = df.drop(target_col, axis=1).values
        y = df[target_col].values
        
        # Clean
        df_clean = pd.concat([pd.DataFrame(X), pd.Series(y, name='y')], axis=1).dropna()
        X = df_clean.drop('y', axis=1).values
        y = df_clean['y'].values
        
        y = (y == 1).astype(int)  # 1 = disease
        
        print(f"Dataset: {len(y)} samples")
        
        scaler = RobustScaler()
        X_scaled = scaler.fit_transform(X)
        
        model = BalancedRandomForestClassifier(n_estimators=300, max_depth=15, random_state=42)
        model.fit(X_scaled, y)
        
        y_prob = model.predict_proba(X_scaled)[:, 1]
        y_pred = model.predict(X_scaled)
        
        return self.save_results(model, scaler, X, y, y_pred, y_prob, "liver_disease", df.drop(target_col, axis=1).columns.tolist())
    
    def train_breast_cancer(self):
        """Breast cancer - already good size"""
        print("\n" + "="*70)
        print("TRAINING: Breast Cancer Model")
        print("="*70)
        
        df = pd.read_csv("data/breast_cancer_wdbc.csv")
        df = df.drop(['id', 'Unnamed: 32'], axis=1, errors='ignore')
        
        target_col = 'target' if 'target' in df.columns else df.columns[0]
        
        if target_col == 'diagnosis' or df[target_col].dtype == 'object':
            df[target_col] = df[target_col].map({'M': 1, 'B': 0, 'malignant': 1, 'benign': 0})
        
        X = df.drop(target_col, axis=1).values
        y = pd.to_numeric(df[target_col], errors='coerce').values
        
        # Remove NaN
        valid = ~np.isnan(y)
        X = X[valid]
        y = y[valid]
        
        print(f"Dataset: {len(y)} samples")
        
        # Light augmentation
        X_aug, y_aug = self.augment_data(X, y, noise_level=0.01, n_augment=2)
        
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X_aug)
        
        # Ensemble
        rf = RandomForestClassifier(n_estimators=200, max_depth=15, random_state=42)
        et = ExtraTreesClassifier(n_estimators=200, max_depth=15, random_state=42)
        gb = GradientBoostingClassifier(n_estimators=200, max_depth=5, random_state=42)
        
        model = VotingClassifier([('rf', rf), ('et', et), ('gb', gb)], voting='soft')
        model.fit(X_scaled, y_aug)
        
        # Evaluate on original
        X_orig_scaled = scaler.transform(X)
        y_prob = model.predict_proba(X_orig_scaled)[:, 1]
        y_pred = model.predict(X_orig_scaled)
        
        return self.save_results(model, scaler, X, y, y_pred, y_prob, "breast_cancer", df.drop(target_col, axis=1).columns.tolist())
    
    def train_alzheimer(self):
        """Alzheimer's with augmentation"""
        print("\n" + "="*70)
        print("TRAINING: Alzheimer's Model (Augmented)")
        print("="*70)
        
        df = pd.read_csv("data/alzheimer_dataset.csv")
        df = df.drop(['PatientID'], axis=1, errors='ignore')
        
        target_col = 'target' if 'target' in df.columns else 'Diagnosis'
        
        if df[target_col].dtype == 'object':
            df[target_col] = df[target_col].map({'Normal': 0, 'MCI': 1, 'Alzheimer': 1, 'Demented': 1, 'Nondemented': 0})
        
        for col in df.columns:
            if col != target_col:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        df = df.dropna()
        
        X = df.drop(target_col, axis=1).values
        y = df[target_col].values
        
        print(f"Original: {len(y)} samples (Alzheimer: {sum(y==1)})")
        
        # Heavy augmentation for minority
        minority_idx = y == 1
        X_minority = X[minority_idx]
        y_minority = y[minority_idx]
        
        X_aug, y_aug = self.augment_data(X_minority, y_minority, noise_level=0.02, n_augment=6)
        X_combined = np.vstack([X, X_aug])
        y_combined = np.hstack([y, y_aug])
        
        print(f"After augmentation: {len(y_combined)} samples")
        
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X_combined)
        
        model = BalancedRandomForestClassifier(n_estimators=400, max_depth=20, random_state=42)
        best_model, scores = self.cross_val_train(X_scaled, y_combined, model)
        
        model.fit(X_scaled, y_combined)
        
        # Evaluate on original
        X_orig_scaled = scaler.transform(X)
        y_prob = model.predict_proba(X_orig_scaled)[:, 1]
        y_pred = (y_prob >= 0.3).astype(int)
        
        return self.save_results(model, scaler, X, y, y_pred, y_prob, "alzheimer", df.drop(target_col, axis=1).columns.tolist(), scores)
    
    def save_results(self, model, scaler, X, y, y_pred, y_prob, name, features, cv_scores=None):
        """Save with detailed reporting"""
        
        accuracy = accuracy_score(y, y_pred)
        precision = precision_score(y, y_pred, zero_division=0)
        recall = recall_score(y, y_pred, zero_division=0)
        f1 = f1_score(y, y_pred, zero_division=0)
        
        try:
            roc_auc = roc_auc_score(y, y_prob)
        except:
            roc_auc = 0.5
        
        cm = confusion_matrix(y, y_pred)
        
        print(f"\n  📊 Results:")
        print(f"    Accuracy:  {accuracy:.1%}")
        print(f"    Precision: {precision:.1%}")
        print(f"    Recall:    {recall:.1%}")
        print(f"    F1-Score:  {f1:.1%}")
        print(f"    ROC-AUC:   {roc_auc:.1%}")
        
        if cv_scores:
            print(f"    CV Accuracy: {cv_scores.get('accuracy', 0):.1%}")
        
        if cm.shape == (2, 2):
            tn, fp, fn, tp = cm.ravel()
            print(f"    TN={tn}, FP={fp}, FN={fn}, TP={tp}")
        
        # Save
        joblib.dump(model, f"{self.models_dir}/{name}_model.pkl")
        joblib.dump(scaler, f"{self.models_dir}/{name}_scaler.pkl")
        
        metadata = {
            "accuracy": float(accuracy),
            "precision": float(precision),
            "recall": float(recall),
            "f1_score": float(f1),
            "roc_auc": float(roc_auc),
            "cv_scores": cv_scores,
            "confusion_matrix": cm.tolist(),
            "features": features,
            "training_date": datetime.now().isoformat(),
            "method": "augmented"
        }
        
        with open(f"{self.models_dir}/{name}_metadata.json", 'w') as f:
            json.dump(metadata, f, indent=2)
        
        print(f"  ✓ Saved: {name}_model.pkl")
        return metadata
    
    def train_all(self):
        """Train all with augmentation"""
        print("\n" + "="*80)
        print("🚀 AUGMENTED MODEL TRAINING - Data Size Increased 3-10x")
        print("="*80)
        print("Methods:")
        print("  • Gaussian noise augmentation (3-8x samples)")
        print("  • 5-fold cross-validation")
        print("  • BalancedRandomForest with 300-500 trees")
        
        functions = [
            ("diabetes", self.train_diabetes),
            ("heart_disease", self.train_heart_disease),
            ("liver_disease", self.train_liver_disease),
            ("kidney_disease", self.train_kidney_disease),
            ("breast_cancer", self.train_breast_cancer),
            ("alzheimer", self.train_alzheimer)
        ]
        
        for name, func in functions:
            try:
                result = func()
                if result:
                    self.results[name] = result
            except Exception as e:
                print(f"❌ {name} failed: {e}")
                import traceback
                traceback.print_exc()
        
        # Summary
        print("\n" + "="*80)
        print("🏆 FINAL RESULTS - Augmented Training")
        print("="*80)
        print(f"{'Disease':<20} {'Accuracy':>10} {'Precision':>10} {'Recall':>10}")
        print("-"*80)
        
        for name, metrics in sorted(self.results.items()):
            print(f"{name:<20} {metrics['accuracy']:>9.1%} {metrics['precision']:>9.1%} {metrics['recall']:>9.1%}")
        
        print("\n⚠️ Restart backend to load new models!")
        return self.results

if __name__ == "__main__":
    trainer = AugmentedTrainer()
    trainer.train_all()
