import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "backend"))
sys.path.insert(0, "backend")

import io
import sqlite3
from PIL import Image
from fastapi.testclient import TestClient
from app.main import app
from app.core.database import get_db

client = TestClient(app)

def get_auth_headers(user_id=1, email="testowner@proppulse.com", role="USER"):
    from app.core.security import create_access_token
    token = create_access_token({"sub": str(user_id), "email": email, "role": role})
    return {"Authorization": f"Bearer {token}"}

def main():
    print("=" * 80)
    print("STARTING PHASE 2 PROPERTY IMAGE SYSTEM AUTOMATED TEST SUITE")
    print("=" * 80)

    # 1. Create a dummy property for testing
    headers = get_auth_headers(user_id=1)
    
    conn = sqlite3.connect('backend/real_estate.db')
    cursor = conn.cursor()
    
    # Ensure user 1 exists
    cursor.execute("SELECT id FROM users WHERE id = 1")
    if not cursor.fetchone():
        cursor.execute("INSERT INTO users (id, email, full_name, hashed_password, role, is_pro) VALUES (1, 'testowner@proppulse.com', 'Test Owner', 'hash', 'USER', 1)")
        conn.commit()

    # Ensure user 2 exists (unauthorized user)
    cursor.execute("SELECT id FROM users WHERE id = 2")
    if not cursor.fetchone():
        cursor.execute("INSERT INTO users (id, email, full_name, hashed_password, role, is_pro) VALUES (2, 'otheruser@proppulse.com', 'Other User', 'hash', 'USER', 0)")
        conn.commit()

    # Create test property owned by user 1
    cursor.execute("""
    INSERT INTO properties (user_id, title, property_type, listing_type, bhk, area_sqft, bathrooms, price, address, locality, latitude, longitude, images)
    VALUES (1, 'Phase 2 Test Villa', 'Villa', 'Buy', 3, 2000.0, 3, 25000000.0, '123 Test Street, Koramangala', 'Koramangala', 12.9357, 77.6240, '[]')
    """)
    conn.commit()
    prop_id = cursor.lastrowid
    print(f"1. Created Test Property ID #{prop_id} (Owned by User #1)")

    # 2. Test fetching images for property with NO images
    resp = client.get(f"/api/v1/properties/{prop_id}/images")
    assert resp.status_code == 200
    images = resp.json()
    print(f"2. Property #{prop_id} initial images count: {len(images)} (Expected: 0)")
    assert len(images) == 0

    # 3. Test uploading invalid file extension (.txt / .sh)
    txt_file = ("script.sh", b"#!/bin/bash\necho hello", "text/x-sh")
    resp = client.post(f"/api/v1/properties/{prop_id}/images", files={"files": txt_file}, headers=headers)
    print(f"3. Uploading invalid extension (.sh) -> Status: {resp.status_code} (Expected: 400)")
    assert resp.status_code == 400

    # 4. Test uploading fake image (renamed text file to .jpg)
    fake_jpg = ("fake.jpg", b"This is not a real image binary", "image/jpeg")
    resp = client.post(f"/api/v1/properties/{prop_id}/images", files={"files": fake_jpg}, headers=headers)
    print(f"4. Uploading fake JPEG binary content -> Status: {resp.status_code} (Expected: 400)")
    assert resp.status_code == 400

    # 5. Test uploading oversized file (> 5MB)
    oversized = ("big.jpg", b"X" * (6 * 1024 * 1024), "image/jpeg")
    resp = client.post(f"/api/v1/properties/{prop_id}/images", files={"files": oversized}, headers=headers)
    print(f"5. Uploading oversized file (>5MB) -> Status: {resp.status_code} (Expected: 400)")
    assert resp.status_code == 400

    # 6. Test unauthorized user upload (User #2 trying to upload to User #1's property)
    unauth_headers = get_auth_headers(user_id=2, email="otheruser@proppulse.com")
    
    img_byte_arr = io.BytesIO()
    valid_img = Image.new('RGB', (400, 300), color = (73, 109, 137))
    valid_img.save(img_byte_arr, format='JPEG')
    valid_img_bytes = img_byte_arr.getvalue()

    file_valid = ("valid1.jpg", valid_img_bytes, "image/jpeg")

    resp = client.post(f"/api/v1/properties/{prop_id}/images", files={"files": file_valid}, headers=unauth_headers)
    print(f"6. Unauthorized User #2 Upload Attempt -> Status: {resp.status_code} (Expected: 403)")
    assert resp.status_code == 403

    # 7. Test authorized owner upload (User #1 uploading 2 valid images)
    img_byte_arr2 = io.BytesIO()
    valid_img2 = Image.new('RGB', (500, 400), color = (200, 100, 50))
    valid_img2.save(img_byte_arr2, format='PNG')
    valid_img_bytes2 = img_byte_arr2.getvalue()

    files_batch = [
        ("files", ("photo1.jpg", valid_img_bytes, "image/jpeg")),
        ("files", ("photo2.png", valid_img_bytes2, "image/png"))
    ]

    resp = client.post(f"/api/v1/properties/{prop_id}/images", files=files_batch, headers=headers)
    print(f"7. Authorized Owner Upload Batch -> Status: {resp.status_code} (Expected: 200)")
    assert resp.status_code == 200
    uploaded = resp.json()
    assert len(uploaded) == 2
    img1_id = uploaded[0]["id"]
    img2_id = uploaded[1]["id"]
    print(f"   Uploaded Image #1 ID: {img1_id} (is_primary: {uploaded[0]['is_primary']})")
    print(f"   Uploaded Image #2 ID: {img2_id} (is_primary: {uploaded[1]['is_primary']})")

    # 8. Test licensed external image upload
    ext_payload = {
        "image_url": "https://images.unsplash.com/photo-1545324418-cc1a3fa10c00?w=800",
        "source_name": "Unsplash License (Author: John Doe)",
        "source_url": "https://unsplash.com/photos/sample"
    }
    resp = client.post(f"/api/v1/properties/{prop_id}/external-images", json=ext_payload, headers=headers)
    print(f"8. Adding Licensed External Image -> Status: {resp.status_code} (Expected: 200)")
    assert resp.status_code == 200
    ext_img = resp.json()
    img3_id = ext_img["id"]

    # 9. Test primary image switching
    resp = client.put(f"/api/v1/properties/{prop_id}/images/{img2_id}/primary", headers=headers)
    print(f"9. Setting Image #{img2_id} as Primary -> Status: {resp.status_code} (Expected: 200)")
    assert resp.status_code == 200

    # Verify primary order via GET /{prop_id}/images
    resp = client.get(f"/api/v1/properties/{prop_id}/images")
    all_imgs = resp.json()
    print(f"   Current Images Count: {len(all_imgs)}")
    print(f"   First Image ID (Primary): {all_imgs[0]['id']} (is_primary: {all_imgs[0]['is_primary']})")
    assert all_imgs[0]['id'] == img2_id
    assert all_imgs[0]['is_primary'] == True

    # 10. Test unauthorized deletion attempt by User #2
    resp = client.delete(f"/api/v1/properties/{prop_id}/images/{img1_id}", headers=unauth_headers)
    print(f"10. Unauthorized User #2 Deletion Attempt -> Status: {resp.status_code} (Expected: 403)")
    assert resp.status_code == 403

    # 11. Test authorized deletion by owner User #1
    resp = client.delete(f"/api/v1/properties/{prop_id}/images/{img1_id}", headers=headers)
    print(f"11. Authorized Owner Deletion of Image #{img1_id} -> Status: {resp.status_code} (Expected: 200)")
    assert resp.status_code == 200

    # 12. Test getting property details enriched output
    resp = client.get(f"/api/v1/properties/{prop_id}")
    assert resp.status_code == 200
    prop_detail = resp.json()
    print(f"12. Property #{prop_id} Detail Enriched Output:")
    print(f"    - Title: {prop_detail['title']}")
    print(f"    - Images List Length: {len(prop_detail['images'])}")
    print(f"    - Uploaded Images Metadata Count: {len(prop_detail['uploaded_images'])}")

    # Clean up test property
    cursor.execute("DELETE FROM properties WHERE id = ?", (prop_id,))
    conn.commit()
    conn.close()

    print("\nALL PHASE 2 AUTOMATED SECURITY & FUNCTIONALITY TESTS PASSED SUCCESSFULLY!")
    print("=" * 80)

if __name__ == "__main__":
    main()
