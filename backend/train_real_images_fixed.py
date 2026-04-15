"""
FIXED Training Script for Real Medical Images
Proper feature scaling and class balancing
"""

import os
import numpy as np
import cv2
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score, precision_score, recall_score
from sklearn.preprocessing import StandardScaler
import joblib
import json
from datetime import datetime
from tqdm import tqdm

PNEUMONIA_BASE = r"C:\Users\asus\Downloads\Pneumonia\chest_xray\chest_xray"
MALARIA_BASE = r"C:\Users\asus\Downloads\malaria\cell_images"

class FixedImageTrainer:
    def __init__(self):
        self.models_dir = "models"
        os.makedirs(self.models_dir, exist_ok=True)
        self.img_size = (224, 224)
        
    def extract_pneumonia_features(self, img):
        """Extract features from chest X-ray"""
        features = []
        
        # Normalize image to 0-1 range
        img = img.astype(np.float32) / 255.0
        
        # 1. Global statistics
        features.append(np.mean(img))
        features.append(np.std(img))
        features.append(np.percentile(img, 10))
        features.append(np.percentile(img, 90))
        
        # 2. Regional analysis
        h, w = img.shape
        upper = img[0:h//3, :]
        lower = img[2*h//3:, :]
        
        features.append(np.mean(upper))
        features.append(np.mean(lower))
        features.append(np.std(lower))
        
        # 3. Bright/dark ratios
        bright_ratio = np.sum(img > 0.7) / (h * w)
        dark_ratio = np.sum(img < 0.2) / (h * w)
        features.append(bright_ratio)
        features.append(dark_ratio)
        
        # 4. Texture
        img_uint8 = (img * 255).astype(np.uint8)
        laplacian = cv2.Laplacian(img_uint8, cv2.CV_64F)
        features.append(np.var(laplacian) / 10000)  # Scale down
        
        # 5. Edge density
        edges = cv2.Canny(img_uint8, 50, 150)
        features.append(np.sum(edges > 0) / (h * w))
        
        # 6. Histogram (8 bins)
        hist, _ = np.histogram(img.flatten(), bins=8, range=(0, 1))
        features.extend(hist / (h * w))
        
        return np.array(features, dtype=np.float32)
    
    def extract_malaria_features(self, img):
        """Extract features from blood cell image"""
        features = []
        
        # Normalize
        img = img.astype(np.float32) / 255.0
        
        # 1. RGB statistics
        for i in range(3):
            features.append(np.mean(img[:, :, i]))
            features.append(np.std(img[:, :, i]))
        
        # 2. Convert to HSV
        hsv = cv2.cvtColor((img * 255).astype(np.uint8), cv2.COLOR_RGB2HSV)
        hsv = hsv.astype(np.float32) / 255.0
        
        features.append(np.mean(hsv[:, :, 0]))  # Hue
        features.append(np.std(hsv[:, :, 0]))
        features.append(np.mean(hsv[:, :, 1]))  # Saturation
        
        # 3. Gray level analysis
        gray = cv2.cvtColor((img * 255).astype(np.uint8), cv2.COLOR_RGB2GRAY)
        
        # Dark spots (parasites)
        _, dark_mask = cv2.threshold(gray, 80, 255, cv2.THRESH_BINARY_INV)
        contours, _ = cv2.findContours(dark_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        features.append(len(contours) / 10)  # Scale
        features.append(np.sum(dark_mask) / (img.shape[0] * img.shape[1] * 255))
        
        # 4. Texture
        laplacian = cv2.Laplacian(gray, cv2.CV_64F)
        features.append(np.var(laplacian) / 10000)
        
        # 5. Red channel (blood cells)
        red = img[:, :, 0]
        features.append(np.mean(red))
        features.append(np.std(red))
        
        return np.array(features, dtype=np.float32)
    
    def load_pneumonia_data(self, max_samples=1000):
        """Load pneumonia X-rays with balanced classes"""
        print("\n" + "="*60)
        print("LOADING: Pneumonia Dataset (BALANCED)")
        print("="*60)
        
        X = []
        y = []
        
        # Load equal numbers from each class
        normal_path = os.path.join(PNEUMONIA_BASE, "train", "NORMAL")
        pneumonia_path = os.path.join(PNEUMONIA_BASE, "train", "PNEUMONIA")
        
        normal_files = [f for f in os.listdir(normal_path) if f.lower().endswith(('.jpeg', '.jpg'))][:max_samples//2]
        pneumonia_files = [f for f in os.listdir(pneumonia_path) if f.lower().endswith(('.jpeg', '.jpg'))][:max_samples//2]
        
        print(f"Loading {len(normal_files)} NORMAL...")
        for f in tqdm(normal_files):
            try:
                img = cv2.imread(os.path.join(normal_path, f), cv2.IMREAD_GRAYSCALE)
                if img is not None:
                    img = cv2.resize(img, self.img_size)
                    X.append(self.extract_pneumonia_features(img))
                    y.append(0)
            except:
                pass
        
        print(f"Loading {len(pneumonia_files)} PNEUMONIA...")
        for f in tqdm(pneumonia_files):
            try:
                img = cv2.imread(os.path.join(pneumonia_path, f), cv2.IMREAD_GRAYSCALE)
                if img is not None:
                    img = cv2.resize(img, self.img_size)
                    X.append(self.extract_pneumonia_features(img))
                    y.append(1)
            except:
                pass
        
        X = np.array(X)
        y = np.array(y)
        
        print(f"\nLoaded {len(X)} images:")
        print(f"  Normal: {sum(y==0)}")
        print(f"  Pneumonia: {sum(y==1)}")
        
        return X, y
    
    def load_malaria_data(self, max_samples=1000):
        """Load malaria cells with balanced classes"""
        print("\n" + "="*60)
        print("LOADING: Malaria Dataset (BALANCED)")
        print("="*60)
        
        X = []
        y = []
        
        uninfected_path = os.path.join(MALARIA_BASE, "Uninfected")
        parasitized_path = os.path.join(MALARIA_BASE, "Parasitized")
        
        uninfected_files = [f for f in os.listdir(uninfected_path) if f.endswith('.png')][:max_samples//2]
        parasitized_files = [f for f in os.listdir(parasitized_path) if f.endswith('.png')][:max_samples//2]
        
        print(f"Loading {len(uninfected_files)} Uninfected...")
        for f in tqdm(uninfected_files):
            try:
                img = cv2.imread(os.path.join(uninfected_path, f))
                if img is not None:
                    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                    img = cv2.resize(img, self.img_size)
                    X.append(self.extract_malaria_features(img))
                    y.append(0)
            except:
                pass
        
        print(f"Loading {len(parasitized_files)} Parasitized...")
        for f in tqdm(parasitized_files):
            try:
                img = cv2.imread(os.path.join(parasitized_path, f))
                if img is not None:
                    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                    img = cv2.resize(img, self.img_size)
                    X.append(self.extract_malaria_features(img))
                    y.append(1)
            except:
                pass
        
        X = np.array(X)
        y = np.array(y)
        
        print(f"\nLoaded {len(X)} images:")
        print(f"  Uninfected: {sum(y==0)}")
        print(f"  Parasitized: {sum(y==1)}")
        
        return X, y
    
    def train_pneumonia(self):
        """Train fixed pneumonia model"""
        print("\n" + "="*60)
        print("TRAINING: Pneumonia (FIXED)")
        print("="*60)
        
        X, y = self.load_pneumonia_data(max_samples=1000)
        
        # Scale features
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        # Split
        X_train, X_test, y_train, y_test = train_test_split(
            X_scaled, y, test_size=0.2, random_state=42, stratify=y
        )
        
        # Train with balanced class weights
        model = RandomForestClassifier(
            n_estimators=200,
            max_depth=10,
            min_samples_split=5,
            class_weight='balanced',
            random_state=42
        )
        
        model.fit(X_train, y_train)
        
        # Evaluate
        y_pred = model.predict(X_test)
        y_prob = model.predict_proba(X_test)
        
        print(f"\nAccuracy: {accuracy_score(y_test, y_pred):.4f}")
        print(f"Precision: {precision_score(y_test, y_pred):.4f}")
        print(f"Recall: {recall_score(y_test, y_pred):.4f}")
        
        cm = confusion_matrix(y_test, y_pred)
        print(f"\nConfusion Matrix:")
        print(f"  TN={cm[0,0]}, FP={cm[0,1]}")
        print(f"  FN={cm[1,0]}, TP={cm[1,1]}")
        
        # Test on specific samples
        print("\nSample Predictions:")
        for i in range(min(10, len(X_test))):
            actual = "Normal" if y_test[i] == 0 else "Pneumonia"
            pred = "Normal" if y_pred[i] == 0 else "Pneumonia"
            prob_normal = y_prob[i][0]
            prob_pneumonia = y_prob[i][1]
            print(f"  Actual: {actual:10s} | Pred: {pred:10s} | Normal={prob_normal:.3f}, Pneumonia={prob_pneumonia:.3f}")
        
        # Save
        joblib.dump(model, f"{self.models_dir}/pneumonia_real_fixed.pkl")
        joblib.dump(scaler, f"{self.models_dir}/pneumonia_scaler.pkl")
        
        metadata = {
            "accuracy": float(accuracy_score(y_test, y_pred)),
            "training_date": datetime.now().isoformat(),
            "samples": len(X),
            "scaler": True
        }
        with open(f"{self.models_dir}/pneumonia_fixed_metadata.json", "w") as f:
            json.dump(metadata, f, indent=2)
        
        print("\n✓ Pneumonia model saved!")
        return model, scaler
    
    def train_malaria(self):
        """Train fixed malaria model"""
        print("\n" + "="*60)
        print("TRAINING: Malaria (FIXED)")
        print("="*60)
        
        X, y = self.load_malaria_data(max_samples=1000)
        
        # Scale features
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        # Split
        X_train, X_test, y_train, y_test = train_test_split(
            X_scaled, y, test_size=0.2, random_state=42, stratify=y
        )
        
        # Train
        model = RandomForestClassifier(
            n_estimators=200,
            max_depth=12,
            class_weight='balanced',
            random_state=42
        )
        
        model.fit(X_train, y_train)
        
        # Evaluate
        y_pred = model.predict(X_test)
        y_prob = model.predict_proba(X_test)
        
        print(f"\nAccuracy: {accuracy_score(y_test, y_pred):.4f}")
        print(f"Precision: {precision_score(y_test, y_pred):.4f}")
        print(f"Recall: {recall_score(y_test, y_pred):.4f}")
        
        cm = confusion_matrix(y_test, y_pred)
        print(f"\nConfusion Matrix:")
        print(f"  TN={cm[0,0]}, FP={cm[0,1]}")
        print(f"  FN={cm[1,0]}, TP={cm[1,1]}")
        
        # Test samples
        print("\nSample Predictions:")
        for i in range(min(10, len(X_test))):
            actual = "Uninfected" if y_test[i] == 0 else "Parasitized"
            pred = "Uninfected" if y_pred[i] == 0 else "Parasitized"
            prob_uninfected = y_prob[i][0]
            prob_parasitized = y_prob[i][1]
            print(f"  Actual: {actual:12s} | Pred: {pred:12s} | Uninfected={prob_uninfected:.3f}, Parasitized={prob_parasitized:.3f}")
        
        # Save
        joblib.dump(model, f"{self.models_dir}/malaria_real_fixed.pkl")
        joblib.dump(scaler, f"{self.models_dir}/malaria_scaler.pkl")
        
        metadata = {
            "accuracy": float(accuracy_score(y_test, y_pred)),
            "training_date": datetime.now().isoformat(),
            "samples": len(X),
            "scaler": True
        }
        with open(f"{self.models_dir}/malaria_fixed_metadata.json", "w") as f:
            json.dump(metadata, f, indent=2)
        
        print("\n✓ Malaria model saved!")
        return model, scaler
    
    def train_all(self):
        """Train all models"""
        print("\n" + "="*60)
        print("FIXED MODEL TRAINING")
        print("="*60)
        
        self.train_pneumonia()
        self.train_malaria()
        
        print("\n" + "="*60)
        print("TRAINING COMPLETE - MODELS FIXED!")
        print("="*60)
        print("\nNow update routers to use _fixed models with scalers")

if __name__ == "__main__":
    trainer = FixedImageTrainer()
    trainer.train_all()
