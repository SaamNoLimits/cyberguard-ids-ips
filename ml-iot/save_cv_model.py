#!/usr/bin/env python3
"""
Save the best LightGBM model after 5-fold cross-validation
Based on your existing cross-validation code
"""

import pandas as pd
import numpy as np
import pickle
import joblib
from datetime import datetime
import os

# ML Libraries
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import classification_report, accuracy_score, f1_score
import lightgbm as lgb

import warnings
warnings.filterwarnings('ignore')

def save_best_cv_model():
    """
    Train LightGBM with 5-fold CV and save the best performing model
    """
    print("🔒 IoT IDS Model Training with 5-Fold Cross-Validation")
    print("=" * 60)
    
    # Note: Make sure your data is already loaded and preprocessed
    # This assumes df, X_scaled, and taxonomy_label column exist
    
    # Prepare data (based on your code)
    print("📊 Preparing data...")
    df_clean = df.dropna(subset=['taxonomy_label']).copy()
    le_lgb_cv = LabelEncoder()
    y_lgb_cv = le_lgb_cv.fit_transform(df_clean['taxonomy_label'])
    X_lgb_cv = X_scaled[df_clean.index]
    
    print(f"Clean dataset shape: {X_lgb_cv.shape}")
    print(f"Classes: {le_lgb_cv.classes_}")
    
    # Set up StratifiedKFold
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    
    # Track best model
    best_model = None
    best_scaler = None
    best_score = 0
    best_fold = 0
    fold_scores = []
    
    print("\n🚀 Starting 5-fold cross-validation...")
    
    # Loop through folds (your existing code)
    for fold, (train_idx, test_idx) in enumerate(skf.split(X_lgb_cv, y_lgb_cv)):
        print(f"\n📘 Fold {fold+1}")
        
        X_train, X_test = X_lgb_cv[train_idx], X_lgb_cv[test_idx]
        y_train, y_test = y_lgb_cv[train_idx], y_lgb_cv[test_idx]
        
        # LightGBM model
        lgb_model = lgb.LGBMClassifier(
            objective='multiclass',
            num_class=len(le_lgb_cv.classes_),
            is_unbalance=True,
            n_estimators=100,
            random_state=42,
            verbose=-1  # Suppress training output
        )
        lgb_model.fit(X_train, y_train)
        
        # Predict and evaluate
        y_pred = lgb_model.predict(X_test)
        
        # Calculate scores
        accuracy = accuracy_score(y_test, y_pred)
        f1 = f1_score(y_test, y_pred, average='weighted')
        fold_scores.append({'fold': fold+1, 'accuracy': accuracy, 'f1': f1})
        
        print(f"Accuracy: {accuracy:.4f}, F1-Score: {f1:.4f}")
        print(classification_report(y_test, y_pred, target_names=le_lgb_cv.classes_))
        
        # Keep track of best model
        if f1 > best_score:
            best_score = f1
            best_fold = fold + 1
            best_model = lgb_model
            # Note: We'll use the original scaler from preprocessing
    
    # Print cross-validation summary
    print("\n📊 Cross-Validation Summary:")
    print("=" * 40)
    avg_accuracy = np.mean([score['accuracy'] for score in fold_scores])
    avg_f1 = np.mean([score['f1'] for score in fold_scores])
    std_accuracy = np.std([score['accuracy'] for score in fold_scores])
    std_f1 = np.std([score['f1'] for score in fold_scores])
    
    print(f"Average Accuracy: {avg_accuracy:.4f} ± {std_accuracy:.4f}")
    print(f"Average F1-Score: {avg_f1:.4f} ± {std_f1:.4f}")
    print(f"Best Model: Fold {best_fold} (F1: {best_score:.4f})")
    
    # Train final model on full dataset
    print(f"\n🎯 Training final model on full dataset...")
    final_model = lgb.LGBMClassifier(
        objective='multiclass',
        num_class=len(le_lgb_cv.classes_),
        is_unbalance=True,
        n_estimators=100,
        random_state=42,
        verbose=-1
    )
    final_model.fit(X_lgb_cv, y_lgb_cv)
    
    # Create model pipeline
    model_pipeline = {
        'model': final_model,  # Final model trained on full data
        'scaler': scaler,  # Original scaler from preprocessing
        'label_encoder': le_lgb_cv,
        'feature_names': list(df.drop(columns=['label', 'taxonomy_label']).columns),
        'model_type': 'LightGBM',
        'timestamp': datetime.now().strftime("%Y%m%d_%H%M%S"),
        'cv_results': {
            'avg_accuracy': avg_accuracy,
            'avg_f1': avg_f1,
            'std_accuracy': std_accuracy,
            'std_f1': std_f1,
            'best_fold': best_fold,
            'best_score': best_score,
            'fold_scores': fold_scores
        },
        'taxonomy_classes': list(le_lgb_cv.classes_)
    }
    
    # Save the model
    timestamp = model_pipeline['timestamp']
    os.makedirs('./models', exist_ok=True)
    
    # Save with pickle
    pickle_path = f"./models/iot_ids_cv_model_{timestamp}.pkl"
    with open(pickle_path, 'wb') as f:
        pickle.dump(model_pipeline, f)
    
    # Save with joblib
    joblib_path = f"./models/iot_ids_cv_model_{timestamp}.joblib"
    joblib.dump(model_pipeline, joblib_path)
    
    print(f"\n💾 Model saved successfully!")
    print(f"Pickle file: {pickle_path}")
    print(f"Joblib file: {joblib_path}")
    
    # Save detailed results
    results_path = f"./models/cv_results_{timestamp}.txt"
    with open(results_path, 'w') as f:
        f.write("IoT IDS Cross-Validation Results\n")
        f.write("=" * 40 + "\n")
        f.write(f"Timestamp: {timestamp}\n")
        f.write(f"Model: LightGBM Classifier\n")
        f.write(f"Cross-Validation: 5-fold StratifiedKFold\n\n")
        
        f.write("Overall Performance:\n")
        f.write(f"  Average Accuracy: {avg_accuracy:.4f} ± {std_accuracy:.4f}\n")
        f.write(f"  Average F1-Score: {avg_f1:.4f} ± {std_f1:.4f}\n")
        f.write(f"  Best Fold: {best_fold} (F1: {best_score:.4f})\n\n")
        
        f.write("Per-Fold Results:\n")
        for score in fold_scores:
            f.write(f"  Fold {score['fold']}: Accuracy={score['accuracy']:.4f}, F1={score['f1']:.4f}\n")
        
        f.write(f"\nClasses ({len(le_lgb_cv.classes_)}):\n")
        for i, class_name in enumerate(le_lgb_cv.classes_):
            f.write(f"  {i}: {class_name}\n")
    
    print(f"📄 Results saved to: {results_path}")
    print(f"\n🎉 Cross-validation completed! Your IoT IDS model is ready.")
    
    return pickle_path, model_pipeline

