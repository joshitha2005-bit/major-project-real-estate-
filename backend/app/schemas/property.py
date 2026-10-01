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
    owner_phone: Optional[str] = None
    images: List[str] = []
    street_view_available: bool = False
    seller_type: str = "Owner"
    seller_name: str = "PropPulse Verified Seller"
    phone: Optional[str] = None
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
    uploaded_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class CanonicalLocation(BaseModel):
    property_id: int
    property_name: Optional[str] = None
    building_name: Optional[str] = None
    project_name: Optional[str] = None
    society_name: Optional[str] = None
    builder_name: Optional[str] = None
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
    identity_confidence: Optional[str] = None  # IDENTITY_RESOLVED, IDENTITY_PARTIAL, IDENTITY_UNRESOLVED
    identity_source: Optional[str] = None
    location_source: str


class PropertyOut(PropertyBase):
    id: int
    user_id: int
    source_listing_id: Optional[str] = None
    city: Optional[str] = "Bengaluru"
    sub_locality: Optional[str] = None
    zone: Optional[str] = None
    society: Optional[str] = None
    property_name: Optional[str] = None
    building_name: Optional[str] = None
    project_name: Optional[str] = None
    society_name: Optional[str] = None
    builder_name: Optional[str] = None
    street: Optional[str] = None
    road: Optional[str] = None
    state: Optional[str] = "Karnataka"
    pincode: Optional[str] = None
    coordinate_confidence: Optional[str] = None
    formatted_address: Optional[str] = None
    identity_confidence: Optional[str] = None
    identity_source: Optional[str] = None
    location_source: Optional[str] = None
    display_title: Optional[str] = None
    canonical_location: Optional[CanonicalLocation] = None
    area_type: Optional[str] = None
    price_inr: Optional[float] = None
    transaction_type: Optional[str] = "sale"
    price_per_sqft: Optional[float] = None
    price_formatted: Optional[str] = None
    dataset_category: Optional[str] = "REFERENCE_HISTORICAL"
    is_main_ai_ready: Optional[bool] = False
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
    # Objective 20B fields
    image_status: Optional[str] = "NO_IMAGE"
    image_source_url: Optional[str] = None
    image_authorization_status: Optional[str] = "NO_IMAGE"
    cnn_analysis_status: Optional[str] = "UNAVAILABLE"
    cnn_embedding_dimensions: Optional[int] = None
    contact_type: Optional[str] = "Owner"
    contact_number: Optional[str] = None
    contact_source_url: Optional[str] = None
    contact_verified_at: Optional[datetime] = None
    contact_display_permission: Optional[bool] = False
    source_platform: Optional[str] = None
    source_listing_url: Optional[str] = None
    anomaly_flags: List[str] = []
    nearby_places: List[Dict[str, Any]] = []
    uploaded_images: List[PropertyImageOut] = []
    gallery: Optional[Dict[str, Any]] = None
    location_provenance: Optional[Dict[str, Any]] = None
    contact_provenance: Optional[Dict[str, Any]] = None
    created_at: datetime
    last_verified_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class PropertyListOut(BaseModel):
    items: List[PropertyOut]
    total: int
    page: Optional[int] = None
    page_size: Optional[int] = None



