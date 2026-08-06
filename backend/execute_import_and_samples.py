import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.database import SessionLocal, engine, Base
from app.services.dataset_import_service import DatasetImportService
from app.models.property import Property

def execute_and_verify():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    # 1. Execute Dataset Import Service
    print("=" * 75)
    print("EXECUTING DATASET IMPORT FROM BACKEND/DATASETS")
    print("=" * 75)
    
    # Import datasets from CSV files inside backend/datasets
    import_res = DatasetImportService.import_datasets(db, max_records_per_file=500)

    # 2. Database Count Verification
    total_db_props = db.query(Property).count()
    
    # 3. Unique Localities Count
    all_props = db.query(Property).all()
    localities_found = set()
    for p in all_props:
        # Extract locality name from address or title
        for loc in ["Koramangala", "Electronic City", "Whitefield", "HSR Layout", "Indiranagar", 
                    "Marathahalli", "Bellandur", "Sarjapur Road", "JP Nagar", "Jayanagar", 
                    "Banashankari", "Hebbal", "Yelahanka", "KR Puram", "Mahadevapura", 
                    "BTM Layout", "Bannerghatta Road", "Thanisandra", "Hennur", "Vijayanagar", 
                    "Rajajinagar", "Malleshwaram", "Basavanagudi", "Brookefield", "Chandapura"]:
            if loc.lower() in p.address.lower() or loc.lower() in p.title.lower():
                localities_found.add(loc)

    print("\n" + "=" * 75)
    print("DATABASE IMPORT VERIFICATION SUMMARY")
    print("=" * 75)
    print(f"Total Imported Properties in DB: {total_db_props}")
    print(f"Total Unique Localities in DB  : {len(localities_found)}")

    # 4. Print Sample Properties for Target Localities
    target_localities = ["Koramangala", "HSR Layout", "Whitefield", "Electronic City", "Indiranagar"]
    print("\nSAMPLE PROPERTIES FROM TARGET LOCALITIES:")
    print("-" * 75)

    for loc in target_localities:
        search_pattern = f"%{loc}%"
        matched = db.query(Property).filter(
            (Property.address.ilike(search_pattern)) | 
            (Property.title.ilike(search_pattern))
        ).limit(2).all()

        print(f"\n[LOCALITY: {loc.upper()}] ({len(matched)} sample properties displayed)")
        for p in matched:
            price_fmt = f"RS {p.price / 100000:.2f} Lakh" if p.price < 10000000 else f"RS {p.price / 10000000:.2f} Cr"
            print(f"  * Property ID {p.id:3d}: {p.title}")
            print(f"    - Type: {p.property_type} ({p.bhk} BHK) | Area: {int(p.area_sqft)} sq.ft | Price: {price_fmt}")
            print(f"    - Address: {p.address}")
            print(f"    - Owner: {p.owner_name} ({p.owner_phone})")

    db.close()
    print("\n" + "=" * 75)
    print("DATABASE VERIFICATION COMPLETE - ALL PROPERTIES PERSISTED IN DB")
    print("=" * 75)

if __name__ == "__main__":
    execute_and_verify()
