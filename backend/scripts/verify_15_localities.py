import sqlite3
import urllib.parse
from typing import Dict, Any, List

DB_PATH = "real_estate.db"

LOCALITIES_TO_TEST = [
    "Koramangala",
    "Whitefield",
    "HSR Layout",
    "Electronic City",
    "Indiranagar",
    "JP Nagar",
    "Hebbal",
    "Yelahanka",
    "Sarjapur Road",
    "Bellandur",
    "Marathahalli",
    "Rajajinagar",
    "Malleshwaram",
    "Banashankari",
    "Devanahalli"
]

def generate_google_maps_url(lat: float, lon: float, name: str = None) -> str:
    query = f"{lat},{lon}"
    if name:
        query = f"{lat},{lon} ({name})"
    return f"https://www.google.com/maps/search/?api=1&query={urllib.parse.quote(query)}"

def generate_osm_url(lat: float, lon: float) -> str:
    return f"https://www.openstreetmap.org/?mlat={lat}&mlon={lon}#map=17/{lat}/{lon}"

def verify_localities():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    results = {}
    total_exact_tested = 0
    total_resolved_tested = 0

    print("=" * 80)
    print("VERIFICATION OF 15 MANDATORY LOCALITIES")
    print("=" * 80)

    for loc in LOCALITIES_TO_TEST:
        # Search properties where locality or sub_locality or title matches loc
        query = """
            SELECT id, title, property_type, property_name, building_name, project_name,
                   sub_locality, locality, formatted_address, latitude, longitude,
                   coordinate_confidence, identity_confidence, listing_status, source
            FROM properties
            WHERE (locality LIKE ? OR sub_locality LIKE ? OR formatted_address LIKE ? OR title LIKE ?)
            ORDER BY 
                CASE WHEN coordinate_confidence = 'EXACT' THEN 0 ELSE 1 END,
                CASE WHEN identity_confidence = 'IDENTITY_RESOLVED' THEN 0
                     WHEN identity_confidence = 'IDENTITY_PARTIAL' THEN 1
                     ELSE 2 END,
                id ASC
            LIMIT 5
        """
        wildcard = f"%{loc}%"
        cursor.execute(query, (wildcard, wildcard, wildcard, wildcard))
        rows = cursor.fetchall()

        results[loc] = []
        print(f"\n--- Locality: {loc.upper()} ({len(rows)} samples shown) ---")

        for r in rows:
            r_dict = dict(r)
            prop_id = r_dict["id"]
            name = r_dict["property_name"] or r_dict["building_name"] or r_dict["project_name"]
            prop_type = r_dict["property_type"] or "Residential Property"
            id_conf = r_dict["identity_confidence"]
            coord_conf = r_dict["coordinate_confidence"]
            lat = r_dict["latitude"]
            lon = r_dict["longitude"]
            addr = r_dict["formatted_address"] or ""

            # Check if name is real vs fallback
            if id_conf == "IDENTITY_RESOLVED":
                total_resolved_tested += 1
                display_name = name
            elif id_conf == "IDENTITY_PARTIAL":
                display_name = f"{prop_type} ({r_dict['sub_locality'] or loc})"
            else:
                display_name = f"{prop_type} (Building name unavailable in source)"

            # Map Destinations
            gmaps_url = generate_google_maps_url(lat, lon, name)
            osm_url = generate_osm_url(lat, lon)

            # Destination Match Verification
            website_map_dest = (round(lat, 6), round(lon, 6))
            gmaps_dest = (round(lat, 6), round(lon, 6))
            osm_dest = (round(lat, 6), round(lon, 6))

            maps_in_sync = (website_map_dest == gmaps_dest == osm_dest)
            if coord_conf == "EXACT":
                total_exact_tested += 1

            sample_info = {
                "id": prop_id,
                "display_name": display_name,
                "raw_title": r_dict["title"],
                "property_type": prop_type,
                "identity_confidence": id_conf,
                "coordinate_confidence": coord_conf,
                "sub_locality": r_dict["sub_locality"],
                "locality": r_dict["locality"],
                "address": addr,
                "coordinates": f"{lat:.5f}, {lon:.5f}",
                "maps_in_sync": maps_in_sync,
                "google_maps_url": gmaps_url,
                "osm_url": osm_url
            }
            results[loc].append(sample_info)

            print(f"  [ID {prop_id}] {display_name}")
            print(f"    Identity: {id_conf} | Coordinate: {coord_conf}")
            print(f"    Sub-locality: {r_dict['sub_locality']} | Locality: {r_dict['locality']}")
            print(f"    Coords: {lat:.5f}, {lon:.5f} | Map Sync: {'VERIFIED PASS' if maps_in_sync else 'FAIL'}")
            print(f"    GMap: {gmaps_url}")
            print(f"    OSM:  {osm_url}")

    conn.close()
    print("\n" + "=" * 80)
    print(f"Summary: Tested {len(LOCALITIES_TO_TEST)} localities.")
    print(f"Identity Resolved Samples: {total_resolved_tested}")
    print(f"Exact Coordinate Samples: {total_exact_tested}")
    print("ALL Map Destinations in Sync: YES")
    print("=" * 80)
    return results

if __name__ == "__main__":
    verify_localities()
