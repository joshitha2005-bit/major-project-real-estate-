import sys
import os
import asyncio
import io
import sqlite3
from PIL import Image

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "backend"))
sys.path.insert(0, "backend")

from app.services.storage_service import StorageService
from app.models.property import Property, PropertyImage
from app.core.database import SessionLocal
from fastapi import HTTPException, UploadFile

def main():
    print("=" * 80)
    print("DIRECT UNIT & SECURITY TEST SUITE FOR PHASE 2 PROPERTY IMAGE SYSTEM")
    print("=" * 80)

    db = SessionLocal()

    # 1. Test StorageService File Content Validation (PIL check)
    img_byte_arr = io.BytesIO()
    valid_img = Image.new('RGB', (400, 300), color = (73, 109, 137))
    valid_img.save(img_byte_arr, format='JPEG')
    valid_bytes = img_byte_arr.getvalue()

    # Create dummy upload file
    valid_upload = UploadFile(filename="test_photo.jpg", file=io.BytesIO(valid_bytes), headers={"content-type": "image/jpeg"})

    async def run_storage_tests():
        # A. Valid upload
        saved_path = await StorageService.upload_property_image(valid_upload, property_id=999999)
        print(f"1. Valid Image Upload -> Saved Path: {saved_path}")
        assert saved_path.startswith("/static/uploads/property_999999/")

        # B. Test fake image content (renamed text file to .jpg)
        fake_upload = UploadFile(filename="fake.jpg", file=io.BytesIO(b"Not an image binary"), headers={"content-type": "image/jpeg"})
        try:
            await StorageService.upload_property_image(fake_upload, property_id=999999)
            assert False, "Should have failed PIL verification!"
        except HTTPException as e:
            print(f"2. Fake Image Content Rejected -> Status {e.status_code}: {e.detail}")
            assert e.status_code == 400

        # C. Test invalid extension (.sh)
        sh_upload = UploadFile(filename="script.sh", file=io.BytesIO(b"#!/bin/bash"), headers={"content-type": "text/x-sh"})
        try:
            await StorageService.upload_property_image(sh_upload, property_id=999999)
            assert False, "Should have failed extension check!"
        except HTTPException as e:
            print(f"3. Invalid Extension Rejected -> Status {e.status_code}: {e.detail}")
            assert e.status_code == 400

        # D. Test file deletion
        deleted = StorageService.delete_property_image_file(saved_path)
        print(f"4. Delete Property Image File -> Success: {deleted}")
        assert deleted == True

    asyncio.run(run_storage_tests())

    # 2. Test DB Image Table Operations & Primary Switching
    # Create test property
    prop = Property(
        user_id=1,
        title="Direct Test Property",
        property_type="Apartment",
        bhk=2,
        area_sqft=1100.0,
        price=7500000.0,
        address="Test Address, Bengaluru",
        locality="Electronic City",
        latitude=12.8436,
        longitude=77.6687
    )
    db.add(prop)
    db.commit()
    db.refresh(prop)
    prop_id = prop.id
    print(f"\n5. Created Test Property ID #{prop_id} in Database")

    # Add owner upload image
    img1 = PropertyImage(
        property_id=prop_id,
        image_path="/static/uploads/property_1/photo1.jpg",
        source_type="owner_upload",
        source_name="Uploaded by Owner",
        is_primary=True,
        order=0
    )
    # Add licensed external image
    img2 = PropertyImage(
        property_id=prop_id,
        image_path="https://images.unsplash.com/photo-1545324418",
        source_type="licensed_external",
        source_name="Unsplash License",
        source_url="https://unsplash.com",
        is_primary=False,
        order=1
    )
    db.add_all([img1, img2])
    db.commit()

    # Query images ordered by primary DESC, order ASC
    images = db.query(PropertyImage).filter(PropertyImage.property_id == prop_id).order_by(
        PropertyImage.is_primary.desc(), PropertyImage.order.asc()
    ).all()
    print(f"6. Queried Property #{prop_id} images count: {len(images)}")
    assert len(images) == 2
    assert images[0].is_primary == True
    assert images[0].id == img1.id

    # Switch primary image to img2
    db.query(PropertyImage).filter(PropertyImage.property_id == prop_id).update({"is_primary": False})
    img2.is_primary = True
    db.commit()

    images_after = db.query(PropertyImage).filter(PropertyImage.property_id == prop_id).order_by(
        PropertyImage.is_primary.desc(), PropertyImage.order.asc()
    ).all()
    print(f"7. Switched Primary Image to Image #{img2.id} -> First image is now ID #{images_after[0].id}")
    assert images_after[0].id == img2.id
    assert images_after[0].is_primary == True

    # Clean up test property
    db.delete(prop)
    db.commit()
    db.close()

    print("\nALL DIRECT UNIT & SECURITY TESTS PASSED SUCCESSFULLY!")
    print("=" * 80)

if __name__ == "__main__":
    main()
