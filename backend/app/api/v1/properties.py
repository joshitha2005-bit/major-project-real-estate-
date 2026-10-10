from sqlalchemy import or_, case, desc, asc
import os
import uuid
import random
import re
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query, status
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.database import get_db
from app.models.user import User
from app.models.property import Property, PropertyImage
from app.schemas.property import PropertyOut, PropertyListOut, PropertyCreate, CanonicalLocation
from app.services.geoapify_service import GeoapifyService
from app.services.storage_service import StorageService
from app.api.deps import get_current_user, get_current_user_with_role



router = APIRouter()

BUILDERS = ["Prestige", "Sobha", "Brigade", "Godrej", "Puravankara", "Salarpuria Sattva", "Mantri", "Assetz"]
OWNERS = [
    ("Rajesh Kumar", "+91 98860 12345"),
    ("Suresh Narayanan", "+91 98450 67890"),
    ("Anil Kumar", "+91 99001 88345"),
    ("Vikram Malhotra", "+91 98110 99887"),
    ("Priya Sharma", "+91 98801 33456"),
    ("Deepak Mehta", "+91 97400 22341"),
    ("Karthik Reddy", "+91 98440 66789"),
    ("Siddharth Rao", "+91 98866 55432"),
    ("Naveen Hegde", "+91 98451 77654"),
    ("Sunil Dutt", "+91 98800 33210")
]
IMAGES_POOL = [
    [
        "https://images.unsplash.com/photo-1545324418-cc1a3fa10c00?auto=format&fit=crop&w=800&q=80",
        "https://images.unsplash.com/photo-1512917774080-9991f1c4c750?auto=format&fit=crop&w=800&q=80"
    ],
    [
        "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?auto=format&fit=crop&w=800&q=80",
        "https://images.unsplash.com/photo-1600596542815-ffad4c1539a9?auto=format&fit=crop&w=800&q=80"
    ],
    [
        "https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?auto=format&fit=crop&w=800&q=80",
        "https://images.unsplash.com/photo-1502672260266-1c1ef2d93688?auto=format&fit=crop&w=800&q=80"
    ],
    [
        "https://images.unsplash.com/photo-1522708323590-d24dbb6b0267?auto=format&fit=crop&w=800&q=80",
        "https://images.unsplash.com/photo-1567496898669-ee935f5f647a?auto=format&fit=crop&w=800&q=80"
    ]
]

LOCALITY_COORDINATES = {
    "koramangala": (12.9357, 77.6240),
    "electronic city": (12.8436, 77.6687),
    "whitefield": (12.9696, 77.7497),
    "hsr layout": (12.9116, 77.6389),
    "indiranagar": (12.9733, 77.6405),
    "marathahalli": (12.9591, 77.6974),
    "bellandur": (12.9279, 77.6756),
    "sarjapur road": (12.9107, 77.6970),
    "jp nagar": (12.9077, 77.5854),
    "jayanagar": (12.9250, 77.5938),
    "banashankari": (12.9255, 77.5468),
    "hebbal": (13.0358, 77.5970),
    "yelahanka": (13.1007, 77.5963),
    "kr puram": (13.0075, 77.6959),
    "mahadevapura": (12.9902, 77.6874),
    "btm layout": (12.9166, 77.6101),
    "bannerghatta road": (12.8950, 77.5990),
    "thanisandra": (13.0547, 77.6338),
    "hennur": (13.0258, 77.6341),
    "vijayanagar": (12.9708, 77.5350),
    "rajajinagar": (12.9882, 77.5549),
    "rajaji nagar": (12.9882, 77.5549),
    "malleshwaram": (13.0031, 77.5643),
    "malleswaram": (13.0031, 77.5643),
    "devanahalli": (13.2485, 77.7126),
    "basavanagudi": (12.9421, 77.5752),
    "brookefield": (12.9658, 77.7183),
    "chandapura": (12.8004, 77.7063),
    "kanakapura road": (12.8760, 77.5480),
    "kanakpura road": (12.8760, 77.5480),
    "rajarajeshwari nagar": (12.9150, 77.5180),
    "raja rajeshwari nagar": (12.9150, 77.5180),
    "rr nagar": (12.9150, 77.5180),
    "uttarahalli": (12.9056, 77.5350),
    "hoodi": (12.9934, 77.7174),
    "bommasandra": (12.8122, 77.6835),
    "kengeri": (12.9081, 77.4837),
    "haralur road": (12.9090, 77.6695),
    "haralur": (12.9090, 77.6695),
    "kasavanahalli": (12.9090, 77.6695),
    "kasavanhalli": (12.9090, 77.6695),
    "kothanur": (13.0560, 77.6520),
    "horamavu": (13.0270, 77.6620),
    "hormavu": (13.0270, 77.6620),
    "varthur": (12.9406, 77.7466),
    "begur road": (12.8824, 77.6253),
    "begur": (12.8824, 77.6253),
    "jakkur": (13.0783, 77.6065),
    "jigani": (12.7845, 77.6405),
    "attibele": (12.7783, 77.7712),
    "yeshwanthpur": (13.0238, 77.5529),
    "budigere": (13.0800, 77.7400),
    "panathur": (12.9350, 77.7020),
    "vidyaranyapura": (13.0827, 77.5583),
    "balagere": (12.9380, 77.7280),
    "kaggadasapura": (12.9830, 77.6810),
    "ramamurthy nagar": (13.0163, 77.6785),
    "akshaya nagar": (12.8730, 77.6180),
    "hulimavu": (12.8765, 77.6015),
    "chikka tirupathi": (12.8980, 77.8650)
}


def format_indian_currency(amount: float) -> str:
    """Format number into Indian Rupee Lakhs / Crores string representation."""
    if amount >= 10000000:
        return f"₹{amount / 10000000:.2f} Cr"
    elif amount >= 100000:
        return f"₹{amount / 100000:.2f} Lakh"
    else:
        return f"₹{int(amount):,}"

def is_anonymized_code(title: str) -> bool:
    """Detect if title is purely an anonymized dataset hash code (e.g. ArsiaEx, Oreldhi, SLiritn, Soiewre, DuenaTa, SollyCl, NRosete, SrisePo)."""
    if not title:
        return True
    t = title.strip()
    if "" in t or "—" in t or "BHK" in t or "Bedroom" in t:
        return True
    COMMON_WORDS = ["apartment", "flat", "villa", "house", "park", "green", "view", "heights", "residency", "nest", "layout", "garden", "enclave", "city", "town", "court", "palace", "manor", "bhk", "bedroom", "floor", "gated", "space", "field", "wood", "sky", "prestige", "sobha", "salarpuria", "brigade", "godrej", "assetz", "puravankara"]
    if re.match(r'^[A-Za-z0-9]{4,12}$', t):
        if not any(w in t.lower() for w in COMMON_WORDS):
            return True
    return False

def extract_location(p: Property) -> str:
    """Extract location string, preserving specific sector or sub-locality if present."""
    raw_title = (p.title or "").strip()
    sector_match = re.search(r'\b(sector\s*\d+\s+[^—]+)', raw_title, re.IGNORECASE)
    if sector_match:
        return sector_match.group(1).strip().title()

    addr = (p.address or "").strip()
    if addr and addr.lower() not in ["bengaluru", "bangalore"]:
        clean_addr = re.sub(r',\s*(bengaluru|bangalore|karnataka|560\d{3})\b', '', addr, flags=re.I).strip()
        if clean_addr:
            return clean_addr.title()
            
    return (p.locality or "Bengaluru").title()

