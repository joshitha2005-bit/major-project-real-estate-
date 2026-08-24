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
from app.schemas.property import PropertyOut, PropertyListOut, PropertyCreate
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
    "malleshwaram": (13.0031, 77.5643),
    "basavanagudi": (12.9421, 77.5752),
    "brookefield": (12.9658, 77.7183),
    "chandapura": (12.8004, 77.7063)
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
    if p.source_type == "historical_dataset" or p.source == "Bengaluru_House_Data.csv":
        coord_status = "LOCALITY_APPROXIMATE"
    elif p.latitude == 0 and p.longitude == 0:
        coord_status = "UNAVAILABLE"
    else:
        coord_status = "EXACT"
        
    # Determine property type source
    is_historical = (p.source_type == "historical_dataset" or p.source == "Bengaluru_House_Data.csv")
    ptype_src = "inferred" if is_historical else "user_provided"
    
    # Determine title & society normalization
    raw_title = (p.title or "").strip()
    loc_str = extract_location(p)
    
    REAL_BUILDERS = ["prestige", "sobha", "salarpuria", "brigade", "godrej", "assetz", "puravankara", "l&t", "embassy", "shriram", "mantri", "dharani", "signature", "century", "provident"]
    is_real_builder = any(b in raw_title.lower() for b in REAL_BUILDERS)
    
    if is_real_builder:
        final_title = raw_title
        society_val = raw_title
        property_type_val = p.property_type
    elif not is_historical and not is_anonymized_code(raw_title):
        final_title = raw_title
        society_val = raw_title
        property_type_val = p.property_type
    else:
        # Rule B & C: Transparent fallback using actual dataset fields (size + location)
        if "bedroom" in raw_title.lower() or (p.bhk and p.bhk > 4):
            size_str = f"{p.bhk} Bedroom"
        elif p.bhk and p.bhk > 0:
            size_str = f"{p.bhk} BHK"
        else:
            size_str = ""
            
        if size_str:
            final_title = f"{size_str} in {loc_str}"
        else:
            final_title = f"Property in {loc_str}"
            
        society_val = None
        property_type_val = p.property_type

    # Filter out synthetic seed images (only genuine uploaded or dataset images allowed)
    raw_images = [img.image_path for img in p.property_images] if p.property_images else (p.images or [])
    filtered_images = [img for img in raw_images if isinstance(img, str) and "unsplash.com" not in img and img.strip()]

    # Phone contact privacy and fallback
    SEED_PHONES = {"+91 98860 12345", "+91 98450 67890", "+91 99001 88345", "+91 98110 99887", "+91 98801 33456", "+91 97400 22341", "+91 98440 66789", "+91 98866 55432", "+91 98451 77654", "+91 98800 33210"}
    if p.source_type == "owner_listing":
        phone_val = "[Redacted - Reveal via contact button]"
    elif p.owner_phone and p.owner_phone.strip() and p.owner_phone not in SEED_PHONES and p.owner_phone != "Contact information unavailable":
        phone_val = p.owner_phone
    else:
        phone_val = "Contact information unavailable"

    out_dict = {
        "id": p.id,
        "user_id": p.user_id,
        "title": final_title,
        "property_type": property_type_val,
        "listing_type": p.listing_type or "Buy",
        "bhk": p.bhk,
        "area_sqft": p.area_sqft,
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
        "description": p.description,
        "address": p.address,
        "locality": p.locality or "",
        "latitude": p.latitude,
        "longitude": p.longitude,
        "owner_name": p.owner_name if p.source_type == "owner_listing" else "Historical Dataset",
        "owner_phone": phone_val,
        "images": filtered_images,
        "nearby_places": p.nearby_places or [],
        "street_view_available": bool(p.street_view_available),
        "seller_type": p.seller_type or "Owner",
        "seller_name": p.seller_name if p.source_type == "owner_listing" else "Historical Dataset",
        "phone": phone_val,
        "verification_status": p.verification_status or "Verified",
        "source_type": p.source_type or "demo_dataset",
        "source": p.source or "PropPulse Direct",
        "source_url": p.source_url or "",
        "image_source": p.image_source or "",
        "verified": bool(p.verified),
        "price_per_sqft": price_sqft,
        "price_formatted": price_formatted,
        "coordinate_status": coord_status,
        "property_type_source": ptype_src,
        "society": society_val,
        "uploaded_images": p.property_images or [],
        "created_at": p.created_at
    }
    return PropertyOut(**out_dict)

