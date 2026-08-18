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
    floor: int = 1
    total_floors: int = 1
    property_age: str = "New"
    facing: str = "East"
    parking: str = "Covered"
    furnishing: str = "Semi-Furnished"
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
    amenities: List[str] = []
    price: float
    description: Optional[str] = None
    address: str
    locality: str
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
    image_source: str
    order: int
    uploaded_at: datetime

    class Config:
        from_attributes = True


class PropertyOut(PropertyBase):
    id: int
    user_id: int
    price_per_sqft: Optional[float] = None
    price_formatted: Optional[str] = None
    nearby_places: List[Dict[str, Any]] = []
    uploaded_images: List[PropertyImageOut] = []
    created_at: datetime

    class Config:
        from_attributes = True

class PropertyListOut(BaseModel):
    items: List[PropertyOut]
    total: int