def enrich_property_out(p: Property) -> PropertyOut:
    """Enrich property model with calculated fields for API response."""
    price_sqft = round(p.price / p.area_sqft, 2) if p.area_sqft > 0 else 0
    price_formatted = format_indian_currency(p.price)
    
    # Determine coordinate status
    coord_quality = getattr(p, "coordinate_quality", None)
    if not coord_quality:
        if p.source_type == "historical_dataset" or p.source == "Bengaluru_House_Data.csv":
            coord_quality = "LOCALITY_APPROXIMATE"
        elif p.latitude == 0 and p.longitude == 0:
            coord_quality = "MISSING"
        else:
            coord_quality = "EXACT"
    if coord_quality == "APPROXIMATE":
        coord_status = "LOCALITY_APPROXIMATE"
    else:
        coord_status = coord_quality

    # Determine property type source
    is_historical = (p.source_type == "historical_dataset" or p.source == "Bengaluru_House_Data.csv")
    ptype_src = "inferred" if is_historical else "user_provided"
    
    # Canonical Property Identity & Location Resolution
    db_identity_conf = getattr(p, "identity_confidence", None)
    db_building_name = getattr(p, "building_name", None)
    db_project_name = getattr(p, "project_name", None)
    db_society_name = getattr(p, "society_name", None)
    db_builder_name = getattr(p, "builder_name", None)
    
    # Priority 1: Check database canonical identity
    raw_title = (p.title or "").strip()
    raw_society = (getattr(p, "society", None) or "").strip()
    
    building_name = None
    project_name = None
    society_name = None
    builder_name = db_builder_name
    
    INVALID_BUILDINGS = {
        'sb', 'apartment', 'apartments', 'aparment', 'stand alone building',
        'standlone building', 'standalone building', 'villa', 'plot', 'land',
        'residential apartment', 'independent house', 'house', 'biotech park'
    }
    is_valid_db_bldg = (
        db_building_name and 
        db_building_name.lower().strip() not in INVALID_BUILDINGS and
        ' village' not in db_building_name.lower() and
        db_building_name.lower().strip() != (p.locality or "").lower().strip()
    )

    if db_identity_conf == "IDENTITY_RESOLVED" and is_valid_db_bldg:
        building_name = db_building_name
        project_name = db_project_name or db_building_name
        society_name = db_society_name or db_building_name
        identity_conf = "IDENTITY_RESOLVED"
    elif raw_society and not is_anonymized_code(raw_society) and raw_society.lower() not in ["none", "null", "nan", ""]:
        building_name = raw_society
        project_name = raw_society
        society_name = raw_society
        identity_conf = "IDENTITY_RESOLVED"
    elif db_identity_conf in ["IDENTITY_PARTIAL", "IDENTITY_UNRESOLVED"]:
        identity_conf = db_identity_conf
        building_name = None
        project_name = None
        society_name = None
    else:
        # Check title if direct listing or legitimate project
        KNOWN_BUILDERS = [
            "prestige", "sobha", "salarpuria", "brigade", "godrej", "assetz", 
            "puravankara", "l&t", "embassy", "shriram", "mantri", "dharani", 
            "signature", "century", "provident", "casagrand", "sukhi", "elgin", 
            "scion", "dra", "mahindra", "vgn", "kg"
        ]
        title_has_builder = any(b in raw_title.lower() for b in KNOWN_BUILDERS)
        if title_has_builder:
            building_name = raw_title
            project_name = raw_title
            society_name = raw_title
            identity_conf = "IDENTITY_RESOLVED"
        elif getattr(p, "sub_locality", None):
            identity_conf = "IDENTITY_PARTIAL"
        else:
            identity_conf = "IDENTITY_UNRESOLVED"

    # Display title distinction: NEVER confuse property type with property name!
    if identity_conf == "IDENTITY_RESOLVED" and building_name:
        display_title = building_name
    else:
        if "bedroom" in raw_title.lower() or (p.bhk and p.bhk > 4):
            size_str = f"{p.bhk} Bedroom"
        elif p.bhk and p.bhk > 0:
            size_str = f"{p.bhk} BHK"
        else:
            size_str = ""

        loc_part = p.locality or "Bengaluru"
        if size_str:
            display_title = f"{size_str} in {loc_part}"
        else:
            display_title = f"Property in {loc_part}"
        
    property_type_val = p.property_type

    # Canonical Location Resolution
    addr = (p.address or "").strip()
    pincode_val = getattr(p, "pincode", None)
    if not pincode_val:
        pincode_match = re.search(r'\b(560\d{3}|561\d{3}|562\d{3})\b', addr)
        pincode_val = pincode_match.group(1) if pincode_match else None
        
    street_val = getattr(p, "street", None)
    road_val = getattr(p, "road", None)
    sub_loc_val = getattr(p, "sub_locality", None)
    loc_val = (p.locality or "Bengaluru").title()
    
    # Coordinate confidence
    coord_conf_db = getattr(p, "coordinate_confidence", None)
    if coord_conf_db in ["EXACT", "APPROXIMATE"]:
        coord_confidence = coord_conf_db
    else:
        coord_confidence = "EXACT" if coord_quality == "EXACT" else "APPROXIMATE"
        
    is_direct = (getattr(p, "source_type", "") in ["PROPPULSE_DIRECT", "owner_listing"])
    loc_source = getattr(p, "location_source", None) or ("VERIFIED_BUILDING_GPS" if coord_confidence == "EXACT" else "LOCALITY_BENCHMARK_CENTROID")
    identity_src = getattr(p, "identity_source", None) or ("VERIFIED_DIRECT" if is_direct else "HISTORICAL_RECORD")
    
    # Formatted address assembly
    formatted_address = getattr(p, "formatted_address", None)
    if not formatted_address:
        addr_segments = []
        if building_name:
            addr_segments.append(building_name)
        if street_val or road_val:
            addr_segments.append(street_val or road_val)
        if sub_loc_val and sub_loc_val.lower() not in loc_val.lower():
            addr_segments.append(sub_loc_val)
        addr_segments.append(loc_val)
        addr_segments.append("Bengaluru, Karnataka" + (f" - {pincode_val}" if pincode_val else ""))
        formatted_address = ", ".join(addr_segments)
    
    canonical_location = CanonicalLocation(
        property_id=p.id,
        property_name=building_name if identity_conf == "IDENTITY_RESOLVED" else None,
        building_name=building_name if identity_conf == "IDENTITY_RESOLVED" else None,
        project_name=project_name if identity_conf == "IDENTITY_RESOLVED" else None,
        society_name=society_name if identity_conf == "IDENTITY_RESOLVED" else None,
        builder_name=builder_name,
        street=street_val,
        road=road_val,
        sub_locality=sub_loc_val,
        locality=loc_val,
        city="Bengaluru",
        state="Karnataka",
        pincode=pincode_val,
        latitude=p.latitude,
        longitude=p.longitude,
        coordinate_confidence=coord_confidence,
        formatted_address=formatted_address,
        identity_confidence=identity_conf,
        identity_source=identity_src,
        location_source=loc_source
    )

    # Use property images ordered by is_primary DESC, order ASC
    if p.property_images:
        sorted_db_imgs = sorted(p.property_images, key=lambda x: (not getattr(x, 'is_primary', False), getattr(x, 'order', 0)))
        filtered_images = [img.image_path for img in sorted_db_imgs if isinstance(img.image_path, str) and img.image_path.strip()]
    else:
        raw_images = p.images or []
        filtered_images = [img for img in raw_images if isinstance(img, str) and img.strip()]

    # Phone contact privacy and fallback
    SEED_PHONES = {"+91 98860 12345", "+91 98450 67890", "+91 99001 88345", "+91 98110 99887", "+91 98801 33456", "+91 97400 22341", "+91 98440 66789", "+91 98866 55432", "+91 98451 77654", "+91 98800 33210"}
    
    # Phase B Source & Provenance attributes
    from app.services.image_provenance import ImageProvenanceService
    from app.services.listing_service import ListingService
    from app.services.contact_verification_service import ContactVerificationService

    img_info = ImageProvenanceService.get_property_image_provenance(p)
    gallery_info = ImageProvenanceService.resolve_property_gallery(p)
    contact_info = ContactVerificationService.resolve_property_contact(p)
    anomalies = ListingService.clean_and_audit_property(p)

    stype = p.source_type
    if stype not in ["HISTORICAL_MARKET_DATA", "CURRENT_AUTHORIZED_LISTING", "PROPPULSE_DIRECT", "DEMO_TEST"]:
        if stype == "historical_dataset" or p.source == "Bengaluru_House_Data.csv":
            stype = "HISTORICAL_MARKET_DATA"
        elif stype in ["owner_listing", "PROPPULSE_DIRECT"]:
            stype = "PROPPULSE_DIRECT"
        else:
            stype = "DEMO_TEST"

    lstatus = getattr(p, "listing_status", None)
    if not lstatus or lstatus not in ["CURRENT", "HISTORICAL", "REFERENCE", "DEMO", "SOLD_INACTIVE", "UNKNOWN"]:
        if stype == "PROPPULSE_DIRECT":
            lstatus = "CURRENT"
        elif stype == "HISTORICAL_MARKET_DATA":
            lstatus = "HISTORICAL"
        elif stype == "DEMO_TEST":
            lstatus = "DEMO"
        else:
            lstatus = "UNKNOWN"

    is_direct = (stype == "PROPPULSE_DIRECT" or p.source_type == "owner_listing")

    out_dict = {
        "id": p.id,
        "user_id": p.user_id,
        "source_listing_id": contact_info["source_listing_id"],
        "city": getattr(p, "city", "Bengaluru"),
        "title": display_title,
        "display_title": display_title,
        "building_name": building_name,
        "project_name": project_name,
        "canonical_location": canonical_location,
        "property_type": property_type_val,
        "listing_type": p.listing_type or "Buy",
        "bhk": p.bhk,
        "area_sqft": p.area_sqft,
        "area_type": getattr(p, "area_type", "super_built_up"),
        "bathrooms": p.bathrooms,
        "balconies": p.balconies,
        "floor": p.floor,
        "total_floors": p.total_floors,
        "property_age": p.property_age,
        "facing": p.facing,
        "parking": p.parking,
        "furnishing": p.furnishing,
        "amenities": p.amenities or [],
        "price": p.price,
        "price_inr": getattr(p, "price_inr", p.price),
        "transaction_type": getattr(p, "transaction_type", "sale"),
        "description": p.description,
        "address": p.address,
        "locality": p.locality or "",
        "sub_locality": getattr(p, "sub_locality", None),
        "zone": getattr(p, "zone", None),
        "latitude": p.latitude,
        "longitude": p.longitude,
        "owner_name": "Historical Dataset" if is_historical else (p.owner_name or "Property Owner" if is_direct else "Verified Contact"),
        "seller_name": "Historical Dataset" if is_historical else (p.owner_name or "Property Owner" if is_direct else "Verified Contact"),
        "owner_phone": contact_info["contact_number"] if contact_info["contact_display_permission"] else "Contact information unavailable",
        "phone": contact_info["contact_number"] if contact_info["contact_display_permission"] else "Contact information unavailable",
        "images": img_info["images"],
        "image_provenance": img_info["image_provenance"],
        "image_provenance_badge": img_info["provenance_badge"],
        "image_disclosure_note": img_info["disclosure_note"],
        "has_genuine_image": img_info["has_genuine_image"],
        "contact_available": contact_info["contact_display_permission"],
        "contact_source": contact_info["contact_source"],
        "anomaly_flags": anomalies,
        "nearby_places": p.nearby_places or [],
        "street_view_available": bool(p.street_view_available),
        "seller_type": contact_info["contact_type"],
        "verification_status": p.verification_status or "Verified",
        "source_type": p.source_type or "demo_dataset",
        "provenance_type": stype,
        "source_name": getattr(p, "source_name", p.source or "Bengaluru_House_Data.csv"),
        "listing_status": lstatus,
        "source": contact_info["source_platform"],
        "source_url": contact_info["source_listing_url"] or p.source_url or "",
        "image_source": p.image_source or "",
        "verified": bool(p.verified),
        "price_per_sqft": price_sqft,
        "price_formatted": price_formatted,
        "coordinate_quality": coord_quality,
        "coordinate_status": coord_status,
        "property_type_source": ptype_src,
        "society": society_name or building_name,
        "property_name": building_name if identity_conf == "IDENTITY_RESOLVED" else None,
        "building_name": building_name if identity_conf == "IDENTITY_RESOLVED" else None,
        "project_name": project_name if identity_conf == "IDENTITY_RESOLVED" else None,
        "society_name": society_name if identity_conf == "IDENTITY_RESOLVED" else None,
        "builder_name": builder_name,
        "street": street_val,
        "road": road_val,
        "state": getattr(p, "state", "Karnataka") or "Karnataka",
        "pincode": pincode_val,
        "coordinate_confidence": coord_confidence,
        "formatted_address": formatted_address,
        "identity_confidence": identity_conf,
        "identity_source": identity_src,
        "location_source": loc_source,
        "display_title": display_title,
        "canonical_location": canonical_location,
        "uploaded_images": p.property_images or [],
        "created_at": p.created_at,
        "last_verified_at": getattr(p, "last_verified_at", None),
        "dataset_category": getattr(p, "dataset_category", "REFERENCE_HISTORICAL"),
        "is_main_ai_ready": bool(getattr(p, "is_main_ai_ready", False)),

        # Objective 20B fields
        "image_status": img_info.get("image_classification", "NO_IMAGE"),
        "image_source_url": img_info.get("primary_image", "") or "",
        "image_authorization_status": img_info.get("image_classification", "NO_IMAGE"),
        "cnn_analysis_status": "ACTIVE" if img_info.get("usable_for_ai") else ("READY_NO_PERMISSION" if img_info.get("image_classification") == "SOURCE_LISTING_IMAGE" else "UNAVAILABLE"),
        "cnn_embedding_dimensions": 512 if img_info.get("usable_for_ai") else None,
        "contact_type": contact_info["contact_type"],
        "contact_number": contact_info["contact_number"],
        "contact_source_url": contact_info["contact_source_url"],
        "contact_verified_at": contact_info["contact_verified_at"],
        "contact_display_permission": contact_info["contact_display_permission"],
        "source_platform": contact_info["source_platform"],
        "source_listing_url": contact_info["source_listing_url"],
        "gallery": gallery_info,
        "location_provenance": {
            "latitude": p.latitude,
            "longitude": p.longitude,
            "accuracy_status": coord_confidence,
            "source": loc_source,
            "formatted_address": formatted_address
        },
        "contact_provenance": {
            "number": contact_info["contact_number"] if contact_info["contact_display_permission"] else None,
            "provenance": "OWNER_PROVIDED" if contact_info["contact_type"] == "Owner" else ("PUBLIC_BUILDER_OFFICE" if contact_info["contact_type"] == "Builder" else "UNAVAILABLE"),
            "publicly_available": bool(contact_info["contact_display_permission"]),
            "display_message": contact_info.get("display_message") or ("Contact number not publicly available" if not contact_info["contact_display_permission"] else "Publicly available contact"),
            "click_to_call": f"tel:{contact_info['contact_number']}" if (contact_info["contact_display_permission"] and contact_info["contact_number"]) else None,
            "contact_type": contact_info["contact_type"],
            "office_address": contact_info.get("office_address")
        }
    }
    return PropertyOut(**out_dict)

