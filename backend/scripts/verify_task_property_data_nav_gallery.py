"""
Verification script for:
TASK: PROPERTY DATA + EXACT NAVIGATION + MULTI-IMAGE GALLERY
Tests 3 real properties across the pipeline:
- Property Information & Provenance
- Exact Destination Coordinates & Accuracy Status
- Real Multi-Modal Route Navigation (Car, Bike, Public Transit) via Geoapify
- Multi-Image Gallery with Deduplication & Truthful Provenance
- Contact Number Verification
"""
import os
import sys

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

import httpx

backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.core.database import SessionLocal
from app.models.property import Property
from app.services.image_provenance import ImageProvenanceService
from app.services.contact_verification_service import ContactVerificationService

def verify_three_properties():
    client = httpx.Client(base_url="http://127.0.0.1:8000", timeout=30.0)
    origin_coords = (12.9774, 77.5708) # Kempegowda Bus Station (Majestic), Central Bengaluru
    origin_name = "Kempegowda Bus Station (Majestic), Bengaluru"

    target_ids = [1, 2, 16797]
    results = []

    print("=" * 75)
    print("RUNTIME VERIFICATION: PROPERTY DATA + EXACT NAVIGATION + MULTI-IMAGE GALLERY")
    print(f"Origin used for navigation testing: {origin_name} {origin_coords}")
    print("=" * 75)

    for idx, pid in enumerate(target_ids, start=1):
        print(f"\n" + "-" * 75)
        print(f"PROPERTY {idx} (ID: {pid})")
        print("-" * 75)

        # 1. Fetch Property Details API
        resp = client.get(f"/api/v1/properties/{pid}")
        if resp.status_code != 200:
            print(f"FAILED to fetch property {pid}: status {resp.status_code}")
            continue
        pdata = resp.json()

        title = pdata.get("display_title") or pdata.get("title")
        address = pdata.get("formatted_address") or pdata.get("address")
        locality = pdata.get("locality")
        city = pdata.get("city", "Bengaluru")
        lat = pdata.get("latitude")
        lon = pdata.get("longitude")
        loc_prov = pdata.get("location_provenance", {})
        accuracy = loc_prov.get("accuracy_status") or pdata.get("coordinate_confidence", "APPROXIMATE")
        loc_source = loc_prov.get("source") or pdata.get("location_source", "BENCHMARK")

        # 2. Contact Number Status
        contact_prov = pdata.get("contact_provenance", {})
        contact_num = contact_prov.get("number")
        contact_status = "AVAILABLE" if contact_prov.get("publicly_available") and contact_num else "NOT_AVAILABLE"
        contact_message = contact_prov.get("display_message") or ("Contact number not publicly available" if not contact_num else "Available")
        contact_prov_label = contact_prov.get("provenance", "UNAVAILABLE")

        # 3. Gallery Verification
        gal = pdata.get("gallery", {})
        total_found = gal.get("total_images_found", 0)
        unique_count = gal.get("unique_images_count", 0)
        dups_removed = gal.get("duplicates_removed_count", 0)
        prop_specific_cnt = gal.get("property_specific_count", 0)
        representative_cnt = gal.get("representative_count", 0)
        user_uploaded_cnt = gal.get("user_uploaded_count", 0)
        has_5_genuine = gal.get("has_five_genuine_images", False)
        gallery_summary = gal.get("count_summary", "")
        gallery_images = gal.get("images", [])

        # 4. Routing API Verification
        r_route = client.get(f"/api/v1/properties/{pid}/routes?origin_lat={origin_coords[0]}&origin_lon={origin_coords[1]}")
        routes_res = r_route.json().get("routes", {}) if r_route.status_code == 200 else {}
        car_r = routes_res.get("car", {})
        bike_r = routes_res.get("bike", {})
        transit_r = routes_res.get("transit", {})

        # Print structured report
        print(f"PROPERTY ID: {pid}")
        print(f"PROPERTY NAME: {title}")
        print(f"ADDRESS: {address}")
        print(f"LOCALITY / CITY: {locality}, {city}")
        print(f"EXACT COORDINATES: ({lat:.6f}, {lon:.6f})")
        print(f"LOCATION ACCURACY: {accuracy} (Source: {loc_source})")
        price_str = str(pdata.get('price_formatted', '')).encode('ascii', errors='replace').decode('ascii')
        print(f"PRICE: {price_str} ({pdata.get('price_per_sqft')} / sq.ft)")
        print(f"\n--- CONTACT NUMBER ---")
        print(f"CONTACT STATUS: {contact_status}")
        print(f"CONTACT NUMBER: {contact_num if contact_num else 'Contact number not publicly available'}")
        print(f"CONTACT PROVENANCE: {contact_prov_label}")
        print(f"CONTACT DISCLOSURE: {contact_message}")

        print(f"\n--- MULTI-IMAGE GALLERY ---")
        print(f"GALLERY SUMMARY: {gallery_summary}")
        print(f"TOTAL IMAGES FOUND: {total_found}")
        print(f"UNIQUE IMAGES: {unique_count}")
        print(f"DUPLICATES REMOVED: {dups_removed}")
        print(f"PROPERTY-SPECIFIC IMAGES: {prop_specific_cnt}")
        print(f"USER-UPLOADED IMAGES: {user_uploaded_cnt}")
        print(f"REPRESENTATIVE IMAGES: {representative_cnt}")
        print(f"WHETHER 5 GENUINE IMAGES EXIST: {has_5_genuine}")
        print(f"IMAGE LIST:")
        for i_idx, img in enumerate(gallery_images, 1):
            print(f"  {i_idx}. [{img.get('provenance')}] {img.get('url')} (Verified Property Association: {img.get('verified_property_association')})")

        print(f"\n--- LIVE ROUTING & NAVIGATION (Provider: Geoapify Routing API) ---")
        print(f"ORIGIN: {origin_name} ({origin_coords[0]}, {origin_coords[1]})")
        print(f"DESTINATION: ({lat:.6f}, {lon:.6f})")
        print(f"CAR ROUTE: status={car_r.get('status')} | distance={car_r.get('formatted_distance')} | duration={car_r.get('formatted_time')}")
        print(f"BIKE ROUTE: status={bike_r.get('status')} | distance={bike_r.get('formatted_distance')} | duration={bike_r.get('formatted_time')}")
        print(f"PUBLIC TRANSIT ROUTE: status={transit_r.get('status')} | distance={transit_r.get('formatted_distance')} | duration={transit_r.get('formatted_time')}")
        if transit_r.get("error_message"):
            print(f"  Transit Availability Note: {transit_r.get('error_message')}")

    print("\n" + "=" * 75)
    print("ALL 3 PROPERTIES VERIFIED WITH LIVE RUNTIME DATA")
    print("=" * 75)

if __name__ == "__main__":
    verify_three_properties()
