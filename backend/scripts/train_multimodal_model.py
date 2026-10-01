import os
import sys
import json
import time
import argparse
import asyncio
import hashlib
import numpy as np
import pandas as pd
import sqlite3
import joblib
from datetime import datetime, timezone
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from xgboost import XGBRegressor

# Add backend directory to sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from app.services.image_ai_service import ImageAIService
from app.services.text_ai_service import TextAIService
from app.services.geoapify_service import GeoapifyService
from app.services.multimodal_model_service import (
    MultimodalModelService,
    STRUCTURED_FEATURE_NAMES,
    GEO_FEATURE_NAMES,
    TFIDF_FEATURE_NAMES,
    IMAGE_FEATURE_NAMES,
    ALL_FEATURE_NAMES
)

DB_PATH = os.path.join(BASE_DIR, "real_estate.db")
MODELS_DIR = os.path.join(BASE_DIR, "models")
IMAGE_CACHE_DIR = os.path.join(MODELS_DIR, "image_cache")
GEO_CACHE_PATH = os.path.join(MODELS_DIR, "geo_training_cache.json")
MODEL_OUTPUT_PATH = os.path.join(MODELS_DIR, "multimodal_xgboost.joblib")
META_OUTPUT_PATH = os.path.join(MODELS_DIR, "multimodal_model_meta.json")


def load_geo_cache() -> dict:
    if os.path.exists(GEO_CACHE_PATH):
        try:
            with open(GEO_CACHE_PATH, "r") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def save_geo_cache(cache: dict):
    os.makedirs(MODELS_DIR, exist_ok=True)
    with open(GEO_CACHE_PATH, "w") as f:
        json.dump(cache, f, indent=2)


def get_image_cache_path(img_src: str) -> str:
    h = hashlib.sha256(img_src.encode("utf-8")).hexdigest()[:16]
    return os.path.join(IMAGE_CACHE_DIR, f"embed_{h}.npy")