def auto_generate_locality_sample_properties(
    locality_name: str, 
    db: Session, 
    lat: Optional[float] = None, 
    lon: Optional[float] = None
) -> List[Property]:
    """Auto-generate realistic sample properties near the searched coordinates for 100% test coverage."""
    default_user = db.query(User).first()
    if not default_user:
        return []

    base_lat = lat if (lat is not None and lat != 0) else 12.9716
    base_lon = lon if (lon is not None and lon != 0) else 77.5946

    created_list = []
    base_price_sqft = 7500.0
    loc_lower = locality_name.lower()
    if "koramangala" in loc_lower: base_price_sqft = 12500.0
    elif "indiranagar" in loc_lower: base_price_sqft = 14000.0
    elif "whitefield" in loc_lower: base_price_sqft = 7800.0
    elif "electronic city" in loc_lower: base_price_sqft = 5600.0
    elif "chandapura" in loc_lower: base_price_sqft = 4500.0

    specs = [
        {"ptype": "Apartment", "bhk": 2, "area": 1200, "baths": 2, "balc": 1},
        {"ptype": "Apartment", "bhk": 3, "area": 1650, "baths": 3, "balc": 2},
        {"ptype": "Villa", "bhk": 4, "area": 3200, "baths": 4, "balc": 3},
        {"ptype": "Independent House", "bhk": 3, "area": 2200, "baths": 3, "balc": 2}
    ]

    for i, spec in enumerate(specs):
        builder = BUILDERS[i % len(BUILDERS)]
        images = []
        
        area = spec["area"]
        price = round(base_price_sqft * area * (1 + (i * 0.1)), -4)

        listing_type = "Rent" if i % 3 == 0 else "Buy"
        p_lat = base_lat + (i * 0.003 - 0.0045)
        p_lon = base_lon + (i * 0.0025 - 0.003)

        amenities_list = ["Security", "Power Backup", "Water Supply"]
        if spec["ptype"] == "Apartment":
            amenities_list += ["Lift", "Gym", "Clubhouse"]
        elif spec["ptype"] == "Villa":
            amenities_list += ["Private Garden", "Swimming Pool", "Car Parking"]
        
        p = Property(
            user_id=default_user.id,
            title=f"{builder} {locality_name.title()} {spec['bhk']}BHK {spec['ptype']}",
            property_type=spec["ptype"],
            listing_type=listing_type,
            bhk=spec["bhk"],
            area_sqft=float(area),
            bathrooms=spec["baths"],
            balconies=spec["balc"],
            floor=3 if spec["ptype"] == "Apartment" else 1,
            total_floors=10 if spec["ptype"] == "Apartment" else 2,
            property_age="1-5 yrs" if i % 2 == 0 else "New",
            facing="East" if i % 2 == 0 else "North",
            parking="Covered",
            furnishing="Semi-Furnished",
            amenities=amenities_list,
            price=float(price),
            description=f"Luxury {spec['ptype']} in {locality_name.title()} built by {builder}. Features {spec['bhk']} BHK layout with 24/7 security, power backup, covered parking, and prime GIS accessibility.",
            address=f"Block {i+1}, Main Road, {locality_name.title()}, Bengaluru - 560001",
            locality=locality_name.title(),
            latitude=round(p_lat, 6),
            longitude=round(p_lon, 6),
            owner_name="PropPulse Verified Owner",
            owner_phone="Contact information unavailable",
            images=images,
            nearby_places=[],
            street_view_available=(i % 2 == 0),
            seller_type="Owner" if i % 2 == 0 else "Broker",
            seller_name="PropPulse Verified Seller",
            phone="Contact information unavailable",
            verification_status="Verified",
            source_type="demo_dataset"
        )
        db.add(p)
        created_list.append(p)

    db.commit()
    return created_list

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
    page = resolve_val(page)
    page_size = resolve_val(page_size)
    
    skip = resolve_val(skip)
    if skip is None: skip = 0
    limit = resolve_val(limit)
    if limit is None: limit = 50

    q = db.query(Property)
    
    parsed_filters = {}
    if query and isinstance(query, str) and query.strip():
        parsed_filters = parse_natural_query(query)

    # 1. Locality strict filter
    final_locality = parsed_filters.get("locality")
    if final_locality:
        search_pattern = f"%{final_locality}%"
        q = q.filter(Property.locality.ilike(search_pattern))
    elif query and isinstance(query, str) and query.strip():
        # Fallback to splitting by comma for traditional locality searches
        clean_locality = query.strip().split(',')[0].strip()
        search_pattern = f"%{clean_locality}%"
        q = q.filter(Property.locality.ilike(search_pattern))
        
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

    # Apply pagination skip/limit
    total = q.count()
    if page is not None and page_size is not None:
        skip = (page - 1) * page_size
        limit = page_size
        
    properties = q.order_by(Property.created_at.desc()).offset(skip).limit(limit).all()
    enriched_items = [enrich_property_out(p) for p in properties]
    return PropertyListOut(items=enriched_items, total=total, page=page, page_size=page_size)


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
        
    if not prop.nearby_places or len(prop.nearby_places) == 0:
        places = await GeoapifyService.get_nearby_places(lat=prop.latitude, lon=prop.longitude, radius_meters=5000)
        if places:
            prop.nearby_places = places
            db.commit()
            db.refresh(prop)
            
    return enrich_property_out(prop)

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

