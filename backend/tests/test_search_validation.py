import os
import sys
import unittest

# Add backend to sys.path so app modules can be imported
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.core.database import SessionLocal
from app.models.property import Property
from app.api.v1.properties import list_properties

class TestSearchValidation(unittest.TestCase):
    def setUp(self):
        self.db = SessionLocal()

    def tearDown(self):
        self.db.close()

    def test_hsr_layout_leakage(self):
        """Assert every property returned for HSR Layout search has locality 'HSR Layout'."""
        res = list_properties(query="HSR Layout", db=self.db)
        self.assertTrue(len(res.items) > 0, "No properties found in HSR Layout to assert.")
        for item in res.items:
            self.assertIn("hsr", item.locality.lower(), f"Leakage detected: Property {item.id} with locality {item.locality} returned in HSR Layout search!")

    def test_whitefield_leakage(self):
        """Assert every property returned for Whitefield search has locality 'Whitefield'."""
        res = list_properties(query="Whitefield", db=self.db)
        self.assertTrue(len(res.items) > 0, "No properties found in Whitefield to assert.")
        for item in res.items:
            self.assertIn("whitefield", item.locality.lower(), f"Leakage detected: Property {item.id} with locality {item.locality} returned in Whitefield search!")

    def test_electronic_city_leakage(self):
        """Assert every property returned for Electronic City search has locality 'Electronic City'."""
        res = list_properties(query="Electronic City", db=self.db)
        self.assertTrue(len(res.items) > 0, "No properties found in Electronic City to assert.")
        for item in res.items:
            self.assertIn("electronic city", item.locality.lower(), f"Leakage detected: Property {item.id} with locality {item.locality} returned in Electronic City search!")

    def test_koramangala_leakage(self):
        """Assert every property returned for Koramangala search has locality 'Koramangala'."""
        res = list_properties(query="Koramangala", db=self.db)
        self.assertTrue(len(res.items) > 0, "No properties found in Koramangala to assert.")
        for item in res.items:
            self.assertIn("koramangala", item.locality.lower(), f"Leakage detected: Property {item.id} with locality {item.locality} returned in Koramangala search!")

    def test_locality_plus_bhk(self):
        """Verify locality + BHK combination filters work strictly without leakage."""
        res = list_properties(query="HSR Layout", bhk=3, db=self.db)
        self.assertTrue(len(res.items) > 0, "No properties matching criteria HSR Layout + 3 BHK")
        for item in res.items:
            self.assertIn("hsr", item.locality.lower())
            self.assertEqual(item.bhk, 3)

    def test_locality_plus_price(self):
        """Verify locality + Price range filters work strictly without leakage."""
        res = list_properties(query="Whitefield", min_price=3000000.0, max_price=8000000.0, db=self.db)
        self.assertTrue(len(res.items) > 0, "No properties matching Whitefield + Price range")
        for item in res.items:
            self.assertIn("whitefield", item.locality.lower())
            self.assertTrue(3000000.0 <= item.price <= 8000000.0, f"Price {item.price} out of range!")

    def test_locality_plus_property_type(self):
        """Verify locality + Property type filters work strictly without leakage."""
        res = list_properties(query="Electronic City", property_type="Apartment", db=self.db)
        self.assertTrue(len(res.items) > 0, "No properties matching Electronic City + Apartment")
        for item in res.items:
            self.assertIn("electronic city", item.locality.lower())
            self.assertEqual(item.property_type, "Apartment")

    def test_locality_plus_listing_type(self):
        """Verify locality + Listing type filters work strictly without leakage."""
        res = list_properties(query="Koramangala", listing_type="Buy", db=self.db)
        self.assertTrue(len(res.items) > 0, "No properties matching Koramangala + Buy type")
        for item in res.items:
            self.assertIn("koramangala", item.locality.lower())
            self.assertEqual(item.listing_type, "Buy")

if __name__ == "__main__":
    unittest.main()
