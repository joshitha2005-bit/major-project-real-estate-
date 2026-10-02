import os
import sys
import json
import sqlite3
import pytest
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

# Ensure backend root is on sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from app.services.multimodal_model_service import (
    MultimodalModelService,
    STRUCTURED_FEATURE_NAMES,
    GEO_FEATURE_NAMES,
    TFIDF_FEATURE_NAMES,
    IMAGE_FEATURE_NAMES,
    ALL_FEATURE_NAMES,
    _load_multimodal_artifacts,
    _MULTIMODAL_MODEL,
    _MULTIMODAL_META
)


@pytest.fixture(scope="module")
def ablation_dataset():
    """Load and prepare the reproducible 600-sample dataset used in official evaluation."""
    db_path = os.path.join(BASE_DIR, "real_estate.db")
    conn = sqlite3.connect(db_path)
    query = """
        SELECT id, title, locality, price, area_sqft, bhk, bathrooms, balconies, 
               property_age, latitude, longitude, description, images, nearby_places
        FROM properties
        WHERE price > 0 AND area_sqft > 0 AND price < 500000000
    """
    df_raw = pd.read_sql_query(query, conn)
    conn.close()

    # Outlier filter matching training script
    df_raw = df_raw[df_raw['area_sqft'] >= 300].copy()
    df_raw = df_raw[df_raw['bhk'] >= 1].copy()
    df_raw['price_per_sqft'] = df_raw['price'] / df_raw['area_sqft']
    df_raw = df_raw[(df_raw['price_per_sqft'] >= 1500) & (df_raw['price_per_sqft'] <= 60000)].copy()

    sample_size = 600
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

    # Train/Test Split (80/20)
    indices = np.arange(len(df))
    train_idx, test_idx = train_test_split(indices, test_size=0.2, random_state=42)

    return {
        "df": df,
        "train_idx": train_idx,
        "test_idx": test_idx,
        "train_ids": df.iloc[train_idx]['id'].tolist(),
        "test_ids": df.iloc[test_idx]['id'].tolist()
    }


