import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add backend directory to sys.path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.models.property import Property, PropertyImage
from app.services.image_provenance import ImageProvenanceService
from app.services.contact_verification_service import ContactVerificationService

def run_audit():
    db_path = os.path.join(backend_dir, "real_estate.db")
    engine = create_engine(f"sqlite:///{db_path}")
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()

    properties = db.query(Property).all()
    total_props = len(properties)
    print(f"Total Properties Audited: {total_props}")

    # Image stats
    usable_images = 0
    source_reference_images = 0
    location_building_ref = 0
    no_images = 0
    invalid_images = 0

    # Contact stats
    legitimately_displayable_contacts = 0
    contact_via_source_only = 0
    contact_unavailable = 0

    builder_office_matches = 0
    direct_owner_contacts = 0

    for p in properties:
        # 1. Image Provenance
        img_info = ImageProvenanceService.get_property_image_provenance(p)
        cls_tag = img_info["image_classification"]
        if cls_tag == "AUTHORIZED_PROPERTY_IMAGE":
            usable_images += 1
        elif cls_tag == "SOURCE_LISTING_IMAGE":
            source_reference_images += 1
        elif cls_tag == "LOCATION_BUILDING_REFERENCE":
            location_building_ref += 1
        elif cls_tag == "NO_IMAGE":
            no_images += 1
        elif cls_tag == "INVALID_IMAGE":
            invalid_images += 1

        # 2. Contact Resolution
        contact_info = ContactVerificationService.resolve_property_contact(p)
        if contact_info["contact_display_permission"]:
            legitimately_displayable_contacts += 1
            if contact_info["contact_type"] == "Builder":
                builder_office_matches += 1
            elif contact_info["contact_type"] == "Owner":
                direct_owner_contacts += 1
        else:
            if contact_info["source_listing_url"] and contact_info["source_listing_url"].startswith("http"):
                contact_via_source_only += 1
            else:
                contact_unavailable += 1

    print("\n--- IMAGE PROVENANCE & CNN FEASIBILITY ---")
    print(f"Authorized Usable for CNN: {usable_images}")
    print(f"Source Listing Reference (View-Only): {source_reference_images}")
    print(f"Location/Building Reference: {location_building_ref}")
    print(f"No Image: {no_images}")
    print(f"Invalid / Placeholder: {invalid_images}")

    print("\n--- CONTACT VERIFICATION & DISPLAY PERMISSION ---")
    print(f"Legitimately Displayable Contacts: {legitimately_displayable_contacts} (Builder: {builder_office_matches}, Direct Owner: {direct_owner_contacts})")
    print(f"Contact Available via Source Listing: {contact_via_source_only}")
    print(f"Contact Unavailable (Historical / Protected): {contact_unavailable}")

    db.close()

if __name__ == "__main__":
    run_audit()
