# ========================================
# PASTE THIS CODE IN YOUR KAGGLE NOTEBOOK
# After your cross-validation loop
# ========================================

import pickle
import joblib
from datetime import datetime

print("💾 Saving the best model after cross-validation...")

# Train final model on full dataset (best practice after CV)
final_model = lgb.LGBMClassifier(
    objective='multiclass',
    num_class=len(le_lgb_cv.classes_),
    is_unbalance=True,
    n_estimators=100,
    random_state=42,
    verbose=-1
)
final_model.fit(X_lgb_cv, y_lgb_cv)

# Create timestamp for versioning
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

# Create complete model pipeline
model_pipeline = {
    'model': final_model,
    'scaler': scaler,  # Your original StandardScaler
    'label_encoder': le_lgb_cv,
    'feature_names': list(df.drop(columns=['label', 'taxonomy_label']).columns),
    'model_type': 'LightGBM',
    'timestamp': timestamp,
    'classes': list(le_lgb_cv.classes_),
    'n_features': len(df.drop(columns=['label', 'taxonomy_label']).columns),
    'cv_folds': 5
}

# Save with pickle (primary format)
pickle_filename = f"iot_ids_model_{timestamp}.pkl"
with open(pickle_filename, 'wb') as f:
    pickle.dump(model_pipeline, f)

# Save with joblib (alternative format)
joblib_filename = f"iot_ids_model_{timestamp}.joblib"
joblib.dump(model_pipeline, joblib_filename)

print(f"✅ Model saved successfully!")
print(f"📁 Pickle file: {pickle_filename}")
print(f"📁 Joblib file: {joblib_filename}")
print(f"📊 Model info:")
print(f"   - Classes: {len(le_lgb_cv.classes_)}")
print(f"   - Features: {len(model_pipeline['feature_names'])}")
print(f"   - Timestamp: {timestamp}")

# Verify the saved model works
print("\n🔍 Testing saved model...")
with open(pickle_filename, 'rb') as f:
    test_pipeline = pickle.load(f)

print("✅ Model loaded successfully!")
print(f"Classes: {test_pipeline['label_encoder'].classes_}")

# Create model info file
info_filename = f"model_info_{timestamp}.txt"
with open(info_filename, 'w') as f:
    f.write("IoT IDS Model Information\n")
    f.write("========================\n")
    f.write(f"Model Type: LightGBM Classifier\n")
    f.write(f"Training Date: {timestamp}\n")
    f.write(f"Cross-Validation: 5-fold StratifiedKFold\n")
    f.write(f"Number of Features: {len(model_pipeline['feature_names'])}\n")
    f.write(f"Number of Classes: {len(le_lgb_cv.classes_)}\n")
    f.write(f"\nClass Labels:\n")
    for i, class_name in enumerate(le_lgb_cv.classes_):
        f.write(f"  {i}: {class_name}\n")
    f.write(f"\nFeature Names (first 10):\n")
    for i, feature in enumerate(model_pipeline['feature_names'][:10]):
        f.write(f"  {i}: {feature}\n")
    if len(model_pipeline['feature_names']) > 10:
        f.write(f"  ... and {len(model_pipeline['feature_names']) - 10} more features\n")

print(f"📄 Model info saved to: {info_filename}")
print(f"\n🎉 Ready for download! Look for these files in Kaggle's output section:")
print(f"   - {pickle_filename}")
print(f"   - {joblib_filename}")
print(f"   - {info_filename}")

# ========================================
# END OF KAGGLE CODE SNIPPET
# ========================================
