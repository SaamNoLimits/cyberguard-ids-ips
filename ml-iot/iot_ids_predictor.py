#!/usr/bin/env python3
"""
IoT IDS Predictor - Load saved model and make predictions
"""

import pandas as pd
import numpy as np
import pickle
import joblib
from datetime import datetime
import os

class IoTIDSPredictor:
    """IoT Intrusion Detection System Predictor"""
    
    def __init__(self, model_path=None):
        """Initialize the predictor with a saved model"""
        self.model_pipeline = None
        self.model = None
        self.scaler = None
        self.label_encoder = None
        self.feature_names = None
        self.taxonomy_map = None
        
        if model_path:
            self.load_model(model_path)
    
    def load_model(self, model_path):
        """Load the saved model pipeline"""
        try:
            # Try joblib first, then pickle
            if model_path.endswith('.joblib'):
                self.model_pipeline = joblib.load(model_path)
            else:
                with open(model_path, 'rb') as f:
                    self.model_pipeline = pickle.load(f)
            
            # Extract components
            self.model = self.model_pipeline['model']
            self.scaler = self.model_pipeline['scaler']
            self.label_encoder = self.model_pipeline['label_encoder']
            self.feature_names = self.model_pipeline['feature_names']
            self.taxonomy_map = self.model_pipeline.get('taxonomy_map', {})
            
            print(f"✅ Model loaded successfully from {model_path}")
            print(f"Model type: {self.model_pipeline.get('model_type', 'Unknown')}")
            print(f"Features: {len(self.feature_names)}")
            print(f"Classes: {len(self.label_encoder.classes_)}")
            
        except Exception as e:
            print(f"❌ Error loading model: {str(e)}")
            raise
    
    def predict_single(self, network_data):
        """Predict attack type for a single network flow"""
        if self.model is None:
            raise ValueError("Model not loaded. Please load a model first.")
        
        # Ensure data is in correct format
        if isinstance(network_data, dict):
            network_data = pd.DataFrame([network_data])
        elif isinstance(network_data, list):
            network_data = pd.DataFrame([network_data], columns=self.feature_names)
        
        # Select only the features used in training
        network_data = network_data[self.feature_names]
        
        # Scale the data
        data_scaled = self.scaler.transform(network_data)
        
        # Make prediction
        prediction = self.model.predict(data_scaled)[0]
        prediction_proba = self.model.predict_proba(data_scaled)[0]
        
        # Get class name
        class_name = self.label_encoder.inverse_transform([prediction])[0]
        confidence = max(prediction_proba)
        
        return {
            'prediction': class_name,
            'confidence': confidence,
            'is_malicious': class_name != 'Benign',
            'threat_level': self._get_threat_level(class_name, confidence)
        }
    
    def predict_batch(self, network_data_df):
        """Predict attack types for multiple network flows"""
        if self.model is None:
            raise ValueError("Model not loaded. Please load a model first.")
        
        # Select only the features used in training
        network_data_df = network_data_df[self.feature_names]
        
        # Scale the data
        data_scaled = self.scaler.transform(network_data_df)
        
        # Make predictions
        predictions = self.model.predict(data_scaled)
        predictions_proba = self.model.predict_proba(data_scaled)
        
        # Get class names and confidences
        class_names = self.label_encoder.inverse_transform(predictions)
        confidences = np.max(predictions_proba, axis=1)
        
        # Create results DataFrame
        results = pd.DataFrame({
            'prediction': class_names,
            'confidence': confidences,
            'is_malicious': class_names != 'Benign',
            'threat_level': [self._get_threat_level(name, conf) 
                           for name, conf in zip(class_names, confidences)]
        })
        
        return results
    
    def _get_threat_level(self, class_name, confidence):
        """Determine threat level based on attack type and confidence"""
        if class_name == 'Benign':
            return 'None'
        
        # Define threat levels based on attack taxonomy
        high_threat = ['Flood Attacks', 'Botnet/Mirai Attacks', 'Backdoors & Exploits']
        medium_threat = ['Injection Attacks', 'Spoofing / MITM']
        low_threat = ['Reconnaissance']
        
        if class_name in high_threat:
            base_level = 'High'
        elif class_name in medium_threat:
            base_level = 'Medium'
        elif class_name in low_threat:
            base_level = 'Low'
        else:
            base_level = 'Unknown'
        
        # Adjust based on confidence
        if confidence < 0.7:
            if base_level == 'High':
                return 'Medium'
            elif base_level == 'Medium':
                return 'Low'
        
        return base_level
    
    def get_model_info(self):
        """Get information about the loaded model"""
        if self.model_pipeline is None:
            return "No model loaded"
        
        info = {
            'model_type': self.model_pipeline.get('model_type', 'Unknown'),
            'timestamp': self.model_pipeline.get('timestamp', 'Unknown'),
            'num_features': len(self.feature_names),
            'num_classes': len(self.label_encoder.classes_),
            'classes': list(self.label_encoder.classes_),
            'feature_names': self.feature_names[:10] + ['...'] if len(self.feature_names) > 10 else self.feature_names
        }
        
        return info

def demo_usage():
    """Demonstrate how to use the IoT IDS Predictor"""
    print("🔒 IoT IDS Predictor Demo")
    print("=" * 30)
    
    # Note: Update this path to your actual saved model
    model_path = "./models/iot_ids_lightgbm_latest.pkl"
    
    if not os.path.exists(model_path):
        print("⚠️  Model file not found. Please train and save a model first.")
        print("Run save_best_model.py to create the model file.")
        return
    
    try:
        # Initialize predictor
        predictor = IoTIDSPredictor(model_path)
        
        # Show model info
        print("\n📊 Model Information:")
        info = predictor.get_model_info()
        for key, value in info.items():
            print(f"  {key}: {value}")
        
        # Example prediction (you would replace this with actual network data)
        print("\n🔍 Example Prediction:")
        # This is just example data - replace with actual network flow features
        example_data = {feature: np.random.random() for feature in predictor.feature_names}
        
        result = predictor.predict_single(example_data)
        print(f"Prediction: {result['prediction']}")
        print(f"Confidence: {result['confidence']:.4f}")
        print(f"Is Malicious: {result['is_malicious']}")
        print(f"Threat Level: {result['threat_level']}")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    demo_usage()
