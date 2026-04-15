import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.preprocessing import StandardScaler
import joblib
import os

def generate_synthetic_alzheimer_data(n_samples=1000):
    """Generate synthetic Alzheimer's dataset for demonstration"""
    np.random.seed(42)
    
    # Generate features based on typical Alzheimer's indicators
    data = {
        'age': np.random.normal(65, 15, n_samples),
        'gender': np.random.choice([0, 1], n_samples, p=[0.5, 0.5]),
        'education_years': np.random.normal(12, 4, n_samples),
        'mmse_score': np.random.normal(20, 8, n_samples),
        'memory_complaints': np.random.choice([0, 1], n_samples, p=[0.6, 0.4]),
        'behavioral_problems': np.random.choice([0, 1], n_samples, p=[0.7, 0.3]),
        'adl_score': np.random.normal(10, 5, n_samples),
        'functional_assessment': np.random.normal(5, 2, n_samples),
        'brain_volume_ratio': np.random.normal(0.8, 0.1, n_samples),
        'cortical_thickness': np.random.normal(3.0, 0.5, n_samples),
        'csf_protein_level': np.random.normal(1.5, 0.5, n_samples),
        'hippocampal_atrophy': np.random.normal(0.3, 0.1, n_samples)
    }
    
    df = pd.DataFrame(data)
    
    # Generate target based on risk factors
    risk_score = (
        (df['age'] > 75) * 0.15 +
        (df['education_years'] < 8) * 0.1 +
        (df['mmse_score'] > 25) * 0.2 +
        (df['memory_complaints'] == 1) * 0.15 +
        (df['behavioral_problems'] == 1) * 0.15 +
        (df['adl_score'] > 15) * 0.15 +
        (df['functional_assessment'] > 7) * 0.1 +
        (df['brain_volume_ratio'] > 0.85) * 0.1 +
        (df['cortical_thickness'] < 2.5) * 0.1 +
        (df['csf_protein_level'] > 2.0) * 0.1 +
        (df['hippocampal_atrophy'] > 0.5) * 0.1
    )
    
    # Add some noise
    noise = np.random.normal(0, 0.1, n_samples)
    probability = risk_score + noise
    probability = np.clip(probability, 0, 1)
    
    # Convert to binary outcome
    df['target'] = (probability > 0.5).astype(int)
    
    # Ensure realistic ranges
    df['age'] = np.clip(df['age'], 45, 90)
    df['education_years'] = np.clip(df['education_years'], 0, 20)
    df['mmse_score'] = np.clip(df['mmse_score'], 0, 30)
    df['adl_score'] = np.clip(df['adl_score'], 0, 30)
    df['functional_assessment'] = np.clip(df['functional_assessment'], 0, 15)
    df['brain_volume_ratio'] = np.clip(df['brain_volume_ratio'], 0.5, 1.5)
    df['cortical_thickness'] = np.clip(df['cortical_thickness'], 1.5, 4.5)
    df['csf_protein_level'] = np.clip(df['csf_protein_level'], 0.5, 3.0)
    df['hippocampal_atrophy'] = np.clip(df['hippocampal_atrophy'], 0.0, 1.0)
    
    return df

def train_alzheimer_model():
    """Train and save Alzheimer's prediction model"""
    print("Generating synthetic Alzheimer's dataset...")
    df = generate_synthetic_alzheimer_data(1000)
    
    # Save dataset
    if not os.path.exists('data'):
        os.makedirs('data')
    df.to_csv('data/alzheimer_dataset.csv', index=False)
    
    # Prepare features and target
    features = ['age', 'gender', 'education_years', 'mmse_score', 'memory_complaints', 
                'behavioral_problems', 'adl_score', 'functional_assessment', 
                'brain_volume_ratio', 'cortical_thickness', 'csf_protein_level', 
                'hippocampal_atrophy']
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
    
    joblib.dump(model, 'models/alzheimer_model.pkl')
    joblib.dump(scaler, 'models/alzheimer_scaler.pkl')
    
    # Save model metadata
    metadata = {
        'model_type': 'RandomForestClassifier',
        'features': features,
        'accuracy': accuracy,
        'feature_importance': feature_importance
    }
    
    import json
    with open('models/alzheimer_metadata.json', 'w') as f:
        json.dump(metadata, f, indent=2)
    
    print("\nAlzheimer's model saved successfully!")
    return model, scaler, metadata

if __name__ == "__main__":
    train_alzheimer_model()
