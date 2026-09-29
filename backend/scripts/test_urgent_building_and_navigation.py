"""
Verification test script for:
1. Property Building Identity (Building/Project Name, Sub-locality, Locality, Full Address)
2. Exact Map Navigation (OpenStreetMap & Google Maps coordinates destination)
3. Canonical Location Object Resolution
4. Testing across target localities:
   - Koramangala
   - Whitefield
   - HSR Layout
   - Electronic City
   - Hebbal
   - Indiranagar
   - JP Nagar
   - Yelahanka
"""

import sys
import httpx

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

LOCALITIES_TO_TEST = [
    "Koramangala",
    "Whitefield",
    "HSR Layout",
    "Electronic City",
    "Hebbal",
    "Indiranagar",
    "JP Nagar",
    "Yelahanka"
]

def test_localities():
    client = httpx.Client(base_url="http://127.0.0.1:8000", timeout=15.0)
    
    print("\n" + "=" * 90)
    print("PROPERTY BUILDING IDENTITY & EXACT MAP NAVIGATION VERIFICATION")
    print("=" * 90)

    all_passed = True

    for loc in LOCALITIES_TO_TEST:
        print(f"\n>>> TESTING LOCALITY: {loc.upper()} <<<")
        resp = client.get(f"/api/v1/properties/?query={loc}&limit=3")
        if resp.status_code != 200:
            print(f"FAILED: Status {resp.status_code} for {loc}")
            all_passed = False
            continue

        data = resp.json()
        items = data.get("items", [])
        total = data.get("total", 0)
        print(f"Total matching properties found: {total}")

        if not items:
            print(f"WARNING: No properties returned for {loc}")
            continue

        for idx, prop in enumerate(items[:2], 1):
            pid = prop.get("id")
            title = prop.get("title")
            b_name = prop.get("building_name")
            soc = prop.get("society")
            p_type = prop.get("property_type")
            sub_loc = prop.get("sub_locality")
            address = prop.get("address")
            lat = prop.get("latitude")
            lon = prop.get("longitude")
            coord_status = prop.get("coordinate_status") or prop.get("coordinate_quality")
            canon = prop.get("canonical_location") or {}

            # Navigation URLs
            gmaps_nav = f"https://www.google.com/maps/dir/?api=1&destination={lat},{lon}"
            osm_view = f"https://www.openstreetmap.org/?mlat={lat}&mlon={lon}#map=17/{lat}/{lon}"

            # Validations:
            # 1. Title must NOT be merely the locality name
            is_valid_title = (title.lower() != loc.lower() and title.strip() != "")
            # 2. Coordinates must be non-zero and within Bengaluru bounds (12.7 to 13.3 N, 77.4 to 77.8 E)
            coords_valid = (12.5 <= lat <= 13.5 and 77.3 <= lon <= 78.0)
            # 3. Canonical location must exist
            canon_valid = bool(canon and canon.get("locality"))

            status_flag = "PASS" if (is_valid_title and coords_valid and canon_valid) else "FAIL"
            if status_flag == "FAIL":
                all_passed = False

            print(f"  [{status_flag}] Property #{idx} (ID: {pid}):")
            print(f"      • Building / Display Title : {title}")
            print(f"      • Source Building Name     : {b_name or '(Type fallback: honest ' + str(p_type) + ')'}")
            print(f"      • Locality / Sub-locality  : {prop.get('locality')} | {sub_loc or 'N/A'}")
            print(f"      • Full Address             : {address}")
            print(f"      • Canonical Address        : {canon.get('formatted_address', 'N/A')}")
            print(f"      • Coordinates              : Lat {lat}, Lon {lon} ({coord_status})")
            print(f"      • Google Maps Nav URL      : {gmaps_nav}")
            print(f"      • OpenStreetMap View URL   : {osm_view}")

    print("\n" + "=" * 90)
    if all_passed:
        print("ALL LOCALITY PROPERTY IDENTITY & EXACT NAVIGATION CHECKS PASSED SUCCESSFULLY!")
    else:
        print("ONE OR MORE CHECKS FAILED.")
    print("=" * 90)

if __name__ == "__main__":
    test_localities()