def auto_generate_locality_sample_properties(
    locality_name: str, 
    db: Session, 
    lat: Optional[float] = None, 
    lon: Optional[float] = None
) -> List[Property]:
    """
    Phase B Data Principle Rule: Disabled auto-generation of synthetic sample properties.
    A locality with no current listings honestly reports 0 current listings.
    """
    return []

def parse_natural_query(query_str: str):
    """Parse natural language real estate search queries into filter parameters."""
    query_str = query_str.lower().strip()
    parsed = {}
    
    # 1. Parse BHK configuration (e.g., 3 BHK, 2 bedroom)
    bhk_match = re.search(r"(\d+)\s*(?:bhk|bedroom|bed|room)", query_str)
    if bhk_match:
        parsed["bhk"] = int(bhk_match.group(1))
        
    # 2. Parse listing type (buy or rent) using word boundaries
    if re.search(r"\b(rent|rental|renting|rented)\b", query_str):
        parsed["listing_type"] = "Rent"
    elif re.search(r"\b(buy|sale|purchase|buying|selling)\b", query_str):
        parsed["listing_type"] = "Buy"
        
    # 3. Parse property type using word boundaries
    if re.search(r"\b(apartment|flat|flats|apartments)\b", query_str):
        parsed["property_type"] = "Apartment"
    elif re.search(r"\b(villa|villas)\b", query_str):
        parsed["property_type"] = "Villa"
    elif re.search(r"\b(house|independent house|independent houses|individual house|independent|individual)\b", query_str):
        parsed["property_type"] = "Independent House"
    elif re.search(r"\b(plot|plots|land|lands)\b", query_str) or (re.search(r"\blayout\b", query_str) and "hsr" not in query_str):
        parsed["property_type"] = "Plot"
        
    # Helper to clean unit
    def parse_money(val_str, unit_str):
        try:
            val = float(val_str)
            if "cr" in unit_str or "crore" in unit_str:
                return val * 10000000.0
            elif "lakh" in unit_str or "lk" in unit_str or "lac" in unit_str:
                return val * 100000.0
            return val
        except Exception:
            return None

    # 4. Parse budget/price constraints
    # E.g. "under 1 crore", "under 60 lakh", "between 1.2 and 2 crore"
    max_match = re.search(r"(?:under|below|less than|max|within|budget|<=)\s*([\d\.]+)\s*(crore|cr|lakh|lakhs|lacs|lk|lac)", query_str)
    if max_match:
        parsed["max_price"] = parse_money(max_match.group(1), max_match.group(2))
        
    min_match = re.search(r"(?:above|more than|greater than|min|>=)\s*([\d\.]+)\s*(crore|cr|lakh|lakhs|lacs|lk|lac)", query_str)
    if min_match:
        parsed["min_price"] = parse_money(min_match.group(1), min_match.group(2))

    # 5. Parse area ranges (e.g. between 1200 and 1800 sqft)
    between_area = re.search(r"between\s+(\d+)\s+and\s+(\d+)\s*(?:sqft|sq.ft|sq ft|sq. ft|sq)", query_str)
    if between_area:
        parsed["min_area"] = float(between_area.group(1))
        parsed["max_area"] = float(between_area.group(2))
    else:
        above_area = re.search(r"(?:above|more than|greater than|min|>=)\s*(\d+)\s*(?:sqft|sq.ft|sq ft|sq. ft|sq)", query_str)
        if above_area:
            parsed["min_area"] = float(above_area.group(1))
        below_area = re.search(r"(?:under|below|less than|max|<=)\s*(\d+)\s*(?:sqft|sq.ft|sq ft|sq. ft|sq)", query_str)
        if below_area:
            parsed["max_area"] = float(below_area.group(1))

    # 6. Locality matching (Whitefield, Koramangala, etc.)
    # Remove filters and helper keywords to extract locality candidate using word boundaries
    clean_words = query_str
    clean_words = re.sub(r"\b\d+\s*(?:bhk|bedroom|bed|room|rooms)\b", "", clean_words)
    clean_words = re.sub(r"\b(?:under|below|less than|above|more than|greater than|between|and|min|max|budget|<=|>=)\s*[\d\.]+\s*(?:crore|cr|lakh|lakhs|lacs|lk|lac|sqft|sq.ft|sq ft|sq. ft|sq)\b", "", clean_words)
    clean_words = re.sub(r"\b(?:apartment|apartments|flat|flats|villa|villas|house|houses|plot|plots|land|lands|buy|rent|rental|sale|purchase|in|near|properties)\b", "", clean_words)
    
    locality_candidate = clean_words.strip()
    if locality_candidate:
        matched_locality = None
        # Mapped canonical locality names
        for canonical_name in LOCALITY_COORDINATES.keys():
            if canonical_name in locality_candidate:
                # Resolve to correct representation
                # Whitefield, Koramangala, etc.
                if canonical_name == "koramangala": matched_locality = "Koramangala"
                elif canonical_name == "electronic city": matched_locality = "Electronic City"
                elif canonical_name == "whitefield": matched_locality = "Whitefield"
                elif canonical_name == "hsr layout": matched_locality = "HSR Layout"
                elif canonical_name == "indiranagar": matched_locality = "Indiranagar"
                elif canonical_name == "marathahalli": matched_locality = "Marathahalli"
                elif canonical_name == "bellandur": matched_locality = "Bellandur"
                elif canonical_name == "sarjapur road": matched_locality = "Sarjapur Road"
                elif canonical_name == "jp nagar": matched_locality = "JP Nagar"
                elif canonical_name == "jayanagar": matched_locality = "Jayanagar"
                elif canonical_name == "banashankari": matched_locality = "Banashankari"
                elif canonical_name == "hebbal": matched_locality = "Hebbal"
                elif canonical_name == "yelahanka": matched_locality = "Yelahanka"
                elif canonical_name == "kr puram": matched_locality = "KR Puram"
                elif canonical_name == "mahadevapura": matched_locality = "Mahadevapura"
                elif canonical_name == "btm layout": matched_locality = "BTM Layout"
                elif canonical_name == "bannerghatta road": matched_locality = "Bannerghatta Road"
                elif canonical_name == "thanisandra": matched_locality = "Thanisandra"
                elif canonical_name == "hennur": matched_locality = "Hennur"
                elif canonical_name == "vijayanagar": matched_locality = "Vijayanagar"
                elif canonical_name == "rajajinagar": matched_locality = "Rajajinagar"
                elif canonical_name == "malleshwaram": matched_locality = "Malleshwaram"
                elif canonical_name == "basavanagudi": matched_locality = "Basavanagudi"
                elif canonical_name == "brookefield": matched_locality = "Brookefield"
                elif canonical_name == "chandapura": matched_locality = "Chandapura"
                break
        if not matched_locality:
            words = [w.strip() for w in locality_candidate.split() if w.strip()]
            if words:
                matched_locality = " ".join([w.capitalize() for w in words])
        if matched_locality:
            parsed["locality"] = matched_locality
            
    return parsed

