from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.core.database import Base

class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    plan_name = Column(String(50), default="PRO_299", nullable=False)
    status = Column(String(50), default="FREE", nullable=False)  # 'FREE', 'ACTIVE', 'EXPIRED', 'CANCELLED'
    start_date = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    end_date = Column(DateTime, nullable=True)
    payment_reference = Column(String(255), nullable=True)

    user = relationship("User", back_populates="subscriptions")