# Example usage for Kaggle
def kaggle_save_cv_model():
    """
    Kaggle-specific version - paste this into your Kaggle notebook
    """
    kaggle_code = '''
# Add this to your Kaggle notebook after your cross-validation loop

# Save the final model trained on full dataset
print("💾 Saving the best model...")

# Train final model on full dataset
final_model = lgb.LGBMClassifier(
    objective='multiclass',
    num_class=len(le_lgb_cv.classes_),
    is_unbalance=True,
    n_estimators=100,
    random_state=42,
    verbose=-1
)
final_model.fit(X_lgb_cv, y_lgb_cv)

# Create model pipeline
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
model_pipeline = {
    'model': final_model,
    'scaler': scaler,  # Your original scaler
    'label_encoder': le_lgb_cv,
    'feature_names': list(df.drop(columns=['label', 'taxonomy_label']).columns),
    'model_type': 'LightGBM',
    'timestamp': timestamp,
    'taxonomy_classes': list(le_lgb_cv.classes_)
}

# Save the model
pickle_filename = f"iot_ids_cv_model_{timestamp}.pkl"
with open(pickle_filename, 'wb') as f:
    pickle.dump(model_pipeline, f)

joblib_filename = f"iot_ids_cv_model_{timestamp}.joblib"
joblib.dump(model_pipeline, joblib_filename)

print(f"✅ Model saved as: {pickle_filename}")
print(f"✅ Alternative format: {joblib_filename}")
print("📥 Download these files from Kaggle output section")

# Test loading
with open(pickle_filename, 'rb') as f:
    loaded_pipeline = pickle.load(f)
    
print("🔍 Model loaded successfully for testing!")
print(f"Classes: {loaded_pipeline['label_encoder'].classes_}")
'''
    
    print("📋 Copy this code to your Kaggle notebook:")
    print("=" * 50)
    print(kaggle_code)
    
    return kaggle_code

if __name__ == "__main__":
    print("Choose an option:")
    print("1. Generate Kaggle code")
    print("2. Run local model saving (requires data)")
    
    choice = input("Enter choice (1 or 2): ")
    
    if choice == "1":
        kaggle_save_cv_model()
    elif choice == "2":
        # This would require your actual data to be loaded
        print("⚠️  Make sure your data (df, X_scaled, scaler) is loaded first")
        # save_best_cv_model()
    else:
        print("Invalid choice")