@router.get("/", response_model=PropertyListOut)
def list_properties(
    query: Optional[str] = Query(None, description="Search term e.g. Koramangala, Whitefield"),
    property_type: Optional[str] = Query(None),
    listing_type: Optional[str] = Query(None),
    bhk: Optional[int] = Query(None),
    min_price: Optional[float] = Query(None),
    max_price: Optional[float] = Query(None),
    min_area: Optional[float] = Query(None),
    max_area: Optional[float] = Query(None),
    furnishing: Optional[str] = Query(None),
    parking: Optional[str] = Query(None),
    current_only: Optional[bool] = Query(None, description="Filter current listings only"),
    verified_only: Optional[bool] = Query(None, description="Filter verified listings only"),
    has_real_image: Optional[bool] = Query(None, description="Filter listings with authentic images"),
    source_type: Optional[str] = Query(None, description="Filter by source type e.g. PROPPULSE_DIRECT, HISTORICAL_MARKET_DATA"),
    dataset_category: Optional[str] = Query(None, description="Filter by category: MAIN_AI_READY, REFERENCE_HISTORICAL"),
    include_historical: Optional[bool] = Query(False, description="Whether to include reference historical properties"),
    lat: Optional[float] = Query(None),
    lon: Optional[float] = Query(None),
    page: Optional[int] = Query(None, description="Page index"),
    page_size: Optional[int] = Query(None, description="Page size"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, le=100),
    db: Session = Depends(get_db)
):
    """Retrieve property listings using strict SQL constraints and Natural Language parsing options."""
    # Resolve FastAPI Query objects if called directly as a function in tests
    from fastapi.params import Query as FastAPIQuery
    
    def resolve_val(v):
        if isinstance(v, FastAPIQuery):
            return v.default
        if hasattr(v, "__class__") and (v.__class__.__name__ == "QueryInfo" or v.__class__.__name__ == "Query"):
            return getattr(v, "default", None)
        # Check if v is a string that starts with QueryInfo representation in some test settings
        if str(type(v)).find("fastapi.params.Query") != -1:
            return getattr(v, "default", None)
        return v

    query = resolve_val(query)
    property_type = resolve_val(property_type)
    listing_type = resolve_val(listing_type)
    bhk = resolve_val(bhk)
    min_price = resolve_val(min_price)
    max_price = resolve_val(max_price)
    min_area = resolve_val(min_area)
    max_area = resolve_val(max_area)
    furnishing = resolve_val(furnishing)
    parking = resolve_val(parking)
    current_only = resolve_val(current_only)
    verified_only = resolve_val(verified_only)
    has_real_image = resolve_val(has_real_image)
    source_type = resolve_val(source_type)
    page = resolve_val(page)
    page_size = resolve_val(page_size)
    
    skip = resolve_val(skip)
    if skip is None: skip = 0
    limit = resolve_val(limit)
    if limit is None: limit = 50

    q = db.query(Property)
    # Exclude private properties from public listings
    q = q.filter(or_(Property.visibility_status != "PRIVATE", Property.visibility_status.is_(None)))
    
    parsed_filters = {}
    if query and isinstance(query, str) and query.strip():
        parsed_filters = parse_natural_query(query)

    # 1. Locality strict filter (with flexible Road/Main Road suffix support)
    final_locality = parsed_filters.get("locality")
    if final_locality:
        if final_locality.lower().endswith(" road"):
            base_loc = final_locality[:-5].strip()
            q = q.filter(or_(Property.locality.ilike(f"%{final_locality}%"), Property.locality.ilike(f"%{base_loc}%")))
        else:
            q = q.filter(Property.locality.ilike(f"%{final_locality}%"))
    elif query and isinstance(query, str) and query.strip():
        # Fallback to splitting by comma for traditional locality searches
        clean_locality = query.strip().split(',')[0].strip()
        if clean_locality.lower().endswith(" road"):
            base_loc = clean_locality[:-5].strip()
            q = q.filter(or_(Property.locality.ilike(f"%{clean_locality}%"), Property.locality.ilike(f"%{base_loc}%")))
        else:
            q = q.filter(Property.locality.ilike(f"%{clean_locality}%"))
        
    # 2. Strict constraint filters
    final_property_type = property_type or parsed_filters.get("property_type")
    if final_property_type and final_property_type != "All":
        q = q.filter(Property.property_type.ilike(final_property_type))
        
    final_listing_type = listing_type or parsed_filters.get("listing_type")
    if final_listing_type and final_listing_type != "All":
        q = q.filter(Property.listing_type.ilike(final_listing_type))
        
    final_bhk = bhk if bhk is not None else parsed_filters.get("bhk")
    if isinstance(final_bhk, int):
        q = q.filter(Property.bhk == final_bhk)
        
    final_min_price = min_price if min_price is not None else parsed_filters.get("min_price")
    if isinstance(final_min_price, (int, float)):
        q = q.filter(Property.price >= final_min_price)
        
    final_max_price = max_price if max_price is not None else parsed_filters.get("max_price")
    if isinstance(final_max_price, (int, float)):
        q = q.filter(Property.price <= final_max_price)
        
    final_min_area = min_area if min_area is not None else parsed_filters.get("min_area")
    if isinstance(final_min_area, (int, float)):
        q = q.filter(Property.area_sqft >= final_min_area)
        
    final_max_area = max_area if max_area is not None else parsed_filters.get("max_area")
    if isinstance(final_max_area, (int, float)):
        q = q.filter(Property.area_sqft <= final_max_area)
        
    if furnishing and furnishing != "All":
        q = q.filter(Property.furnishing.ilike(furnishing))
    if parking and parking != "All":
        q = q.filter(Property.parking.ilike(parking))

    # Master AI-Ready Dataset default isolation:
    # By default, query ONLY MAIN_AI_READY properties unless explicitly querying historical or specific category
    dataset_category = resolve_val(dataset_category)
    include_historical = resolve_val(include_historical)

    if dataset_category:
        q = q.filter(Property.dataset_category == dataset_category)
    elif not include_historical and not source_type and not current_only and final_listing_type != "Dataset":
        q = q.filter(Property.is_main_ai_ready == True)

    # Phase C Filters
    if current_only:
        q = q.filter(
            (Property.source_type.in_(["PROPPULSE_DIRECT", "CURRENT_AUTHORIZED_LISTING", "owner_listing"])) |
            (Property.listing_status == "CURRENT")
        )

    if verified_only:
        q = q.filter(
            (Property.verification_status.in_(["Verified", "VERIFIED"])) |
            (Property.verified == True)
        )

    if has_real_image:
        q = q.filter(
            (Property.image_provenance.in_(["OWNER_UPLOADED", "AUTHORIZED_PROVIDER", "LICENSED_EXTERNAL"])) |
            (Property.image_count > 0)
        )

    if source_type:
        st = source_type.strip()
        if st.lower() == "historical":
            q = q.filter(Property.source_type.in_(["HISTORICAL_MARKET_DATA", "historical_dataset"]))
        elif st.lower() in ["direct", "proppulse_direct"]:
            q = q.filter(Property.source_type.in_(["PROPPULSE_DIRECT", "owner_listing"]))
        elif st.lower() == "demo":
            q = q.filter(Property.source_type.in_(["DEMO_TEST", "demo_dataset"]))
        else:
            q = q.filter(Property.source_type.ilike(st))

    # Apply pagination skip/limit
    total = q.count()
    if page is not None and page_size is not None:
        skip = (page - 1) * page_size
        limit = page_size
        
    properties = q.order_by(
        case(
            (Property.identity_confidence == 'IDENTITY_RESOLVED', 1),
            (Property.identity_confidence == 'IDENTITY_PARTIAL', 2),
            else_=3
        ),
        case(
            (Property.coordinate_confidence == 'EXACT', 1),
            else_=2
        ),
        case(
            (Property.listing_status == 'CURRENT', 1),
            else_=2
        ),
        Property.created_at.desc(),
        Property.id.asc()
    ).offset(skip).limit(limit).all()
    enriched_items = [enrich_property_out(p) for p in properties]
    return PropertyListOut(items=enriched_items, total=total, page=page, page_size=page_size)


