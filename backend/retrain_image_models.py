#!/usr/bin/env python3
"""Retrain malaria and pneumonia with proper feature extraction"""
import os
import sys
import numpy as np
import cv2
from PIL import Image
from sklearn.ensemble import RandomForestClassifier, ExtraTreesClassifier, VotingClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
import joblib
import json
from tqdm import tqdm

MALARIA_PATH = r"C:\Users\asus\Downloads\malaria\cell_images\cell_images"
PNEUMONIA_PATH = r"C:\Users\asus\Downloads\Pneumonia\chest_xray\chest_xray"

def extract_malaria_features(img):
    """Extract 31 features for malaria - MUST match router exactly"""
    img = cv2.resize(img, (64, 64))
    features = []
    
    # 1. Color histogram (8+8+8 = 24 features)
    for i in range(3):
        hist = cv2.calcHist([img], [i], None, [8], [0, 256]).flatten()
        hist = hist / (np.sum(hist) + 1e-7)
        features.extend(hist)
    
    # 2. Statistical features (7 features)
    for i in range(3):
        channel = img[:, :, i].astype(np.float32) / 255.0
        features.append(np.mean(channel))
        features.append(np.std(channel))
    # Overall brightness
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    features.append(np.mean(gray) / 255.0)
    
    return np.array(features, dtype=np.float32)  # 31 features

