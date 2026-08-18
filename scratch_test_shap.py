import os
import joblib
import pandas as pd
import numpy as np
import shap

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "backend", "models", "price_model.pkl")

pipeline = joblib.load(MODEL_PATH)
preprocessor = pipeline.named_steps['preprocessor']
model = pipeline.named_steps['model']

# Test sample input
sample_data = pd.DataFrame([{
    "location": "Koramangala",
    "area_type": "Super built-up Area",
    "total_sqft": 1500.0,
    "bhk": 3.0,
    "bath": 2.0,
    "balcony": 2.0
}])

# Transform
X_trans = preprocessor.transform(sample_data)

# Explainer
explainer = shap.TreeExplainer(model)
shap_vals = explainer.shap_values(X_trans)

feature_names = preprocessor.get_feature_names_out()

print("Sample Prediction (INR):", pipeline.predict(sample_data)[0])
print("SHAP Values shape:", shap_vals.shape)
print("Feature names count:", len(feature_names))

# Sort top features
df_shap = pd.DataFrame({
    'feature': feature_names,
    'shap_val': shap_vals[0]
})
df_shap['abs_shap'] = df_shap['shap_val'].abs()
df_shap = df_shap.sort_values(by='abs_shap', ascending=False)

print("\nTop 10 SHAP Attributions:")
print(df_shap.head(10))
