import pytest
import numpy as np
import os
import joblib
import shap
from app.services.text_ai_service import TextAIService
from app.services.multimodal_model_service import MultimodalModelService, ALL_FEATURE_NAMES, TFIDF_FEATURE_NAMES
from app.core.database import SessionLocal
from app.models.property import Property

@pytest.fixture(scope="module")
def multimodal_model():
    model_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "models", "multimodal_xgboost.joblib")
    return joblib.load(model_path)

def test_tfidf_vectorizer_artifact_loaded():
    vec = TextAIService._get_vectorizer()
    assert vec is not None
    assert len(vec.vocabulary_) == 125
    assert vec.max_features == 1000
    assert vec.ngram_range == (1, 2)

def test_nlp_preprocessing():
    raw_text = "  Luxury  3 BHK Flat, with 24/7 Security & Power-Backup!  "
    preprocessed = TextAIService._preprocess_text(raw_text)
    assert preprocessed == "luxury 3 bhk flat with 24 7 security power backup"

def test_tfidf_16d_dimension_and_bounds():
    desc = "3 BHK Penthouse for sale in Koramangala with 24 security and covered parking amenities"
    vec = TextAIService.extract_text_feature_vector(desc, n_features=16)
    assert isinstance(vec, np.ndarray)
    assert vec.shape == (16,)
    assert vec.dtype == np.float32
    assert np.all(vec >= 0.0)
    assert np.count_nonzero(vec) > 0

def test_tfidf_text_sensitivity():
    desc_a = "2 BHK Apartment in Koramangala"
    desc_b = "3 BHK Penthouse with 24 security power backup covered parking amenities in Koramangala"
    vec_a = TextAIService.extract_text_feature_vector(desc_a, n_features=16)
    vec_b = TextAIService.extract_text_feature_vector(desc_b, n_features=16)
    l2_dist = float(np.linalg.norm(vec_a - vec_b))
    assert l2_dist > 0.0

def test_multimodal_544d_fusion_slice():
    db = SessionLocal()
    try:
        prop = db.query(Property).filter(Property.source_type == "source_portal").first()
        assert prop is not None
        assert prop.description is not None
        
        tfidf_vec = TextAIService.extract_text_feature_vector(prop.description, n_features=16)
        assert len(tfidf_vec) == 16
        
        struct_vec = np.zeros(6, dtype=np.float32)
        geo_vec = np.zeros(10, dtype=np.float32)
        cnn_vec = np.zeros(512, dtype=np.float32)
        
        fused_vec = np.concatenate([struct_vec, geo_vec, tfidf_vec, cnn_vec])
        assert len(fused_vec) == 544
        assert np.allclose(fused_vec[16:32], tfidf_vec)
    finally:
        db.close()

def test_xgboost_and_shap_tfidf_integration(multimodal_model):
    db = SessionLocal()
    try:
        prop = db.query(Property).filter(Property.source_type == "source_portal").first()
        assert prop is not None
        
        tfidf_vec = TextAIService.extract_text_feature_vector(prop.description, n_features=16)
        struct_vec = MultimodalModelService.extract_structured_vector(
            area_sqft=prop.area_sqft or 1200.0,
            bhk=prop.bhk or 2,
            bathrooms=prop.bathrooms or 2,
            balconies=prop.balconies or 1,
            locality=prop.locality or "Koramangala",
            property_age=5
        )
        geo_vec = np.zeros(10, dtype=np.float32)
        cnn_vec = np.zeros(512, dtype=np.float32)
        
        fused_vec = np.concatenate([struct_vec, geo_vec, tfidf_vec, cnn_vec]).astype(np.float32)
        assert len(fused_vec) == 544
        
        # XGBoost prediction
        pred_price = float(multimodal_model.predict(fused_vec.reshape(1, -1))[0])
        assert pred_price > 0.0
        
        # SHAP calculation
        explainer = shap.TreeExplainer(multimodal_model)
        shap_vals = explainer.shap_values(fused_vec.reshape(1, -1))[0]
        assert len(shap_vals) == 544
        
        # Verify TF-IDF slice in SHAP
        tfidf_shap = shap_vals[16:32]
        assert len(tfidf_shap) == 16
        assert len(TFIDF_FEATURE_NAMES) == 16
    finally:
        db.close()