@router.get("/dashboard-stats")
def get_dashboard_stats(db: Session = Depends(get_db)):
    """Return live dataset statistics across historical, demo, and owner listings with locality distributions."""
    from sqlalchemy import func

    total = db.query(Property).count()
    historical = db.query(Property).filter(Property.source_type == "historical_dataset").count()
    demo = db.query(Property).filter(Property.source_type == "demo_dataset").count()
    owner = db.query(Property).filter(Property.source_type == "owner_listing").count()
    buy_count = db.query(Property).filter(
        (Property.transaction_type == "sale") | (Property.listing_type.ilike("Buy"))
    ).count()
    rent_count = db.query(Property).filter(
        (Property.transaction_type == "rent") | (Property.listing_type.ilike("Rent"))
    ).count()
    exact_count = db.query(Property).filter(Property.coordinate_quality == "EXACT").count()
    approx_count = db.query(Property).filter(Property.coordinate_quality == "LOCALITY_APPROXIMATE").count()
    
    main_ai_ready_count = db.query(Property).filter(Property.is_main_ai_ready == True).count()
    historical_ref_count = db.query(Property).filter(Property.dataset_category == "REFERENCE_HISTORICAL").count()
    quarantine_count = db.query(Property).filter(Property.dataset_category == "INVALID_QUARANTINE").count()

    apartments = db.query(Property).filter(Property.property_type.ilike("%Apartment%")).count()
    villas = db.query(Property).filter(Property.property_type.ilike("%Villa%")).count()
    houses = db.query(Property).filter(Property.property_type.ilike("%House%")).count()
    plots = db.query(Property).filter(Property.property_type.ilike("%Plot%")).count()
    
    localities_covered = db.query(Property.locality).distinct().count()

    # Top localities count for executive dashboard
    top_loc_query = (
        db.query(Property.locality, func.count(Property.id))
        .filter(Property.locality.isnot(None), Property.locality != "")
        .group_by(Property.locality)
        .order_by(func.count(Property.id).desc())
        .limit(10)
        .all()
    )
    top_localities = [{"name": loc or "Unknown", "count": count} for loc, count in top_loc_query]
    
    return {
        "total_properties": total,
        "historical_properties": historical,
        "demo_properties": demo,
        "owner_properties": owner,
        "buy_properties": buy_count,
        "rent_properties": rent_count,
        "dataset_listings": historical,
        "verified_direct": owner + demo,
        "exact_coords": exact_count,
        "approx_coords": approx_count,
        "main_ai_ready": main_ai_ready_count,
        "reference_historical": historical_ref_count,
        "quarantined": quarantine_count,
        "apartments": apartments,
        "villas": villas,
        "houses": houses,
        "independent_houses": houses,
        "plots": plots,
        "localities_covered": localities_covered,
        "top_localities": top_localities
    }

