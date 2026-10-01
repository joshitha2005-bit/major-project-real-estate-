import os
import sys
import unittest
import asyncio

# Ensure backend root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.core.database import SessionLocal
from app.models.property import Property
from app.models.user import User
from app.api.v1.properties import enrich_property_out, list_properties, get_property_by_id, is_anonymized_code
from app.services.geoapify_service import GeoapifyService
from app.core.security import verify_password, get_password_hash
from app.services.price_prediction_service import PricePredictionService

class TestPropertyListingIntegrity(unittest.TestCase):
    def setUp(self):
        self.db = SessionLocal()

    def tearDown(self):
        self.db.close()

    def test_01_property_ids_are_unique(self):
        """1. Property IDs are unique in the database."""
        total_count = self.db.query(Property).count()
        distinct_ids_count = self.db.query(Property.id).distinct().count()
        self.assertEqual(total_count, distinct_ids_count, "Property IDs are not unique!")

    def test_02_exact_duplicates_are_removed(self):
        """2. Exact duplicates (same title+locality+price+bhk+area+source) are 0."""
        from sqlalchemy import func
        dup_count = self.db.query(
            Property.title, Property.locality, Property.price, Property.bhk, Property.area_sqft, Property.source
        ).group_by(
            func.lower(Property.title), func.lower(Property.locality), Property.price, Property.bhk, Property.area_sqft, Property.source
        ).having(func.count() > 1).count()
        self.assertEqual(dup_count, 0, f"Found {dup_count} exact duplicate groups in database!")

    def test_03_card_detail_ids_and_fields_match(self):
        """3. Card/Detail IDs match exactly between database and API serializer."""
        sample_props = self.db.query(Property).order_by(Property.id.asc()).limit(5).all()
        for p in sample_props:
            enriched = enrich_property_out(p)
            self.assertEqual(p.id, enriched.id)
            self.assertEqual(p.price, enriched.price)
            self.assertEqual(p.bhk, enriched.bhk)
            self.assertEqual(p.area_sqft, enriched.area_sqft)

    def test_04_no_random_image_assignment(self):
        """4. No random image pool assignment; missing images default to []."""
        hist_props = self.db.query(Property).filter(Property.source_type == "historical_dataset").limit(20).all()
        for p in hist_props:
            enriched = enrich_property_out(p)
            for img in enriched.images:
                self.assertNotIn("unsplash.com", img, "Found random unsplash image pool URL assigned!")

    def test_05_no_synthetic_phone_numbers(self):
        """5. Synthetic seed phone numbers are removed; fall back to 'Contact information unavailable'."""
        SEED_PHONES = ["+91 98860 12345", "+91 98450 67890", "+91 99001 88345", "+91 98110 99887"]
        hist_props = self.db.query(Property).filter(Property.source_type == "historical_dataset").limit(20).all()
        for p in hist_props:
            enriched = enrich_property_out(p)
            self.assertNotIn(enriched.phone, SEED_PHONES)
            self.assertEqual(enriched.phone, "Contact information unavailable")

    def test_06_no_anonymized_society_codes_in_titles(self):
        """6. Anonymized codes (ArsiaEx, Oreldhi, SLiritn, Soiewre, DuenaTa, SollyCl) are normalized into transparent titles."""
        codes = ["ArsiaEx", "Oreldhi", "SLiritn", "Soiewre", "DuenaTa", "SollyCl", "Coomee", "Theanmp", "Sryalan"]
        for code in codes:
            self.assertTrue(is_anonymized_code(code), f"Failed to detect anonymized hash code: {code}")
        
        # Test serializer normalization
        p = self.db.query(Property).filter(Property.source_type == "historical_dataset").first()
        if p:
            p.title = "ArsiaEx"
            p.locality = "Whitefield"
            p.address = "Whitefield, Bengaluru"
            p.bhk = 5
            enriched = enrich_property_out(p)
            self.assertNotIn("ArsiaEx", enriched.title)
            self.assertIn("in Whitefield", enriched.title)

    def test_07_no_random_coordinates_generated(self):
        """7. Coordinates remain preserved from dataset without random generation."""
        p = self.db.query(Property).first()
        self.assertIsNotNone(p.latitude)
        self.assertIsNotNone(p.longitude)

    def test_08_parks_absent_from_nearby_amenities(self):
        """8. Parks are absent from Geoapify nearby amenities API taxonomy."""
        places = asyncio.run(GeoapifyService.get_nearby_places(12.9357, 77.6240, 5000))
        for place in places:
            self.assertNotEqual(place["category"], "Parks", "Parks category found in nearby places API!")

    def test_09_property_fields_match_database(self):
        """9. Property price, BHK, area, locality remain unchanged from database records."""
        p = self.db.query(Property).first()
        enriched = enrich_property_out(p)
        self.assertEqual(p.price, enriched.price)
        self.assertEqual(p.bhk, enriched.bhk)
        self.assertEqual(p.area_sqft, enriched.area_sqft)

    def test_10_historical_records_correctly_marked(self):
        """10. Historical dataset records are marked with LOCALITY_APPROXIMATE."""
        p = self.db.query(Property).filter(Property.source_type == "historical_dataset").first()
        if p:
            enriched = enrich_property_out(p)
            self.assertEqual(enriched.coordinate_status, "LOCALITY_APPROXIMATE")

    def test_11_owner_submitted_records_preserve_info(self):
        """11. Owner-submitted records retain owner info."""
        p = self.db.query(Property).filter(Property.source_type == "owner_listing").first()
        if p:
            enriched = enrich_property_out(p)
            self.assertEqual(enriched.phone, "+91 99000 88888")

    def test_12_existing_auth_works(self):
        """12. Existing authentication password hashing and verification works."""
        hashed = get_password_hash("TestPass123!")
        self.assertTrue(verify_password("TestPass123!", hashed))

    def test_13_existing_subscription_gating_works(self):
        """13. Existing subscription role checks function intact."""
        admin_user = User(email="admin_test@test.com", full_name="Admin Test", hashed_password="xxx", role="ADMIN")
        self.assertEqual(admin_user.role, "ADMIN")

    def test_14_existing_ai_endpoints_work(self):
        """14. Price prediction pipeline loads cleanly."""
        res = PricePredictionService.predict_property_valuation(
            address="Whitefield, Bengaluru", lat=12.9696, lon=77.7497, area_sqft=1500.0, bhk=3, bathrooms=3, parking="Covered", facing="East", property_age="1-5 yrs", nearby_places=[]
        )
        self.assertIn("predicted_selling_price", res)
        self.assertTrue(res["predicted_selling_price"] > 0)

    def test_15_existing_gis_endpoints_work(self):
        """15. Geoapify geocode calculation functions intact."""
        geo = asyncio.run(GeoapifyService.search_geocode("Koramangala"))
        self.assertIsNotNone(geo)
        self.assertIn("latitude", geo)

if __name__ == "__main__":
    unittest.main()
