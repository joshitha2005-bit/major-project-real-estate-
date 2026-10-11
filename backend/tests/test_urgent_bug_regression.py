import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.core.database import SessionLocal
from app.models.property import Property
from app.api.v1.properties import enrich_property_out, get_dashboard_stats

class TestUrgentBugRegression(unittest.TestCase):
    def setUp(self):
        self.db = SessionLocal()

    def tearDown(self):
        self.db.close()

    def test_01_total_property_count_matches_database(self):
        """Verify total property count matches database and dashboard stats endpoint returns true counts."""
        total_count = self.db.query(Property).count()
        self.assertGreaterEqual(total_count, 863, f"Database count is {total_count}, expected >= 863 MAIN_AI_READY!")

        stats = get_dashboard_stats(db=self.db)
        self.assertEqual(stats.get("total_properties"), total_count, "Dashboard stats endpoint total_properties mismatch!")

    def test_02_source_type_integrity(self):
        """Verify all properties have valid source_type categorization."""
        source_portal_cnt = self.db.query(Property).filter(Property.source_type == "source_portal").count()
        demo_cnt = self.db.query(Property).filter(Property.source_type == "demo_dataset").count()
        total_cnt = self.db.query(Property).count()
        
        self.assertGreaterEqual(source_portal_cnt, 863)
        owner_cnt = self.db.query(Property).filter(Property.source_type.in_(["owner_listing", "PROPPULSE_DIRECT"])).count()
        historical_cnt = self.db.query(Property).filter(Property.source_type == "historical_dataset").count()
        self.assertEqual(source_portal_cnt + demo_cnt + owner_cnt + historical_cnt, total_cnt)

    def test_03_historical_contact_owner_restriction(self):
        """Verify dataset records hide contact phone and do not represent as live owner listings."""
        prop = self.db.query(Property).filter(Property.source_type.in_(["source_portal", "historical_dataset"])).first()
        self.assertIsNotNone(prop)
        
        enriched = enrich_property_out(prop)
        self.assertEqual(enriched.owner_phone, "Contact information unavailable")
        self.assertEqual(enriched.phone, "Contact information unavailable")

    def test_04_owner_listing_preserves_contact_info(self):
        """Verify direct owner_listing records preserve contact information."""
        owner_prop = self.db.query(Property).filter(Property.source_type == "owner_listing").first()
        if owner_prop:
            enriched = enrich_property_out(owner_prop)
            self.assertEqual(enriched.source_type, "owner_listing")
            self.assertEqual(enriched.owner_phone, "+91 99000 88888")

    def test_05_price_per_sqft_exactness(self):
        """Verify price_per_sqft == price_inr / area_sqft for all database records."""
        props = self.db.query(Property).filter(Property.price_inr > 0, Property.area_sqft > 0).limit(200).all()
        for p in props:
            expected = round(p.price_inr / p.area_sqft, 2)
            self.assertAlmostEqual(p.price_per_sqft, expected, delta=0.05,
                                   msg=f"Price/sqft mismatch for property ID {p.id}")

    def test_06_transaction_type_integrity(self):
        """Verify transaction_type is strictly 'sale' or 'rent'."""
        sale_cnt = self.db.query(Property).filter(Property.transaction_type == "sale").count()
        rent_cnt = self.db.query(Property).filter(Property.transaction_type == "rent").count()
        total = self.db.query(Property).count()
        self.assertEqual(sale_cnt + rent_cnt, total, "Properties missing transaction_type!")

    def test_07_provenance_badges_in_enriched_output(self):
        """Verify coordinate_quality and coordinate_status are correctly output."""
        prop = self.db.query(Property).first()
        enriched = enrich_property_out(prop)
        valid_statuses = ["EXACT", "LOCALITY_APPROXIMATE", "APPROXIMATE", "MISSING"]
        self.assertIn(enriched.coordinate_quality, valid_statuses)
        self.assertIn(enriched.coordinate_status, valid_statuses)

if __name__ == "__main__":
    unittest.main()