@router.get("/dataset-stats")
def get_dataset_stats(db: Session = Depends(get_db)):
    """Retrieve data quality statistics and distributions for admin review."""
    from sqlalchemy import func

    total_properties = db.query(Property).count()
    dataset_listings = db.query(Property).filter(Property.source_type == "historical_dataset").count()
    direct_listings = db.query(Property).filter(Property.source_type.in_(["owner_listing", "demo_dataset"])).count()

    missing_coords = db.query(Property).filter(
        Property.latitude.between(12.95, 12.99),
        Property.longitude.between(77.57, 77.61)
    ).count()

    missing_images = db.query(Property).filter(
        (Property.images.is_(None)) |
        (Property.image_count == 0) |
        (Property.image_count.is_(None))
    ).count()

    missing_contact = db.query(Property).filter(
        (Property.owner_phone == "") | (Property.owner_phone.is_(None))
    ).count()

    locality_dist = (
        db.query(Property.locality, func.count(Property.id))
        .filter(Property.locality.isnot(None), Property.locality != "")
        .group_by(Property.locality)
        .order_by(func.count(Property.id).desc())
        .limit(15)
        .all()
    )
    locality_distribution = [{"locality": loc or "Unknown", "count": count} for loc, count in locality_dist]

    source_dist = (
        db.query(Property.source, func.count(Property.id))
        .filter(Property.source.isnot(None))
        .group_by(Property.source)
        .all()
    )
    source_distribution = [{"source": src or "Unknown", "count": count} for src, count in source_dist]

    return {
        "total_properties": total_properties,
        "dataset_listings": dataset_listings,
        "direct_listings": direct_listings,
        "missing_coordinates": missing_coords,
        "missing_images": missing_images,
        "missing_contact": missing_contact,
        "locality_distribution": locality_distribution,
        "source_distribution": source_distribution
    }


@router.get("/{id}", response_model=PropertyOut)
async def get_property_by_id(
    id: int,
    db: Session = Depends(get_db)
):
    """Get single property details by ID, dynamically populating live Geoapify nearby places if empty."""
    prop = db.query(Property).filter(Property.id == id).first()
    if not prop:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Property not found"
        )
    if getattr(prop, 'visibility_status', None) == 'PRIVATE':
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Property listing not found or is currently private."
        )
        
    if not prop.nearby_places or len(prop.nearby_places) == 0:
        places = await GeoapifyService.get_nearby_places(lat=prop.latitude, lon=prop.longitude, radius_meters=5000)
        if places:
            prop.nearby_places = places
            db.commit()
            db.refresh(prop)

    return enrich_property_out(prop)

