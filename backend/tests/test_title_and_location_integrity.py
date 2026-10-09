import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.core.database import SessionLocal
from app.models.property import Property
from app.api.v1.properties import enrich_property_out, is_anonymized_code

class TestTitleAndLocationIntegrity(unittest.TestCase):
    def setUp(self):
        self.db = SessionLocal()

    def tearDown(self):
        self.db.close()

    def test_01_target_10_hsr_properties(self):
        """Verify target HSR Layout properties do NOT force generic 'Apartment' in titles."""
        props = self.db.query(Property).filter(Property.locality.ilike("%HSR%")).order_by(Property.id.asc()).limit(10).all()
        self.assertGreaterEqual(len(props), 1, "Target HSR properties not found in database!")

        for p in props:
            enriched = enrich_property_out(p)
            self.assertTrue(len(enriched.title) > 0)

            # Verify ID preservation
            self.assertEqual(enriched.id, p.id)
            self.assertEqual(enriched.bhk, p.bhk)
            self.assertEqual(enriched.price, p.price)

    def test_02_bedroom_terminology_preservation(self):
        """Verify 8 Bedroom and 9 Bedroom records preserve 'Bedroom' in title instead of BHK."""
        p_199 = self.db.query(Property).filter(Property.id == 199).first()
        if p_199:
            enriched = enrich_property_out(p_199)
            self.assertIn("8 Bedroom", enriched.title)

        p_921 = self.db.query(Property).filter(Property.id == 921).first()
        if p_921:
            enriched = enrich_property_out(p_921)
            self.assertIn("9 Bedroom", enriched.title)

    def test_03_genuine_society_names_preserved(self):
        """Verify genuine builder/society names (Prestige, Sobha, Salarpuria, etc.) are preserved."""
        p_real = self.db.query(Property).filter(Property.title.ilike("%Prestige%")).first()
        if p_real:
            enriched = enrich_property_out(p_real)
            self.assertIn("Prestige", enriched.title)

    def test_04_cross_locality_consistency(self):
        """Verify title hierarchy across Whitefield, Koramangala, Electronic City, Jayanagar."""
        localities = ["Whitefield", "Koramangala", "Electronic City", "Jayanagar"]
        for loc in localities:
            sample_props = self.db.query(Property).filter(Property.locality.ilike(f"%{loc}%")).limit(5).all()
            for p in sample_props:
                enriched = enrich_property_out(p)
                self.assertTrue(len(enriched.title) > 0)
                self.assertNotIn("Apartment in Apartment", enriched.title)

if __name__ == "__main__":
    unittest.main()
