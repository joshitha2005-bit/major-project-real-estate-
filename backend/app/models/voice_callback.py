from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.core.database import Base


class VoiceCallbackRequest(Base):
    __tablename__ = "voice_callback_requests"

    id = Column(Integer, primary_key=True, index=True)
    property_id = Column(Integer, ForeignKey("properties.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    phone_number = Column(String(50), nullable=False)
    session_id = Column(String(100), unique=True, index=True, nullable=False)
    call_sid = Column(String(100), nullable=True, index=True)
    status = Column(String(50), default="calling")  # calling, connected, completed, failed
    inquiry_text = Column(Text, nullable=True)
    error_message = Column(Text, nullable=True)
    consent = Column(Boolean, default=True)
    consent_timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    call_started_at = Column(DateTime, nullable=True)
    call_completed_at = Column(DateTime, nullable=True)
    duration_seconds = Column(Integer, default=0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    property = relationship("Property")
    user = relationship("User")


class PropertyInquiry(Base):
    __tablename__ = "property_inquiries"

    id = Column(Integer, primary_key=True, index=True)
    property_id = Column(Integer, ForeignKey("properties.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    phone_number = Column(String(50), nullable=False)
    session_id = Column(String(100), nullable=True)
    question_or_request = Column(Text, nullable=False)
    status = Column(String(50), default="PENDING")  # PENDING, CONTACTED, RESOLVED
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    property = relationship("Property")
    user = relationship("User")
