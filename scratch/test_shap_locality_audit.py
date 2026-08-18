import sys, os, pandas as pd, numpy as np, joblib, shap

sys.path.insert(0, os.path.abspath('backend'))

from app.services.price_prediction_service import _MODEL_PIPELINE, PricePredictionService

address = "Block 1, Main Road, Koramangala, Bengaluru - 560034"
matched_locality = PricePredictionService.extract_locality(address)

print("=== PART 1 AUDIT: SHAP LOCALITY MAPPING ===")
print("1. Extracted Locality from address:", matched_locality)

X_infer = pd.DataFrame([{
    "location": matched_locality,
    "area_type": "Super built-up Area",
    "total_sqft": 1200.0,
    "bhk": 2.0,
    "bath": 2.0,
    "balcony": 1.0
}])

preprocessor = _MODEL_PIPELINE.named_steps['preprocessor']
xgb_model = _MODEL_PIPELINE.named_steps['model']
explainer = shap.TreeExplainer(xgb_model)

X_trans = preprocessor.transform(X_infer)
feature_names = preprocessor.get_feature_names_out()
shap_vals = explainer.shap_values(X_trans)[0]

# Inspect active one-hot features in X_trans vs SHAP values
active_features = []
inactive_high_shap_features = []

# Convert X_trans to dense if sparse
X_dense = X_trans.toarray()[0] if hasattr(X_trans, "toarray") else X_trans[0]

for fname, x_val, s_val in zip(feature_names, X_dense, shap_vals):
    if x_val > 0:
        active_features.append((fname, x_val, s_val))
    elif abs(s_val) > 100000:
        inactive_high_shap_features.append((fname, x_val, s_val))

print("\n2. Active Input Features (x_val == 1 or x_val > 0):")
for f, x, s in active_features:
    print(f"   [ACTIVE] Feature: {f:45s} | Input Val: {x:.1f} | SHAP Impact: {s:+,.2f}")

print("\n3. Top 5 Inactive Features with High SHAP values (x_val == 0 but s_val > 100k):")
inactive_high_shap_features.sort(key=lambda item: abs(item[2]), reverse=True)
for f, x, s in inactive_high_shap_features[:5]:
    print(f"   [INACTIVE] Feature: {f:45s} | Input Val: {x:.1f} | SHAP Impact: {s:+,.2f}")
