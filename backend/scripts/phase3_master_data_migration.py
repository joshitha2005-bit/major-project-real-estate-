import sqlite3
import pandas as pd
import numpy as np
import re
import os

DB_PATH = "backend/real_estate.db"
CSV_PATH = "backend/datasets/Bengaluru_House_Data.csv"

# Zone Mapping for Bengaluru Localities
ZONE_MAPPING = {
    "east": [
        "whitefield", "marathahalli", "bellandur", "varthur", "hoodi", "kr puram", "kallugoppa", 
        "brookefield", "kadugodi", "mahadevapura", "hal", "old airport road", "ramamurthy nagar",
        "budigere", "soukya road", "domlur", "indiranagar", "cv raman nagar", "jee vanity"
    ],
    "west": [
        "rajajinagar", "malleshwaram", "vijayanagar", "kengeri", "basaveshwaranagar", "yeshwanthpur",
        "nagasandra", "peenya", "magadi road", "mahalakshmi layout", "chickpet", "okalipuram"
    ],
    "north": [
        "hebbal", "yelahanka", "thanisandra", "hennur", "jahanvi", "bagalur", "devanahalli",
        "kogilu", "jakkur", "sahakara nagar", "nagavara", "rt nagar", "horamavu", "kalyan nagar",
        "hegde nagar", "vidyaranyapura", "hbr layout", "mathikere", "tumkur road"
    ],
    "south": [
        "koramangala", "hsr layout", "electronic city", "jp nagar", "jayanagar", "banashankari",
        "btm layout", "bommanahalli", "bannerghatta road", "begur", "hosa road", "singasandra",
        "arekere", "hulimavu", "kanakapura road", "gottigere", "uttarahalli", "kumaraswamy layout"
    ],
    "central": [
        "mg road", "brigade road", "richmond town", "lavelle road", "cubbon park", "vasanth nagar",
        "frazer town", "benson town", "cox town", "cunningham road", "ulsoor", "residency road",
        "sadashivanagar", "shanthi nagar", "wilson garden"
    ],
    "outer": [
        "sarjapur", "sarjapur road", "attibele", "chandapura", "hosur road", "anekal", "bidadi",
        "nelamangala", "doddaballapur"
    ]
}

def get_zone_for_locality(locality: str) -> str:
    loc_lower = str(locality).lower()
    for zone, keywords in ZONE_MAPPING.items():
        for kw in keywords:
            if kw in loc_lower:
                return zone.title() + " Bengaluru"
    return "South Bengaluru" # Default prominent region fallback for unmatched Bengaluru suburbs

def parse_sqft(sqft_str):
    if pd.isna(sqft_str):
        return None
    sqft_str = str(sqft_str).strip()
    # Check range like "1200 - 1500"
    if "-" in sqft_str:
        parts = sqft_str.split("-")
        try:
            val1 = float(re.sub(r"[^\d.]", "", parts[0]))
            val2 = float(re.sub(r"[^\d.]", "", parts[1]))
            return round((val1 + val2) / 2.0, 2)
        except Exception:
            return None
    # Single value parsing (supporting Sq. Meter, Sq. Yards conversion if applicable)
    try:
        if "Sq. Meter" in sqft_str:
            val = float(re.sub(r"[^\d.]", "", sqft_str))
            return round(val * 10.7639, 2)
        elif "Perch" in sqft_str:
            val = float(re.sub(r"[^\d.]", "", sqft_str))
            return round(val * 272.25, 2)
        elif "Acres" in sqft_str:
            val = float(re.sub(r"[^\d.]", "", sqft_str))
            return round(val * 43560, 2)
        elif "Guntha" in sqft_str:
            val = float(re.sub(r"[^\d.]", "", sqft_str))
            return round(val * 1089, 2)
        elif "Grounds" in sqft_str:
            val = float(re.sub(r"[^\d.]", "", sqft_str))
            return round(val * 2400, 2)
        else:
            val = float(re.sub(r"[^\d.]", "", sqft_str))
            return round(val, 2)
    except Exception:
        return None

def normalize_area_type(area_type_str):
    if not area_type_str or pd.isna(area_type_str):
        return "super_built_up"
    s = str(area_type_str).lower()
    if "super" in s:
        return "super_built_up"
    elif "plot" in s:
        return "plot"
    elif "carpet" in s:
        return "carpet"
    elif "built" in s:
        return "built_up"
    return "super_built_up"

