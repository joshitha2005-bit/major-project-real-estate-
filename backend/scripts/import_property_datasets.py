import os
import sys
import csv
import argparse
import random
import re
from sqlalchemy.orm import Session

# Add backend to sys.path so app modules can be imported
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.core.database import SessionLocal, get_db
from app.models.property import Property
from app.models.user import User

LOCALITY_COORDINATES = {
    "koramangala": (12.9357, 77.6240),
    "electronic city": (12.8436, 77.6687),
    "whitefield": (12.9696, 77.7497),
    "hsr layout": (12.9116, 77.6389),
    "indiranagar": (12.9733, 77.6405),
    "marathahalli": (12.9591, 77.6974),
    "bellandur": (12.9279, 77.6756),
    "sarjapur road": (12.9107, 77.6970),
    "jp nagar": (12.9077, 77.5854),
    "jayanagar": (12.9250, 77.5938),
    "banashankari": (12.9255, 77.5468),
    "hebbal": (13.0358, 77.5970),
    "yelahanka": (13.1007, 77.5963),
    "kr puram": (13.0075, 77.6959),
    "mahadevapura": (12.9902, 77.6874),
    "btm layout": (12.9166, 77.6101),
    "bannerghatta road": (12.8950, 77.5990),
    "thanisandra": (13.0547, 77.6338),
    "hennur": (13.0258, 77.6341),
    "vijayanagar": (12.9708, 77.5350),
    "rajajinagar": (12.9882, 77.5549),
    "malleshwaram": (13.0031, 77.5643),
    "basavanagudi": (12.9421, 77.5752),
    "brookefield": (12.9658, 77.7183),
    "chandapura": (12.8004, 77.7063)
}

def clean_total_sqft(sqft_str):
    """Normalize total_sqft into a numeric float in square feet."""
    sqft_str = str(sqft_str).strip().lower()
    
    # Handle range e.g. "1000 - 1200"
    if "-" in sqft_str:
        try:
            parts = [float(p.strip()) for p in sqft_str.split("-") if p.strip()]
            return sum(parts) / len(parts)
        except Exception:
            return None
            
    # Handle units conversions
    try:
        if "sq. yards" in sqft_str:
            num = float(re.findall(r"[\d\.]+", sqft_str)[0])
            return num * 9.0
        elif "sq. meter" in sqft_str:
            num = float(re.findall(r"[\d\.]+", sqft_str)[0])
            return num * 10.7639
        elif "acres" in sqft_str:
            num = float(re.findall(r"[\d\.]+", sqft_str)[0])
            return num * 43560.0
        elif "grounds" in sqft_str:
            num = float(re.findall(r"[\d\.]+", sqft_str)[0])
            return num * 2400.0
        elif "guntha" in sqft_str:
            num = float(re.findall(r"[\d\.]+", sqft_str)[0])
            return num * 1089.0
        elif "cents" in sqft_str:
            num = float(re.findall(r"[\d\.]+", sqft_str)[0])
            return num * 435.6
        elif "perch" in sqft_str:
            num = float(re.findall(r"[\d\.]+", sqft_str)[0])
            return num * 272.25
        else:
            # Just try to parse standard numeric string
            num = float(re.findall(r"[\d\.]+", sqft_str)[0])
            return num
    except Exception:
        return None

def clean_bhk(size_str):
    """Normalize size configuration into numeric BHK counts."""
    size_str = str(size_str).strip().lower()
    if not size_str or size_str == "nan":
        return 2 # Safe default
    try:
        num = int(re.findall(r"\d+", size_str)[0])
        return num
    except Exception:
        return 2

