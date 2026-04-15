import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.preprocessing import StandardScaler
import joblib
import os

def load_real_liver_disease_data():
    """Load real Indian Liver Patient Dataset (ILPD)"""
    print("Loading real Indian Liver Patient Dataset...")
    
    data_path = 'data/liver_disease_indian.csv'
    
    if not os.path.exists(data_path):
        print(f"Dataset not found at {data_path}")
        print("Please run: python download_datasets_fixed.py")
        return None
    
    df = pd.read_csv(data_path)
    print(f"  Loaded {len(df)} real patient records")
    print(f"  Features: {len(df.columns)-1}")
    
    # Map column names to match expected format
    column_mapping = {
        'Age': 'age',
        'Gender': 'gender',
        'Total_Bilirubin': 'total_bilirubin',
        'Direct_Bilirubin': 'direct_bilirubin',
        'Alkaline_Phosphotase': 'alkaline_phosphatase',
        'Alamine_Aminotransferase': 'alamine_aminotransferase',
        'Aspartate_Aminotransferase': 'aspartate_aminotransferase',
        'Total_Protiens': 'total_proteins',
        'Albumin': 'albumin',
        'Albumin_and_Globulin_Ratio': 'albumin_globulin_ratio',
        'Dataset': 'target'
    }
    
    df = df.rename(columns=column_mapping)
    
    print(f"  Liver disease cases: {df['target'].sum()}")
    print(f"  No liver disease: {len(df) - df['target'].sum()}")
    
    return df

def train_liver_disease_model():
    """Train and save liver disease prediction model using real data"""
    df = load_real_liver_disease_data()
    
    if df is None:
        print("Error: Could not load real dataset")
        return None, None, None
    
    # Save dataset
    if not os.path.exists('data'):
        os.makedirs('data')
    df.to_csv('data/liver_disease_dataset.csv', index=False)
    
    # Prepare features and target
    features = ['age', 'gender', 'total_bilirubin', 'direct_bilirubin', 
                'alkaline_phosphatase', 'alamine_aminotransferase', 
                'aspartate_aminotransferase', 'total_proteins', 
                'albumin', 'albumin_globulin_ratio']
    X = df[features]
    y = df['target']
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Scale features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Train model
    print("Training Random Forest model...")
    model = RandomForestClassifier(
        n_estimators=100,
        max_depth=15,
        random_state=42,
        class_weight='balanced'
    )
    model.fit(X_train_scaled, y_train)
    
    # Evaluate
    y_pred = model.predict(X_test_scaled)
    accuracy = accuracy_score(y_test, y_pred)
    
    print(f"Model Accuracy: {accuracy:.4f}")
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred))
    print("\nConfusion Matrix:")
    print(confusion_matrix(y_test, y_pred))
    
    # Feature importance
    feature_importance = dict(zip(features, model.feature_importances_))
    print("\nFeature Importance:")
    for feature, importance in sorted(feature_importance.items(), key=lambda x: x[1], reverse=True):
        print(f"{feature}: {importance:.4f}")
    
    # Save model and scaler
    if not os.path.exists('models'):
        os.makedirs('models')
    
    joblib.dump(model, 'models/liver_disease_model.pkl')
    joblib.dump(scaler, 'models/liver_disease_scaler.pkl')
    
    # Save model metadata
    metadata = {
        'model_type': 'RandomForestClassifier',
        'features': features,
        'accuracy': accuracy,
        'feature_importance': feature_importance
    }
    
    import json
    with open('models/liver_disease_metadata.json', 'w') as f:
        json.dump(metadata, f, indent=2)
    
    print("\nLiver disease model saved successfully!")
    return model, scaler, metadata

if __name__ == "__main__":
    train_liver_disease_model()
