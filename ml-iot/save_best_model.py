#!/usr/bin/env python3
"""
Script to train and save the best LightGBM model for IoT IDS
Optimized for Kaggle environment
"""

import pandas as pd
import numpy as np
import pickle
import joblib
from datetime import datetime
import os

# ML Libraries
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split, StratifiedKFold
from sklearn.metrics import classification_report, accuracy_score, f1_score
import lightgbm as lgb

# Suppress warnings
import warnings
warnings.filterwarnings('ignore')

def load_and_prepare_data(data_path):
    """Load and prepare the IoT dataset"""
    print("📊 Loading dataset...")
    df = pd.read_csv(data_path)
    print(f"Dataset shape: {df.shape}")
    
    # Drop rows with missing taxonomy labels
    df_clean = df.dropna(subset=['label']).copy()
    print(f"Clean dataset shape: {df_clean.shape}")
    
    # Prepare features (drop label column)
    X = df_clean.drop(columns=['label'])
    y = df_clean['label']
    
    # Handle any remaining non-numeric columns
    numeric_columns = X.select_dtypes(include=[np.number]).columns
    X = X[numeric_columns]
    
    print(f"Feature matrix shape: {X.shape}")
    print(f"Unique labels: {y.nunique()}")
    
    return X, y, df_clean

def create_taxonomy_mapping():
    """Create taxonomy mapping for attack classification"""
    taxonomy_map = {
        # Flood Attacks
        'DoS-TCP_Flood': 'Flood Attacks',
        'DoS-UDP_Flood': 'Flood Attacks', 
        'DoS-SYN_Flood': 'Flood Attacks',
        'DoS-HTTP_Flood': 'Flood Attacks',
        
        # Botnet/Mirai Attacks
        'Mirai-greeth_flood': 'Botnet/Mirai Attacks',
        'Mirai-greip_flood': 'Botnet/Mirai Attacks',
        'Mirai-udpplain': 'Botnet/Mirai Attacks',
        
        # Spoofing/MITM
        'MITM-ArpSpoofing': 'Spoofing / MITM',
        'DNS_Spoofing': 'Spoofing / MITM',
        
        # Reconnaissance  
        'Recon-PingSweep': 'Reconnaissance',
        'Recon-OSScan': 'Reconnaissance',
        'Recon-PortScan': 'Reconnaissance',
        'VulnerabilityScan': 'Reconnaissance',
        
        # Backdoors & Exploits
        'Backdoor_Malware': 'Backdoors & Exploits',
        'BrowserHijacking': 'Backdoors & Exploits',
        'CommandInjection': 'Backdoors & Exploits',
        
        # Injection Attacks
        'SqlInjection': 'Injection Attacks',
        'XSS': 'Injection Attacks',
        
        # Benign
        'BenignTraffic': 'Benign'
    }
    return taxonomy_map

def train_best_model(X, y):
    """Train the best performing LightGBM model"""
    print("🚀 Training LightGBM model...")
    
    # Apply taxonomy mapping
    taxonomy_map = create_taxonomy_mapping()
    y_taxonomy = y.map(taxonomy_map).fillna('Unknown')
    
    # Encode labels
    le = LabelEncoder()
    y_encoded = le.fit_transform(y_taxonomy)
    
    # Scale features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Train-test split
    X_train, X_test, y_train, y_test = train_test_split(
        X_scaled, y_encoded, test_size=0.2, stratify=y_encoded, random_state=42
    )
    
    # Define best model configuration
    lgb_model = lgb.LGBMClassifier(
        objective='multiclass',
        num_class=len(le.classes_),
        is_unbalance=True,
        n_estimators=200,  # Increased for better performance
        learning_rate=0.1,
        max_depth=10,
        num_leaves=31,
        random_state=42,
        verbose=-1  # Suppress training output
    )
    
    # Train model
    lgb_model.fit(X_train, y_train)
    
    # Evaluate
    y_pred = lgb_model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred, average='weighted')
    
    print(f"✅ Model trained successfully!")
    print(f"Accuracy: {accuracy:.4f}")
    print(f"F1-Score (weighted): {f1:.4f}")
    print("\n📋 Classification Report:")
    print(classification_report(y_test, y_pred, target_names=le.classes_))
    
    return lgb_model, scaler, le, X.columns.tolist()

def save_model_pipeline(model, scaler, label_encoder, feature_names, save_dir="./models"):
    """Save the complete model pipeline"""
    
    # Create models directory
    os.makedirs(save_dir, exist_ok=True)
    
    # Create timestamp for versioning
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Model pipeline dictionary
    model_pipeline = {
        'model': model,
        'scaler': scaler,
        'label_encoder': label_encoder,
        'feature_names': feature_names,
        'model_type': 'LightGBM',
        'timestamp': timestamp,
        'taxonomy_map': create_taxonomy_mapping()
    }
    
    # Save using both pickle and joblib for compatibility
    pickle_path = os.path.join(save_dir, f"iot_ids_lightgbm_{timestamp}.pkl")
    joblib_path = os.path.join(save_dir, f"iot_ids_lightgbm_{timestamp}.joblib")
    
    # Save with pickle
    with open(pickle_path, 'wb') as f:
        pickle.dump(model_pipeline, f)
    
    # Save with joblib (often better for sklearn models)
    joblib.dump(model_pipeline, joblib_path)
    
    print(f"💾 Model saved successfully!")
    print(f"Pickle file: {pickle_path}")
    print(f"Joblib file: {joblib_path}")
    
    # Save model info
    info_path = os.path.join(save_dir, f"model_info_{timestamp}.txt")
    with open(info_path, 'w') as f:
        f.write(f"IoT IDS Model Information\n")
        f.write(f"========================\n")
        f.write(f"Model Type: LightGBM Classifier\n")
        f.write(f"Timestamp: {timestamp}\n")
        f.write(f"Features: {len(feature_names)}\n")
        f.write(f"Classes: {len(label_encoder.classes_)}\n")
        f.write(f"Class Names: {', '.join(label_encoder.classes_)}\n")
        f.write(f"\nTaxonomy Mapping:\n")
        for original, taxonomy in create_taxonomy_mapping().items():
            f.write(f"  {original} -> {taxonomy}\n")
    
    return pickle_path, joblib_path

def main():
    """Main execution function"""
    print("🔒 IoT IDS Model Training and Saving Pipeline")
    print("=" * 50)
    
    # Note: Update this path to your actual dataset path in Kaggle
    data_path = "/kaggle/input/your-dataset/iot_dataset.csv"  # Update this path
    
    # For local testing, use a different path
    if not os.path.exists(data_path):
        print("⚠️  Dataset path not found. Please update the data_path variable.")
        print("For Kaggle: /kaggle/input/your-dataset-name/filename.csv")
        return
    
    try:
        # Load and prepare data
        X, y, df_clean = load_and_prepare_data(data_path)
        
        # Train best model
        model, scaler, le, feature_names = train_best_model(X, y)
        
        # Save model pipeline
        pickle_path, joblib_path = save_model_pipeline(model, scaler, le, feature_names)
        
        print("\n🎉 Pipeline completed successfully!")
        print(f"Model files saved and ready for IoT IDS deployment.")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        print("Please check your dataset path and format.")

if __name__ == "__main__":
    main()