def normalize_locality(loc_str):
    """Standardize common locality variations to canonical names."""
    loc_str = str(loc_str).strip()
    loc_lower = loc_str.lower()
    
    if "white field" in loc_lower or loc_lower == "whitefield":
        return "Whitefield"
    elif "electronic city" in loc_lower:
        return "Electronic City"
    elif "koramangla" in loc_lower or loc_lower == "koramangala":
        return "Koramangala"
    elif loc_lower == "hsr" or "hsr layout" in loc_lower:
        return "HSR Layout"
    elif "jp nagar" in loc_lower:
        return "JP Nagar"
    elif "jayanagar" in loc_lower:
        return "Jayanagar"
    elif "indiranagar" in loc_lower:
        return "Indiranagar"
    elif "bellandur" in loc_lower:
        return "Bellandur"
    elif "sarjapur" in loc_lower:
        return "Sarjapur Road"
    elif "marathahalli" in loc_lower:
        return "Marathahalli"
    elif "hebbal" in loc_lower:
        return "Hebbal"
    elif "yelahanka" in loc_lower:
        return "Yelahanka"
    elif "chandapura" in loc_lower:
        return "Chandapura"
    
    # Capitalize first letter of each word as fallback
    return " ".join([w.capitalize() for w in loc_str.split()])

