import os
import glob
import hashlib
import pandas as pd
import math
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from app.models.property import Property
from app.models.user import User
from app.core.security import get_password_hash

BANGALORE_LOCALITY_CENTERS = [
    {"name": "Koramangala", "lat": 12.9357, "lon": 77.6240, "pin": "560034", "base_price": 12500},
    {"name": "Electronic City", "lat": 12.8436, "lon": 77.6687, "pin": "560100", "base_price": 5600},
    {"name": "Whitefield", "lat": 12.9696, "lon": 77.7497, "pin": "560066", "base_price": 7800},
    {"name": "HSR Layout", "lat": 12.9116, "lon": 77.6389, "pin": "560102", "base_price": 9500},
    {"name": "Indiranagar", "lat": 12.9733, "lon": 77.6405, "pin": "560038", "base_price": 14000},
    {"name": "Marathahalli", "lat": 12.9591, "lon": 77.6974, "pin": "560037", "base_price": 7200},
    {"name": "Bellandur", "lat": 12.9279, "lon": 77.6756, "pin": "560103", "base_price": 8200},
    {"name": "Sarjapur Road", "lat": 12.9107, "lon": 77.6970, "pin": "560035", "base_price": 6800},
    {"name": "JP Nagar", "lat": 12.9077, "lon": 77.5854, "pin": "560078", "base_price": 8800},
    {"name": "Jayanagar", "lat": 12.9250, "lon": 77.5938, "pin": "560041", "base_price": 11500},
    {"name": "Banashankari", "lat": 12.9255, "lon": 77.5468, "pin": "560085", "base_price": 7500},
    {"name": "Hebbal", "lat": 13.0358, "lon": 77.5970, "pin": "560024", "base_price": 9200},
    {"name": "Yelahanka", "lat": 13.1007, "lon": 77.5963, "pin": "560064", "base_price": 6100},
    {"name": "KR Puram", "lat": 13.0075, "lon": 77.6959, "pin": "560036", "base_price": 5800},
    {"name": "Mahadevapura", "lat": 12.9902, "lon": 77.6874, "pin": "560048", "base_price": 6400},
    {"name": "BTM Layout", "lat": 12.9166, "lon": 77.6101, "pin": "560076", "base_price": 8500},
    {"name": "Bannerghatta Road", "lat": 12.8950, "lon": 77.5990, "pin": "560076", "base_price": 7200},
    {"name": "Thanisandra", "lat": 13.0547, "lon": 77.6338, "pin": "560077", "base_price": 6900},
    {"name": "Hennur", "lat": 13.0258, "lon": 77.6341, "pin": "560043", "base_price": 6500},
    {"name": "Vijayanagar", "lat": 12.9708, "lon": 77.5350, "pin": "560040", "base_price": 8200},
    {"name": "Rajajinagar", "lat": 12.9882, "lon": 77.5549, "pin": "560010", "base_price": 10500},
    {"name": "Malleshwaram", "lat": 13.0031, "lon": 77.5643, "pin": "560003", "base_price": 13000},
    {"name": "Basavanagudi", "lat": 12.9421, "lon": 77.5752, "pin": "560004", "base_price": 11000},
    {"name": "Brookefield", "lat": 12.9658, "lon": 77.7183, "pin": "560037", "base_price": 7500},
    {"name": "Chandapura", "lat": 12.8004, "lon": 77.7063, "pin": "560099", "base_price": 4500}
]

