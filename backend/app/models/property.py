from sqlalchemy import Column, Integer, String, Float, Text, JSON, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.core.database import Base

class Property(Base):
    __tablename__ = "properties"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    title = Column(String(255), nullable=False)
    property_type = Column(String(100), nullable=False)  # Apartment, Villa, Independent House, Plot, Penthouse
    bhk = Column(Integer, nullable=False)
    area_sqft = Column(Float, nullable=False)
    bathrooms = Column(Integer, default=1)
    balconies = Column(Integer, default=0)
    floor = Column(Integer, default=1)
    total_floors = Column(Integer, default=1)
    
    property_age = Column(String(50), default="New")  # New, 1-5 yrs, 5-10 yrs, 10+ yrs
    facing = Column(String(50), default="East")  # North, South, East, West, North-East, etc.
    parking = Column(String(50), default="Covered")  # Covered, Open, None
    furnishing = Column(String(50), default="Semi-Furnished")  # Fully Furnished, Semi-Furnished, Unfurnished
    
    price = Column(Float, nullable=False)  # Total expected price in INR
    description = Column(Text, nullable=True)
    
    address = Column(String(500), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    
    owner_name = Column(String(255), default="PropPulse Verified Owner")
    owner_phone = Column(String(50), default="+91 98860 12345")
    
    images = Column(JSON, default=list)  # List of image URLs
    nearby_places = Column(JSON, default=list)  # Geoapify fetched nearby places JSON
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="properties")
