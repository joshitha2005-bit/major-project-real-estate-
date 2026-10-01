from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Form, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User
from app.models.property import Property, PropertyImage
from app.schemas.property import PropertyOut, PropertyCreate
from app.services.listing_service import ListingService
from app.services.image_provenance import ImageProvenanceService
from app.api.deps import get_current_user, get_current_user_with_role

router = APIRouter()

@router.post("/", response_model=Dict[str, Any], status_code=status.HTTP_201_CREATED)
def create_direct_listing(
    listing_in: PropertyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new PropPulse Direct property listing.
    Initial status is set to PENDING (Pending Verification).
    Calculates ₹/sqft and enforces image provenance.
    """
    sqft_rate = ListingService.calculate_price_per_sqft(listing_in.price, listing_in.area_sqft)

    v_status = "Verified" if current_user.role == "ADMIN" else "Pending Verification"
    l_status = "CURRENT" if v_status == "Verified" else "PENDING"

    new_prop = Property(
        user_id=current_user.id,
        title=listing_in.title,
        property_type=listing_in.property_type,
        listing_type=listing_in.listing_type or "Buy",
        bhk=listing_in.bhk,
        area_sqft=listing_in.area_sqft,
        bathrooms=listing_in.bathrooms,
        balconies=listing_in.balconies,
        floor=listing_in.floor,
        total_floors=listing_in.total_floors,
        property_age=listing_in.property_age,
        facing=listing_in.facing,
        parking=listing_in.parking,
        furnishing=listing_in.furnishing,
        availability=getattr(listing_in, "availability", "Ready to Move"),
        amenities=listing_in.amenities or [],
        price=listing_in.price,
        description=listing_in.description,
        address=listing_in.address,
        locality=listing_in.locality,
        sub_locality=getattr(listing_in, "sub_locality", None),
        latitude=listing_in.latitude if listing_in.latitude else 12.9716,
        longitude=listing_in.longitude if listing_in.longitude else 77.5946,
        owner_name=listing_in.owner_name or current_user.full_name or "PropPulse Owner",
        owner_phone=listing_in.phone or listing_in.owner_phone or "+91 98860 12345",
        images=listing_in.images or [],
        seller_type=listing_in.seller_type or "Owner",
        seller_name=listing_in.seller_name or current_user.full_name or "PropPulse Seller",
        phone=listing_in.phone or "+91 98860 12345",
        verification_status=v_status,
        source_type="PROPPULSE_DIRECT",
        source="PropPulse Direct",
        source_name="PropPulse Direct",
        listing_status=l_status,
        coordinate_quality="EXACT",
        image_provenance="OWNER_UPLOADED" if listing_in.images else "NO_IMAGE",
        image_count=len(listing_in.images) if listing_in.images else 0,
        contact_available=True,
        contact_source="Owner Provided",
        price_per_sqft=sqft_rate
    )
    db.add(new_prop)
    db.commit()
    db.refresh(new_prop)

    return ListingService.format_listing_out(new_prop)

@router.post("/upload-images", response_model=Dict[str, Any])
async def upload_property_images(
    property_id: int = Form(...),
    primary_index: int = Form(0),
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Upload real property photos for a listing with duplicate hash check,
    resolution validation (>= 400x300), and OWNER_UPLOADED provenance tagging.
    """
    prop = db.query(Property).filter(Property.id == property_id).first()
    if not prop:
        raise HTTPException(status_code=404, detail="Property listing not found.")

    if prop.user_id != current_user.id and current_user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="Not authorized to add photos to this listing.")

    uploaded_results = []
    errors = []

    for idx, f in enumerate(files):
        content = await f.read()
        is_primary = (idx == primary_index)
        
        res = ImageProvenanceService.process_and_store_owner_upload(
            db=db,
            image_bytes=content,
            filename=f.filename,
            property_id=property_id,
            user_id=current_user.id,
            is_primary=is_primary
        )
        if res.get("success"):
            uploaded_results.append(res)
        else:
            errors.append({"filename": f.filename, "error": res.get("error")})

    db.refresh(prop)
    img_info = ImageProvenanceService.get_property_image_provenance(prop)

    return {
        "property_id": property_id,
        "uploaded_count": len(uploaded_results),
        "images": img_info["images"],
        "image_provenance": img_info["image_provenance"],
        "provenance_badge": img_info["provenance_badge"],
        "errors": errors
    }

@router.get("/admin/pending", response_model=List[Dict[str, Any]])
def list_pending_listings_admin(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_with_role("ADMIN"))
):
    """
    Admin endpoint to view all listings pending verification.
    """
    props = db.query(Property).filter(
        Property.verification_status.in_(["Pending", "Pending Verification", "PENDING"])
    ).order_by(Property.id.desc()).all()
    return [ListingService.format_listing_out(p) for p in props]