@router.get("/{id}/routes")
async def get_property_navigation_routes(
    id: int,
    origin_lat: Optional[float] = Query(None, ge=-90.0, le=90.0, description="Origin user latitude"),
    origin_lon: Optional[float] = Query(None, ge=-180.0, le=180.0, description="Origin user longitude"),
    origin_text: Optional[str] = Query(None, description="Origin address string e.g. 'Majestic, Bengaluru'"),
    db: Session = Depends(get_db)
):
    """
    Compute real multi-modal navigation routes (Car, Bike, Public Transit) to this property.
    Uses property's actual destination coordinates.
    Origin is resolved from user GPS coordinates or user-entered location string.
    """
    prop = db.query(Property).filter(Property.id == id).first()
    if not prop:
        raise HTTPException(status_code=404, detail="Property not found")
    
    # Check if property is private - only authorized administrators may view
    if getattr(prop, 'visibility_status', None) == 'PRIVATE':
        # Default public users receive 404
        raise HTTPException(status_code=404, detail="Property listing not found or is currently private.")

    dest_lat = prop.latitude
    dest_lon = prop.longitude
    resolved_origin_address = None

    if origin_lat is not None and origin_lon is not None:
        o_lat, o_lon = float(origin_lat), float(origin_lon)
    elif origin_text and origin_text.strip():
        geo_res = await GeoapifyService.search_geocode(origin_text.strip())
        if not geo_res:
            raise HTTPException(status_code=400, detail=f"Could not geocode origin location: '{origin_text}'")
        o_lat, o_lon = geo_res["latitude"], geo_res["longitude"]
        resolved_origin_address = geo_res.get("formatted_address")
    else:
        raise HTTPException(
            status_code=400, 
            detail="Must provide either (origin_lat, origin_lon) coordinates or origin_text location string."
        )

    routes_data = await GeoapifyService.get_multi_mode_routes(
        origin_lat=o_lat,
        origin_lon=o_lon,
        dest_lat=dest_lat,
        dest_lon=dest_lon
    )
    routes_data["property_id"] = prop.id
    routes_data["property_title"] = prop.title
    routes_data["property_address"] = prop.address
    routes_data["destination"]["address"] = prop.address
    routes_data["destination"]["coordinates"] = f"{dest_lat:.6f}, {dest_lon:.6f}"
    if resolved_origin_address:
        routes_data["origin"]["address"] = resolved_origin_address
        routes_data["origin"]["source"] = "Searched Location (Geocoded via Geoapify)"
    else:
        routes_data["origin"]["address"] = f"Current Location GPS ({o_lat:.6f}, {o_lon:.6f})"
        routes_data["origin"]["source"] = "Browser Geolocation (GPS)"
    routes_data["origin"]["coordinates"] = f"{o_lat:.6f}, {o_lon:.6f}"

    return routes_data

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_property(
    id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete property listing (owner protected)."""
    prop = db.query(Property).filter(Property.id == id).first()
    if not prop:
        raise HTTPException(status_code=404, detail="Property not found")
    if prop.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this property")
        
    db.delete(prop)
    db.commit()
    return None

@router.post("/", response_model=PropertyOut, status_code=status.HTTP_201_CREATED)
async def create_direct_listing(
    payload: PropertyCreate,
    current_user: User = Depends(get_current_user_with_role("OWNER")),
    db: Session = Depends(get_db)
):

    """Submit a genuine PropPulse Direct property listing."""
    # 1. Validation checks
    if payload.price <= 0:
        raise HTTPException(status_code=400, detail="Price must be a positive numeric value")
    if payload.area_sqft <= 0:
        raise HTTPException(status_code=400, detail="Area in sqft must be a positive numeric value")
    if payload.bhk < 0:
        raise HTTPException(status_code=400, detail="BHK config must be non-negative")
    
    listing_type_clean = payload.listing_type.strip().title()
    if listing_type_clean not in ["Buy", "Rent"]:
        raise HTTPException(status_code=400, detail="Listing type must be 'Buy' or 'Rent'")
        
    prop_type_clean = payload.property_type.strip().title()
    valid_types = ["Apartment", "Independent House", "Villa", "Plot"]
    if prop_type_clean not in valid_types:
        raise HTTPException(
            status_code=400, 
            detail=f"Property type must be one of: {', '.join(valid_types)}"
        )
        
    if not payload.locality.strip():
        raise HTTPException(status_code=400, detail="Locality name is required")
    if not payload.address.strip():
        raise HTTPException(status_code=400, detail="Property address is required")
        
    # 2. Coordinate resolution using the existing Geoapify geocoder
    query_address = f"{payload.locality}, {payload.address}, Bengaluru"
    lat, lon = 12.9716, 77.5946  # Default Bangalore center coordinates fallback
    
    geocode_res = await GeoapifyService.search_geocode(query_address)
    if not geocode_res:
        # Retry with just locality name and Bengaluru bias
        geocode_res = await GeoapifyService.search_geocode(f"{payload.locality}, Bengaluru")
        
    if geocode_res:
        res_lat = geocode_res["latitude"]
        res_lon = geocode_res["longitude"]
        # Bounding box check within Bengaluru corporation scope
        if 12.75 <= res_lat <= 13.25 and 77.30 <= res_lon <= 77.85:
            lat = res_lat
            lon = res_lon

    # Fetch nearby places using coordinates resolved
    places = []
    try:
        from app.services.geoapify_service import GeoapifyService
        places = await GeoapifyService.get_nearby_places(lat=lat, lon=lon, radius_meters=5000)
    except Exception as e:
        print(f"Error fetching nearby places during listing creation: {e}")

    # 3. Create property listing instance with default pending metadata
    p = Property(
        user_id=current_user.id,
        title=payload.title,
        property_type=prop_type_clean,
        listing_type=listing_type_clean,
        bhk=payload.bhk,
        area_sqft=payload.area_sqft,
        bathrooms=payload.bathrooms,
        balconies=payload.balconies,
        floor=payload.floor,
        total_floors=payload.total_floors,
        property_age=payload.property_age,
        facing=payload.facing,
        parking=payload.parking,
        furnishing=payload.furnishing,
        amenities=payload.amenities,
        price=payload.price,
        description=payload.description,
        address=payload.address,
        locality=payload.locality,
        latitude=lat,
        longitude=lon,
        owner_name=payload.owner_name or current_user.full_name,
        owner_phone=payload.owner_phone or "Contact information unavailable",
        images=payload.images or [],
        nearby_places=places or [],
        street_view_available=False,
        seller_type=payload.seller_type or "Owner",
        seller_name=payload.seller_name or payload.owner_name or current_user.full_name,
        phone=payload.phone or payload.owner_phone or "Contact information unavailable",
        verification_status="Pending Verification",
        source_type="owner_listing",
        source="PropPulse Direct",
        source_url="",
        image_source="",
        verified=False
    )
    
    db.add(p)
    db.commit()
    db.refresh(p)
    return enrich_property_out(p)

@router.put("/{id}/verify", response_model=PropertyOut)
def verify_property(
    id: int,
    status: str = Query(..., description="Verification status: Verified, Rejected, or Pending Verification"),
    current_user: User = Depends(get_current_user_with_role("ADMIN")),
    db: Session = Depends(get_db)
):

    """Admin workflow endpoint to transition verification status states."""
    prop = db.query(Property).filter(Property.id == id).first()
    if not prop:
        raise HTTPException(status_code=404, detail="Property not found")
        
    status_clean = status.strip().title()
    if status_clean not in ["Verified", "Rejected", "Pending Verification"]:
        raise HTTPException(
            status_code=400, 
            detail="Invalid verification status. Must be 'Verified', 'Rejected', or 'Pending Verification'"
        )
        
    prop.verification_status = status_clean
    if status_clean == "Verified":
        prop.verified = True
    else:
        prop.verified = False
        
    db.commit()
    db.refresh(prop)
    return enrich_property_out(prop)

@router.get("/{id}/images", response_model=List[dict])
def get_property_images(
    id: int,
    db: Session = Depends(get_db)
):
    """Retrieve all images for a property ordered by primary status and display order."""
    prop = db.query(Property).filter(Property.id == id).first()
    if not prop:
        raise HTTPException(status_code=404, detail="Property not found")

    images = db.query(PropertyImage).filter(PropertyImage.property_id == id).order_by(
        PropertyImage.is_primary.desc(), PropertyImage.order.asc()
    ).all()

    return [{
        "id": img.id,
        "property_id": img.property_id,
        "image_path": img.image_path,
        "source_type": img.source_type or "owner_upload",
        "source_name": img.source_name or "Owner Uploaded",
        "source_url": img.source_url or "",
        "is_primary": bool(img.is_primary),
        "order": img.order,
        "uploaded_at": img.uploaded_at
    } for img in images]

@router.post("/{id}/images", response_model=List[dict])
async def upload_property_images(
    id: int,
    files: List[UploadFile] = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Multipart upload for authentic property photos. Owner or Admin authorization required."""
    prop = db.query(Property).filter(Property.id == id).first()
    if not prop:
        raise HTTPException(status_code=404, detail="Property not found")
    if prop.user_id != current_user.id and getattr(current_user, 'role', 'USER') != 'ADMIN':
        raise HTTPException(status_code=403, detail="Not authorized to modify images for this property")

    saved_refs = []
    start_order = db.query(PropertyImage).filter(PropertyImage.property_id == id).count()
    existing_primary = db.query(PropertyImage).filter(
        PropertyImage.property_id == id, PropertyImage.is_primary == True
    ).first()

    for i, file in enumerate(files):
        # StorageService validates file size <= 5MB, allowed extension, MIME type, and PIL binary content
        path = await StorageService.upload_property_image(file, id)
        
        is_first_primary = (existing_primary is None and i == 0)

        img_db = PropertyImage(
            property_id=id,
            image_path=path,
            source_type="owner_upload",
            source_name=f"Uploaded by Owner ({current_user.full_name or current_user.email})",
            source_url="",
            is_primary=is_first_primary,
            order=start_order + i,
            uploaded_by=current_user.id
        )
        db.add(img_db)
        db.commit()
        db.refresh(img_db)

        saved_refs.append({
            "id": img_db.id,
            "property_id": img_db.property_id,
            "image_path": img_db.image_path,
            "source_type": img_db.source_type,
            "source_name": img_db.source_name,
            "is_primary": img_db.is_primary,
            "order": img_db.order
        })

    return saved_refs

from pydantic import BaseModel, HttpUrl

class ExternalImageRequest(BaseModel):
    image_url: str
    source_name: str
    source_url: Optional[str] = ""

@router.post("/{id}/external-images", response_model=dict)
def add_external_property_image(
    id: int,
    payload: ExternalImageRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add a legitimate licensed external property image URL."""
    prop = db.query(Property).filter(Property.id == id).first()
    if not prop:
        raise HTTPException(status_code=404, detail="Property not found")
    if prop.user_id != current_user.id and getattr(current_user, 'role', 'USER') != 'ADMIN':
        raise HTTPException(status_code=403, detail="Not authorized to modify images for this property")

    url = payload.image_url.strip()
    if not url.startswith("https://") and not url.startswith("http://"):
        raise HTTPException(status_code=400, detail="Invalid image URL scheme. Must be an HTTP/HTTPS URL.")

    start_order = db.query(PropertyImage).filter(PropertyImage.property_id == id).count()
    existing_primary = db.query(PropertyImage).filter(
        PropertyImage.property_id == id, PropertyImage.is_primary == True
    ).first()

    img_db = PropertyImage(
        property_id=id,
        image_path=url,
        source_type="licensed_external",
        source_name=payload.source_name or "Licensed External Source",
        source_url=payload.source_url or "",
        is_primary=(existing_primary is None),
        order=start_order,
        uploaded_by=current_user.id
    )
    db.add(img_db)
    db.commit()
    db.refresh(img_db)

    return {
        "id": img_db.id,
        "property_id": img_db.property_id,
        "image_path": img_db.image_path,
        "source_type": img_db.source_type,
        "source_name": img_db.source_name,
        "source_url": img_db.source_url,
        "is_primary": img_db.is_primary,
        "order": img_db.order
    }

@router.delete("/{id}/images/{image_id}", response_model=dict)
def delete_property_image(
    id: int,
    image_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete specific property image. Owner or Admin authorization required."""
    prop = db.query(Property).filter(Property.id == id).first()
    if not prop:
        raise HTTPException(status_code=404, detail="Property not found")
    if prop.user_id != current_user.id and getattr(current_user, 'role', 'USER') != 'ADMIN':
        raise HTTPException(status_code=403, detail="Not authorized to modify images for this property")

    img_db = db.query(PropertyImage).filter(
        PropertyImage.id == image_id, PropertyImage.property_id == id
    ).first()
    if not img_db:
        raise HTTPException(status_code=404, detail="Image record not found")

    # Safely delete disk file if local upload
    if img_db.source_type == "owner_upload" or img_db.image_path.startswith("/static/uploads/"):
        StorageService.delete_property_image_file(img_db.image_path)

    was_primary = img_db.is_primary
    db.delete(img_db)
    db.commit()

    # If deleted image was primary, set next image as primary
    if was_primary:
        next_img = db.query(PropertyImage).filter(PropertyImage.property_id == id).order_by(PropertyImage.order.asc()).first()
        if next_img:
            next_img.is_primary = True
            db.commit()

    return {"message": "Image deleted successfully", "image_id": image_id}

@router.put("/{id}/images/{image_id}/primary", response_model=dict)
def set_primary_property_image(
    id: int,
    image_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Set specified image as the primary image for the property."""
    prop = db.query(Property).filter(Property.id == id).first()
    if not prop:
        raise HTTPException(status_code=404, detail="Property not found")
    if prop.user_id != current_user.id and getattr(current_user, 'role', 'USER') != 'ADMIN':
        raise HTTPException(status_code=403, detail="Not authorized to modify images for this property")

    target_img = db.query(PropertyImage).filter(
        PropertyImage.id == image_id, PropertyImage.property_id == id
    ).first()
    if not target_img:
        raise HTTPException(status_code=404, detail="Image record not found")

    # Reset all images for this property to is_primary = False
    db.query(PropertyImage).filter(PropertyImage.property_id == id).update({"is_primary": False})
    
    target_img.is_primary = True
    db.commit()
    db.refresh(target_img)

    return {
        "message": "Primary image updated successfully",
        "primary_image_id": target_img.id,
        "image_path": target_img.image_path
    }

@router.post("/{id}/contact")
def get_property_contact_details(
    id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Secure workflow exposing owner contact information only when legitimately permitted."""
    prop = db.query(Property).filter(Property.id == id).first()
    if not prop:
        raise HTTPException(status_code=404, detail="Property not found")

    from app.services.contact_verification_service import ContactVerificationService
    contact_info = ContactVerificationService.resolve_property_contact(prop)

    return {
        "owner_name": prop.owner_name or "Verified Contact",
        "seller_name": prop.seller_name or "Verified Seller",
        "contact_type": contact_info["contact_type"],
        "contact_number": contact_info["contact_number"],
        "phone": contact_info["contact_number"],
        "owner_phone": contact_info["contact_number"],
        "contact_source": contact_info["contact_source"],
        "contact_source_url": contact_info["contact_source_url"],
        "contact_display_permission": contact_info["contact_display_permission"],
        "source_platform": contact_info["source_platform"],
        "source_listing_id": contact_info["source_listing_id"],
        "display_message": contact_info["display_message"]
    }




