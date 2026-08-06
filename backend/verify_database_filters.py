import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.database import SessionLocal, engine, Base
from app.models.property import Property
from app.services.seed_service import SeedService
from app.api.v1.properties import list_properties

def test_db_and_filters():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    
    # 1. Trigger Seed
    SeedService.seed_properties(db)
    
    # 2. Total Properties Check
    total_props = db.query(Property).count()
    print("=" * 70)
    print(f"VERIFYING PROPERTY DATABASE: Total Count = {total_props}")
    print("=" * 70)
    assert total_props >= 100, f"Expected >= 100 properties, found {total_props}"
    print("[OK] Requirement 1 PASSED: At least 100 properties exist in DB.")
    
    # 3. Required Localities Check
    required_localities = [
        "Koramangala", "Electronic City", "Whitefield", "HSR Layout",
        "Indiranagar", "JP Nagar", "Bellandur", "Marathahalli",
        "Chandapura", "Hebbal"
    ]
    
    print("\nVerifying Locality Distribution and Strict Search:")
    locality_counts = {}
    for loc in required_localities:
        res = list_properties(query=loc, skip=0, limit=50, db=db)
        items = res.items
        locality_counts[loc] = len(items)
        print(f"  - Locality '{loc}': {len(items)} properties returned.")
        assert len(items) > 0, f"Locality {loc} returned 0 properties!"
        
        # Verify strict match
        for item in items:
            matches_title = loc.lower() in item.title.lower()
            matches_addr = loc.lower() in item.address.lower()
            assert matches_title or matches_addr, f"Property '{item.title}' in address '{item.address}' does not match '{loc}'"
            
    print("[OK] Requirement 2 & 3 PASSED: All localities have properties and search is strictly matching.")
    
    # 4. BHK Filters Check
    print("\nVerifying BHK Filters:")
    for bhk in [1, 2, 3, 4]:
        res = list_properties(bhk=bhk, skip=0, limit=50, db=db)
        print(f"  - {bhk} BHK Filter: {len(res.items)} properties returned.")
        for item in res.items:
            assert item.bhk == bhk, f"Expected {bhk} BHK, got {item.bhk}"
    print("[OK] Requirement 4 PASSED: BHK filters (1, 2, 3, 4) work correctly.")
    
    # 5. Property Type Filters Check
    print("\nVerifying Property Type Filters:")
    for ptype in ["Apartment", "Villa", "Independent House", "Plot"]:
        res = list_properties(property_type=ptype, skip=0, limit=50, db=db)
        print(f"  - Property Type '{ptype}' Filter: {len(res.items)} properties returned.")
        for item in res.items:
            assert item.property_type.lower() == ptype.lower(), f"Expected {ptype}, got {item.property_type}"
    print("[OK] Requirement 5 PASSED: Property Type filters work correctly.")
    
    db.close()
    print("\n" + "=" * 70)
    print("ALL PROPERTY DATABASE & FILTER VERIFICATIONS COMPLETED SUCCESSFULLY!")
    print("=" * 70)

if __name__ == "__main__":
    test_db_and_filters()
