from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List, Dict, Any

class PropertyBase(BaseModel):
    title: str
    property_type: str
    listing_type: str = "Buy"
    bhk: int
    area_sqft: float
    bathrooms: int = 1
    balconies: int = 0
    floor: Optional[int] = None
    total_floors: Optional[int] = None
    property_age: Optional[str] = "New"
    facing: Optional[str] = "East"
    parking: Optional[str] = None
    furnishing: Optional[str] = None
    amenities: List[str] = []
    price: float
    description: Optional[str] = None
    address: str
    locality: str = ""
    latitude: float
    longitude: float
    owner_name: Optional[str] = "PropPulse Verified Owner"
    owner_phone: Optional[str] = "+91 98860 12345"
    images: List[str] = []
    street_view_available: bool = False
    seller_type: str = "Owner"
    seller_name: str = "PropPulse Verified Seller"
    phone: str = "+91 98860 12345"
    verification_status: str = "Verified"
    source_type: str = "demo_dataset"
    source: Optional[str] = "PropPulse Direct"
    source_url: Optional[str] = ""
    image_source: Optional[str] = ""
    verified: Optional[bool] = True


class PropertyCreate(BaseModel):
    title: str
    property_type: str
    listing_type: str = "Buy"
    bhk: int
    area_sqft: float
    bathrooms: int = 1
    balconies: int = 0
    floor: int = 1
    total_floors: int = 1
    property_age: str = "New"
    facing: str = "East"
    parking: str = "Covered"
    furnishing: str = "Semi-Furnished"
    availability: Optional[str] = "Ready to Move"
    amenities: List[str] = []
    price: float
    description: Optional[str] = None
    address: str
    locality: str
    sub_locality: Optional[str] = None
    latitude: Optional[float] = 12.9716
    longitude: Optional[float] = 77.5946
    images: List[str] = []
    owner_name: Optional[str] = ""
    owner_phone: Optional[str] = ""
    seller_type: Optional[str] = "Owner"
    seller_name: Optional[str] = ""
    phone: Optional[str] = ""



class PropertyImageOut(BaseModel):
    id: int
    property_id: int
    image_path: str
    source_type: str = "owner_upload"
    source_name: str = "Owner Uploaded"
    source_url: str = ""
    is_primary: bool = False
    order: int = 0
    uploaded_by: Optional[int] = None
    uploaded_at: datetime

    class Config:
        from_attributes = True


class CanonicalLocation(BaseModel):
    property_id: int
    building_name: Optional[str] = None
    project_name: Optional[str] = None
    society_name: Optional[str] = None
    street: Optional[str] = None
    road: Optional[str] = None
    sub_locality: Optional[str] = None
    locality: str
    city: str = "Bengaluru"
    state: str = "Karnataka"
    pincode: Optional[str] = None
    latitude: float
    longitude: float
    coordinate_confidence: str  # EXACT or APPROXIMATE
    formatted_address: str
    location_source: str


class PropertyOut(PropertyBase):
    id: int
    user_id: int
    source_listing_id: Optional[str] = None
    city: Optional[str] = "Bengaluru"
    sub_locality: Optional[str] = None
    zone: Optional[str] = None
    society: Optional[str] = None
    building_name: Optional[str] = None
    project_name: Optional[str] = None
    display_title: Optional[str] = None
    canonical_location: Optional[CanonicalLocation] = None
    area_type: Optional[str] = None
    price_inr: Optional[float] = None
    transaction_type: Optional[str] = "sale"
    price_per_sqft: Optional[float] = None
    price_formatted: Optional[str] = None
    coordinate_quality: Optional[str] = None
    coordinate_status: Optional[str] = None
    property_type_source: Optional[str] = None
    source_name: Optional[str] = None
    listing_status: Optional[str] = None
    availability_date: Optional[str] = None
    image_provenance: Optional[str] = None
    image_provenance_badge: Optional[str] = None
    image_disclosure_note: Optional[str] = None
    has_genuine_image: Optional[bool] = None
    contact_available: Optional[bool] = None
    contact_source: Optional[str] = None
    anomaly_flags: List[str] = []
    nearby_places: List[Dict[str, Any]] = []
    uploaded_images: List[PropertyImageOut] = []
    created_at: datetime
    last_verified_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class PropertyListOut(BaseModel):
    items: List[PropertyOut]
    total: int
    page: Optional[int] = None
    page_size: Optional[int] = None



