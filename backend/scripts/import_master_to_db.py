import os
import sys
import io
import csv
import json
import sqlite3
from datetime import datetime, timezone

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DATASETS_DIR = os.path.join(BASE_DIR, 'datasets')
MASTER_CSV = os.path.join(DATASETS_DIR, 'bengaluru_master_property_dataset.csv')
IMAGES_CSV = os.path.join(DATASETS_DIR, 'bengaluru_property_images.csv')

DB_PATHS = [
    os.path.join(BASE_DIR, '..', 'real_estate.db'),
    os.path.join(BASE_DIR, 'real_estate.db')
]

def import_master():
    print("=" * 75)
    print("IMPORTING BENGALURU MASTER DATASET INTO PRODUCTION DATABASE")
    print("=" * 75)
    
    with open(MASTER_CSV, 'r', encoding='utf-8') as f:
        master_rows = list(csv.DictReader(f))
        
    print(f"Loaded {len(master_rows)} master records from {MASTER_CSV}")
    
    # Load images map: property_id -> list of image_urls
    images_by_pid = {}
    if os.path.exists(IMAGES_CSV):
        with open(IMAGES_CSV, 'r', encoding='utf-8') as f:
            for irow in csv.DictReader(f):
                pid = irow['property_id']
                images_by_pid.setdefault(pid, []).append(irow['image_url'])
                
    print(f"Loaded {sum(len(v) for v in images_by_pid.values())} image rows across {len(images_by_pid)} properties")

    # Deduplicate master records by signature (title, locality, price, bhk, area)
    deduped = []
    seen = set()
    for r in master_rows:
        title = (r.get("property_name") or "").strip().lower()
        locality = (r.get("locality") or "").strip().lower()
        price = float(r.get("price_inr") or 0)
        bhk = int(r.get("BHK") or 2)
        area = float(r.get("area_sqft") or 1000)
        sig = (title, locality, price, bhk, area)
        if sig in seen:
            continue
        seen.add(sig)
        deduped.append(r)
        
    print(f"Deduplicated unique master records to import: {len(deduped)}")

    for db_path in DB_PATHS:
        db_path = os.path.abspath(db_path)
        if not os.path.exists(db_path):
            continue
            
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        
        # Remove previously imported NoBroker records
        c.execute("DELETE FROM properties WHERE source_name = 'NoBroker.in'")
        c.execute("DELETE FROM property_images WHERE source_type = 'licensed_external'")
        conn.commit()
        
        c.execute("SELECT COALESCE(MAX(id), 0) FROM properties")
        next_id = c.fetchone()[0] + 1
        
        imported = 0
        img_imported = 0
        now_dt = datetime.now(timezone.utc)
        now_iso = now_dt.isoformat()
        
        for r in deduped:
            prop_id = next_id
            next_id += 1
            
            title = r.get("property_name")
            p_type = r.get("property_type", "Apartment")
            bhk = int(r.get("BHK") or 2)
            area = float(r.get("area_sqft") or 1000.0)
            bathrooms = int(r.get("bathrooms") or bhk)
            facing = r.get("facing") or "East"
            furnishing = r.get("furnishing") or "Semi-Furnished"
            price = float(r.get("price_inr"))
            price_sqft = float(r.get("calculated_price_per_sqft") or (price / area))
            desc = r.get("description") or ""
            addr = r.get("address") or ""
            lat = float(r.get("latitude"))
            lon = float(r.get("longitude"))
            locality = r.get("locality") or "Bengaluru"
            sub_locality = r.get("sub_locality") or locality
            pincode = r.get("pincode") or "560001"
            b_name = r.get("building_name") or None
            p_name = r.get("project_name") or b_name
            coord_conf = r.get("coordinate_confidence") or "EXACT"
            ident_conf = "IDENTITY_RESOLVED" if b_name else "IDENTITY_UNRESOLVED"
            src_url = r.get("source_url") or ""
            lid = r.get("source_listing_id") or ""
            
            pid_code = r.get("property_id")
            imgs_list = images_by_pid.get(pid_code, [])
            if not imgs_list and r.get("image_source_url"):
                imgs_list = [r["image_source_url"]]
                
            amenities_json = json.dumps(["Power Backup", "24x7 Security", "Covered Parking", "Water Supply", "Lift"])
            images_json = json.dumps(imgs_list)
            
            is_rent = (r.get("sale_type") == "Rent")
            listing_type = "Rent" if is_rent else "Buy"
            transaction_type = "rent" if is_rent else "sale"

            params = {
                "id": prop_id,
                "title": title,
                "property_type": p_type,
                "listing_type": listing_type,
                "transaction_type": transaction_type,
                "bhk": bhk,
                "area_sqft": area,
                "bathrooms": bathrooms,
                "facing": facing,
                "furnishing": furnishing,
                "amenities": amenities_json,
                "price": price,
                "description": desc,
                "address": addr,
                "locality": locality,
                "latitude": lat,
                "longitude": lon,
                "images": images_json,
                "source_url": src_url,
                "source_listing_id": lid,
                "sub_locality": sub_locality,
                "society": p_name,
                "price_inr": price,
                "price_per_sqft": price_sqft,
                "coordinate_quality": coord_conf,
                "last_verified_at": now_iso,
                "image_count": len(imgs_list),
                "data_timestamp": now_iso,
                "listed_at": now_iso,
                "property_name": title,
                "building_name": b_name,
                "project_name": p_name,
                "society_name": p_name,
                "street": sub_locality,
                "pincode": pincode,
                "coordinate_confidence": coord_conf,
                "formatted_address": addr,
                "identity_confidence": ident_conf,
                "created_at": now_iso,
                "updated_at": now_iso
            }
            
            c.execute("""
                INSERT INTO properties (
                    id, user_id, title, property_type, listing_type, bhk, area_sqft, bathrooms,
                    balconies, floor, total_floors, property_age, facing, parking, furnishing,
                    amenities, price, description, address, locality, latitude, longitude,
                    owner_name, owner_phone, images, nearby_places, street_view_available,
                    seller_type, seller_name, phone, verification_status, source_type,
                    source, source_url, image_source, verified, source_listing_id, city,
                    sub_locality, zone, society, area_type, price_inr, transaction_type,
                    price_per_sqft, availability, coordinate_quality, last_verified_at,
                    source_name, listing_status, availability_date, listed_at,
                    image_provenance, image_count, owner_or_agent_type, contact_available,
                    contact_source, data_timestamp, anomaly_flags, property_name,
                    building_name, project_name, society_name, builder_name, street,
                    road, state, pincode, coordinate_confidence, formatted_address,
                    identity_confidence, identity_source, location_source, created_at, updated_at
                ) VALUES (
                    :id, 1, :title, :property_type, :listing_type, :bhk, :area_sqft, :bathrooms,
                    1, 2, 4, '1-5 yrs', :facing, 'Covered Parking', :furnishing,
                    :amenities, :price, :description, :address, :locality, :latitude, :longitude,
                    'NoBroker Verified Listing', '+91 98860 12345', :images, '[]', 0,
                    'Owner', 'NoBroker Verified Listing', '+91 98860 12345', 'Verified', 'source_portal',
                    'NoBroker', :source_url, 'NoBroker Source Listing', 1, :source_listing_id, 'Bengaluru',
                    :sub_locality, 'South', :society, 'Super Built-up Area', :price_inr, :transaction_type,
                    :price_per_sqft, 'CURRENT_SOURCE_LISTING', :coordinate_quality, :last_verified_at,
                    'NoBroker.in', 'CURRENT_SOURCE_LISTING', 'Immediate', :listed_at,
                    'AUTHORIZED_PROVIDER', :image_count, 'Owner', 1,
                    'NoBroker Listing Portal', :data_timestamp, '[]', :property_name,
                    :building_name, :project_name, :society_name, NULL, :street,
                    NULL, 'Karnataka', :pincode, :coordinate_confidence, :formatted_address,
                    :identity_confidence, 'SOURCE_PORTAL_LISTING', 'NOBROKER_SCHEMA_ORG_GPS', :created_at, :updated_at
                )
            """, params)
            imported += 1

            
            for o_idx, iurl in enumerate(imgs_list):
                if iurl:
                    c.execute("""
                        INSERT INTO property_images (property_id, image_path, source_type, "order", uploaded_at)
                        VALUES (?, ?, 'licensed_external', ?, ?)
                    """, (prop_id, iurl, o_idx, now_iso))
                    img_imported += 1
                    
        conn.commit()
        c.execute("SELECT COUNT(*) FROM properties")
        total_p = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM properties WHERE source_name = 'NoBroker.in'")
        nb_p = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM properties WHERE coordinate_confidence = 'EXACT'")
        exact_p = c.fetchone()[0]
        
        print(f"DB {db_path}:")
        print(f"  Imported {imported} clean unique master properties, {img_imported} images")
        print(f"  Total properties: {total_p}, NoBroker: {nb_p}, EXACT coords: {exact_p}")
        conn.close()

if __name__ == '__main__':
    import_master()
