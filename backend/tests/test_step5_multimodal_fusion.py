import pytest
import sqlite3
import json
import numpy as np
import pandas as pd
import os
import joblib

from app.services.multimodal_model_service import (
    MultimodalModelService,
    ALL_FEATURE_NAMES,
    STRUCTURED_FEATURE_NAMES,
    GEO_FEATURE_NAMES,
    TFIDF_FEATURE_NAMES,
    IMAGE_FEATURE_NAMES,
    _load_multimodal_artifacts,
    _MULTIMODAL_MODEL,
    _SHAP_EXPLAINER
)
from app.services.image_ai_service import ImageAIService

@pytest.fixture(scope="module")
def multimodal_artifacts():
    _load_multimodal_artifacts()
    assert _MULTIMODAL_MODEL is not None
    assert _SHAP_EXPLAINER is not None
    return _MULTIMODAL_MODEL, _SHAP_EXPLAINER

@pytest.fixture(scope="module")
def sample_property():
    conn = sqlite3.connect('real_estate.db')
    c = conn.cursor()
    c.execute("""
        SELECT id, locality, area_sqft, bhk, bathrooms, balconies, property_age,
               nearby_places, description, images, price, image_provenance
        FROM properties
        WHERE is_main_ai_ready = 1 AND image_count >= 2
        LIMIT 1
    """)
    row = c.fetchone()
    conn.close()
    assert row is not None, "At least one MAIN_AI_READY property with images must exist"
    return {
        "id": row[0],
        "locality": row[1],
        "area_sqft": row[2],
        "bhk": row[3],
        "bathrooms": row[4] or 2,
        "balconies": row[5] or 1,
        "property_age": row[6] or 5,
        "nearby_places": json.loads(row[7]) if row[7] else [],
        "description": row[8] or "",
        "images": json.loads(row[9]) if row[9] else [],
        "price": row[10],
        "image_provenance": row[11]
    }

