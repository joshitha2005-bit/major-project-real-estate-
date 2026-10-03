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

    source_listing_id = Column(String(100), nullable=True)
    city = Column(String(100), default="Bengaluru")
    sub_locality = Column(String(255), nullable=True)
    zone = Column(String(100), nullable=True)
    society = Column(String(255), nullable=True)
    area_type = Column(String(100), nullable=True)
    price_inr = Column(Float, nullable=True)
    transaction_type = Column(String(50), default="sale")
    price_per_sqft = Column(Float, nullable=True)
    availability = Column(String(100), nullable=True)
    coordinate_quality = Column(String(50), default="LOCALITY_APPROXIMATE")
    last_verified_at = Column(DateTime, nullable=True)

    # Phase B Source & Provenance Architecture fields
    source_name = Column(String(255), default="Bengaluru_House_Data.csv")
    listing_status = Column(String(50), default="HISTORICAL")  # CURRENT, HISTORICAL, REFERENCE, DEMO, SOLD_INACTIVE, UNKNOWN
    availability_date = Column(String(100), nullable=True)
    listed_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    image_provenance = Column(String(100), default="NO_IMAGE") # OWNER_UPLOADED, AUTHORIZED_PROVIDER, LICENSED_EXTERNAL, NO_IMAGE, DEMO_ONLY
    image_count = Column(Integer, default=0)
    owner_or_agent_type = Column(String(50), default="Owner")
    contact_available = Column(Boolean, default=False)
    contact_source = Column(String(255), default="Historical Dataset - No Contact")
    data_timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    anomaly_flags = Column(JSON, default=list)

    # Master AI Ready Dataset Separation
    dataset_category = Column(String(50), default="REFERENCE_HISTORICAL", index=True) # MAIN_AI_READY, REFERENCE_HISTORICAL, INVALID_QUARANTINE
    is_main_ai_ready = Column(Boolean, default=False, index=True)

    # Canonical Property Identity & Location Resolution fields
    property_name = Column(String(255), nullable=True)
    building_name = Column(String(255), nullable=True)
    project_name = Column(String(255), nullable=True)
    society_name = Column(String(255), nullable=True)
    builder_name = Column(String(255), nullable=True)
    street = Column(String(255), nullable=True)
    road = Column(String(255), nullable=True)
    state = Column(String(100), default="Karnataka")
    pincode = Column(String(20), nullable=True)
    coordinate_confidence = Column(String(50), default="APPROXIMATE")
    formatted_address = Column(String(500), nullable=True)
    identity_confidence = Column(String(50), default="IDENTITY_UNRESOLVED")
    identity_source = Column(String(255), nullable=True)
    location_source = Column(String(255), nullable=True)

    # Objective 20B: Real Image Intelligence & Verified Contact fields
    image_status = Column(String(100), default="NO_IMAGE") # ANALYSIS_COMPLETE, SOURCE_REFERENCE_ONLY, LOCATION_REFERENCE, NO_IMAGE, INVALID_IMAGE
    image_source_url = Column(String(500), nullable=True)
    image_authorization_status = Column(String(100), default="NO_IMAGE") # AUTHORIZED_PROPERTY_IMAGE, SOURCE_LISTING_IMAGE, LOCATION_BUILDING_REFERENCE, INVALID_IMAGE, NO_IMAGE
    cnn_analysis_status = Column(String(100), default="UNAVAILABLE") # ACTIVE, READY_NO_PERMISSION, UNAVAILABLE
    cnn_embedding_dimensions = Column(Integer, nullable=True) # 512 for ResNet-18

    contact_type = Column(String(100), default="Owner") # Owner, Agent, Builder, Source Platform
    contact_number = Column(String(100), nullable=True)
    contact_source_url = Column(String(500), nullable=True)
    contact_verified_at = Column(DateTime, nullable=True)
    contact_display_permission = Column(Boolean, default=False)
    source_platform = Column(String(100), nullable=True)
    source_listing_url = Column(String(500), nullable=True)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    visibility_status = Column(String(50), default="PUBLIC", index=True)  # PUBLIC or PRIVATE
    user = relationship("User", back_populates="properties")
    private_owner_contact = relationship("PrivateOwnerContact", back_populates="property", uselist=False, cascade="all, delete-orphan")
    property_images = relationship("PropertyImage", back_populates="property", cascade="all, delete-orphan", order_by="PropertyImage.order")

PropertyListing = Property

class PropertyImage(Base):
    __tablename__ = "property_images"

    id = Column(Integer, primary_key=True, index=True)
    property_id = Column(Integer, ForeignKey("properties.id", ondelete="CASCADE"), nullable=False)
    image_path = Column(String(500), nullable=False)
    source_type = Column(String(50), default="owner_upload")  # owner_upload or licensed_external
    source_name = Column(String(255), default="Owner Uploaded")
    source_url = Column(String(500), default="")
    is_primary = Column(Boolean, default=False)
    order = Column(Integer, default=0)
    uploaded_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    uploaded_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Phase B Image Hash & Validation fields
    image_hash = Column(String(255), nullable=True)
    width = Column(Integer, nullable=True)
    height = Column(Integer, nullable=True)
    image_provenance = Column(String(100), default="OWNER_UPLOADED")
    verification_status = Column(String(50), default="Verified")
    image_quality_score = Column(Float, nullable=True)
    image_validation_status = Column(String(50), default="Valid")

    property = relationship("Property", back_populates="property_images")
    uploader = relationship("User")




