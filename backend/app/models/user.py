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
        """
        Calculates effective subscription status for the user.
        Admins automatically have ACTIVE access.
        For normal users, checks for active PRO subscription within valid date range.
        """
        if self.role == "ADMIN":
            return "ACTIVE"
        if not self.subscriptions:
            return "FREE"
        
        now = datetime.now(timezone.utc)
        for sub in self.subscriptions:
            st = (getattr(sub, "subscription_status", None) or getattr(sub, "status", None) or "").upper()
            plan = (getattr(sub, "plan", None) or getattr(sub, "plan_name", None) or "").upper()
            if st == "ACTIVE" and ("PRO" in plan or plan == "PROPULSE_PRO_299"):
                if not sub.end_date:
                    return "ACTIVE"
                end_dt = sub.end_date if sub.end_date.tzinfo else sub.end_date.replace(tzinfo=timezone.utc)
                if end_dt > now:
                    return "ACTIVE"
        return "FREE"

    @property
    def current_plan(self) -> str:
        return "PRO" if self.subscription_status == "ACTIVE" else "FREE"

    def is_pro_active(self) -> bool:
        return self.subscription_status == "ACTIVE"