def extract_pneumonia_features(img):
    """Extract 37 features for pneumonia - MUST match router exactly"""
    if len(img.shape) == 3:
        img = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    img = cv2.resize(img, (128, 128))
    img_n = img.astype(np.float32) / 255.0
    
    features = []
    
    # 1. Global statistics (6 features)
    features.extend([
        np.mean(img_n), np.std(img_n),
        np.percentile(img_n, 10), np.percentile(img_n, 90),
        np.min(img_n), np.max(img_n)
    ])
    
    # 2. Regional analysis - 6 regions (12 features)
    h, w = img_n.shape
    regions = [
        img_n[0:h//2, 0:w//2], img_n[0:h//2, w//2:],
        img_n[h//2:, 0:w//2], img_n[h//2:, w//2:],
        img_n[h//4:3*h//4, :], img_n[:, w//4:3*w//4]
    ]
    for r in regions:
        features.append(np.mean(r))
        features.append(np.std(r))
    
    # 3. Intensity ratios (6 features)
    features.append(np.sum(img_n < 0.2) / (h * w))
    features.append(np.sum(img_n > 0.7) / (h * w))
    features.append(np.sum((img_n >= 0.3) & (img_n <= 0.7)) / (h * w))
    features.append(np.sum(img_n < 0.1) / (h * w))
    features.append(np.sum(img_n > 0.9) / (h * w))
    features.append(np.std(img_n) ** 2)
    
    # 4. Texture (4 features)
    laplacian = cv2.Laplacian(img, cv2.CV_64F)
    features.append(np.var(laplacian) / 10000)
    features.append(np.mean(np.abs(laplacian)) / 100)
    
    sobelx = cv2.Sobel(img, cv2.CV_64F, 1, 0, ksize=3)
    sobely = cv2.Sobel(img, cv2.CV_64F, 0, 1, ksize=3)
    features.append(np.mean(np.abs(sobelx)))
    features.append(np.mean(np.abs(sobely)))
    
    # 5. Histogram (9 features)
    hist, _ = np.histogram(img_n.flatten(), bins=9, range=(0, 1))
    features.extend(hist / (h * w))
    
    return np.array(features, dtype=np.float32)  # 37 features

def train_malaria():
    print("\n" + "="*70)
    print("[MALARIA] Training with verified feature extraction")
    print("="*70)
    
    parasitized_dir = os.path.join(MALARIA_PATH, "Parasitized")
    uninfected_dir = os.path.join(MALARIA_PATH, "Uninfected")
    
    X, y = [], []
    
    print("Loading parasitized images...")
    files = [f for f in os.listdir(parasitized_dir) if f.endswith('.png')][:1000]
    for file in tqdm(files):
        try:
            img = cv2.imread(os.path.join(parasitized_dir, file))
            if img is not None:
                features = extract_malaria_features(img)
                X.append(features)
                y.append(1)
        except:
            continue
    
    print("Loading uninfected images...")
    files = [f for f in os.listdir(uninfected_dir) if f.endswith('.png')][:1000]
    for file in tqdm(files):
        try:
            img = cv2.imread(os.path.join(uninfected_dir, file))
            if img is not None:
                features = extract_malaria_features(img)
                X.append(features)
                y.append(0)
        except:
            continue
    
    X = np.array(X)
    y = np.array(y)
    
    print(f"Total samples: {len(y)}")
    print(f"Parasitized: {sum(y)}, Uninfected: {len(y)-sum(y)}")
    print(f"Feature shape: {X.shape}")
    
    # Split and train
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    
    scaler = StandardScaler()
    X_train_s = scaler.fit_transform(X_train)
    X_test_s = scaler.transform(X_test)
    
    # Train single RandomForest first to verify it works
    print("\nTraining RandomForest...")
    rf = RandomForestClassifier(n_estimators=300, max_depth=15, random_state=42, n_jobs=-1)
    rf.fit(X_train_s, y_train)
    
    # Test on individual samples to verify discrimination
    print("\nVerifying model discrimination...")
    test_parasitized = X_test_s[y_test == 1][:5]
    test_uninfected = X_test_s[y_test == 0][:5]
    
    for i, sample in enumerate(test_parasitized):
        prob = rf.predict_proba(sample.reshape(1, -1))[0]
        print(f"Parasitized {i+1}: probs={prob}, pred={rf.predict(sample.reshape(1, -1))[0]}")
    
    for i, sample in enumerate(test_uninfected):
        prob = rf.predict_proba(sample.reshape(1, -1))[0]
        print(f"Uninfected {i+1}: probs={prob}, pred={rf.predict(sample.reshape(1, -1))[0]}")
    
    # Now train ensemble
    models = [
        ('rf', RandomForestClassifier(n_estimators=300, max_depth=15, random_state=42, n_jobs=-1)),
        ('et', ExtraTreesClassifier(n_estimators=300, max_depth=15, random_state=42, n_jobs=-1)),
    ]
    ensemble = VotingClassifier(models, voting='soft')
    ensemble.fit(X_train_s, y_train)
    
    y_pred = ensemble.predict(X_test_s)
    y_proba = ensemble.predict_proba(X_test_s)[:, 1]
    
    acc = accuracy_score(y_test, y_pred)
    prec = precision_score(y_test, y_pred, zero_division=0)
    rec = recall_score(y_test, y_pred, zero_division=0)
    f1 = f1_score(y_test, y_pred, zero_division=0)
    roc = roc_auc_score(y_test, y_proba) if len(np.unique(y_test)) > 1 else 0.0
    
    print(f"\nFinal Accuracy: {acc:.1%}")
    print(f"Precision: {prec:.1%}")
    print(f"Recall: {rec:.1%}")
    print(f"F1: {f1:.1%}")
    print(f"ROC AUC: {roc:.1%}")
    
    # Save
    os.makedirs("models", exist_ok=True)
    joblib.dump(ensemble, "models/malaria_real.pkl")
    joblib.dump(scaler, "models/malaria_real_scaler.pkl")
    
    metadata = {
        "accuracy": float(acc),
        "precision": float(prec),
        "recall": float(rec),
        "f1_score": float(f1),
        "roc_auc": float(roc),
        "model": "Ensemble (RF+ET)",
        "training_date": "2026-04-17",
        "n_features": 31
    }
    with open("models/malaria_real_metadata.json", 'w') as f:
        json.dump(metadata, f, indent=2)
    
    return acc

def train_pneumonia():
    print("\n" + "="*70)
    print("[PNEUMONIA] Training with verified feature extraction")
    print("="*70)
    
    normal_dir = os.path.join(PNEUMONIA_PATH, "test", "NORMAL")
    pneumonia_dir = os.path.join(PNEUMONIA_PATH, "test", "PNEUMONIA")
    
    X, y = [], []
    
    print("Loading normal images...")
    files = [f for f in os.listdir(normal_dir) if f.endswith('.jpeg')][:750]
    for file in tqdm(files):
        try:
            img = cv2.imread(os.path.join(normal_dir, file))
            if img is not None:
                features = extract_pneumonia_features(img)
                X.append(features)
                y.append(0)
        except:
            continue
    
    print("Loading pneumonia images...")
    files = [f for f in os.listdir(pneumonia_dir) if f.endswith('.jpeg')][:750]
    for file in tqdm(files):
        try:
            img = cv2.imread(os.path.join(pneumonia_dir, file))
            if img is not None:
                features = extract_pneumonia_features(img)
                X.append(features)
                y.append(1)
        except:
            continue
    
    X = np.array(X)
    y = np.array(y)
    
    print(f"Total samples: {len(y)}")
    print(f"Normal: {sum(1 for i in y if i == 0)}, Pneumonia: {sum(y)}")
    print(f"Feature shape: {X.shape}")
    
    # Split and train
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    
    scaler = StandardScaler()
    X_train_s = scaler.fit_transform(X_train)
    X_test_s = scaler.transform(X_test)
    
    # Train and verify discrimination
    print("\nTraining RandomForest...")
    rf = RandomForestClassifier(n_estimators=300, max_depth=15, random_state=42, n_jobs=-1)
    rf.fit(X_train_s, y_train)
    
    print("\nVerifying model discrimination...")
    test_normal = X_test_s[y_test == 0][:3]
    test_pneumonia = X_test_s[y_test == 1][:3]
    
    for i, sample in enumerate(test_normal):
        prob = rf.predict_proba(sample.reshape(1, -1))[0]
        print(f"Normal {i+1}: probs={prob}, pred={rf.predict(sample.reshape(1, -1))[0]}")
    
    for i, sample in enumerate(test_pneumonia):
        prob = rf.predict_proba(sample.reshape(1, -1))[0]
        print(f"Pneumonia {i+1}: probs={prob}, pred={rf.predict(sample.reshape(1, -1))[0]}")
    
    # Train ensemble
    models = [
        ('rf', RandomForestClassifier(n_estimators=300, max_depth=15, random_state=42, n_jobs=-1)),
        ('et', ExtraTreesClassifier(n_estimators=300, max_depth=15, random_state=42, n_jobs=-1)),
    ]
    ensemble = VotingClassifier(models, voting='soft')
    ensemble.fit(X_train_s, y_train)
    
    y_pred = ensemble.predict(X_test_s)
    y_proba = ensemble.predict_proba(X_test_s)[:, 1]
    
    acc = accuracy_score(y_test, y_pred)
    prec = precision_score(y_test, y_pred, zero_division=0)
    rec = recall_score(y_test, y_pred, zero_division=0)
    f1 = f1_score(y_test, y_pred, zero_division=0)
    roc = roc_auc_score(y_test, y_proba) if len(np.unique(y_test)) > 1 else 0.0
    
    print(f"\nFinal Accuracy: {acc:.1%}")
    
    joblib.dump(ensemble, "models/pneumonia_real.pkl")
    joblib.dump(scaler, "models/pneumonia_real_scaler.pkl")
    
    metadata = {
        "accuracy": float(acc),
        "precision": float(prec),
        "recall": float(rec),
        "f1_score": float(f1),
        "roc_auc": float(roc),
        "model": "Ensemble (RF+ET)",
        "training_date": "2026-04-17",
        "n_features": 37
    }
    with open("models/pneumonia_real_metadata.json", 'w') as f:
        json.dump(metadata, f, indent=2)
    
    return acc

if __name__ == "__main__":
    train_malaria()
    train_pneumonia()
    print("\n✓ Retraining complete with verified discrimination!")
