"""
Train Model Script
Generates sample water quality dataset and trains ML model using RandomForestClassifier
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import joblib
import os

def generate_sample_data():
    """Generate sample water quality dataset"""
    np.random.seed(42)
    
    # Number of samples
    n_samples = 1000
    
    # Generate features
    # pH: 0-14 scale, optimal around 7
    ph = np.random.uniform(0, 14, n_samples)
    
    # Turbidity: 0-100 NTU
    turbidity = np.random.uniform(0, 100, n_samples)
    
    # Temperature: 0-40 Celsius
    temperature = np.random.uniform(0, 40, n_samples)
    
    # TDS: 0-1000 mg/L
    tds = np.random.uniform(0, 1000, n_samples)
    
    # Create labels based on water quality rules
    labels = []
    for i in range(n_samples):
        # Safe for Reuse: pH 6.5-8.5, turbidity < 10, temp 15-30, tds < 500
        if (6.5 <= ph[i] <= 8.5 and 
            turbidity[i] < 10 and 
            15 <= temperature[i] <= 30 and 
            tds[i] < 500):
            labels.append(0)  # Safe for Reuse
        # Needs Treatment: moderate values
        elif (4 <= ph[i] <= 10 and 
              turbidity[i] < 50 and 
              5 <= temperature[i] <= 40 and 
              tds[i] < 800):
            labels.append(1)  # Needs Treatment
        else:
            labels.append(2)  # Unsafe
    
    # Create DataFrame
    df = pd.DataFrame({
        'ph': ph,
        'turbidity': turbidity,
        'temperature': temperature,
        'tds': tds,
        'label': labels
    })
    
    return df

def train_model():
    """Train the RandomForestClassifier model"""
    print("Generating sample water quality dataset...")
    df = generate_sample_data()
    
    print("Dataset shape:", df.shape)
    print("\nLabel distribution:")
    print(df['label'].value_counts().sort_index())
    
    # Prepare features and labels
    X = df[['ph', 'turbidity', 'temperature', 'tds']]
    y = df['label']
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    # Scale features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Train model
    print("\nTraining RandomForestClassifier...")
    model = RandomForestClassifier(
        n_estimators=100,
        max_depth=10,
        random_state=42,
        n_jobs=-1
    )
    model.fit(X_train_scaled, y_train)
    
    # Evaluate model
    train_score = model.score(X_train_scaled, y_train)
    test_score = model.score(X_test_scaled, y_test)
    print(f"Training accuracy: {train_score:.4f}")
    print(f"Test accuracy: {test_score:.4f}")
    
    # Save model and scaler
    model_path = os.path.join(os.path.dirname(__file__), 'water_model.pkl')
    scaler_path = os.path.join(os.path.dirname(__file__), 'scaler.pkl')
    
    joblib.dump(model, model_path)
    joblib.dump(scaler, scaler_path)
    
    print(f"\nModel saved to: {model_path}")
    print(f"Scaler saved to: {scaler_path}")
    
    # Save sample data for reference
    df.to_csv('water_quality_data.csv', index=False)
    print("Sample data saved to: water_quality_data.csv")

if __name__ == "__main__":
    train_model()
    print("\nModel training completed successfully!")
