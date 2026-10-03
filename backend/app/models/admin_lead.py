from sqlalchemy import Column, Integer, String, Float, Text, JSON, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.core.database import Base


class PrivateOwnerContact(Base):
    __tablename__ = "private_owner_contacts"

    id = Column(Integer, primary_key=True, index=True)
    property_id = Column(Integer, ForeignKey("properties.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    contact_name = Column(String(150), default="Property Owner / Agent", nullable=False)
    contact_type = Column(String(50), default="OWNER", nullable=False)  # OWNER, AGENT, BUILDER, BROKER
    phone = Column(String(50), nullable=True)
    email = Column(String(150), nullable=True)
    source = Column(String(150), default="Direct Listing Verification")
    verification_status = Column(String(50), default="UNVERIFIED", nullable=False)  # VERIFIED, UNVERIFIED
    permission_status = Column(String(50), default="PENDING", nullable=False)  # GRANTED, PENDING, REVOKED
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    property = relationship("Property", back_populates="private_owner_contact")


class AILead(Base):
    __tablename__ = "ai_leads"

    id = Column(Integer, primary_key=True, index=True)
    lead_code = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(150), nullable=False)
    phone = Column(String(50), nullable=False, index=True)
    property_id = Column(Integer, ForeignKey("properties.id", ondelete="SET NULL"), nullable=True, index=True)
    property_name = Column(String(255), nullable=False)
    buy_or_rent = Column(String(50), default="BUY", nullable=False)  # BUY, RENT
    property_type = Column(String(100), default="Apartment")
    bhk = Column(String(50), default="3 BHK")
    budget = Column(String(100), default="₹80–90 Lakh")
    loan_required = Column(String(50), default="YES")  # YES, NO, UNDECIDED
    purchase_timeline = Column(String(100), default="Within 1-3 months")
    location_preference = Column(String(150), default="Bengaluru")
    additional_requirements = Column(Text, nullable=True)
    owner_callback_requested = Column(Boolean, default=True)
    site_visit_requested = Column(Boolean, default=False)
    site_visit_date = Column(String(50), nullable=True)
    site_visit_time = Column(String(50), nullable=True)
    call_summary = Column(Text, nullable=True)
    call_duration_seconds = Column(Integer, default=0)
    call_session_id = Column(String(100), nullable=True, index=True)
    call_sid = Column(String(100), nullable=True, index=True)
    call_status = Column(String(50), default="REQUESTED")  # REQUESTED, CALLING, RINGING, CONNECTED, COMPLETED, FAILED, TELEPHONY_NOT_CONFIGURED
    call_started_at = Column(DateTime, nullable=True)
    call_completed_at = Column(DateTime, nullable=True)
    transcript = Column(Text, nullable=True)
    lead_status = Column(String(50), default="NEW", nullable=False, index=True)  # NEW, CONTACTED, INTERESTED, SITE_VISIT_REQUESTED, SITE_VISIT_CONFIRMED, FOLLOW_UP, CLOSED, INVALID, SPAM
    validation_status = Column(String(50), default="VALID", nullable=False)  # VALID, NEEDS_REVIEW, INVALID, SPAM
    is_duplicate = Column(Boolean, default=False)
    duplicate_of_id = Column(Integer, ForeignKey("ai_leads.id", ondelete="SET NULL"), nullable=True)
    owner_sent_status = Column(String(50), default="NOT_SENT")  # NOT_SENT, SENT, FAILED, NOT_CONFIGURED
    owner_sent_at = Column(DateTime, nullable=True)
    admin_notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    property = relationship("Property")
    site_visits = relationship("SiteVisit", back_populates="lead", cascade="all, delete-orphan")


class SiteVisit(Base):
    __tablename__ = "site_visits"

    id = Column(Integer, primary_key=True, index=True)
    appointment_code = Column(String(50), unique=True, index=True, nullable=False)
    lead_id = Column(Integer, ForeignKey("ai_leads.id", ondelete="CASCADE"), nullable=False, index=True)
    property_id = Column(Integer, ForeignKey("properties.id", ondelete="CASCADE"), nullable=False, index=True)
    user_name = Column(String(150), nullable=False)
    user_phone = Column(String(50), nullable=False)
    visit_date = Column(String(50), nullable=False)
    visit_time = Column(String(50), nullable=False)
    status = Column(String(50), default="REQUESTED", nullable=False, index=True)  # REQUESTED, CONFIRMED, RESCHEDULED, CANCELLED, COMPLETED
    admin_notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    lead = relationship("AILead", back_populates="site_visits")
    property = relationship("Property")


class AdminAuditLog(Base):
    __tablename__ = "admin_audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    admin_id = Column(Integer, nullable=False)
    admin_email = Column(String(150), nullable=False)
    action = Column(String(100), nullable=False)
    entity_type = Column(String(50), nullable=False)  # PROPERTY, LEAD, SITE_VISIT
    entity_id = Column(Integer, nullable=False)
    details = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