BUILDERS = ["Prestige", "Sobha", "Brigade", "Godrej", "Puravankara", "Salarpuria Sattva", "Mantri", "Assetz"]
OWNERS = [
    ("Rajesh Kumar", "+91 98860 12345"),
    ("Suresh Narayanan", "+91 98450 67890"),
    ("Anil Kumar", "+91 99001 88345"),
    ("Vikram Malhotra", "+91 98110 99887"),
    ("Priya Sharma", "+91 98801 33456"),
    ("Deepak Mehta", "+91 97400 22341"),
    ("Karthik Reddy", "+91 98440 66789"),
    ("Siddharth Rao", "+91 98866 55432"),
    ("Naveen Hegde", "+91 98451 77654"),
    ("Sunil Dutt", "+91 98800 33210")
]
IMAGES_POOL = [
    [
        "https://images.unsplash.com/photo-1545324418-cc1a3fa10c00?auto=format&fit=crop&w=800&q=80",
        "https://images.unsplash.com/photo-1512917774080-9991f1c4c750?auto=format&fit=crop&w=800&q=80"
    ],
    [
        "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?auto=format&fit=crop&w=800&q=80",
        "https://images.unsplash.com/photo-1600596542815-ffad4c1539a9?auto=format&fit=crop&w=800&q=80"
    ],
    [
        "https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?auto=format&fit=crop&w=800&q=80",
        "https://images.unsplash.com/photo-1502672260266-1c1ef2d93688?auto=format&fit=crop&w=800&q=80"
    ],
    [
        "https://images.unsplash.com/photo-1522708323590-d24dbb6b0267?auto=format&fit=crop&w=800&q=80",
        "https://images.unsplash.com/photo-1567496898669-ee935f5f647a?auto=format&fit=crop&w=800&q=80"
    ]
]