def main():
    parser = argparse.ArgumentParser(description="Import real-estate datasets safely.")
    parser.add_argument("--dry-run", action="store_true", help="Perform import checks without database changes.")
    args = parser.parse_args()

    db = SessionLocal()
    
    csv_path = os.path.join(os.path.dirname(__file__), "..", "datasets", "Bengaluru_House_Data.csv")
    if not os.path.exists(csv_path):
        print(f"Error: Dataset not found at {csv_path}")
        sys.exit(1)
        
    print(f"Reading dataset: {csv_path}")
    
    # Counter variables
    source_rows = 0
    valid_rows = 0
    rejected_rows = 0
    duplicate_rows = 0
    imported_rows = 0
    
    locality_counts = {}
    dataset_count = 0
    missing_coordinates = 0
    missing_images = 0
    missing_contact = 0
    
    # Clean up old database records of same source before re-importing (skip if dry-run)
    if not args.dry_run:
        print("Cleaning up old dataset records to avoid duplication...")
        db.query(Property).filter(Property.source == "Bengaluru_House_Data.csv").delete(synchronize_session=False)
        db.commit()

    # Preload existing properties to avoid duplicates
    existing_fingerprints = set()
    for p in db.query(Property.locality, Property.price, Property.area_sqft, Property.bhk, Property.property_type).all():
        fingerprint = (str(p.locality).lower(), float(p.price), float(p.area_sqft), int(p.bhk), str(p.property_type).lower())
        existing_fingerprints.add(fingerprint)

    # Get system default user
    default_user = db.query(User).first()
    default_user_id = default_user.id if default_user else 1

    try:
        with open(csv_path, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                source_rows += 1
                
                raw_location = row.get("location")
                raw_size = row.get("size")
                raw_sqft = row.get("total_sqft")
                raw_bath = row.get("bath")
                raw_balcony = row.get("balcony")
                raw_price = row.get("price")
                raw_area_type = row.get("area_type")
                raw_availability = row.get("availability")
                raw_society = row.get("society")
                
                # Check for critical missing values
                if not raw_location or not raw_price or not raw_sqft:
                    rejected_rows += 1
                    continue
                
                # Clean total_sqft
                area_sqft = clean_total_sqft(raw_sqft)
                if not area_sqft or area_sqft <= 0:
                    rejected_rows += 1
                    continue
                
                # Clean BHK
                bhk = clean_bhk(raw_size)
                
                # Clean Price (Convert lakhs to INR)
                try:
                    price_val = float(raw_price) * 100000.0
                    if price_val <= 0:
                        rejected_rows += 1
                        continue
                except Exception:
                    rejected_rows += 1
                    continue
                
                # Clean bathrooms & balconies
                try:
                    bathrooms = int(float(raw_bath)) if raw_bath else 1
                except Exception:
                    bathrooms = 1
                    
                try:
                    balconies = int(float(raw_balcony)) if raw_balcony else 0
                except Exception:
                    balconies = 0
                
                # Normalize locality
                locality = normalize_locality(raw_location)
                
                # Property type resolution
                if raw_area_type == "Plot Area" and bhk == 0:
                    property_type = "Plot"
                elif raw_area_type == "Plot Area" and bhk > 0:
                    property_type = "Villa" if (bhk >= 4 or area_sqft >= 2500) else "Independent House"
                else:
                    property_type = "Apartment"
                
                # Duplicate check
                fingerprint = (locality.lower(), float(price_val), float(area_sqft), int(bhk), property_type.lower())
                if fingerprint in existing_fingerprints:
                    duplicate_rows += 1
                    continue
                
                # Geocode coordinates lookup (No random offset!)
                loc_lower = locality.lower()
                base_coords = LOCALITY_COORDINATES.get(loc_lower)
                if base_coords:
                    lat = base_coords[0]
                    lon = base_coords[1]
                else:
                    lat = 12.9716
                    lon = 77.5946
                    missing_coordinates += 1
                
                # Construct Property title from actual society name if present, else neutral template
                if raw_society and raw_society.strip() and raw_society.lower() not in ["none", "nan", "null"]:
                    title = raw_society.strip()
                else:
                    title = f"{bhk} BHK — {locality}"
                    
                description = f"Historical dataset record from Bengaluru_House_Data.csv. Status: {raw_availability or 'N/A'}."
                address = f"{locality}, Bengaluru"
                
                # Mappings
                p = Property(
                    user_id=default_user_id,
                    title=title,
                    property_type=property_type,
                    listing_type="Dataset", # Strict dataset classification
                    bhk=bhk,
                    area_sqft=area_sqft,
                    bathrooms=bathrooms,
                    balconies=balconies,
                    price=price_val,
                    description=description,
                    address=address,
                    locality=locality,
                    latitude=round(lat, 6),
                    longitude=round(lon, 6),
                    owner_name="Historical Dataset",
                    owner_phone="", # Never invent contact info
                    phone="", # Never invent phone
                    images=[], # No fake images
                    street_view_available=False,
                    seller_type="Broker",
                    seller_name="System Importer",
                    verification_status="Historical Dataset", # Strict quality label
                    source_type="historical_dataset",
                    source="Bengaluru_House_Data.csv",
                    verified=False # Historical records are not verified direct listings
                )
                
                if not args.dry_run:
                    db.add(p)
                    # Add to existing fingerprints set in case source contains duplicates
                    existing_fingerprints.add(fingerprint)
                
                valid_rows += 1
                imported_rows += 1
                dataset_count += 1
                missing_images += 1
                missing_contact += 1
                
                locality_counts[locality] = locality_counts.get(locality, 0) + 1

        if not args.dry_run:
            db.commit() # Commit transaction
            print("Import successfully completed & committed!")
        else:
            print("Dry-run completed. No database changes were written.")
            
    except Exception as e:
        db.rollback()
        print(f"Error during import session: {e}")
        sys.exit(1)
    finally:
        db.close()
        
    # Print reporting log
    print("\n" + "="*50)
    print("IMPORT STATUS REPORT")
    print("="*50)
    print(f"Source Rows:          {source_rows}")
    print(f"Valid Rows:           {valid_rows}")
    print(f"Rejected Rows:        {rejected_rows}")
    print(f"Duplicate Rows:       {duplicate_rows}")
    print(f"Imported Rows:        {imported_rows}")
    print(f"DATASET Listings:     {dataset_count}")
    print(f"Missing Coordinates:  {missing_coordinates}")
    print(f"Missing Images:       {missing_images}")
    print(f"Missing Contact Info: {missing_contact}")
    
    print("\nTop Localities Imported:")
    sorted_locs = sorted(locality_counts.items(), key=lambda x: x[1], reverse=True)[:10]
    for loc, c in sorted_locs:
        print(f"  - {loc}: {c}")
    print("="*50)

if __name__ == "__main__":
    main()
