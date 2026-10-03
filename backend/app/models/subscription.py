from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.core.database import Base

class Subscription(Base):
    """
    User Subscription Model for PropPulse Pro.
    Tracks live payment identifiers and subscription validity.
    """
    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Core Plan & Status
    plan = Column(String(50), default="FREE", nullable=False)  # 'FREE', 'PRO'
    plan_name = Column(String(50), default="PROPULSE_PRO_299", nullable=False)  # Backward compatibility
    subscription_status = Column(String(50), default="FREE", nullable=False)  # 'FREE', 'ACTIVE', 'PENDING', 'EXPIRED', 'CANCELLED'
    status = Column(String(50), default="FREE", nullable=False)  # Backward compatibility
    
    # Razorpay Payment Gateway Identifiers (no secrets stored)
    razorpay_customer_id = Column(String(255), nullable=True)
    razorpay_subscription_id = Column(String(255), nullable=True)
    razorpay_order_id = Column(String(255), nullable=True, index=True)
    razorpay_payment_id = Column(String(255), nullable=True, index=True)
    
    # Financial details
    plan_amount = Column(Float, default=299.0, nullable=False)
    currency = Column(String(10), default="INR", nullable=False)
    
    # Timestamps
    start_date = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    end_date = Column(DateTime, nullable=True)
    payment_reference = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    user = relationship("User", back_populates="subscriptions")