def clean_locality_and_sublocality(loc_str):
    if not loc_str or pd.isna(loc_str):
        return "Bengaluru", None
    
    loc = str(loc_str).strip()
    # Normalize common typos
    loc = re.sub(r"\s+", " ", loc)
    
    # Extract sub-locality if comma or sector/phase present
    sub_loc = None
    if "," in loc:
        parts = [p.strip() for p in loc.split(",") if p.strip()]
        if len(parts) >= 2:
            loc = parts[0]
            sub_loc = ", ".join(parts[1:])
    elif "phase" in loc.lower() or "sector" in loc.lower() or "block" in loc.lower() or "stage" in loc.lower():
        sub_loc = loc
    
    return loc, sub_loc

def migrate_and_clean_database():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 1. Add missing master data columns if not present
    existing_cols = [col[1] for col in cursor.execute("PRAGMA table_info(properties)").fetchall()]
    
    new_columns = {
        "source_listing_id": "VARCHAR(100)",
        "city": "VARCHAR(100) DEFAULT 'Bengaluru'",
        "sub_locality": "VARCHAR(255)",
        "zone": "VARCHAR(100)",
        "society": "VARCHAR(255)",
        "area_type": "VARCHAR(100)",
        "price_inr": "FLOAT",
        "transaction_type": "VARCHAR(50) DEFAULT 'sale'",
        "price_per_sqft": "FLOAT",
        "availability": "VARCHAR(100)",
        "coordinate_quality": "VARCHAR(50)",
        "last_verified_at": "DATETIME"
    }
    
    for col_name, col_type in new_columns.items():
        if col_name not in existing_cols:
            print(f"Adding column '{col_name}' to properties table...")
            cursor.execute(f"ALTER TABLE properties ADD COLUMN {col_name} {col_type}")
            
    conn.commit()

    # 2. Audit before state
    cursor.execute("SELECT COUNT(*) FROM properties")
    total_props = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM properties WHERE round(latitude, 4)=12.9716 AND round(longitude, 4)=77.5946")
    blr_center_fallback = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM properties WHERE round(latitude, 4)=12.9696 AND round(longitude, 4)=77.7497")
    whitefield_fallback = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM properties WHERE round(latitude, 4)=12.9107 AND round(longitude, 4)=77.6970 OR round(latitude, 4)=12.9252 AND round(longitude, 4)=77.7274")
    sarjapur_fallback = cursor.fetchone()[0]
    
    print("================ BEFORE MIGRATION AUDIT ================")
    print(f"Total Properties: {total_props}")
    print(f"Bengaluru Center Fallback Properties: {blr_center_fallback}")
    print(f"Whitefield Fallback Properties: {whitefield_fallback}")
    print(f"Sarjapur Fallback Properties: {sarjapur_fallback}")
    print("========================================================")
    
    # 3. Read original CSV to map original area_type, availability, society, etc.
    df_csv = pd.read_csv(CSV_PATH)
    
    # We will update each property record
    cursor.execute("SELECT id, title, locality, address, latitude, longitude, area_sqft, price, source_type, listing_type FROM properties")
    rows = cursor.fetchall()
    
    exact_count = 0
    approx_count = 0
    missing_count = 0
    updated_count = 0
    
    for row in rows:
        p_id, title, loc, addr, lat, lon, area_sqft, price, source_type, listing_type = row
        
        # Determine coordinate quality
        # Known fallback centroids:
        # Bengaluru Center: (12.9716, 77.5946)
        # Whitefield: (12.9696, 77.7497)
        # Sarjapur: (12.9107, 77.6970) or (12.9252, 77.7274)
        # JP Nagar: (12.9077, 77.5854)
        # Electronic City: (12.8436, 77.6687)
        # Yelahanka: (13.1007, 77.5963)
        # Hebbal: (13.0354, 77.5988) or (13.0358, 77.597)
        # Marathahalli: (12.9569, 77.7011) or (12.9591, 77.6974)
        
        r_lat = round(lat, 4) if lat is not None else None
        r_lon = round(lon, 4) if lon is not None else None
        
        coord_quality = "EXACT"
        if r_lat is None or r_lon is None or (r_lat == 0 and r_lon == 0):
            coord_quality = "MISSING"
            missing_count += 1
        elif (r_lat == 12.9716 and r_lon == 77.5946) or \
             (r_lat == 12.9696 and r_lon == 77.7497) or \
             (r_lat == 12.9107 and r_lon == 77.6970) or \
             (r_lat == 12.9252 and r_lon == 77.7274) or \
             (r_lat == 12.9077 and r_lon == 77.5854) or \
             (r_lat == 12.8436 and r_lon == 77.6687) or \
             (r_lat == 13.1007 and r_lon == 77.5963) or \
             (r_lat in [13.0354, 13.0358] and r_lon in [77.5988, 77.5970]) or \
             (r_lat in [12.9569, 12.9591] and r_lon in [77.7011, 77.6974]):
            coord_quality = "LOCALITY_APPROXIMATE"
            approx_count += 1
        else:
            exact_count += 1

        # Locality & Sub-locality normalization
        norm_loc, sub_loc = clean_locality_and_sublocality(loc)
        zone = get_zone_for_locality(norm_loc)
        
        # Transaction Type ('sale' or 'rent')
        trans_type = "rent" if (listing_type and str(listing_type).lower() == "rent") else "sale"
        
        # Price INR normalization
        # In DB, price is already stored in total INR or Lakhs. Let's verify:
        # If price < 10000 and source_type == 'historical_dataset', price was originally in Lakhs (e.g. 39.07 -> 3,907,000 INR).
        price_inr = price
        if price is not None and price < 10000.0 and trans_type == "sale":
            price_inr = float(price * 100000.0)
            
        price_per_sqft = None
        if price_inr and area_sqft and area_sqft > 0:
            price_per_sqft = round(price_inr / area_sqft, 2)
            
        # Map original CSV fields if historical_dataset
        # For historical_dataset, row index in CSV corresponds to ID or order
        area_type = "super_built_up"
        society = None
        availability = "Ready To Move"
        source_listing_id = f"BLR-HIST-{p_id}" if source_type == "historical_dataset" else f"BLR-LIST-{p_id}"
        
        if source_type == "historical_dataset" and (p_id - 1) < len(df_csv):
            csv_row = df_csv.iloc[p_id - 1]
            area_type = normalize_area_type(csv_row.get("area_type"))
            society_raw = csv_row.get("society")
            society = str(society_raw).strip() if pd.notna(society_raw) else None
            avail_raw = csv_row.get("availability")
            availability = str(avail_raw).strip() if pd.notna(avail_raw) else None
            
        # Clean fake metadata defaults for historical records where original source did NOT provide furnishing/parking/floor
        # For historical records, original CSV didn't have furnishing or parking. Set to None if historical.
        if source_type == "historical_dataset":
            cursor.execute("""
                UPDATE properties SET
                    source_listing_id = ?,
                    city = 'Bengaluru',
                    locality = ?,
                    sub_locality = ?,
                    zone = ?,
                    society = ?,
                    area_type = ?,
                    price_inr = ?,
                    price = ?,
                    transaction_type = ?,
                    price_per_sqft = ?,
                    availability = ?,
                    coordinate_quality = ?,
                    furnishing = NULL,
                    parking = NULL,
                    floor = NULL,
                    total_floors = NULL,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (source_listing_id, norm_loc, sub_loc, zone, society, area_type, price_inr, price_inr, trans_type, price_per_sqft, availability, coord_quality, p_id))
        else:
            cursor.execute("""
                UPDATE properties SET
                    source_listing_id = ?,
                    city = 'Bengaluru',
                    locality = ?,
                    sub_locality = ?,
                    zone = ?,
                    society = ?,
                    area_type = ?,
                    price_inr = ?,
                    price = ?,
                    transaction_type = ?,
                    price_per_sqft = ?,
                    availability = ?,
                    coordinate_quality = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (source_listing_id, norm_loc, sub_loc, zone, society, area_type, price_inr, price_inr, trans_type, price_per_sqft, availability, coord_quality, p_id))
            
        updated_count += 1

    conn.commit()
    
    print("================ AFTER MIGRATION AUDIT ================")
    print(f"Updated Properties: {updated_count}")
    print(f"Exact Coordinates: {exact_count}")
    print(f"Locality Approximate Coordinates: {approx_count}")
    print(f"Missing Coordinates: {missing_count}")
    print("=======================================================")
    
    # 4. Duplicate Coordinate Cluster Analysis
    cursor.execute("""
        SELECT round(latitude, 4), round(longitude, 4), COUNT(*), GROUP_CONCAT(DISTINCT locality)
        FROM properties
        GROUP BY round(latitude, 4), round(longitude, 4)
        HAVING COUNT(*) > 10
        ORDER BY COUNT(*) DESC
        LIMIT 10
    """)
    clusters = cursor.fetchall()
    print("\nSuspicious Coordinate Clusters (>10 properties at exact same lat/lon):")
    for cl in clusters:
        print(f"  Lat/Lon ({cl[0]}, {cl[1]}): {cl[2]} properties | Localities: {cl[3][:100]}...")

    conn.close()

if __name__ == "__main__":
    migrate_and_clean_database()