def main():
    parser = argparse.ArgumentParser(description="Train Multimodal XGBoost Model on Structured + Geo + NLP + ResNet-18 Image features.")
    parser.add_argument("--live-geo", action="store_true", help="Enable live Geoapify API queries for un-cached coordinates")
    parser.add_argument("--sample-size", type=int, default=600, help="Number of diverse properties to train on")
    args = parser.parse_args()

    print("=" * 80)
    print("PROPULSE MULTIMODAL REAL ESTATE PIPELINE TRAINING")
    print("Pipeline: Structured + Geoapify + TF-IDF/NLP + ResNet-18 CNN -> XGBoost")
    print("=" * 80)

    os.makedirs(MODELS_DIR, exist_ok=True)
    os.makedirs(IMAGE_CACHE_DIR, exist_ok=True)

    # 1. Load data from SQLite database
    print("\n[Step 1/6] Loading property records from database...")
    conn = sqlite3.connect(DB_PATH)
    query = """
        SELECT id, title, locality, price, area_sqft, bhk, bathrooms, balconies, 
               property_age, latitude, longitude, description, images, nearby_places
        FROM properties
        WHERE price > 0 AND area_sqft > 0 AND price < 500000000
    """
    df_raw = pd.read_sql_query(query, conn)
    conn.close()
    print(f"Loaded {len(df_raw)} total eligible properties from {DB_PATH}")

    # Outlier filter
    df_raw = df_raw[df_raw['area_sqft'] >= 300].copy()
    df_raw = df_raw[df_raw['bhk'] >= 1].copy()
    df_raw['price_per_sqft'] = df_raw['price'] / df_raw['area_sqft']
    df_raw = df_raw[(df_raw['price_per_sqft'] >= 1500) & (df_raw['price_per_sqft'] <= 60000)].copy()

    # Stratified or balanced sampling across localities
    sample_size = min(args.sample_size, len(df_raw))
    print(f"Selecting balanced subset of {sample_size} properties across localities...")
    top_localities = df_raw['locality'].value_counts().head(30).index.tolist()
    sampled_dfs = []
    per_loc = max(10, sample_size // len(top_localities))
    for loc in top_localities:
        sub = df_raw[df_raw['locality'] == loc]
        if len(sub) > 0:
            sampled_dfs.append(sub.sample(n=min(len(sub), per_loc), random_state=42))
    
    df_sample = pd.concat(sampled_dfs).drop_duplicates(subset=['id'])
    if len(df_sample) < sample_size:
        remaining_needed = sample_size - len(df_sample)
        remaining_pool = df_raw[~df_raw['id'].isin(df_sample['id'])]
        if len(remaining_pool) > 0:
            df_sample = pd.concat([df_sample, remaining_pool.sample(n=min(len(remaining_pool), remaining_needed), random_state=42)])

    df = df_sample.reset_index(drop=True)
    print(f"Final training sample: {len(df)} properties across {df['locality'].nunique()} localities.")

    # Calculate locality rate mapping
    locality_medians = df.groupby('locality')['price_per_sqft'].median().to_dict()
    locality_map = {loc: float(val) for loc, val in locality_medians.items()}
    locality_map["Other"] = float(df['price_per_sqft'].median())

    # 2. Extract Geospatial features (with caching & live-geo option)
    print("\n[Step 2/6] Processing Geospatial features (Geoapify POIs)...")
    geo_cache = load_geo_cache()
    live_queries_run = 0

    async def fetch_missing_geo(lat, lon):
        nonlocal live_queries_run
        coord_key = f"{lat:.4f},{lon:.4f}"
        if coord_key in geo_cache:
            return geo_cache[coord_key]
        if args.live_geo and live_queries_run < 40:
            try:
                places = await GeoapifyService.get_nearby_places(lat=lat, lon=lon, radius_meters=3000)
                if places:
                    geo_cache[coord_key] = places
                    live_queries_run += 1
                    await asyncio.sleep(0.1)
                    return places
            except Exception as e:
                print(f"Live Geoapify fetch warning for {lat}, {lon}: {e}")
        return []

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    all_geo_places = []
    for idx, row in df.iterrows():
        places = []
        if row['nearby_places']:
            try:
                places = json.loads(row['nearby_places']) if isinstance(row['nearby_places'], str) else row['nearby_places']
            except Exception:
                places = []

        if not places and row['latitude'] and row['longitude']:
            coord_key = f"{row['latitude']:.4f},{row['longitude']:.4f}"
            if coord_key in geo_cache:
                places = geo_cache[coord_key]
            elif args.live_geo:
                places = loop.run_until_complete(fetch_missing_geo(row['latitude'], row['longitude']))

        all_geo_places.append(places)

    save_geo_cache(geo_cache)
    print(f"Geospatial feature caching complete (Live queries made: {live_queries_run}, Cache size: {len(geo_cache)})")

    # 3. Extract ResNet-18 Image features with local caching
    print("\n[Step 3/6] Extracting 512-dimensional CNN visual embeddings using PyTorch ResNet-18...")
    img_vectors = []
    cached_hits = 0
    extracted_now = 0

    for idx, row in df.iterrows():
        # Select first valid image path
        img_src = None
        if row['images']:
            try:
                raw_imgs = json.loads(row['images']) if isinstance(row['images'], str) else row['images']
                if isinstance(raw_imgs, list) and len(raw_imgs) > 0:
                    img_src = raw_imgs[0]
            except Exception:
                img_src = None

        if img_src:
            cache_file = get_image_cache_path(img_src)
            if os.path.exists(cache_file):
                try:
                    vec = np.load(cache_file)
                    if len(vec) == 512:
                        img_vectors.append(vec)
                        cached_hits += 1
                        continue
                except Exception:
                    pass

            # Extract via ResNet-18
            vec = ImageAIService.extract_image_embedding(img_src, base_dir=BASE_DIR)
            if len(vec) == 512:
                np.save(cache_file, vec)
                extracted_now += 1
            img_vectors.append(vec)
        else:
            img_vectors.append(np.zeros(512, dtype=np.float32))

    X_img = np.array(img_vectors, dtype=np.float32)
    print(f"ResNet-18 image extraction complete: {len(X_img)} embeddings (Cache hits: {cached_hits}, Extracted: {extracted_now})")
    print(f"ResNet-18 matrix shape: {X_img.shape} (Expected: (N, 512))")

    # 4. Extract Structured, Geospatial, and TF-IDF Text matrices
    print("\n[Step 4/6] Assembling Structured, Geospatial, and TF-IDF feature matrices...")
    struct_list = []
    for idx, row in df.iterrows():
        loc_val = locality_map.get(row['locality'], locality_map.get("Other", 5000.0))
        struct_list.append([
            float(row['area_sqft']),
            float(row['bhk'] or 2),
            float(row['bathrooms'] or 2),
            float(row['balconies'] or 1),
            loc_val,
            float(row['property_age'] if str(row['property_age']).replace('.','',1).isdigit() else 5.0)
        ])
    X_struct = np.array(struct_list, dtype=np.float32)

    geo_list = []
    for places in all_geo_places:
        geo_list.append(MultimodalModelService.extract_geoapify_vector(places))
    X_geo = np.array(geo_list, dtype=np.float32)

    tfidf_list = []
    for desc in df['description']:
        tfidf_list.append(TextAIService.extract_text_feature_vector(str(desc or ""), n_features=16))
    X_text = np.array(tfidf_list, dtype=np.float32)

    # Full Fused Feature Matrix
    X_fused = np.concatenate([X_struct, X_geo, X_text, X_img], axis=1).astype(np.float32)
    y = df['price'].values.astype(np.float32)

    print(f"  - Structured feature dimensions : {X_struct.shape[1]}")
    print(f"  - Geoapify feature dimensions  : {X_geo.shape[1]}")
    print(f"  - TF-IDF feature dimensions     : {X_text.shape[1]}")
    print(f"  - ResNet-18 CNN dimensions      : {X_img.shape[1]}")
    print(f"  - TOTAL FUSED VECTOR DIMENSIONS : {X_fused.shape[1]} (Shape: {X_fused.shape})")

    # 5. Ablation Study Comparison
    print("\n[Step 5/6] Executing Multimodal Ablation Study...")
    indices = np.arange(len(df))
    train_idx, test_idx = train_test_split(indices, test_size=0.2, random_state=42)

    y_train, y_test = y[train_idx], y[test_idx]

    ablation_results = {}

    def evaluate_stage(name: str, X_feat: np.ndarray):
        X_tr, X_te = X_feat[train_idx], X_feat[test_idx]
        reg = XGBRegressor(
            n_estimators=350,
            learning_rate=0.04,
            max_depth=6,
            subsample=0.85,
            colsample_bytree=0.8,
            random_state=42,
            n_jobs=-1
        )
        reg.fit(X_tr, y_train)
        preds = reg.predict(X_te)
        mae = float(mean_absolute_error(y_test, preds))
        rmse = float(np.sqrt(mean_squared_error(y_test, preds)))
        r2 = float(r2_score(y_test, preds))
        mape = float(np.mean(np.abs((y_test - preds) / np.maximum(y_test, 1.0))) * 100.0)
        return reg, {
            "features": X_feat.shape[1],
            "mae_inr": round(mae, 2),
            "mae_lakhs": round(mae / 100000.0, 2),
            "rmse_inr": round(rmse, 2),
            "rmse_lakhs": round(rmse / 100000.0, 2),
            "r2_score": round(r2, 4),
            "mape_percent": round(mape, 2)
        }

    # Model 1: Structured only
    _, ablation_results["Stage 1: Structured Only"] = evaluate_stage(
        "Structured Only", X_struct
    )

    # Model 2: Structured + Geoapify
    X_s_g = np.concatenate([X_struct, X_geo], axis=1)
    _, ablation_results["Stage 2: Structured + Geoapify"] = evaluate_stage(
        "Structured + Geoapify", X_s_g
    )

    # Model 3: Structured + Geoapify + TF-IDF
    X_s_g_t = np.concatenate([X_struct, X_geo, X_text], axis=1)
    _, ablation_results["Stage 3: Structured + Geoapify + TF-IDF"] = evaluate_stage(
        "Structured + Geoapify + TF-IDF", X_s_g_t
    )

    # Model 4: Full Multimodal with ResNet-18 (512-dim CNN)
    final_model, ablation_results["Stage 4: Full Multimodal (ResNet-18 + TF-IDF + Geo + Struct)"] = evaluate_stage(
        "Full Multimodal", X_fused
    )

    print("\n" + "=" * 90)
    print("MULTIMODAL ABLATION STUDY RESULTS")
    print("=" * 90)
    print(f"{'Stage Name':<52} | {'Features':<8} | {'MAE (Lakhs)':<12} | {'RMSE (Lakhs)':<12} | {'R² Score':<8}")
    print("-" * 90)
    for stage, res in ablation_results.items():
        print(f"{stage:<52} | {res['features']:<8} | {res['mae_lakhs']:<12} | {res['rmse_lakhs']:<12} | {res['r2_score']:<8}")
    print("=" * 90)

    # 6. Save Model and Metadata
    print("\n[Step 6/6] Saving trained Multimodal XGBoost model and metadata...")
    joblib.dump(final_model, MODEL_OUTPUT_PATH)
    print(f"  [SAVED] Multimodal XGBoost model -> {MODEL_OUTPUT_PATH}")

    meta = {
        "model_version": "2.0.0-multimodal-resnet18-xgboost",
        "training_datetime": datetime.now(timezone.utc).isoformat(),
        "total_properties_trained": len(df),
        "fused_feature_dimension": X_fused.shape[1],
        "feature_breakdown": {
            "structured_features": len(STRUCTURED_FEATURE_NAMES),
            "geoapify_features": len(GEO_FEATURE_NAMES),
            "tfidf_features": len(TFIDF_FEATURE_NAMES),
            "resnet18_image_features": len(IMAGE_FEATURE_NAMES),
            "total_fused_features": len(ALL_FEATURE_NAMES)
        },
        "all_feature_names": ALL_FEATURE_NAMES,
        "locality_map": locality_map,
        "ablation_results": ablation_results,
        "final_metrics": ablation_results["Stage 4: Full Multimodal (ResNet-18 + TF-IDF + Geo + Struct)"]
    }

    with open(META_OUTPUT_PATH, "w") as f:
        json.dump(meta, f, indent=2)
    print(f"  [SAVED] Multimodal Model Metadata -> {META_OUTPUT_PATH}")
    print("\nTRAINING COMPLETE SUCCESSFULLY!")


if __name__ == "__main__":
    main()
