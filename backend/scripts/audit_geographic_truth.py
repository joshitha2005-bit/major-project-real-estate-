import sqlite3
import json
from collections import defaultdict

conn = sqlite3.connect("real_estate.db")
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

print("=" * 80)
print("GEOGRAPHIC TRUTH AUDIT")
print("=" * 80)

# 1. Total records
cursor.execute("SELECT COUNT(*) FROM properties")
total_records = cursor.fetchone()[0]

# 2. Coordinate confidence distribution
cursor.execute("SELECT coordinate_confidence, COUNT(*) FROM properties GROUP BY coordinate_confidence")
coord_conf_dist = {r[0]: r[1] for r in cursor.fetchall()}

# 3. Identity confidence distribution
cursor.execute("SELECT identity_confidence, COUNT(*) FROM properties GROUP BY identity_confidence")
identity_conf_dist = {r[0]: r[1] for r in cursor.fetchall()}

print(f"Total Records: {total_records}")
print(f"Coordinate Confidence: {coord_conf_dist}")
print(f"Identity Confidence: {identity_conf_dist}")

# 4. Audit all EXACT properties
print("\n" + "=" * 80)
print("AUDITING ALL 'EXACT' PROPERTIES")
print("=" * 80)
cursor.execute("""
    SELECT id, title, property_name, building_name, project_name, sub_locality, locality,
           formatted_address, latitude, longitude, coordinate_confidence, location_source,
           identity_confidence, source
    FROM properties
    WHERE coordinate_confidence = 'EXACT'
    ORDER BY id ASC
""")
exact_props = cursor.fetchall()
print(f"Total EXACT properties found: {len(exact_props)}")

exact_coords_map = defaultdict(list)
suspicious_exact = []

for ep in exact_props:
    ep_dict = dict(ep)
    coords = (round(ep_dict["latitude"], 5), round(ep_dict["longitude"], 5))
    exact_coords_map[coords].append(ep_dict)
    
    # Check if coords are (12.9716, 77.5946)
    if coords == (12.9716, 77.5946):
        suspicious_exact.append((ep_dict, "Matches Bangalore City-Center Fallback (12.9716, 77.5946)"))

print(f"Unique coordinate pairs among {len(exact_props)} EXACT properties: {len(exact_coords_map)}")

for coords, plist in exact_coords_map.items():
    if len(plist) > 1:
        names = [p["property_name"] or p["title"] for p in plist]
        print(f"  DUPLICATE EXACT COORD: {coords} shared by {len(plist)} properties: {names[:4]}")

# 5. Check repeated coordinates across the entire database
print("\n" + "=" * 80)
print("TOP REPEATED COORDINATES ACROSS ENTIRE DATABASE")
print("=" * 80)
cursor.execute("""
    SELECT round(latitude, 4) as rlat, round(longitude, 4) as rlon, COUNT(*) as cnt,
           COUNT(DISTINCT locality) as dist_locs
    FROM properties
    GROUP BY rlat, rlon
    HAVING cnt > 50
    ORDER BY cnt DESC
    LIMIT 20
""")
top_repeats = cursor.fetchall()
for tr in top_repeats:
    # Get sample localities
    cursor.execute("""
        SELECT DISTINCT locality FROM properties 
        WHERE round(latitude, 4) = ? AND round(longitude, 4) = ?
        LIMIT 5
    """, (tr["rlat"], tr["rlon"]))
    sample_locs = [r[0] for r in cursor.fetchall() if r[0]]
    print(f"  Coords: ({tr['rlat']}, {tr['rlon']}) -> {tr['cnt']} properties across {tr['dist_locs']} distinct localities: {sample_locs}")

# 6. Check the 15 mandatory localities specifically
LOCALITIES = [
    "Koramangala", "Whitefield", "HSR Layout", "Electronic City", "Indiranagar",
    "JP Nagar", "Hebbal", "Yelahanka", "Sarjapur Road", "Bellandur",
    "Marathahalli", "Rajajinagar", "Malleshwaram", "Banashankari", "Devanahalli"
]

print("\n" + "=" * 80)
print("INSPECTING 15 MANDATORY LOCALITIES IN DATABASE")
print("=" * 80)
for loc in LOCALITIES:
    cursor.execute("""
        SELECT id, property_name, building_name, property_type, sub_locality, locality,
               latitude, longitude, coordinate_confidence, identity_confidence
        FROM properties
        WHERE locality LIKE ? OR sub_locality LIKE ?
        ORDER BY 
            CASE WHEN coordinate_confidence = 'EXACT' THEN 0 ELSE 1 END,
            CASE WHEN identity_confidence = 'IDENTITY_RESOLVED' THEN 0 ELSE 1 END,
            id ASC
        LIMIT 3
    """, (f"%{loc}%", f"%{loc}%"))
    loc_rows = cursor.fetchall()
    print(f"\n[{loc.upper()}] (Found {len(loc_rows)} top records):")
    for lr in loc_rows:
        print(f"  ID {lr['id']}: name={lr['property_name'] or lr['building_name']}, type={lr['property_type']}, loc={lr['locality']}, sub={lr['sub_locality']}, coords=({lr['latitude']:.5f}, {lr['longitude']:.5f}), coord_conf={lr['coordinate_confidence']}, id_conf={lr['identity_confidence']}")

conn.close()
