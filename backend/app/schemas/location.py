from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List, Dict, Any

class GeocodeResult(BaseModel):
    query: str
    formatted_address: str
    latitude: float
    longitude: float
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    postcode: Optional[str] = None
    place_id: Optional[str] = None
    estimated_price_sqft: Optional[float] = None
    price_range: Optional[str] = None

class NearbyPlace(BaseModel):
    name: str
    category: str
    distance_meters: float
    latitude: float
    longitude: float
    address: Optional[str] = None

class SearchHistoryOut(BaseModel):
    id: int
    query: str
    formatted_address: str
    latitude: float
    longitude: float
    created_at: datetime

    class Config:
        from_attributes = True

class SavedLocationCreate(BaseModel):
    title: str
    address: str
    latitude: float
    longitude: float

class SavedLocationOut(BaseModel):
    id: int
    title: str
    address: str
    latitude: float
    longitude: float
    created_at: datetime

    class Config:
        from_attributes = True

class LocationQuery(BaseModel):
    text: str