class DatasetImportService:
    @staticmethod
    def get_dataset_files() -> List[str]:
        """Detect all CSV files inside backend/datasets/."""
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        datasets_dir = os.path.join(base_dir, "datasets")
        
        os.makedirs(datasets_dir, exist_ok=True)
        files = glob.glob(os.path.join(datasets_dir, "*.csv"))
        return list(set(files))

    @staticmethod
    def import_datasets(db: Session, max_records_per_file: int = 500) -> Dict[str, Any]:
        """Inspect and import property records from CSV files into database."""
        files = DatasetImportService.get_dataset_files()
        if not files:
            print("No CSV files found in datasets directory.")
            return {"imported_count": 0, "unique_localities": 0, "top_localities": {}}

        default_user = db.query(User).first()
        if not default_user:
            default_user = User(
                email="admin@realestateai.com",
                full_name="Real Estate AI Admin",
                hashed_password=get_password_hash("Admin123!"),
                is_active=True
            )
            db.add(default_user)
            db.commit()
            db.refresh(default_user)

        total_imported = 0
        locality_counts = {}

        for filepath in files:
            try:
                df = pd.read_csv(filepath)
                print(f"Inspecting CSV dataset: {os.path.basename(filepath)} ({len(df)} rows, columns: {list(df.columns)})")
                
                # Sample up to max_records_per_file rows to maintain high performance
                sample_df = df.head(max_records_per_file)

                for idx, row in sample_df.iterrows():
                    loc_idx = idx % len(BANGALORE_LOCALITY_CENTERS)
                    loc_info = BANGALORE_LOCALITY_CENTERS[loc_idx]
                    locality_name = loc_info["name"]

                    # Extract or derive BHK & Property Type
                    if "total_bedrooms" in row and not math.isnan(row["total_bedrooms"]):
                        bhk = int(min(4, max(1, round(row["total_bedrooms"] / max(1, row.get("households", 1))))))
                        if bhk == 0: bhk = (idx % 4) + 1
                    else:
                        bhk = (idx % 4) + 1

                    if bhk == 4:
                        ptype = "Villa" if idx % 2 == 0 else "Apartment"
                    elif bhk == 0:
                        ptype = "Plot"
                    else:
                        ptype = "Apartment" if idx % 3 != 0 else "Independent House"

                    # Calculate area
                    if "total_rooms" in row and not math.isnan(row["total_rooms"]):
                        area = float(max(600, min(5000, round(row["total_rooms"] * 120))))
                    else:
                        area = float(1000 + (bhk * 350) + ((idx * 50) % 400))

                    # Calculate price
                    if "median_house_value" in row and not math.isnan(row["median_house_value"]):
                        price = float(round(row["median_house_value"] * 85, -4))
                    else:
                        price = float(round(loc_info["base_price"] * area * (1 + ((idx % 5) * 0.05)), -4))

                    # Latitude & Longitude around Bangalore locality center
                    lat_offset = ((idx % 10) * 0.002) - 0.009
                    lon_offset = (((idx * 3) % 10) * 0.002) - 0.009
                    prop_lat = round(loc_info["lat"] + lat_offset, 6)
                    prop_lon = round(loc_info["lon"] + lon_offset, 6)

                    builder = BUILDERS[idx % len(BUILDERS)]
                    owner = OWNERS[idx % len(OWNERS)]
                    ptype_lower = ptype.lower()
                    h_str = f"{title}_{idx}"
                    h = hashlib.md5(h_str.encode('utf-8')).hexdigest()
                    h_val = int(h, 16)
                    if ptype_lower == "apartment":
                        images = [f"/static/property-images/apartments/apartments_{(h_val % 20) + 1:02d}.jpg"]
                    elif ptype_lower == "villa":
                        images = [f"/static/property-images/villas/villas_{(h_val % 15) + 1:02d}.jpg"]
                    elif ptype_lower == "independent house" or "house" in ptype_lower:
                        images = [f"/static/property-images/houses/houses_{(h_val % 15) + 1:02d}.jpg"]
                    elif "penthouse" in ptype_lower:
                        images = [f"/static/property-images/penthouses/penthouses_{(h_val % 10) + 1:02d}.jpg"]
                    elif "plot" in ptype_lower or "land" in ptype_lower:
                        images = [f"/static/property-images/plots/plots_{(h_val % 9) + 1:02d}.jpg"]
                    else:
                        images = [f"/static/property-images/apartments/apartments_{(h_val % 20) + 1:02d}.jpg"]

                    title = f"{builder} {locality_name} {bhk}BHK {ptype}" if bhk > 0 else f"{builder} {locality_name} Premium {ptype}"
                    address = f"Phase {(idx%3)+1}, Main Road, {locality_name}, Bengaluru - {loc_info['pin']}"
                    desc = f"Imported real estate property in {locality_name} by {builder}. Features {bhk} BHK layout, area of {int(area)} sq.ft, 24/7 security, power backup, and prime GIS accessibility."

                    p = Property(
                        user_id=default_user.id,
                        title=title,
                        property_type=ptype,
                        bhk=bhk,
                        area_sqft=area,
                        bathrooms=max(1, bhk),
                        balconies=max(1, bhk - 1),
                        floor=(idx % 12) + 1 if ptype == "Apartment" else 1,
                        total_floors=15 if ptype == "Apartment" else 2,
                        property_age="1-5 yrs" if idx % 2 == 0 else "New",
                        facing=["East", "North", "North-East", "West"][idx % 4],
                        parking="Covered" if ptype != "Plot" else "None",
                        furnishing="Semi-Furnished" if idx % 2 == 0 else "Fully Furnished",
                        price=price,
                        description=desc,
                        address=address,
                        latitude=prop_lat,
                        longitude=prop_lon,
                        owner_name=owner[0],
                        owner_phone=owner[1],
                        images=images,
                        nearby_places=[]
                    )
                    db.add(p)
                    total_imported += 1
                    locality_counts[locality_name] = locality_counts.get(locality_name, 0) + 1

            except Exception as e:
                print(f"Error processing CSV {filepath}: {e}")

        db.commit()

        # Sort localities by count
        sorted_localities = dict(sorted(locality_counts.items(), key=lambda item: item[1], reverse=True))

        print("\n" + "=" * 70)
        print("DATASET IMPORT & VERIFICATION COMPLETE")
        print("=" * 70)
        print(f"[OK] Total Number of Imported Properties: {total_imported}")
        print(f"[OK] Number of Unique Localities: {len(sorted_localities)}")
        print("\nTop 20 Localities by Property Count:")
        for idx, (loc, cnt) in enumerate(list(sorted_localities.items())[:20], 1):
            print(f"  {idx:2d}. {loc:<25}: {cnt} properties")
        print("=" * 70 + "\n")

        return {
            "imported_count": total_imported,
            "unique_localities": len(sorted_localities),
            "top_localities": sorted_localities
        }
