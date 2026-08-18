import os
import json
import re
import numpy as np
import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from xgboost import XGBRegressor

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_PATH = os.path.join(BASE_DIR, "datasets", "banglore_housing_data", "Bengaluru_House_Data.csv")
MODELS_DIR = os.path.join(BASE_DIR, "models")
MODEL_PATH = os.path.join(MODELS_DIR, "price_model.pkl")
META_PATH = os.path.join(MODELS_DIR, "price_model_meta.json")

def parse_total_sqft(val):
    """Safely convert total_sqft string to float sqft value."""
    if pd.isna(val):
        return np.nan
    val_str = str(val).strip()
    
    # Handle ranges like "2100 - 2850"
    if '-' in val_str:
        tokens = val_str.split('-')
        try:
            return (float(tokens[0].strip()) + float(tokens[1].strip())) / 2.0
        except Exception:
            return np.nan
            
    # Handle units conversion if string contains letters
    val_lower = val_str.lower()
    if 'sq. meter' in val_lower or 'sq meter' in val_lower:
        match = re.search(r'[\d\.]+', val_str)
        return float(match.group()) * 10.7639 if match else np.nan
    elif 'perch' in val_lower:
        match = re.search(r'[\d\.]+', val_str)
        return float(match.group()) * 272.25 if match else np.nan
    elif 'acre' in val_lower:
        match = re.search(r'[\d\.]+', val_str)
        return float(match.group()) * 43560.0 if match else np.nan
    elif 'sq. yard' in val_lower or 'sq yard' in val_lower:
        match = re.search(r'[\d\.]+', val_str)
        return float(match.group()) * 9.0 if match else np.nan
    elif 'ground' in val_lower:
        match = re.search(r'[\d\.]+', val_str)
        return float(match.group()) * 2400.0 if match else np.nan
        
    try:
        return float(val_str)
    except Exception:
        return np.nan

def parse_bhk(val):
    """Extract numeric BHK integer from size column string."""
    if pd.isna(val):
        return np.nan
    match = re.search(r'(\d+)', str(val))
    if match:
        return int(match.group(1))
    return np.nan

def remove_location_outliers(df):
    """Remove price-per-sqft outliers per location (within 1 std dev bounds)."""
    df_out = pd.DataFrame()
    for key, subdf in df.groupby('location'):
        m = np.mean(subdf['price_per_sqft'])
        st = np.std(subdf['price_per_sqft'])
        reduced_df = subdf[(subdf['price_per_sqft'] >= (m - st)) & (subdf['price_per_sqft'] <= (m + st))]
        df_out = pd.concat([df_out, reduced_df], ignore_index=True)
    return df_out

