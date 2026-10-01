from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime, timezone
from app.core.database import Base

class MarketReference(Base):
    __tablename__ = "market_references"

    id = Column(Integer, primary_key=True, index=True)
    provider_name = Column(String(255), nullable=False)
    source_listing_id = Column(String(100), nullable=True, index=True)
    locality = Column(String(255), nullable=False, index=True)
    property_type = Column(String(100), nullable=False)
    bhk = Column(Integer, nullable=False)
    area_sqft = Column(Float, nullable=False)
    price_inr = Column(Float, nullable=False)
    price_per_sqft = Column(Float, nullable=False)
    listing_url = Column(String(500), nullable=True)
    observed_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    reference_status = Column(String(50), default="REFERENCE")