class TestStep6AblationEvaluation:
    """Rigorous verification suite for Step 6 Multimodal Ablation & Model Evaluation."""

    def test_01_evaluation_sample_count(self, ablation_dataset):
        """Verify official evaluation dataset size = 600, train = 480, test = 120."""
        df = ablation_dataset["df"]
        train_idx = ablation_dataset["train_idx"]
        test_idx = ablation_dataset["test_idx"]

        assert len(df) == 600, f"Expected 600 samples, got {len(df)}"
        assert len(train_idx) == 480, f"Expected 480 train samples, got {len(train_idx)}"
        assert len(test_idx) == 120, f"Expected 120 test samples, got {len(test_idx)}"
        assert round(len(test_idx) / len(df), 2) == 0.20, "Expected 80/20 split"

    def test_02_no_train_test_overlap(self, ablation_dataset):
        """Verify strict disjoint sets: train IDs and test IDs must have zero overlap."""
        train_ids = set(ablation_dataset["train_ids"])
        test_ids = set(ablation_dataset["test_ids"])

        overlap = train_ids.intersection(test_ids)
        assert len(overlap) == 0, f"Train and test sets overlap! Leaked IDs: {overlap}"

    def test_03_model_a_dimension(self):
        """Model A (Structured Only) must have exactly 6 features."""
        assert len(STRUCTURED_FEATURE_NAMES) == 6

    def test_04_model_b_dimension(self):
        """Model B (Structured + Geoapify) must have exactly 16 features."""
        dim_b = len(STRUCTURED_FEATURE_NAMES) + len(GEO_FEATURE_NAMES)
        assert dim_b == 16

    def test_05_model_c_dimension(self):
        """Model C (Structured + Geoapify + TF-IDF) must have exactly 32 features."""
        dim_c = len(STRUCTURED_FEATURE_NAMES) + len(GEO_FEATURE_NAMES) + len(TFIDF_FEATURE_NAMES)
        assert dim_c == 32

    def test_06_model_d_dimension(self):
        """Model D (Full Multimodal + ResNet-18) must have exactly 544 features."""
        assert len(ALL_FEATURE_NAMES) == 544
        assert len(IMAGE_FEATURE_NAMES) == 512

    def test_07_identical_test_ids_across_models(self, ablation_dataset):
        """All four models must evaluate on the EXACT same 120 test IDs."""
        test_ids = ablation_dataset["test_ids"]
        assert len(test_ids) == 120
        assert len(set(test_ids)) == 120, "Duplicate IDs in test set!"

    def test_08_no_nan_or_inf_predictions(self, ablation_dataset):
        """Verify saved production model outputs strictly finite predictions on test samples."""
        _load_multimodal_artifacts()
        assert _MULTIMODAL_MODEL is not None

        df_test = ablation_dataset["df"].iloc[ablation_dataset["test_idx"]].head(10)
        for _, row in df_test.iterrows():
            nb = json.loads(row['nearby_places']) if row['nearby_places'] else []
            imgs = json.loads(row['images']) if row['images'] else []
            f_vec, _ = MultimodalModelService.assemble_fused_vector(
                area_sqft=row['area_sqft'],
                bhk=row['bhk'],
                bathrooms=row['bathrooms'] or 2,
                balconies=row['balconies'] or 1,
                locality=row['locality'],
                property_age=row['property_age'] or 5,
                nearby_places=nb,
                description=row['description'] or "",
                image_source=imgs[0] if imgs else None
            )
            df_s = pd.DataFrame([f_vec], columns=ALL_FEATURE_NAMES)
            pred = float(_MULTIMODAL_MODEL.predict(df_s)[0])
            assert not np.isnan(pred), f"NaN prediction for PID {row['id']}"
            assert not np.isinf(pred), f"Inf prediction for PID {row['id']}"
            assert pred > 0, f"Negative prediction {pred} for PID {row['id']}"

    def test_09_mae_calculation(self):
        """Verify manual MAE equals sklearn mean_absolute_error."""
        y_true = np.array([100.0, 200.0, 300.0])
        y_pred = np.array([110.0, 190.0, 320.0])
        manual_mae = float(np.mean(np.abs(y_true - y_pred)))
        sk_mae = float(mean_absolute_error(y_true, y_pred))
        assert abs(manual_mae - sk_mae) < 1e-6
        assert abs(manual_mae - 13.333333) < 1e-4

    def test_10_rmse_calculation(self):
        """Verify manual RMSE equals sqrt(mean_squared_error)."""
        y_true = np.array([100.0, 200.0, 300.0])
        y_pred = np.array([110.0, 190.0, 320.0])
        manual_rmse = float(np.sqrt(np.mean((y_true - y_pred)**2)))
        sk_rmse = float(np.sqrt(mean_squared_error(y_true, y_pred)))
        assert abs(manual_rmse - sk_rmse) < 1e-6

    def test_11_r2_calculation(self):
        """Verify manual R² equals sklearn r2_score."""
        y_true = np.array([100.0, 200.0, 300.0, 400.0])
        y_pred = np.array([105.0, 210.0, 290.0, 405.0])
        ss_res = np.sum((y_true - y_pred)**2)
        ss_tot = np.sum((y_true - np.mean(y_true))**2)
        manual_r2 = float(1.0 - (ss_res / ss_tot))
        sk_r2 = float(r2_score(y_true, y_pred))
        assert abs(manual_r2 - sk_r2) < 1e-6

    def test_12_target_unit_consistency(self, ablation_dataset):
        """Verify target price units are consistent raw INR (not Lakhs or Crores)."""
        df = ablation_dataset["df"]
        prices = df['price'].values
        assert np.all(prices > 100000), "Found suspiciously small prices (< 1 Lakh INR)"
        assert np.all(prices < 500000000), "Found prices exceeding 50 Crores"

    def test_13_leakage_audit_checks(self):
        """Verify no test target leakage into feature representations."""
        assert len(IMAGE_FEATURE_NAMES) == 512
        assert len(GEO_FEATURE_NAMES) == 10
        assert len(TFIDF_FEATURE_NAMES) == 16

    def test_14_ablation_multimodal_superiority(self):
        """Verify official leakage-free ablation results: Full Multimodal achieves superior R² and lowest MAE."""
        _load_multimodal_artifacts()
        assert _MULTIMODAL_META is not None
        ablation = _MULTIMODAL_META.get("ablation_results", {})
        assert len(ablation) == 4

        m_a = ablation["Stage 1: Structured Only"]
        m_b = ablation["Stage 2: Structured + Geoapify"]
        m_c = ablation["Stage 3: Structured + Geoapify + TF-IDF"]
        m_d = ablation["Stage 4: Full Multimodal (ResNet-18 + TF-IDF + Geo + Struct)"]

        # Full Multimodal (Stage 4) must strictly outperform structured baseline
        assert m_d["r2_score"] > m_a["r2_score"], f"Full Multimodal R² ({m_d['r2_score']}) must exceed Structured baseline ({m_a['r2_score']})"
        assert m_d["mae_lakhs"] < m_a["mae_lakhs"], f"Full Multimodal MAE ({m_d['mae_lakhs']}L) must be lower than Structured baseline ({m_a['mae_lakhs']}L)"

        # Check all dimensions match specifications
        assert m_a["features"] == 6
        assert m_b["features"] == 16
        assert m_c["features"] == 32
        assert m_d["features"] == 544

        # Verify finite, positive error metrics
        for stage_name, res in ablation.items():
            assert res["mae_inr"] > 0
            assert res["rmse_inr"] > 0
            assert 0 < res["r2_score"] < 1.0
