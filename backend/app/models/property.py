from sqlalchemy import Column, Integer, String, Float, Text, JSON, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.core.database import Base

class Property(Base):
    __tablename__ = "properties"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    title = Column(String(255), nullable=False)
    property_type = Column(String(100), nullable=False)  # Apartment, Villa, Independent House, Plot, Penthouse
    listing_type = Column(String(100), default="Buy")  # Buy or Rent
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
    amenities = Column(JSON, default=list)  # List of string amenities e.g. ["Gym", "Pool", "Lift"]
    
    price = Column(Float, nullable=False)  # Total expected price in INR
    description = Column(Text, nullable=True)
    
    address = Column(String(500), nullable=False)
    locality = Column(String(255), default="")  # Clean geocoded locality
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    
    owner_name = Column(String(255), default="PropPulse Verified Owner")
    owner_phone = Column(String(50), default="+91 98860 12345")
    
    images = Column(JSON, default=list)  # List of image URLs
    nearby_places = Column(JSON, default=list)  # Geoapify fetched nearby places JSON
    street_view_available = Column(Boolean, default=False)
    
    seller_type = Column(String(100), default="Owner")  # Owner, Broker, Builder
    seller_name = Column(String(255), default="PropPulse Verified Seller")
    phone = Column(String(100), default="+91 98860 12345")
    verification_status = Column(String(100), default="Verified")  # Verified, Pending
    source_type = Column(String(100), default="demo_dataset")  # demo_dataset, owner_listing, etc.
    
    source = Column(String(255), default="PropPulse Direct")
    source_url = Column(String(500), default="")
    image_source = Column(String(500), default="")
    verified = Column(Boolean, default=True)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="properties")
    property_images = relationship("PropertyImage", back_populates="property", cascade="all, delete-orphan", order_by="PropertyImage.order")


class PropertyImage(Base):
    __tablename__ = "property_images"

    id = Column(Integer, primary_key=True, index=True)
    property_id = Column(Integer, ForeignKey("properties.id", ondelete="CASCADE"), nullable=False)
    image_path = Column(String(500), nullable=False)
    image_source = Column(String(255), default="user_upload")
    order = Column(Integer, default=0)
    uploaded_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    property = relationship("Property", back_populates="property_images")


