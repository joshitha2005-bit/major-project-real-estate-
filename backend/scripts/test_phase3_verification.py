import asyncio
import sqlite3
import httpx
import math
from typing import Dict, Any, List

DB_PATH = "backend/real_estate.db"

import sys
sys.path.append('backend')
from app.core.config import settings

LOCALITIES_TO_TEST = [
    ("HSR Layout", "hsr layout"),
    ("Koramangala", "koramangala"),
    ("Whitefield", "whitefield"),
    ("Electronic City", "electronic city"),
    ("Sarjapur Road", "sarjapur"),
    ("North Bengaluru (Hebbal)", "hebbal"),
    ("Central Bengaluru (Indiranagar)", "indiranagar")
]

# Geoapify category map test
GEOAPIFY_CATEGORIES = {
    "Hospitals": ["healthcare.hospital", "healthcare.clinic"],
    "Parks": ["leisure.park", "landuse.recreation_ground"],
    "Metro Stations": ["building.transportation", "public_transport.subway", "public_transport.subway_entrance", "public_transport.train"],
    "Schools": ["education.school"]
}

def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return round(6371.0 * c, 3)

async def test_geoapify_nearby(lat: float, lon: float, radius_m: int, api_key: str = None) -> Dict[str, Any]:
    url = "https://api.geoapify.com/v2/places"
    results = {}
    if not api_key:
        api_key = settings.GEOAPIFY_API_KEY
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        for cat_name, geo_cats in GEOAPIFY_CATEGORIES.items():
            cats_str = ",".join(geo_cats)
            params = {
                "categories": cats_str,
                "filter": f"circle:{lon},{lat},{radius_m}",
                "bias": f"proximity:{lon},{lat}",
                "limit": 5,
                "apiKey": api_key
            }
            try:
                resp = await client.get(url, params=params)
                if resp.status_code == 200:
                    data = resp.json()
                    feats = data.get("features", [])
                    places = []
                    for f in feats:
                        props = f.get("properties", {})
                        geom = f.get("geometry", {})
                        coords = geom.get("coordinates", [lon, lat])
                        p_lon, p_lat = coords[0], coords[1]
                        dist_km = haversine_km(lat, lon, p_lat, p_lon)
                        places.append({
                            "name": props.get("name") or props.get("formatted") or f"Unnamed {cat_name[:-1]}",
                            "lat": p_lat,
                            "lon": p_lon,
                            "dist_km": dist_km
                        })
                    results[cat_name] = places
                else:
                    results[cat_name] = []
            except Exception as e:
                results[cat_name] = []
    return results

async def run_verification():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("==========================================================================")
    print("PHASE 3 — BENGALURU MASTER DATA & COORDINATE ACCURACY VERIFICATION REPORT")
    print("==========================================================================")

    print("\n--- TEST 1: 7 BENGALURU LOCALITIES PROPERTY DATA & COORDINATE QUALITY ---")
    
    sample_coords_for_amenities = []

    for label, kw in LOCALITIES_TO_TEST:
        cursor.execute("""
            SELECT id, title, locality, sub_locality, zone, area_sqft, price, price_per_sqft, latitude, longitude, coordinate_quality, source_type, transaction_type
            FROM properties
            WHERE lower(locality) LIKE ? OR lower(address) LIKE ?
            ORDER BY id ASC
            LIMIT 1
        """, (f"%{kw}%", f"%{kw}%"))
        
        row = cursor.fetchone()
        if row:
            p_id, title, loc, sub_loc, zone, area, price, p_sqft, lat, lon, coord_qual, src_type, trans_type = row
            print(f"\n[+] Locality Test Target: {label}")
            print(f"   Property ID: {p_id}")
            print(f"   Title: {title}")
            print(f"   Locality / Sub-Locality: {loc} | Sub: {sub_loc or 'N/A'}")
            print(f"   Zone: {zone}")
            print(f"   Area: {area} sqft | Price: INR {price:,.2f} | Transaction: {trans_type.upper()}")
            print(f"   Price/sqft: INR {p_sqft:,.2f}/sqft" if p_sqft else "   Price/sqft: N/A")
            print(f"   Coordinates: ({lat}, {lon})")
            print(f"   Coordinate Quality: {coord_qual}")
            print(f"   Source Provenance: {src_type}")
            
            sample_coords_for_amenities.append((label, lat, lon, coord_qual))
        else:
            print(f"\n[!] Locality '{label}' not found in database sample search.")

    print("\n--------------------------------------------------------------------------")
    print("--- TEST 2: NEARBY AMENITIES (GEOAPIFY API TAXONOMY & DISTANCE SORT) ---")
    print("--------------------------------------------------------------------------")

    test_point = sample_coords_for_amenities[0] if sample_coords_for_amenities else ("HSR Layout", 12.9116, 77.6389, "LOCALITY_APPROXIMATE")
    lbl, lat, lon, qual = test_point
    print(f"\nFetching Nearby Amenities around {lbl} ({lat}, {lon}) [Coordinate Quality: {qual}]...")

    for r_km, r_m in [(1, 1000), (5, 5000)]:
        print(f"\n  Radius: {r_km} km ({r_m} meters)")
        amenities = await test_geoapify_nearby(lat, lon, r_m)
        for cat_name, places in amenities.items():
            print(f"    Category: {cat_name} ({len(places)} found)")
            for p in places[:3]:
                print(f"      - {p['name']} | Distance: {p['dist_km']} km | Coords: ({p['lat']:.4f}, {p['lon']:.4f})")

    # Aggregate Data Quality Stats
    print("\n--------------------------------------------------------------------------")
    print("--- TEST 3: BEFORE vs AFTER DATA FOUNDATION METRICS ---")
    print("--------------------------------------------------------------------------")

    cursor.execute("SELECT COUNT(*) FROM properties")
    total_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM properties WHERE coordinate_quality = 'EXACT'")
    exact_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM properties WHERE coordinate_quality = 'LOCALITY_APPROXIMATE'")
    approx_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM properties WHERE coordinate_quality = 'MISSING'")
    missing_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM properties WHERE price_inr IS NOT NULL AND price_inr > 0")
    valid_price = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM properties WHERE area_sqft IS NOT NULL AND area_sqft > 0")
    valid_area = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM properties WHERE price_per_sqft IS NOT NULL AND price_per_sqft > 0")
    valid_p_sqft = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM properties WHERE transaction_type = 'sale'")
    sale_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM properties WHERE transaction_type = 'rent'")
    rent_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(DISTINCT locality) FROM properties")
    norm_localities = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(DISTINCT sub_locality) FROM properties WHERE sub_locality IS NOT NULL")
    norm_sub_localities = cursor.fetchone()[0]

    print(f"  Total Master Properties: {total_count}")
    print(f"  Exact Coordinates: {exact_count}")
    print(f"  Locality Approximate Coordinates: {approx_count}")
    print(f"  Missing Coordinates: {missing_count}")
    print(f"  Fallback Coordinates Flagged/Categorized: {approx_count}")
    print(f"  Valid Area Records: {valid_area}")
    print(f"  Valid Price INR Records: {valid_price}")
    print(f"  Valid Price/sqft Records: {valid_p_sqft}")
    print(f"  Sale Records: {sale_count}")
    print(f"  Rent Records: {rent_count}")
    print(f"  Normalized Localities: {norm_localities}")
    print(f"  Normalized Sub-Localities: {norm_sub_localities}")
    print("==========================================================================")

    conn.close()

if __name__ == "__main__":
    asyncio.run(run_verification())
