from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.core.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    full_name = Column(String(255), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    role = Column(String(50), default="USER", nullable=False)  # 'USER', 'OWNER', 'ADMIN'
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    search_histories = relationship("SearchHistory", back_populates="user", cascade="all, delete-orphan")
    saved_locations = relationship("SavedLocation", back_populates="user", cascade="all, delete-orphan")
    properties = relationship("Property", back_populates="user", cascade="all, delete-orphan")
    subscriptions = relationship("Subscription", back_populates="user", cascade="all, delete-orphan")

    @property
    def subscription_status(self) -> str:
        if not self.subscriptions:
            return "FREE"
        for sub in self.subscriptions:
            if sub.status == "ACTIVE":
                if not sub.end_date or sub.end_date.replace(tzinfo=timezone.utc) > datetime.now(timezone.utc):
                    return "ACTIVE"
        return "FREE"


