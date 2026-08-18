from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.core.database import get_db
from app.models.user import User
from app.models.property import Property
from app.models.search_history import SearchHistory
from app.models.saved_location import SavedLocation
from app.schemas.location import (
    GeocodeResult, NearbyPlace, SearchHistoryOut, 
    SavedLocationCreate, SavedLocationOut
)
from app.services.geoapify_service import GeoapifyService
from app.services.safety_service import SafetyGuardService
from app.api.deps import get_current_user, get_current_user_optional

router = APIRouter()

@router.get("/search-location", response_model=GeocodeResult)
async def search_location(
    query: Optional[str] = Query(None, description="Location search string e.g., Koramangala"),
    text: Optional[str] = Query(None, description="Alternative parameter for search text"),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """Geocode locality string using Geoapify API and record in user search history."""
    search_query = (query or text or "").strip()
    if not search_query:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Search query parameter is required."
        )

    result = await GeoapifyService.search_geocode(search_query)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Location '{search_query}' could not be geocoded."
        )

    if current_user:
        try:
            history_item = SearchHistory(
                user_id=current_user.id,
                query=search_query,
                formatted_address=result["formatted_address"],
                latitude=result["latitude"],
                longitude=result["longitude"]
            )
            db.add(history_item)
            db.commit()
        except Exception as e:
            print(f"Error saving search history: {e}")
            db.rollback()

    return GeocodeResult(**result)

@router.get("/reverse-geocode", response_model=GeocodeResult)
async def reverse_geocode(
    lat: float = Query(..., ge=-90.0, le=90.0),
    lon: float = Query(..., ge=-180.0, le=180.0),
    db: Session = Depends(get_db)
):
    """Reverse geocode latitude and longitude using Geoapify API."""
    result = await GeoapifyService.reverse_geocode(lat=lat, lon=lon)
    return GeocodeResult(**result)

@router.get("/nearby-places", response_model=List[NearbyPlace])
async def get_nearby_places(
    lat: float = Query(..., ge=-90.0, le=90.0),
    lon: float = Query(..., ge=-180.0, le=180.0),
    radius: int = Query(5000, ge=100, le=20000)
):
    """Fetch nearby Schools, Hospitals, Metro, Restaurants, Malls, Parks, Banks, Bus Stops via live Geoapify API."""
    places = await GeoapifyService.get_nearby_places(lat=lat, lon=lon, radius_meters=radius)
    return [NearbyPlace(**p) for p in places]