def main():
    print("=" * 70)
    print("STARTING BANGALORE REAL ESTATE XGBOOST MODEL TRAINING")
    print("=" * 70)
    
    if not os.path.exists(DATASET_PATH):
        raise FileNotFoundError(f"Dataset not found at {DATASET_PATH}")
        
    df_raw = pd.read_csv(DATASET_PATH)
    original_row_count = len(df_raw)
    print(f"1. Raw Dataset Loaded: {original_row_count} rows, {len(df_raw.columns)} columns")

    # 2. Drop duplicates
    df = df_raw.drop_duplicates().copy()
    print(f"2. After Dropping Duplicates: {len(df)} rows (Removed {original_row_count - len(df)} duplicates)")

    # 3. Clean location
    df['location'] = df['location'].fillna('Other').astype(str).str.strip()
    
    # Group rare locations (<10 occurrences) into 'Other'
    location_stats = df['location'].value_counts()
    locations_less_than_10 = location_stats[location_stats < 10]
    df['location'] = df['location'].apply(lambda x: 'Other' if x in locations_less_than_10 else x)
    num_unique_locations = df['location'].nunique()
    print(f"3. Unique Locations normalized & grouped into 'Other' (<10 records): {num_unique_locations} unique locations")

    # 4. Clean size -> BHK
    df['bhk'] = df['size'].apply(parse_bhk)
    df['bhk'] = df['bhk'].fillna(df['bhk'].median())

    # 5. Clean total_sqft
    df['total_sqft_num'] = df['total_sqft'].apply(parse_total_sqft)
    df = df.dropna(subset=['total_sqft_num']).copy()
    df = df[df['total_sqft_num'] > 0].copy()

    # 6. Clean bath & balcony
    df['bath'] = pd.to_numeric(df['bath'], errors='coerce')
    df['bath'] = df.groupby('bhk')['bath'].transform(lambda x: x.fillna(x.median()))
    df['bath'] = df['bath'].fillna(2.0)

    df['balcony'] = pd.to_numeric(df['balcony'], errors='coerce')
    df['balcony'] = df.groupby('bhk')['balcony'].transform(lambda x: x.fillna(x.median()))
    df['balcony'] = df['balcony'].fillna(1.0)

    # Clean area_type
    df['area_type'] = df['area_type'].fillna('Super built-up Area').astype(str).str.strip()

    # 7. Clean price (Dataset price is in Lakhs -> Convert to actual INR)
    df['price'] = pd.to_numeric(df['price'], errors='coerce')
    df = df.dropna(subset=['price']).copy()
    df['price_inr'] = df['price'] * 100000.0
    df['price_per_sqft'] = df['price_inr'] / df['total_sqft_num']

    # 8. Outlier Removal
    # Rule A: Minimum sqft per BHK should be >= 300 sqft
    df = df[~(df['total_sqft_num'] / df['bhk'] < 300)].copy()

    # Rule B: Price per sqft outlier filtering by location
    df = remove_location_outliers(df)

    rows_after_cleaning = len(df)
    print(f"4. Rows After Outlier Removal & Cleaning: {rows_after_cleaning} rows")

    # 9. Features & Target
    feature_cols = ['location', 'area_type', 'total_sqft_num', 'bhk', 'bath', 'balcony']
    X = df[feature_cols].rename(columns={'total_sqft_num': 'total_sqft'})
    y = df['price_inr']

    # Train / Test Split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    print(f"5. Train/Test Split: Train = {len(X_train)} rows, Test = {len(X_test)} rows")

    # 10. Building ML Pipeline
    categorical_cols = ['location', 'area_type']
    numerical_cols = ['total_sqft', 'bhk', 'bath', 'balcony']

    preprocessor = ColumnTransformer(
        transformers=[
            ('cat', OneHotEncoder(handle_unknown='ignore', sparse_output=False), categorical_cols),
            ('num', StandardScaler(), numerical_cols)
        ],
        remainder='drop'
    )

    xgb_model = XGBRegressor(
        n_estimators=350,
        learning_rate=0.04,
        max_depth=6,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42
    )

    model_pipeline = Pipeline(steps=[
        ('preprocessor', preprocessor),
        ('model', xgb_model)
    ])

    print("6. Training XGBoost Model...")
    model_pipeline.fit(X_train, y_train)

    # 11. Evaluation
    y_pred = model_pipeline.predict(X_test)
    
    mae = float(mean_absolute_error(y_test, y_pred))
    rmse = float(np.sqrt(mean_squared_error(y_test, y_pred)))
    r2 = float(r2_score(y_test, y_pred))

    print("\n" + "=" * 50)
    print("MODEL EVALUATION RESULTS (TEST SET)")
    print("=" * 50)
    print(f"  MAE  : Rs. {mae:,.2f} ({mae/100000:.2f} Lakhs)")
    print(f"  RMSE : Rs. {rmse:,.2f} ({rmse/100000:.2f} Lakhs)")
    print(f"  R²   : {r2:.4f}")
    print("=" * 50 + "\n")

    # 12. Save Model & Meta
    os.makedirs(MODELS_DIR, exist_ok=True)
    joblib.dump(model_pipeline, MODEL_PATH)
    print(f"7. Model Pipeline Saved -> {MODEL_PATH}")

    meta_data = {
        "dataset_name": "Bengaluru_House_Data.csv",
        "original_rows": original_row_count,
        "cleaned_rows": rows_after_cleaning,
        "unique_locations": num_unique_locations,
        "train_rows": len(X_train),
        "test_rows": len(X_test),
        "features": list(X.columns),
        "metrics": {
            "mae_inr": mae,
            "mae_lakhs": round(mae / 100000.0, 2),
            "rmse_inr": rmse,
            "rmse_lakhs": round(rmse / 100000.0, 2),
            "r2": round(r2, 4)
        }
    }

    with open(META_PATH, "w") as f:
        json.dump(meta_data, f, indent=2)
    print(f"8. Metadata Saved -> {META_PATH}")

if __name__ == "__main__":
    main()
