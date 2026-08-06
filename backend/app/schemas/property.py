from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List, Dict, Any

class PropertyBase(BaseModel):
    title: str
    property_type: str
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
    price: float
    description: Optional[str] = None
    address: str
    latitude: float
    longitude: float
    owner_name: Optional[str] = "PropPulse Verified Owner"
    owner_phone: Optional[str] = "+91 98860 12345"
    images: List[str] = []

class PropertyOut(PropertyBase):
    id: int
    user_id: int
    price_per_sqft: Optional[float] = None
    price_formatted: Optional[str] = None
    nearby_places: List[Dict[str, Any]] = []
    created_at: datetime

    class Config:
        from_attributes = True

class PropertyListOut(BaseModel):
    items: List[PropertyOut]
    total: int