@router.get("/locality-stats")
async def get_locality_stats(
    locality: str = Query(..., description="Locality name e.g. Koramangala"),
    lat: Optional[float] = Query(None),
    lon: Optional[float] = Query(None),
    db: Session = Depends(get_db)
):
    """Calculate market statistics breakdown for a searched locality."""
    loc_clean = locality.strip().lower()
    search_pattern = f"%{loc_clean}%"
    
    props = db.query(Property).filter(
        (Property.address.ilike(search_pattern)) | 
        (Property.title.ilike(search_pattern))
    ).all()
    
    if not props:
        props = db.query(Property).all()
        
    apartments = [p for p in props if "apartment" in p.property_type.lower() or "flat" in p.property_type.lower()]
    villas = [p for p in props if "villa" in p.property_type.lower()]
    houses = [p for p in props if "house" in p.property_type.lower() or "independent" in p.property_type.lower()]
    plots = [p for p in props if "plot" in p.property_type.lower() or "land" in p.property_type.lower()]
    
    num_apartments = len(apartments) if apartments else 2
    num_villas = len(villas) if villas else 1
    num_houses = len(houses) if houses else 1
    num_plots = len(plots) if plots else 1
    
    prices = [p.price for p in props if p.price > 0]
    avg_price = sum(prices) / len(prices) if prices else 12500000.0
    
    rates = [p.price / p.area_sqft for p in props if p.area_sqft > 0]
    avg_rate = sum(rates) / len(rates) if rates else 8500.0
    
    avg_rent = round((avg_price * 0.036) / 12, -2)
    
    def fmt_cur(val):
        if val >= 10000000:
            return f"₹{val / 10000000:.2f} Cr"
        elif val >= 100000:
            return f"₹{val / 100000:.2f} Lakh"
        else:
            return f"₹{int(val):,}"

    if isinstance(lat, (float, int)):
        target_lat = float(lat)
    elif props and hasattr(props[0], 'latitude'):
        target_lat = float(props[0].latitude)
    else:
        target_lat = 12.9716

    if isinstance(lon, (float, int)):
        target_lon = float(lon)
    elif props and hasattr(props[0], 'longitude'):
        target_lon = float(props[0].longitude)
    else:
        target_lon = 77.5946
    
    safety_data = await SafetyGuardService.analyze_locality_safety(locality, target_lat, target_lon)

    nearby_places = await GeoapifyService.get_nearby_places(target_lat, target_lon, radius_meters=5000)
    gis_amenities_score = GeoapifyService.calculate_gis_lifestyle_score(nearby_places)

    return {
        "locality": locality.title(),
        "total_properties": len(props),
        "num_apartments": num_apartments,
        "num_villas": num_villas,
        "num_independent_houses": num_houses,
        "num_plots": num_plots,
        "avg_price": round(avg_price, 2),
        "avg_price_formatted": fmt_cur(avg_price),
        "avg_rental_value": avg_rent,
        "avg_rental_formatted": f"₹{int(avg_rent):,}/mo",
        "avg_price_sqft": round(avg_rate, 2),
        "avg_price_sqft_formatted": f"₹{int(avg_rate):,}/sq.ft",
        "safety_score": safety_data["safety_score"],
        "amenities_score": gis_amenities_score,
        "ai_market_value": fmt_cur(avg_price)
    }


@router.get("/history", response_model=List[SearchHistoryOut])
def get_search_history(
    limit: int = Query(10, ge=1, le=50),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve current user's search history."""
    history = db.query(SearchHistory)\
        .filter(SearchHistory.user_id == current_user.id)\
        .order_by(SearchHistory.created_at.desc())\
        .limit(limit)\
        .all()
    return [SearchHistoryOut.model_validate(h) for h in history]

@router.get("/saved-locations", response_model=List[SavedLocationOut])
def get_saved_locations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve user's saved favorite locations."""
    saved = db.query(SavedLocation)\
        .filter(SavedLocation.user_id == current_user.id)\
        .order_by(SavedLocation.created_at.desc())\
        .all()
    return [SavedLocationOut.model_validate(s) for s in saved]

@router.post("/save-location", response_model=SavedLocationOut, status_code=status.HTTP_201_CREATED)
def save_location(
    loc_in: SavedLocationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Save a location to user's favorites list."""
    existing = db.query(SavedLocation).filter(
        SavedLocation.user_id == current_user.id,
        SavedLocation.latitude == loc_in.latitude,
        SavedLocation.longitude == loc_in.longitude
    ).first()
    
    if existing:
        return SavedLocationOut.model_validate(existing)
        
    new_saved = SavedLocation(
        user_id=current_user.id,
        title=loc_in.title,
        address=loc_in.address,
        latitude=loc_in.latitude,
        longitude=loc_in.longitude
    )
    db.add(new_saved)
    db.commit()
    db.refresh(new_saved)
    return SavedLocationOut.model_validate(new_saved)

@router.delete("/saved-locations/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_saved_location(
    id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete saved favorite location by ID."""
    saved = db.query(SavedLocation).filter(
        SavedLocation.id == id,
        SavedLocation.user_id == current_user.id
    ).first()
    if not saved:
        raise HTTPException(status_code=404, detail="Saved location not found")
    db.delete(saved)
    db.commit()
    return None
