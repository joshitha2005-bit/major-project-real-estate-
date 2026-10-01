import os
import sys
import unittest
import asyncio
import numpy as np

# Add backend directory to sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from app.services.text_ai_service import TextAIService
from app.services.image_ai_service import ImageAIService
from app.services.image_provenance import ImageProvenanceService
from app.services.geoapify_service import GeoapifyService
from app.services.price_prediction_service import PricePredictionService
from app.services.listing_service import ListingService
from app.models.property import Property


class TestObjective2MultimodalPipeline(unittest.TestCase):
    """
    Empirical Test Suite for Objective 2:
    'Use advanced features such as image analysis, text processing and location data
    for real-estate intelligence.'
    """

    @classmethod
    def setUpClass(cls):
        # Representative test property in Koramangala
        cls.test_prop_structured = {
            "id": 1,
            "title": "Sobha Koramangala 2BHK Apartment",
            "locality": "Koramangala",
            "property_type": "Apartment",
            "bhk": 2,
            "area_sqft": 1200.0,
            "price_inr": 15000000.0,
            "latitude": 12.9342,
            "longitude": 77.6235,
            "address": "80 Feet Road, 4th Block, Koramangala, Bengaluru, Karnataka",
            "source": "Bengaluru_House_Data.csv",
            "source_type": "HISTORICAL_MARKET_DATA"
        }

        # Authentic listing description for text testing
        cls.sample_description = (
            "Spacious and premium 2 BHK apartment in prime Koramangala built by Sobha. "
            "Features modern interior woodwork, modular kitchen, 24/7 security, power backup, "
            "covered parking, and close access to schools, hospitals, and Metro connectivity."
        )

        # Legitimate verified image asset
        cls.valid_image_path = os.path.join(BASE_DIR, "static", "images", "apartment_1.jpg")

    # -------------------------------------------------------------
    # 1. Structured Property Data Validation
    # -------------------------------------------------------------
    def test_01_structured_property_data_reaches_pipeline(self):
        """Verify structured property data reaches pipeline and strictly calculates price/sqft."""
        prop = self.test_prop_structured
        price_per_sqft = ListingService.calculate_price_per_sqft(prop["price_inr"], prop["area_sqft"])
        self.assertEqual(price_per_sqft, 12500.0)
        self.assertGreater(prop["bhk"], 0)
        self.assertGreater(prop["area_sqft"], 0)
        self.assertGreater(prop["price_inr"], 0)
        self.assertTrue(bool(prop["locality"]))

    # -------------------------------------------------------------
    # 2. Text Processing via TF-IDF Vectorizer
    # -------------------------------------------------------------
    def test_02_tfidf_processes_actual_description(self):
        """Verify TF-IDF extracts key terms and weights from genuine descriptions and handles missing text."""
        # A: Real description path
        nlp_out = TextAIService.analyze_description(self.sample_description)
        self.assertTrue(nlp_out.get("text_available"))
        self.assertEqual(nlp_out.get("status"), "TEXT DATA AVAILABLE")
        self.assertGreater(nlp_out["word_count"], 15)
        self.assertIsInstance(nlp_out["top_tfidf_terms"], list)
        self.assertGreater(len(nlp_out["top_tfidf_terms"]), 0)
        for term_item in nlp_out["top_tfidf_terms"]:
            self.assertIn("term", term_item)
            self.assertIn("weight", term_item)
            self.assertGreater(term_item["weight"], 0.0)

        # B: Missing description path -> Must truthfully return TEXT DATA UNAVAILABLE
        empty_out = TextAIService.analyze_description("")
        self.assertFalse(empty_out.get("text_available"))
        self.assertEqual(empty_out.get("status"), "TEXT DATA UNAVAILABLE")
        self.assertEqual(len(empty_out["top_tfidf_terms"]), 0)
        self.assertEqual(empty_out["word_count"], 0)

    # -------------------------------------------------------------
    # 3. Legitimate Image OpenCV / ResNet-18 Processing
    # -------------------------------------------------------------
    def test_03_legitimate_image_reaches_opencv_resnet(self):
        """Verify legitimate actual property image undergoes format/quality validation and ResNet-18 inference."""
        self.assertTrue(os.path.exists(self.valid_image_path), f"Image missing at {self.valid_image_path}")

        # Image validation
        with open(self.valid_image_path, "rb") as f:
            img_bytes = f.read()
        is_valid, meta = ImageProvenanceService.inspect_and_validate_image(img_bytes)
        self.assertTrue(is_valid)
        self.assertEqual(meta["validation_status"], "Valid")
        self.assertGreaterEqual(meta["width"], 400)
        self.assertGreaterEqual(meta["height"], 300)

        # OpenCV + PyTorch ResNet-18 CNN feature extraction
        cv_out = ImageAIService.analyze_single_image(self.valid_image_path)
        self.assertIn("quality_score", cv_out)
        self.assertIn("brightness_score", cv_out)
        self.assertIn("sharpness_score", cv_out)
        self.assertIn("cnn_feature_score", cv_out)
        self.assertGreater(cv_out["cnn_feature_score"], 0.0)
        self.assertGreater(cv_out["quality_score"], 0.0)

    # -------------------------------------------------------------
    # 4. Location / Geoapify Nearby Facilities Retrieval
    # -------------------------------------------------------------
    def test_04_geoapify_returns_nearby_facilities(self):
        """Verify Geoapify queries and returns facilities within 500m / local radius."""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            places = loop.run_until_complete(
                GeoapifyService.get_nearby_places(lat=12.9342, lon=77.6235, radius_meters=5000)
            )
            self.assertIsInstance(places, list)
            if len(places) > 0:
                categories = {p["category"] for p in places}
                self.assertTrue(any(c in categories for c in ["Hospitals", "Schools", "Metro Stations", "Restaurants", "Banks"]))
        finally:
            loop.close()

    # -------------------------------------------------------------
    # 5. POI Distance Calculation
    # -------------------------------------------------------------
    def test_05_poi_distances_are_calculated(self):
        """Verify actual distances are calculated for facilities."""
        d = GeoapifyService.haversine_distance(12.9342, 77.6235, 12.9350, 77.6240)
        self.assertGreater(d, 0.0)
        self.assertLess(d, 500.0)  # Near points within ~100m

    # -------------------------------------------------------------
    # 6. XGBoost Price Prediction
    # -------------------------------------------------------------
    def test_06_xgboost_prediction_works(self):
        """Verify XGBoost price prediction model produces valid estimated valuation."""
        pred = PricePredictionService.predict_property_valuation(
            address="80 Feet Road, 4th Block, Koramangala, Bengaluru",
            lat=12.9342,
            lon=77.6235,
            area_sqft=1200.0,
            bhk=2,
            bathrooms=2,
            listed_price=15000000.0
        )
        self.assertFalse(pred.get("error", False))
        self.assertGreater(pred["predicted_selling_price"], 0.0)
        self.assertGreater(pred["price_per_sqft"], 0.0)
        self.assertEqual(pred["data_quality"]["locality_matched"], "Koramangala")

    # -------------------------------------------------------------
    # 7. SHAP Explanation Attribution
    # -------------------------------------------------------------
    def test_07_shap_explanation_works(self):
        """Verify SHAP explainer attributes feature contributions to valuation."""
        pred = PricePredictionService.predict_property_valuation(
            address="80 Feet Road, 4th Block, Koramangala, Bengaluru",
            lat=12.9342,
            lon=77.6235,
            area_sqft=1200.0,
            bhk=2,
            bathrooms=2,
            listed_price=15000000.0
        )
        self.assertIn("shap_explanation", pred)
        shap_info = pred["shap_explanation"]
        self.assertTrue(
            len(shap_info.get("top_positive_factors", [])) > 0 or 
            len(shap_info.get("top_negative_factors", [])) > 0 or
            len(shap_info.get("feature_importance", [])) > 0
        )

    # -------------------------------------------------------------
    # 8. Missing Image Honest Fallback (No Fake ResNet)
    # -------------------------------------------------------------
    def test_08_missing_image_does_not_trigger_fake_analysis(self):
        """Verify missing image returns IMAGE_ANALYSIS_UNAVAILABLE without running ResNet."""
        cv_out = ImageAIService.analyze_property_images([])
        self.assertFalse(cv_out["image_analysis_available"])
        self.assertEqual(cv_out["cnn_status"], "IMAGE_ANALYSIS_UNAVAILABLE")
        self.assertEqual(cv_out["overall_condition"], "IMAGE_ANALYSIS_UNAVAILABLE")
        self.assertIsNone(cv_out["overall_score"])
        self.assertEqual(cv_out["processed_count"], 0)

    # -------------------------------------------------------------
    # 9. Location Reference Separated from Actual Property Photo
    # -------------------------------------------------------------
    def test_09_location_reference_separated_from_actual_image(self):
        """Verify historical records without authentic image default to truthful visual fallback."""
        fake_hist_prop = Property(
            id=9999,
            title="Historical Record",
            source_type="HISTORICAL_MARKET_DATA",
            source="Bengaluru_House_Data.csv",
            price=5000000.0,
            area_sqft=1000.0,
            locality="Whitefield",
            property_images=[]
        )
        prov = ImageProvenanceService.get_property_image_provenance(fake_hist_prop)
        self.assertFalse(prov["has_genuine_image"])
        self.assertEqual(prov["image_provenance"], "NO_IMAGE")
        self.assertEqual(prov["provenance_badge"], "PROPERTY IMAGE UNAVAILABLE")

    # -------------------------------------------------------------
    # 10. Combined Multimodal Property Intelligence Workflow
    # -------------------------------------------------------------
    def test_10_combined_multimodal_analysis_returns_valid_response(self):
        """Verify integrated multimodal workflow combines structured, text, image/fallback, location, XGBoost, and SHAP."""
        # 1. Structured Data
        prop = self.test_prop_structured
        sqft_rate = ListingService.calculate_price_per_sqft(prop["price_inr"], prop["area_sqft"])
        
        # 2. NLP Text Intelligence
        nlp_out = TextAIService.analyze_description(self.sample_description)
        
        # 3. Computer Vision Image Intelligence
        cv_out = ImageAIService.analyze_property_images([self.valid_image_path])
        
        # 4. Location / GIS Intelligence
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            places = loop.run_until_complete(
                GeoapifyService.get_nearby_places(lat=prop["latitude"], lon=prop["longitude"], radius_meters=1000)
            )
        finally:
            loop.close()
            
        # 5. XGBoost Valuation & SHAP
        pred_out = PricePredictionService.predict_property_valuation(
            address=prop["address"],
            lat=prop["latitude"],
            lon=prop["longitude"],
            area_sqft=prop["area_sqft"],
            bhk=prop["bhk"],
            bathrooms=2,
            nearby_places=places,
            image_score=cv_out.get("overall_score", 80.0),
            text_score=nlp_out.get("text_quality_score", 75.0),
            listed_price=prop["price_inr"]
        )

        combined_report = {
            "property_id": prop["id"],
            "structured_data": {
                "locality": prop["locality"],
                "bhk": prop["bhk"],
                "area_sqft": prop["area_sqft"],
                "price_inr": prop["price_inr"],
                "price_per_sqft": sqft_rate
            },
            "text_intelligence": {
                "status": nlp_out["status"],
                "quality_score": nlp_out["text_quality_score"],
                "top_terms": [t["term"] for t in nlp_out["top_tfidf_terms"][:3]]
            },
            "image_intelligence": {
                "available": cv_out["image_analysis_available"],
                "condition": cv_out["overall_condition"],
                "quality_score": cv_out["image_quality_score"],
                "cnn_status": cv_out["cnn_status"]
            },
            "location_intelligence": {
                "facilities_found": len(places),
                "coordinate_quality": prop.get("coordinate_quality", "LOCALITY_APPROXIMATE")
            },
            "ai_intelligence": {
                "predicted_price": pred_out["predicted_selling_price"],
                "shap_factors": len(pred_out.get("shap_explanation", {}).get("top_positive_factors", []))
            }
        }

        # Verifications
        self.assertEqual(combined_report["property_id"], 1)
        self.assertEqual(combined_report["structured_data"]["price_per_sqft"], 12500.0)
        self.assertEqual(combined_report["text_intelligence"]["status"], "TEXT DATA AVAILABLE")
        self.assertTrue(combined_report["image_intelligence"]["available"])
        self.assertGreater(combined_report["ai_intelligence"]["predicted_price"], 0.0)


if __name__ == "__main__":
    unittest.main()
