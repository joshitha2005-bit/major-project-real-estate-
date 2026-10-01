import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))

from app.core.security import create_access_token
import httpx
import json

BACKEND_URL = "http://localhost:8000/api/v1"

def test_runtime_properties():
    # Generate admin token
    token = create_access_token(subject="joshithareddy3b@gmail.com")
    headers = {"Authorization": f"Bearer {token}"}

    client = httpx.Client(base_url=BACKEND_URL, headers=headers, timeout=60.0)

    # 4 target test properties demonstrating all image count regimes
    test_specs = [
        {"id": 101, "category": "5+ Images (Owner Direct Listing with 6 Multi-Angle Views)"},
        {"id": 16797, "category": "3-4 Images (NoBroker Verified Listing with 3 Unique Views, 1 Duplicate Removed)"},
        {"id": 16807, "category": "Fewer Images (< 3) (NoBroker Verified Listing with 1 Property-Specific Photo)"},
        {"id": 1, "category": "Representative Images Fallback (Historical Dataset with 4 Reference Images)"}
    ]

    results = {}

    for spec in test_specs:
        pid = spec["id"]
        category = spec["category"]
        print(f"\n=======================================================")
        print(f"VERIFYING: {category}")
        print(f"Property ID: {pid}")
        print(f"=======================================================")

        # 1. Fetch Property details
        res = client.get(f"/properties/{pid}")
        if res.status_code != 200:
            print(f"Failed to fetch property {pid}: {res.status_code} {res.text}")
            continue
        pdata = res.json()

        # 2. Fetch AI Analytics / ResNet-18 Multi-Image CNN Analysis
        ai_res = client.get(f"/ai/analyze-property/{pid}")
        ai_data = ai_res.json() if ai_res.status_code == 200 else {}

        # 3. Fetch Navigation Routes (using tested origin: Indiranagar Metro Station)
        route_res = client.get(f"/properties/{pid}/routes", params={"origin_text": "Indiranagar Metro Station, Bengaluru"})
        route_data = route_res.json() if route_res.status_code == 200 else {}

        gallery = pdata.get("gallery", {})

        results[pid] = {
            "category": category,
            "property": pdata,
            "ai": ai_data,
            "routes": route_data
        }

        print(f"Name / Title: {pdata.get('title')}")
        print(f"Address: {pdata.get('address')}")
        print(f"Exact Coordinates: {pdata.get('latitude')}, {pdata.get('longitude')} (Quality: {pdata.get('coordinate_quality')})")
        print(f"Source: {pdata.get('source')} | Source Type: {pdata.get('source_type')}")
        print(f"Contact Status: {'AVAILABLE' if pdata.get('contact_display_permission') else 'UNAVAILABLE'}")
        print(f"Contact Number: {pdata.get('contact_number') or 'Not publicly available'}")
        print(f"Contact Provenance: {pdata.get('contact_provenance', {}).get('provenance_category')} ({pdata.get('contact_provenance', {}).get('display_message')})")
        print(f"--- GALLERY ---")
        print(f"Gallery Summary: {gallery.get('count_summary')}")
        print(f"Total Advertised / Found: {gallery.get('total_images_found')}")
        print(f"Unique Images: {gallery.get('unique_images_count')}")
        print(f"Duplicates Removed: {gallery.get('duplicates_removed_count')}")
        print(f"Property-Specific Photos: {gallery.get('property_specific_count')}")
        print(f"Representative Images: {gallery.get('representative_count')}")
        print(f"Separated Sections: has_property_photos={gallery.get('has_property_photos')}, has_reference_images={gallery.get('has_reference_images')}")
        
        # Image AI
        image_ai = ai_data.get("image_ai", {})
        print(f"--- CNN RESNET-18 ANALYSIS ---")
        print(f"CNN Model: {image_ai.get('cnn_model')}")
        print(f"Images Analyzed by ResNet-18: {image_ai.get('number_of_images_analyzed')}")
        print(f"Aggregation Method: {image_ai.get('aggregation_method')}")
        print(f"Aggregated Embedding Dimensions: {image_ai.get('embedding_dimensions')} dimensions")
        print(f"Aggregated L2 Norm: {image_ai.get('embedding_norm')}")
        print(f"Non-Zero Feature Count: {image_ai.get('non_zero_features')} / 512")
        print(f"Aggregated Embedding Sample (first 6): {image_ai.get('embedding_sample', [])[:6]}")

        # Valuation
        val = ai_data.get("price_prediction", {})
        print(f"AI Valuation Predicted: {val.get('formatted_price')} ({val.get('predicted_selling_price')})")
        print(f"Fused Vector Architecture: 544 Dimensions (6 Structured + 10 Geoapify + 16 TF-IDF + 512 Aggregated ResNet-18)")

        # Routes
        origin = route_data.get("origin", {})
        dest = route_data.get("destination", {})
        car = route_data.get("routes", {}).get("car", {})
        bike = route_data.get("routes", {}).get("bike", {})
        transit = route_data.get("routes", {}).get("transit", {})

        print(f"--- ROUTING ---")
        print(f"Origin: {origin.get('address')} (Coords: {origin.get('coordinates')})")
        print(f"Origin Source: {origin.get('source')}")
        print(f"Destination: {dest.get('address')} (Coords: {dest.get('coordinates')})")
        print(f"Car: Distance: {car.get('formatted_distance')}, Time: {car.get('formatted_time')}, Status: {car.get('status')}")
        print(f"Bike: Distance: {bike.get('formatted_distance')}, Time: {bike.get('formatted_time')}, Status: {bike.get('status')}")
        print(f"Bus / Public Transport: Status: {transit.get('status')}, Provider: {transit.get('source')}")
        print(f"Transit Note: {transit.get('error_message')}")

    with open("verification_results.json", "w") as f:
        json.dump(results, f, indent=2)
    print("\nVerification complete! Full details stored in verification_results.json")

if __name__ == "__main__":
    test_runtime_properties()
