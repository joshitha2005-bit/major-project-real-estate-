import os
import uuid
import random
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query, status
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.database import get_db
from app.models.user import User
from app.models.property import Property
from app.schemas.property import PropertyOut, PropertyListOut
from app.services.geoapify_service import GeoapifyService
from app.api.deps import get_current_user

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

def format_indian_currency(amount: float) -> str:
    """Format number into Indian Rupee Lakhs / Crores string representation."""
    if amount >= 10000000:
        return f"₹{amount / 10000000:.2f} Cr"
    elif amount >= 100000:
        return f"₹{amount / 100000:.2f} Lakh"
    else:
        return f"₹{int(amount):,}"

def enrich_property_out(p: Property) -> PropertyOut:
    """Enrich property model with calculated fields for API response."""
    price_sqft = round(p.price / p.area_sqft, 2) if p.area_sqft > 0 else 0
    price_formatted = format_indian_currency(p.price)
    
    out_dict = {
        "id": p.id,
        "user_id": p.user_id,
        "title": p.title,
        "property_type": p.property_type,
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
        "price": p.price,
        "description": p.description,
        "address": p.address,
        "latitude": p.latitude,
        "longitude": p.longitude,
        "owner_name": p.owner_name or "PropPulse Verified Owner",
        "owner_phone": p.owner_phone or "+91 98860 12345",
        "images": p.images or [],
        "nearby_places": p.nearby_places or [],
        "price_per_sqft": price_sqft,
        "price_formatted": price_formatted,
        "created_at": p.created_at
    }
    return PropertyOut(**out_dict)

def auto_generate_locality_sample_properties(locality_name: str, db: Session) -> List[Property]:
    """Auto-generate realistic sample properties for any new searched Bangalore locality."""
    default_user = db.query(User).first()
    if not default_user:
        return []

    created_list = []
    base_price_sqft = 7500.0
    if "koramangala" in locality_name.lower(): base_price_sqft = 12500.0
    elif "indiranagar" in locality_name.lower(): base_price_sqft = 14000.0
    elif "whitefield" in locality_name.lower(): base_price_sqft = 7800.0
    elif "electronic city" in locality_name.lower(): base_price_sqft = 5600.0
    elif "chandapura" in locality_name.lower(): base_price_sqft = 4500.0

    specs = [
        {"ptype": "Apartment", "bhk": 2, "area": 1200, "baths": 2, "balc": 1},
        {"ptype": "Apartment", "bhk": 3, "area": 1650, "baths": 3, "balc": 2},
        {"ptype": "Villa", "bhk": 4, "area": 3200, "baths": 4, "balc": 3},
        {"ptype": "Independent House", "bhk": 3, "area": 2200, "baths": 3, "balc": 2}
    ]

    for i, spec in enumerate(specs):
        builder = BUILDERS[i % len(BUILDERS)]
        owner = OWNERS[i % len(OWNERS)]
        images = IMAGES_POOL[i % len(IMAGES_POOL)]
        
        area = spec["area"]
        price = round(base_price_sqft * area * (1 + (i * 0.1)), -4)
        
        p = Property(
            user_id=default_user.id,
            title=f"{builder} {locality_name.title()} {spec['bhk']}BHK {spec['ptype']}",
            property_type=spec["ptype"],
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
            price=float(price),
            description=f"Luxury {spec['ptype']} in {locality_name.title()} built by {builder}. Features {spec['bhk']} BHK layout with 24/7 security, power backup, covered parking, and prime GIS accessibility.",
            address=f"Main Road, {locality_name.title()}, Bengaluru - 560001",
            latitude=12.9716 + (i * 0.003),
            longitude=77.5946 + (i * 0.002),
            owner_name=owner[0],
            owner_phone=owner[1],
            images=images,
            nearby_places=[]
        )
        db.add(p)
        created_list.append(p)

    db.commit()
    return created_list

@router.get("/", response_model=PropertyListOut)
def list_properties(
    query: Optional[str] = Query(None, description="Search term e.g. Koramangala, Whitefield"),
    property_type: Optional[str] = Query(None),
    bhk: Optional[int] = Query(None),
    min_price: Optional[float] = Query(None),
    max_price: Optional[float] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, le=100),
    db: Session = Depends(get_db)
):
    """Retrieve property listings with locality extraction & auto-sample generation for 100% coverage."""
    q = db.query(Property)
    
    clean_locality = None
    if query and isinstance(query, str) and query.strip():
        # Extract primary locality keyword e.g. "Koramangala, Bengaluru..." -> "Koramangala"
        raw_query = query.strip()
        clean_locality = raw_query.split(',')[0].strip()
        search_pattern = f"%{clean_locality}%"
        
        q = q.filter(
            (Property.title.ilike(search_pattern)) | 
            (Property.address.ilike(search_pattern)) |
            (Property.description.ilike(search_pattern))
        )
        
    if property_type and isinstance(property_type, str) and property_type != "All":
        q = q.filter(Property.property_type.ilike(property_type))
    if isinstance(bhk, int):
        q = q.filter(Property.bhk == bhk)
    if isinstance(min_price, (int, float)):
        q = q.filter(Property.price >= min_price)
    if isinstance(max_price, (int, float)):
        q = q.filter(Property.price <= max_price)
        
    properties = q.order_by(Property.created_at.desc()).offset(skip).limit(limit).all()
    
    # Auto-seed if specific locality query returned 0 properties
    if len(properties) == 0 and clean_locality and len(clean_locality) > 2:
        auto_generate_locality_sample_properties(clean_locality, db)
        
        # Re-query
        search_pattern = f"%{clean_locality}%"
        q_new = db.query(Property).filter(
            (Property.title.ilike(search_pattern)) | 
            (Property.address.ilike(search_pattern)) |
            (Property.description.ilike(search_pattern))
        )
        properties = q_new.order_by(Property.created_at.desc()).offset(skip).limit(limit).all()

    total = len(properties)
    enriched_items = [enrich_property_out(p) for p in properties]
    return PropertyListOut(items=enriched_items, total=total)

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