class TestStep5MultimodalFusion:

    def test_01_structured_dimension(self, sample_property):
        """1. structured dimension = 6"""
        struct_vec = MultimodalModelService.extract_structured_vector(
            sample_property["area_sqft"],
            sample_property["bhk"],
            sample_property["bathrooms"],
            sample_property["balconies"],
            sample_property["locality"],
            sample_property["property_age"]
        )
        assert isinstance(struct_vec, np.ndarray)
        assert struct_vec.shape == (6,)
        assert len(struct_vec) == 6

    def test_02_geoapify_dimension(self, sample_property):
        """2. Geo dimension = 10"""
        geo_vec = MultimodalModelService.extract_geoapify_vector(sample_property["nearby_places"])
        assert isinstance(geo_vec, np.ndarray)
        assert geo_vec.shape == (10,)
        assert len(geo_vec) == 10

    def test_03_tfidf_dimension(self, sample_property):
        """3. TF-IDF dimension = 16"""
        tfidf_vec = MultimodalModelService.extract_tfidf_vector(sample_property["description"])
        assert isinstance(tfidf_vec, np.ndarray)
        assert tfidf_vec.shape == (16,)
        assert len(tfidf_vec) == 16

    def test_04_cnn_dimension(self, sample_property):
        """4. CNN dimension = 512"""
        cnn_vec = MultimodalModelService.extract_image_vector(sample_property["images"][:3])
        assert isinstance(cnn_vec, np.ndarray)
        assert cnn_vec.shape == (512,)
        assert len(cnn_vec) == 512

    def test_05_fused_dimension(self, sample_property):
        """5. fused dimension = 544"""
        fused_vec, breakdown = MultimodalModelService.assemble_fused_vector(
            area_sqft=sample_property["area_sqft"],
            bhk=sample_property["bhk"],
            bathrooms=sample_property["bathrooms"],
            balconies=sample_property["balconies"],
            locality=sample_property["locality"],
            property_age=sample_property["property_age"],
            nearby_places=sample_property["nearby_places"],
            description=sample_property["description"],
            image_source=sample_property["images"][:3]
        )
        assert isinstance(fused_vec, np.ndarray)
        assert fused_vec.shape == (544,)
        assert len(fused_vec) == 544
        assert breakdown["total_fused_dimensions"] == 544

    def test_06_structured_fusion_slice(self, sample_property):
        """6. structured fusion slice [0:6]"""
        struct_vec = MultimodalModelService.extract_structured_vector(
            sample_property["area_sqft"], sample_property["bhk"],
            sample_property["bathrooms"], sample_property["balconies"],
            sample_property["locality"], sample_property["property_age"]
        )
        fused_vec, _ = MultimodalModelService.assemble_fused_vector(
            area_sqft=sample_property["area_sqft"], bhk=sample_property["bhk"],
            bathrooms=sample_property["bathrooms"], balconies=sample_property["balconies"],
            locality=sample_property["locality"], property_age=sample_property["property_age"],
            nearby_places=sample_property["nearby_places"], description=sample_property["description"],
            image_source=sample_property["images"][:3]
        )
        assert np.allclose(fused_vec[0:6], struct_vec, atol=1e-6)

    def test_07_geo_fusion_slice(self, sample_property):
        """7. Geo fusion slice [6:16]"""
        geo_vec = MultimodalModelService.extract_geoapify_vector(sample_property["nearby_places"])
        fused_vec, _ = MultimodalModelService.assemble_fused_vector(
            area_sqft=sample_property["area_sqft"], bhk=sample_property["bhk"],
            bathrooms=sample_property["bathrooms"], balconies=sample_property["balconies"],
            locality=sample_property["locality"], property_age=sample_property["property_age"],
            nearby_places=sample_property["nearby_places"], description=sample_property["description"],
            image_source=sample_property["images"][:3]
        )
        assert np.allclose(fused_vec[6:16], geo_vec, atol=1e-6)

    def test_08_tfidf_fusion_slice(self, sample_property):
        """8. TF-IDF fusion slice [16:32]"""
        tfidf_vec = MultimodalModelService.extract_tfidf_vector(sample_property["description"])
        fused_vec, _ = MultimodalModelService.assemble_fused_vector(
            area_sqft=sample_property["area_sqft"], bhk=sample_property["bhk"],
            bathrooms=sample_property["bathrooms"], balconies=sample_property["balconies"],
            locality=sample_property["locality"], property_age=sample_property["property_age"],
            nearby_places=sample_property["nearby_places"], description=sample_property["description"],
            image_source=sample_property["images"][:3]
        )
        assert np.allclose(fused_vec[16:32], tfidf_vec, atol=1e-6)

    def test_09_cnn_fusion_slice(self, sample_property):
        """9. CNN fusion slice [32:544]"""
        cnn_vec = MultimodalModelService.extract_image_vector(sample_property["images"][:3])
        fused_vec, _ = MultimodalModelService.assemble_fused_vector(
            area_sqft=sample_property["area_sqft"], bhk=sample_property["bhk"],
            bathrooms=sample_property["bathrooms"], balconies=sample_property["balconies"],
            locality=sample_property["locality"], property_age=sample_property["property_age"],
            nearby_places=sample_property["nearby_places"], description=sample_property["description"],
            image_source=sample_property["images"][:3]
        )
        assert np.allclose(fused_vec[32:544], cnn_vec, atol=1e-6)

    def test_10_xgboost_input_dimension(self, sample_property, multimodal_artifacts):
        """10. XGBoost input dimension = (1, 544)"""
        model, _ = multimodal_artifacts
        fused_vec, _ = MultimodalModelService.assemble_fused_vector(
            area_sqft=sample_property["area_sqft"], bhk=sample_property["bhk"],
            bathrooms=sample_property["bathrooms"], balconies=sample_property["balconies"],
            locality=sample_property["locality"], property_age=sample_property["property_age"],
            nearby_places=sample_property["nearby_places"], description=sample_property["description"],
            image_source=sample_property["images"][:3]
        )
        X_df = pd.DataFrame([fused_vec], columns=ALL_FEATURE_NAMES)
        assert X_df.shape == (1, 544)
        pred = model.predict(X_df)
        assert len(pred) == 1
        assert pred[0] > 0

    def test_11_shap_input_dimension(self, sample_property, multimodal_artifacts):
        """11. SHAP input dimension = (1, 544)"""
        _, explainer = multimodal_artifacts
        fused_vec, _ = MultimodalModelService.assemble_fused_vector(
            area_sqft=sample_property["area_sqft"], bhk=sample_property["bhk"],
            bathrooms=sample_property["bathrooms"], balconies=sample_property["balconies"],
            locality=sample_property["locality"], property_age=sample_property["property_age"],
            nearby_places=sample_property["nearby_places"], description=sample_property["description"],
            image_source=sample_property["images"][:3]
        )
        X_df = pd.DataFrame([fused_vec], columns=ALL_FEATURE_NAMES)
        shap_vals = explainer.shap_values(X_df)
        if isinstance(shap_vals, list):
            shap_vals = shap_vals[0]
        vals = np.array(shap_vals[0], dtype=float)
        assert vals.shape == (544,)
        visual_shap_sum = float(np.sum(np.abs(vals[32:544])))
        assert visual_shap_sum > 0.0

    def test_12_cnn_to_model_sensitivity(self, sample_property, multimodal_artifacts):
        """12. CNN-to-model sensitivity"""
        model, _ = multimodal_artifacts
        fused_A, _ = MultimodalModelService.assemble_fused_vector(
            area_sqft=sample_property["area_sqft"], bhk=sample_property["bhk"],
            bathrooms=sample_property["bathrooms"], balconies=sample_property["balconies"],
            locality=sample_property["locality"], property_age=sample_property["property_age"],
            nearby_places=sample_property["nearby_places"], description=sample_property["description"],
            image_source=sample_property["images"][:3]
        )
        fused_B = np.copy(fused_A)
        fused_B[32:544] = 0.0  # Zero CNN region
        
        df_A = pd.DataFrame([fused_A], columns=ALL_FEATURE_NAMES)
        df_B = pd.DataFrame([fused_B], columns=ALL_FEATURE_NAMES)
        
        pred_A = float(model.predict(df_A)[0])
        pred_B = float(model.predict(df_B)[0])
        
        assert pred_A != pred_B, "Changing CNN features MUST change XGBoost prediction"
        diff = abs(pred_A - pred_B)
        assert diff > 100.0, f"CNN feature change impact {diff} too small"

    def test_13_no_nan_or_inf(self, sample_property):
        """13. No NaN / Inf in fused vector"""
        fused_vec, _ = MultimodalModelService.assemble_fused_vector(
            area_sqft=sample_property["area_sqft"], bhk=sample_property["bhk"],
            bathrooms=sample_property["bathrooms"], balconies=sample_property["balconies"],
            locality=sample_property["locality"], property_age=sample_property["property_age"],
            nearby_places=sample_property["nearby_places"], description=sample_property["description"],
            image_source=sample_property["images"][:3]
        )
        assert not np.isnan(fused_vec).any()
        assert not np.isinf(fused_vec).any()

    def test_14_genuine_image_provenance(self, sample_property):
        """14. Genuine image provenance classification"""
        assert sample_property["image_provenance"] == "PROPERTY_SPECIFIC"
        for img in sample_property["images"]:
            assert "nobroker.in" in img

    def test_15_main_endpoint_uses_multimodal_model(self):
        """15. Main endpoint uses multimodal 544-D model"""
        from app.api.v1.ai import analyze_property_full_ai
        import inspect
        source = inspect.getsource(analyze_property_full_ai)
        assert "MultimodalModelService.predict_property" in source
        assert "544" in source or "fused_feature_dimension" in source

    def test_16_frontend_uses_main_multimodal_endpoint(self):
        """16. Frontend uses main multimodal endpoint"""
        fe_service = "frontend/src/services/aiService.js"
        if not os.path.exists(fe_service):
            fe_service = "c:/major real estate/frontend/src/services/aiService.js"
        with open(fe_service, "r", encoding="utf-8") as f:
            code = f.read()
        assert "/ai/analyze-property" in code
