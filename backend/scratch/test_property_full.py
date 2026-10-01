import httpx

client = httpx.Client(base_url="http://127.0.0.1:8000", timeout=20.0)

for pid in [1, 2, 16797]:
    r = client.get(f"/api/v1/properties/{pid}")
    print(f"\n=== Property {pid} Status: {r.status_code} ===")
    if r.status_code == 200:
        d = r.json()
        print("Title:", d.get("display_title"))
        print("Address:", d.get("formatted_address"))
        print("Coordinates:", d.get("latitude"), d.get("longitude"))
        print("Location Prov:", d.get("location_provenance"))
        print("Contact Prov:", d.get("contact_provenance"))
        gal = d.get("gallery")
        if gal:
            print(f"Gallery Summary: {gal.get('count_summary')}")
            print(f"Total: {gal.get('total_images_found')}, Unique: {gal.get('unique_images_count')}, Duplicates Removed: {gal.get('duplicates_removed_count')}")
            print(f"Property-Specific: {gal.get('property_specific_count')}, Representative: {gal.get('representative_count')}")
            for img in gal.get("images", [])[:3]:
                print(f"  - [{img.get('provenance')}] {img.get('url')[:60]} (verified={img.get('verified_property_association')})")

    # Also test route
    r_route = client.get(f"/api/v1/properties/{pid}/routes?origin_lat=12.9774&origin_lon=77.5708")
    if r_route.status_code == 200:
        rd = r_route.json()
        routes = rd.get("routes", {})
        car = routes.get("car", {})
        bike = routes.get("bike", {})
        transit = routes.get("transit", {})
        print(f"Car Route: {car.get('status')} - {car.get('distance_km')} km, {car.get('time_minutes')} mins")
        print(f"Bike Route: {bike.get('status')} - {bike.get('distance_km')} km, {bike.get('time_minutes')} mins")
        print(f"Transit Route: {transit.get('status')} - {transit.get('error_message')}")