@router.post("/admin/{listing_id}/verify", response_model=Dict[str, Any])
def verify_listing_admin(
    listing_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_with_role("ADMIN"))
):
    """
    Admin endpoint to verify a direct listing.
    """
    try:
        pid = int(listing_id.replace("BLR-", ""))
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid listing_id format.")

    prop = db.query(Property).filter(Property.id == pid).first()
    if not prop:
        raise HTTPException(status_code=404, detail="Property listing not found.")

    prop.verification_status = "Verified"
    prop.verified = True
    prop.listing_status = "CURRENT"
    prop.last_verified_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(prop)

    return ListingService.format_listing_out(prop)

@router.post("/admin/{listing_id}/reject", response_model=Dict[str, Any])
def reject_listing_admin(
    listing_id: str,
    reason: Optional[str] = Query("Listing details do not satisfy verification guidelines"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_with_role("ADMIN"))
):
    """
    Admin endpoint to reject a direct listing.
    """
    try:
        pid = int(listing_id.replace("BLR-", ""))
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid listing_id format.")

    prop = db.query(Property).filter(Property.id == pid).first()
    if not prop:
        raise HTTPException(status_code=404, detail="Property listing not found.")

    prop.verification_status = "Rejected"
    prop.verified = False
    prop.listing_status = "INACTIVE"
    db.commit()
    db.refresh(prop)

    return ListingService.format_listing_out(prop)

@router.post("/admin/{listing_id}/expire", response_model=Dict[str, Any])
def expire_listing_admin(
    listing_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_with_role("ADMIN"))
):
    """
    Admin endpoint to mark a direct listing as EXPIRED.
    """
    try:
        pid = int(listing_id.replace("BLR-", ""))
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid listing_id format.")

    prop = db.query(Property).filter(Property.id == pid).first()
    if not prop:
        raise HTTPException(status_code=404, detail="Property listing not found.")

    prop.verification_status = "Expired"
    prop.listing_status = "EXPIRED"
    prop.verified = False
    db.commit()
    db.refresh(prop)

    return ListingService.format_listing_out(prop)

@router.get("/", response_model=List[Dict[str, Any]])
def list_direct_listings(
    locality: Optional[str] = Query(None),
    property_type: Optional[str] = Query(None),
    bhk: Optional[int] = Query(None),
    verified_only: Optional[bool] = Query(None),
    db: Session = Depends(get_db)
):
    """
    List PropPulse Direct listings with search filtering.
    """
    q = db.query(Property).filter(
        (Property.source_type == "PROPPULSE_DIRECT") | (Property.source_type == "owner_listing")
    )
    if verified_only:
        q = q.filter(Property.verification_status.in_(["Verified", "VERIFIED"]))

    if locality:
        q = q.filter(Property.locality.ilike(f"%{locality.strip()}%"))
    if property_type:
        q = q.filter(Property.property_type.ilike(f"%{property_type.strip()}%"))
    if bhk:
        q = q.filter(Property.bhk == bhk)

    props = q.order_by(Property.id.desc()).all()
    return [ListingService.format_listing_out(p) for p in props]

@router.get("/{listing_id}", response_model=Dict[str, Any])
def get_direct_listing_detail(
    listing_id: str,
    db: Session = Depends(get_db)
):
    """
    Get detailed view of single direct property listing.
    """
    try:
        pid = int(listing_id.replace("BLR-", ""))
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid listing_id format.")

    prop = db.query(Property).filter(Property.id == pid).first()
    if not prop:
        raise HTTPException(status_code=404, detail="Property listing not found.")

    return ListingService.format_listing_out(prop)

@router.put("/{listing_id}", response_model=Dict[str, Any])
def update_direct_listing(
    listing_id: str,
    listing_in: PropertyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update an existing PropPulse Direct listing.
    """
    try:
        pid = int(listing_id.replace("BLR-", ""))
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid listing_id format.")

    prop = db.query(Property).filter(Property.id == pid).first()
    if not prop:
        raise HTTPException(status_code=404, detail="Property listing not found.")

    if prop.user_id != current_user.id and current_user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="Not authorized to edit this listing.")

    for field, val in listing_in.model_dump(exclude_unset=True).items():
        if hasattr(prop, field) and val is not None:
            setattr(prop, field, val)

    prop.price_per_sqft = ListingService.calculate_price_per_sqft(prop.price, prop.area_sqft)
    db.commit()
    db.refresh(prop)

    return ListingService.format_listing_out(prop)

@router.delete("/{listing_id}", status_code=status.HTTP_200_OK)
def delete_direct_listing(
    listing_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a direct property listing.
    """
    try:
        pid = int(listing_id.replace("BLR-", ""))
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid listing_id format.")

    prop = db.query(Property).filter(Property.id == pid).first()
    if not prop:
        raise HTTPException(status_code=404, detail="Property listing not found.")

    if prop.user_id != current_user.id and current_user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="Not authorized to delete this listing.")

    db.delete(prop)
    db.commit()
    return {"message": f"Listing BLR-{pid} deleted successfully."}