@router.post("/{id}/images", response_model=List[dict])
async def upload_property_images(
    id: int,
    files: List[UploadFile] = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Multipart upload for genuine direct listing property photos."""
    prop = db.query(Property).filter(Property.id == id).first()
    if not prop:
        raise HTTPException(status_code=404, detail="Property not found")
    if prop.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to modify this property")
        
    saved_refs = []
    # Clear existing if uploading fresh batch or just append them preserving order index
    start_order = db.query(PropertyImage).filter(PropertyImage.property_id == id).count()
    
    for i, file in enumerate(files):
        if not file.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail=f"File '{file.filename}' is not a valid image")
            
        path = await StorageService.upload_property_image(file, id)
        img_db = PropertyImage(
            property_id=id,
            image_path=path,
            image_source="user_upload",
            order=start_order + i
        )
        db.add(img_db)
        db.commit()
        db.refresh(img_db)
        saved_refs.append({
            "id": img_db.id,
            "image_path": img_db.image_path,
            "order": img_db.order
        })
        
    return saved_refs

@router.post("/{id}/contact")
def get_property_contact_details(
    id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Secure workflow exposing owner contact information only to authenticated sessions."""
    prop = db.query(Property).filter(Property.id == id).first()
    if not prop:
        raise HTTPException(status_code=404, detail="Property not found")
        
    return {
        "owner_name": prop.owner_name or "PropPulse Verified Owner",
        "owner_phone": prop.owner_phone or "+91 98860 12345",
        "seller_name": prop.seller_name or "PropPulse Verified Seller",
        "phone": prop.phone or "+91 98860 12345"
    }

@router.get("/dashboard-stats")
def get_dashboard_stats(db: Session = Depends(get_db)):
    """Retrieve aggregate database statistics for the main dashboard dashboard."""
    from sqlalchemy import func
    
    total_properties = db.query(Property).count()
    buy_properties = db.query(Property).filter(Property.listing_type.ilike("Buy")).count()
    rent_properties = db.query(Property).filter(Property.listing_type.ilike("Rent")).count()
    
    apartments = db.query(Property).filter(Property.property_type.ilike("Apartment")).count()
    villas = db.query(Property).filter(Property.property_type.ilike("Villa")).count()
    independent_houses = db.query(Property).filter(Property.property_type.ilike("Independent House")).count()
    
    localities_covered = db.query(Property.locality).distinct().count()
    
    verified_direct = db.query(Property).filter(
        Property.source_type == "owner_listing",
        Property.verification_status == "Verified"
    ).count()
    
    dataset_listings = db.query(Property).filter(
        Property.source_type == "historical_dataset"
    ).count()
    
    # Top localities count
    top_loc_query = db.query(Property.locality, func.count(Property.id)).group_by(Property.locality).order_by(func.count(Property.id).desc()).limit(10).all()
    top_localities = [{"name": loc or "Unknown", "count": count} for loc, count in top_loc_query]
    
    return {
        "total_properties": total_properties,
        "buy_properties": buy_properties,
        "rent_properties": rent_properties,
        "apartments": apartments,
        "villas": villas,
        "independent_houses": independent_houses,
        "localities_covered": localities_covered,
        "verified_direct": verified_direct,
        "dataset_listings": dataset_listings,
        "top_localities": top_localities
    }

@router.get("/dataset-stats")
def get_dataset_stats(
    current_user: User = Depends(get_current_user_with_role("ADMIN")),
    db: Session = Depends(get_db)
):
    """Retrieve data quality statistics for admin review."""
    from sqlalchemy import func
    
    total_properties = db.query(Property).count()
    dataset_listings = db.query(Property).filter(Property.source_type == "historical_dataset").count()
    direct_listings = db.query(Property).filter(Property.source_type == "owner_listing").count()
    
    # Missing coordinates ( बेंगलुरु center check )
    missing_coords = db.query(Property).filter(
        Property.latitude.between(12.95, 12.99),
        Property.longitude.between(77.57, 77.61)
    ).count()
    
    # Missing images
    missing_images = db.query(Property).filter(
        (Property.images == "[]") | (Property.images == "") | (Property.images.is_(None))
    ).count()
    
    # Missing contact
    missing_contact = db.query(Property).filter(
        (Property.owner_phone == "") | (Property.owner_phone.is_(None))
    ).count()
    
    # Locality distribution
    locality_dist = db.query(Property.locality, func.count(Property.id)).group_by(Property.locality).order_by(func.count(Property.id).desc()).limit(15).all()
    locality_distribution = [{"locality": loc or "Unknown", "count": count} for loc, count in locality_dist]
    
    # Source distribution
    source_dist = db.query(Property.source, func.count(Property.id)).group_by(Property.source).all()
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



