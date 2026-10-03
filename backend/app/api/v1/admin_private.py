import uuid
import re
import math
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query, status, Response, Body
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, desc, asc

from app.core.config import settings
from app.core.database import get_db
from app.core.security import verify_password, create_access_token, get_password_hash
from app.api.deps import get_current_user, get_current_user_with_role
from app.models.user import User
from app.models.subscription import Subscription
from app.models.property import Property, PropertyImage
from app.models.admin_lead import AILead, PrivateOwnerContact, SiteVisit, AdminAuditLog
from app.models.voice_callback import VoiceCallbackRequest
from app.services.lead_management_service import LeadManagementService

router = APIRouter()


# -------------------------------------------------------------
# PYDANTIC SCHEMAS
# -------------------------------------------------------------
class AdminLoginPayload(BaseModel):
    identifier: str = Field(..., description="Email or phone number")
    password: str = Field(..., description="Admin secret password")


class VisibilityPayload(BaseModel):
    visibility_status: str = Field(..., description="PUBLIC or PRIVATE")


class OwnerContactUpdatePayload(BaseModel):
    contact_name: Optional[str] = None
    contact_type: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    source: Optional[str] = None
    verification_status: Optional[str] = None
    permission_status: Optional[str] = None
    notes: Optional[str] = None


class LeadUpdatePayload(BaseModel):
    lead_status: Optional[str] = None
    validation_status: Optional[str] = None
    buy_or_rent: Optional[str] = None
    budget: Optional[str] = None
    bhk: Optional[str] = None
    loan_required: Optional[str] = None
    purchase_timeline: Optional[str] = None
    admin_notes: Optional[str] = None
    site_visit_requested: Optional[bool] = None
    site_visit_date: Optional[str] = None
    site_visit_time: Optional[str] = None


class SiteVisitUpdatePayload(BaseModel):
    status: str = Field(..., description="REQUESTED, CONFIRMED, RESCHEDULED, CANCELLED, COMPLETED")
    visit_date: Optional[str] = None
    visit_time: Optional[str] = None
    admin_notes: Optional[str] = None


class VoiceCallRequestPayload(BaseModel):
    property_id: int
    user_phone: str
    consent: bool = True
    inquiry_text: Optional[str] = None


# -------------------------------------------------------------
# 1. ADMIN AUTHENTICATION
# -------------------------------------------------------------
@router.post("/login")
def admin_login(payload: AdminLoginPayload, db: Session = Depends(get_db)):
    """
    Authenticate administrator using Email/Phone + password.
    Returns secure JWT session token with role ADMIN.
    """
    identifier = payload.identifier.strip()
    
    # Query user by email or by phone/name matching admin role
    admin_user = db.query(User).filter(
        or_(
            User.email == identifier,
            User.email == settings.PRIVATE_ADMIN_EMAIL
        )
    ).first()

    if not admin_user or admin_user.role != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid administrative credentials or unauthorized role."
        )

    # Verify password against hashed password
    if not verify_password(payload.password, admin_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid administrative credentials."
        )

    # Issue authenticated session token
    access_token = create_access_token(subject=admin_user.id)

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": admin_user.id,
            "email": admin_user.email,
            "full_name": admin_user.full_name,
            "role": admin_user.role
        }
    }


# -------------------------------------------------------------
# 2. DASHBOARD KPI SUMMARY CARDS
# -------------------------------------------------------------
@router.get("/stats")
@router.get("/private/stats")
def get_private_dashboard_stats(
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_user_with_role("ADMIN"))
):
    """
    Returns 10 summary KPI counts directly from live database tables.
    Zero static or fake numbers.
    """
    total_properties = db.query(Property).count()
    private_properties = db.query(Property).filter(Property.visibility_status == "PRIVATE").count()
    public_properties = total_properties - private_properties

    total_leads = db.query(AILead).count()
    new_requests = db.query(AILead).filter(AILead.lead_status == "NEW").count()
    owner_callbacks = db.query(AILead).filter(AILead.owner_callback_requested == True).count()
    site_visit_requests = db.query(SiteVisit).count()
    
    pending_review = db.query(AILead).filter(
        AILead.validation_status.in_(["VALID", "NEEDS_REVIEW"]),
        AILead.lead_status.in_(["NEW", "INTERESTED", "SITE_VISIT_REQUESTED"])
    ).count()

    contacted = db.query(AILead).filter(AILead.lead_status == "CONTACTED").count()
    closed = db.query(AILead).filter(AILead.lead_status == "CLOSED").count()
    spam_leads = db.query(AILead).filter(
        or_(AILead.lead_status == "SPAM", AILead.validation_status == "SPAM")
    ).count()

    total_calls = db.query(VoiceCallbackRequest).count()
    completed_calls = db.query(VoiceCallbackRequest).filter(VoiceCallbackRequest.status == "completed").count()
    failed_calls = db.query(VoiceCallbackRequest).filter(VoiceCallbackRequest.status.in_(["failed", "telephony_not_configured"])).count()
    new_leads = db.query(AILead).filter(AILead.lead_status == "NEW").count()
    leads_needing_review = db.query(AILead).filter(AILead.validation_status == "NEEDS_REVIEW").count()
    
    total_subscriptions = db.query(Subscription).count()
    active_subscriptions = db.query(Subscription).filter(Subscription.subscription_status == "ACTIVE").count()
    pro_users = active_subscriptions

    return {
        "total_properties": total_properties,
        "public_properties": public_properties,
        "private_properties": private_properties,
        "total_leads": total_leads,
        "new_requests": new_requests,
        "owner_callbacks": owner_callbacks,
        "site_visit_requests": site_visit_requests,
        "pending_review": pending_review,
        "contacted": contacted,
        "closed": closed,
        "spam_leads": spam_leads,
        "total_calls": total_calls,
        "completed_calls": completed_calls,
        "failed_calls": failed_calls,
        "new_leads": new_leads,
        "leads_needing_review": leads_needing_review,
        "total_subscriptions": total_subscriptions,
        "active_subscriptions": active_subscriptions,
        "pro_users": pro_users
    }


# -------------------------------------------------------------
# 3. PROPERTY MANAGEMENT (PUBLIC / PRIVATE VISIBILITY)
# -------------------------------------------------------------
@router.get("/properties")
def list_admin_properties(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    visibility: Optional[str] = Query(None, description="PUBLIC, PRIVATE, or ALL"),
    property_type: Optional[str] = None,
    bhk: Optional[int] = None,
    sort_by: str = "id",
    sort_order: str = "desc",
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_user_with_role("ADMIN"))
):
    """
    Search, filter, sort, and paginate all properties for private admin management.
    Includes private owner/agent contact details.
    """
    query = db.query(Property)

    # Filter by visibility
    if visibility and visibility.upper() == "PRIVATE":
        query = query.filter(Property.visibility_status == "PRIVATE")
    elif visibility and visibility.upper() == "PUBLIC":
        query = query.filter(or_(Property.visibility_status == "PUBLIC", Property.visibility_status.is_(None)))

    # Filter by type & BHK
    if property_type:
        query = query.filter(Property.property_type.ilike(f"%{property_type}%"))
    if bhk:
        query = query.filter(Property.bhk == bhk)

    # Search
    if search and search.strip():
        term = f"%{search.strip()}%"
        query = query.filter(
            or_(
                Property.title.ilike(term),
                Property.locality.ilike(term),
                Property.property_name.ilike(term),
                Property.address.ilike(term)
            )
        )

    total = query.count()

    # Sort
    sort_col = getattr(Property, sort_by, Property.id)
    if sort_order.lower() == "asc":
        query = query.order_by(asc(sort_col))
    else:
        query = query.order_by(desc(sort_col))

    offset = (page - 1) * limit
    props = query.offset(offset).limit(limit).all()

    items = []
    for p in props:
        # Load private contact if exists
        contact = db.query(PrivateOwnerContact).filter(PrivateOwnerContact.property_id == p.id).first()
        items.append({
            "id": p.id,
            "title": p.title,
            "property_name": p.property_name or p.title,
            "locality": p.locality,
            "address": p.address,
            "bhk": p.bhk,
            "property_type": p.property_type,
            "price": p.price,
            "area_sqft": p.area_sqft,
            "visibility_status": p.visibility_status or "PUBLIC",
            "image_count": len(p.images) if p.images else p.image_count,
            "created_at": p.created_at,
            "updated_at": p.updated_at,
            "private_contact": {
                "id": contact.id if contact else None,
                "contact_name": contact.contact_name if contact else "Unassigned",
                "contact_type": contact.contact_type if contact else "OWNER",
                "phone": contact.phone if contact else None,
                "email": contact.email if contact else None,
                "source": contact.source if contact else "Unverified",
                "verification_status": contact.verification_status if contact else "UNVERIFIED",
                "permission_status": contact.permission_status if contact else "PENDING"
            } if contact else None
        })

    return {
        "items": items,
        "total": total,
        "page": page,
        "limit": limit,
        "total_pages": math.ceil(total / limit) if total > 0 else 1
    }


@router.get("/properties/{property_id}")
def get_admin_property_details(
    property_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_user_with_role("ADMIN"))
):
    """
    Detailed property view with private contact, associated leads, and site visits.
    """
    p = db.query(Property).filter(Property.id == property_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Property not found.")

    contact = db.query(PrivateOwnerContact).filter(PrivateOwnerContact.property_id == p.id).first()
    leads = db.query(AILead).filter(AILead.property_id == p.id).order_by(desc(AILead.created_at)).all()
    visits = db.query(SiteVisit).filter(SiteVisit.property_id == p.id).order_by(desc(SiteVisit.created_at)).all()
    callbacks = db.query(VoiceCallbackRequest).filter(VoiceCallbackRequest.property_id == p.id).order_by(desc(VoiceCallbackRequest.created_at)).all()

    return {
        "property": {
            "id": p.id,
            "title": p.title,
            "property_name": p.property_name or p.title,
            "locality": p.locality,
            "address": p.address,
            "bhk": p.bhk,
            "area_sqft": p.area_sqft,
            "price": p.price,
            "description": p.description,
            "property_type": p.property_type,
            "listing_type": p.listing_type,
            "visibility_status": p.visibility_status or "PUBLIC",
            "images": p.images or [],
            "nearby_places": p.nearby_places or [],
            "created_at": p.created_at,
            "updated_at": p.updated_at
        },
        "private_contact": {
            "id": contact.id if contact else None,
            "contact_name": contact.contact_name if contact else "Unassigned",
            "contact_type": contact.contact_type if contact else "OWNER",
            "phone": contact.phone if contact else None,
            "email": contact.email if contact else None,
            "source": contact.source if contact else "Direct Verification",
            "verification_status": contact.verification_status if contact else "UNVERIFIED",
            "permission_status": contact.permission_status if contact else "PENDING",
            "notes": contact.notes if contact else None
        } if contact else None,
        "leads": [
            {
                "id": l.id,
                "lead_code": l.lead_code,
                "name": l.name,
                "phone": l.phone,
                "budget": l.budget,
                "bhk": l.bhk,
                "lead_status": l.lead_status,
                "validation_status": l.validation_status,
                "created_at": l.created_at
            } for l in leads
        ],
        "site_visits": [
            {
                "id": v.id,
                "appointment_code": v.appointment_code,
                "user_name": v.user_name,
                "user_phone": v.user_phone,
                "visit_date": v.visit_date,
                "visit_time": v.visit_time,
                "status": v.status
            } for v in visits
        ],
        "callback_requests": [
            {
                "id": c.id,
                "session_id": c.session_id,
                "phone_number": c.phone_number,
                "status": c.status,
                "created_at": c.created_at
            } for c in callbacks
        ]
    }


@router.patch("/properties/{property_id}/visibility")
def toggle_property_visibility(
    property_id: int,
    payload: VisibilityPayload,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_user_with_role("ADMIN"))
):
    """
    Toggle property visibility: PUBLIC vs PRIVATE.
    When PRIVATE, completely removed from public listings & search.
    """
    p = db.query(Property).filter(Property.id == property_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Property not found.")

    new_status = payload.visibility_status.upper()
    if new_status not in ["PUBLIC", "PRIVATE"]:
        raise HTTPException(status_code=400, detail="Invalid visibility_status. Must be PUBLIC or PRIVATE.")

    p.visibility_status = new_status
    p.updated_at = datetime.now(timezone.utc)
    db.commit()

    # Log action in audit trail
    action = "PROPERTY_MADE_PRIVATE" if new_status == "PRIVATE" else "PROPERTY_MADE_PUBLIC"
    log = AdminAuditLog(
        admin_id=current_admin.id,
        admin_email=current_admin.email,
        action=action,
        entity_type="PROPERTY",
        entity_id=p.id,
        details=f"Property ID #{p.id} ('{p.title}') visibility changed to {new_status}."
    )
    db.add(log)
    db.commit()

    return {
        "success": True,
        "property_id": p.id,
        "visibility_status": p.visibility_status,
        "message": f"Property is now {new_status}."
    }


@router.patch("/properties/{property_id}/owner-contact")
def update_private_owner_contact(
    property_id: int,
    payload: OwnerContactUpdatePayload,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_user_with_role("ADMIN"))
):
    """
    Update or create private owner/agent contact info. Stored strictly in private database.
    """
    p = db.query(Property).filter(Property.id == property_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Property not found.")

    contact = db.query(PrivateOwnerContact).filter(PrivateOwnerContact.property_id == property_id).first()
    if not contact:
        contact = PrivateOwnerContact(
            property_id=property_id,
            contact_name=payload.contact_name or "Property Owner / Agent",
            contact_type=payload.contact_type or "OWNER",
            phone=payload.phone,
            email=payload.email,
            source=payload.source or "Manual Admin Entry",
            verification_status=payload.verification_status or "UNVERIFIED",
            permission_status=payload.permission_status or "PENDING",
            notes=payload.notes
        )
        db.add(contact)
    else:
        if payload.contact_name is not None: contact.contact_name = payload.contact_name
        if payload.contact_type is not None: contact.contact_type = payload.contact_type
        if payload.phone is not None: contact.phone = payload.phone
        if payload.email is not None: contact.email = payload.email
        if payload.source is not None: contact.source = payload.source
        if payload.verification_status is not None: contact.verification_status = payload.verification_status
        if payload.permission_status is not None: contact.permission_status = payload.permission_status
        if payload.notes is not None: contact.notes = payload.notes
        contact.updated_at = datetime.now(timezone.utc)

    db.commit()

    log = AdminAuditLog(
        admin_id=current_admin.id,
        admin_email=current_admin.email,
        action="OWNER_CONTACT_UPDATED",
        entity_type="PROPERTY",
        entity_id=p.id,
        details=f"Updated private owner contact for Property ID #{p.id}."
    )
    db.add(log)
    db.commit()

    return {
        "success": True,
        "property_id": property_id,
        "contact": {
            "id": contact.id,
            "contact_name": contact.contact_name,
            "contact_type": contact.contact_type,
            "phone": contact.phone,
            "email": contact.email,
            "verification_status": contact.verification_status,
            "permission_status": contact.permission_status
        }
    }


# -------------------------------------------------------------
# 4. LEAD & AI CONVERSATION MANAGEMENT
# -------------------------------------------------------------
@router.get("/leads")
def list_admin_leads(
    page: int = Query(1, ge=1),
    limit: int = Query(25, ge=1, le=100),
    status: Optional[str] = None,
    validation: Optional[str] = None,
    search: Optional[str] = None,
    property_id: Optional[int] = None,
    sort_by: str = "id",
    sort_order: str = "desc",
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_user_with_role("ADMIN"))
):
    """
    Search, filter, and paginate AI leads with duplicate detection flags.
    """
    query = db.query(AILead)

    if status and status.upper() != "ALL":
        query = query.filter(AILead.lead_status == status.upper())

    if validation and validation.upper() != "ALL":
        query = query.filter(AILead.validation_status == validation.upper())

    if property_id:
        query = query.filter(AILead.property_id == property_id)

    if search and search.strip():
        term = f"%{search.strip()}%"
        query = query.filter(
            or_(
                AILead.name.ilike(term),
                AILead.phone.ilike(term),
                AILead.property_name.ilike(term),
                AILead.lead_code.ilike(term)
            )
        )

    total = query.count()

    sort_col = getattr(AILead, sort_by, AILead.id)
    if sort_order.lower() == "asc":
        query = query.order_by(asc(sort_col))
    else:
        query = query.order_by(desc(sort_col))

    offset = (page - 1) * limit
    leads = query.offset(offset).limit(limit).all()

    items = []
    for l in leads:
        items.append({
            "id": l.id,
            "lead_code": l.lead_code,
            "name": l.name,
            "phone": l.phone,
            "property_id": l.property_id,
            "property_name": l.property_name,
            "buy_or_rent": l.buy_or_rent,
            "property_type": l.property_type,
            "bhk": l.bhk,
            "budget": l.budget,
            "loan_required": l.loan_required,
            "purchase_timeline": l.purchase_timeline,
            "site_visit_requested": l.site_visit_requested,
            "site_visit_date": l.site_visit_date,
            "site_visit_time": l.site_visit_time,
            "owner_callback_requested": l.owner_callback_requested,
            "call_summary": l.call_summary,
            "call_duration_seconds": l.call_duration_seconds,
            "lead_status": l.lead_status,
            "validation_status": l.validation_status,
            "is_duplicate": l.is_duplicate,
            "duplicate_of_id": l.duplicate_of_id,
            "owner_sent_status": l.owner_sent_status,
            "created_at": l.created_at
        })

    return {
        "items": items,
        "total": total,
        "page": page,
        "limit": limit,
        "total_pages": math.ceil(total / limit) if total > 0 else 1
    }


@router.get("/leads/{lead_id}")
def get_admin_lead_details(
    lead_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_user_with_role("ADMIN"))
):
    """
    Get comprehensive details for a single AI lead including duplicate references and owner info.
    """
    lead = db.query(AILead).filter(AILead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found.")

    prop = db.query(Property).filter(Property.id == lead.property_id).first() if lead.property_id else None
    owner = db.query(PrivateOwnerContact).filter(PrivateOwnerContact.property_id == lead.property_id).first() if lead.property_id else None
    visits = db.query(SiteVisit).filter(SiteVisit.lead_id == lead.id).all()

    duplicate_lead = None
    if lead.duplicate_of_id:
        dup = db.query(AILead).filter(AILead.id == lead.duplicate_of_id).first()
        if dup:
            duplicate_lead = {
                "id": dup.id,
                "lead_code": dup.lead_code,
                "name": dup.name,
                "created_at": dup.created_at
            }

    return {
        "lead": {
            "id": lead.id,
            "lead_code": lead.lead_code,
            "name": lead.name,
            "phone": lead.phone,
            "property_id": lead.property_id,
            "property_name": lead.property_name,
            "buy_or_rent": lead.buy_or_rent,
            "property_type": lead.property_type,
            "bhk": lead.bhk,
            "budget": lead.budget,
            "loan_required": lead.loan_required,
            "purchase_timeline": lead.purchase_timeline,
            "location_preference": lead.location_preference,
            "additional_requirements": lead.additional_requirements,
            "owner_callback_requested": lead.owner_callback_requested,
            "site_visit_requested": lead.site_visit_requested,
            "site_visit_date": lead.site_visit_date,
            "site_visit_time": lead.site_visit_time,
            "call_summary": lead.call_summary,
            "call_duration_seconds": lead.call_duration_seconds,
            "call_session_id": lead.call_session_id,
            "call_sid": getattr(lead, "call_sid", None),
            "call_status": getattr(lead, "call_status", "COMPLETED"),
            "call_started_at": getattr(lead, "call_started_at", None),
            "call_completed_at": getattr(lead, "call_completed_at", None),
            "transcript": getattr(lead, "transcript", None),
            "lead_status": lead.lead_status,
            "validation_status": lead.validation_status,
            "is_duplicate": lead.is_duplicate,
            "duplicate_of_id": lead.duplicate_of_id,
            "duplicate_lead": duplicate_lead,
            "owner_sent_status": lead.owner_sent_status,
            "owner_sent_at": lead.owner_sent_at,
            "admin_notes": lead.admin_notes,
            "created_at": lead.created_at,
            "updated_at": lead.updated_at
        },
        "property": {
            "id": prop.id,
            "title": prop.title,
            "locality": prop.locality,
            "price": prop.price,
            "visibility_status": prop.visibility_status
        } if prop else None,
        "owner_contact": {
            "contact_name": owner.contact_name,
            "contact_type": owner.contact_type,
            "phone": owner.phone,
            "email": owner.email,
            "verification_status": owner.verification_status
        } if owner else None,
        "site_visits": [
            {
                "id": v.id,
                "appointment_code": v.appointment_code,
                "visit_date": v.visit_date,
                "visit_time": v.visit_time,
                "status": v.status
            } for v in visits
        ]
    }


@router.patch("/leads/{lead_id}")
def update_admin_lead(
    lead_id: int,
    payload: LeadUpdatePayload,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_user_with_role("ADMIN"))
):
    """
    Update lead details, status, or admin notes.
    """
    lead = db.query(AILead).filter(AILead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found.")

    if payload.lead_status is not None: lead.lead_status = payload.lead_status
    if payload.validation_status is not None: lead.validation_status = payload.validation_status
    if payload.buy_or_rent is not None: lead.buy_or_rent = payload.buy_or_rent
    if payload.budget is not None: lead.budget = payload.budget
    if payload.bhk is not None: lead.bhk = payload.bhk
    if payload.loan_required is not None: lead.loan_required = payload.loan_required
    if payload.purchase_timeline is not None: lead.purchase_timeline = payload.purchase_timeline
    if payload.admin_notes is not None: lead.admin_notes = payload.admin_notes
    if payload.site_visit_requested is not None: lead.site_visit_requested = payload.site_visit_requested
    if payload.site_visit_date is not None: lead.site_visit_date = payload.site_visit_date
    if payload.site_visit_time is not None: lead.site_visit_time = payload.site_visit_time
    lead.updated_at = datetime.now(timezone.utc)

    db.commit()

    log = AdminAuditLog(
        admin_id=current_admin.id,
        admin_email=current_admin.email,
        action="LEAD_EDITED",
        entity_type="LEAD",
        entity_id=lead.id,
        details=f"Admin updated Lead #{lead.id} ({lead.name})."
    )
    db.add(log)
    db.commit()

    return {"success": True, "lead_id": lead.id, "message": "Lead updated successfully."}


@router.post("/leads/{lead_id}/approve")
def approve_admin_lead(
    lead_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_user_with_role("ADMIN"))
):
    """
    Approve lead after human review. Marks lead as VALID and INTERESTED.
    """
    lead = db.query(AILead).filter(AILead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found.")

    lead.validation_status = "VALID"
    if lead.lead_status in ["NEW", "SPAM", "INVALID"]:
        lead.lead_status = "INTERESTED"
    lead.updated_at = datetime.now(timezone.utc)
    db.commit()

    log = AdminAuditLog(
        admin_id=current_admin.id,
        admin_email=current_admin.email,
        action="LEAD_APPROVED",
        entity_type="LEAD",
        entity_id=lead.id,
        details=f"Lead #{lead.id} approved by admin."
    )
    db.add(log)
    db.commit()

    return {"success": True, "lead_id": lead.id, "lead_status": lead.lead_status, "message": "Lead approved."}


@router.post("/leads/{lead_id}/reject")
def reject_admin_lead(
    lead_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_user_with_role("ADMIN"))
):
    """
    Reject lead after review. Marks lead as INVALID and CLOSED.
    """
    lead = db.query(AILead).filter(AILead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found.")

    lead.validation_status = "INVALID"
    lead.lead_status = "CLOSED"
    lead.updated_at = datetime.now(timezone.utc)
    db.commit()

    log = AdminAuditLog(
        admin_id=current_admin.id,
        admin_email=current_admin.email,
        action="LEAD_REJECTED",
        entity_type="LEAD",
        entity_id=lead.id,
        details=f"Lead #{lead.id} rejected by admin."
    )
    db.add(log)
    db.commit()

    return {"success": True, "lead_id": lead.id, "lead_status": lead.lead_status, "message": "Lead rejected."}


@router.post("/leads/{lead_id}/mark-spam")
def mark_admin_lead_spam(
    lead_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_user_with_role("ADMIN"))
):
    """
    Flag lead as SPAM / rubbish.
    """
    lead = db.query(AILead).filter(AILead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found.")

    lead.validation_status = "SPAM"
    lead.lead_status = "SPAM"
    lead.updated_at = datetime.now(timezone.utc)
    db.commit()

    log = AdminAuditLog(
        admin_id=current_admin.id,
        admin_email=current_admin.email,
        action="LEAD_MARKED_SPAM",
        entity_type="LEAD",
        entity_id=lead.id,
        details=f"Lead #{lead.id} flagged as SPAM by admin."
    )
    db.add(log)
    db.commit()

    return {"success": True, "lead_id": lead.id, "lead_status": "SPAM", "message": "Lead marked as SPAM."}


@router.post("/leads/{lead_id}/send-owner")
def send_lead_to_owner(
    lead_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_user_with_role("ADMIN"))
):
    """
    Send lead information to the verified owner/agent.
    If notification channel is not configured, records NOT_CONFIGURED without false claims.
    """
    result = LeadManagementService.send_to_owner(db, lead_id, current_admin)
    return result


@router.post("/leads/{lead_id}/generate-report")
@router.get("/leads/{lead_id}/report-pdf")
def download_lead_pdf_report(
    lead_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_user_with_role("ADMIN"))
):
    """
    Generate and download AI_Property_Lead_Report_[lead_id].pdf.
    Protected strictly inside private admin dashboard.
    """
    try:
        pdf_bytes = LeadManagementService.generate_lead_pdf(db, lead_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=AI_Property_Lead_Report_{lead_id}.pdf"
        }
    )


# -------------------------------------------------------------
# 5. SITE VISIT APPOINTMENT MANAGEMENT
# -------------------------------------------------------------
@router.get("/site-visits")
def list_admin_site_visits(
    page: int = Query(1, ge=1),
    limit: int = Query(25, ge=1, le=100),
    status: Optional[str] = None,
    property_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_user_with_role("ADMIN"))
):
    """
    List and filter site visit requests.
    """
    query = db.query(SiteVisit)

    if status and status.upper() != "ALL":
        query = query.filter(SiteVisit.status == status.upper())

    if property_id:
        query = query.filter(SiteVisit.property_id == property_id)

    total = query.count()
    offset = (page - 1) * limit
    visits = query.order_by(desc(SiteVisit.created_at)).offset(offset).limit(limit).all()

    items = []
    for v in visits:
        prop = db.query(Property).filter(Property.id == v.property_id).first()
        items.append({
            "id": v.id,
            "appointment_code": v.appointment_code,
            "lead_id": v.lead_id,
            "property_id": v.property_id,
            "property_name": prop.title if prop else f"Property #{v.property_id}",
            "locality": prop.locality if prop else "Bengaluru",
            "user_name": v.user_name,
            "user_phone": v.user_phone,
            "visit_date": v.visit_date,
            "visit_time": v.visit_time,
            "status": v.status,
            "admin_notes": v.admin_notes,
            "created_at": v.created_at
        })

    return {
        "items": items,
        "total": total,
        "page": page,
        "limit": limit,
        "total_pages": math.ceil(total / limit) if total > 0 else 1
    }


@router.patch("/site-visits/{visit_id}")
def update_admin_site_visit(
    visit_id: int,
    payload: SiteVisitUpdatePayload,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_user_with_role("ADMIN"))
):
    """
    Confirm, reschedule, cancel, or complete site visit appointments.
    """
    visit = db.query(SiteVisit).filter(SiteVisit.id == visit_id).first()
    if not visit:
        raise HTTPException(status_code=404, detail="Site visit not found.")

    valid_statuses = ["REQUESTED", "CONFIRMED", "RESCHEDULED", "CANCELLED", "COMPLETED"]
    new_status = payload.status.upper()
    if new_status not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of {valid_statuses}")

    old_status = visit.status
    visit.status = new_status
    if payload.visit_date: visit.visit_date = payload.visit_date
    if payload.visit_time: visit.visit_time = payload.visit_time
    if payload.admin_notes: visit.admin_notes = payload.admin_notes
    visit.updated_at = datetime.now(timezone.utc)

    # Sync lead status if confirmed
    lead = db.query(AILead).filter(AILead.id == visit.lead_id).first()
    if lead and new_status == "CONFIRMED":
        lead.lead_status = "SITE_VISIT_CONFIRMED"

    db.commit()

    action_map = {
        "CONFIRMED": "SITE_VISIT_CONFIRMED",
        "RESCHEDULED": "SITE_VISIT_RESCHEDULED",
        "CANCELLED": "SITE_VISIT_CANCELLED",
        "COMPLETED": "SITE_VISIT_COMPLETED",
        "REQUESTED": "SITE_VISIT_UPDATED"
    }
    log = AdminAuditLog(
        admin_id=current_admin.id,
        admin_email=current_admin.email,
        action=action_map.get(new_status, "SITE_VISIT_UPDATED"),
        entity_type="SITE_VISIT",
        entity_id=visit.id,
        details=f"Site Visit {visit.appointment_code} status changed from {old_status} to {new_status}."
    )
    db.add(log)
    db.commit()

    return {
        "success": True,
        "visit_id": visit.id,
        "status": visit.status,
        "message": f"Site visit status updated to {new_status}."
    }


# -------------------------------------------------------------
# 6. AUDIT TRAIL LOGS
# -------------------------------------------------------------
@router.get("/audit-logs")
def get_admin_audit_logs(
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_user_with_role("ADMIN"))
):
    """
    Returns chronological log of private administrative actions.
    """
    logs = db.query(AdminAuditLog).order_by(desc(AdminAuditLog.timestamp)).limit(limit).all()
    return [
        {
            "id": l.id,
            "admin_id": l.admin_id,
            "admin_email": l.admin_email,
            "action": l.action,
            "entity_type": l.entity_type,
            "entity_id": l.entity_id,
            "details": l.details,
            "timestamp": l.timestamp
        } for l in logs
    ]


# -------------------------------------------------------------
# 7. PUBLIC VOICE CALL REQUEST (SECTION 27)
# -------------------------------------------------------------
@router.post("/voice/call-request")
@router.post("/private/voice/call-request")
def record_voice_call_request(
    payload: VoiceCallRequestPayload,
    db: Session = Depends(get_db)
):
    """
    Public endpoint invoked by 'Contact Owner with AI' button to register user call request,
    consent, and immediately create structured lead record in private database.
    """
    prop = db.query(Property).filter(Property.id == payload.property_id).first()
    if not prop:
        raise HTTPException(status_code=404, detail="Property not found.")

    if not payload.consent:
        raise HTTPException(status_code=400, detail="User consent is required for AI call.")

    from app.services.voice_assistant_service import VoiceAssistantService
    
    # Execute real outbound call via Twilio (or truthful TELEPHONY_NOT_CONFIGURED status)
    voice_res = VoiceAssistantService.initiate_voice_callback(
        property_id=payload.property_id,
        phone_number=payload.user_phone,
        user_id=None,
        db=db
    )
    session_id = voice_res.get("session_id")

    # Retrieve callback record and attach consent
    vc_req = db.query(VoiceCallbackRequest).filter(VoiceCallbackRequest.session_id == session_id).first()
    if vc_req:
        vc_req.consent = payload.consent
        vc_req.consent_timestamp = datetime.now(timezone.utc)
        db.commit()

    # Process structured lead in private system
    lead = LeadManagementService.create_or_process_call_lead(
        db=db,
        phone=payload.user_phone,
        property_id=payload.property_id,
        inquiry_text=payload.inquiry_text,
        session_id=session_id,
        bhk=f"{prop.bhk} BHK",
        buy_or_rent="BUY",
        budget=f"₹{prop.price:,.0f}" if prop.price else "₹80–90 Lakh"
    )

    return {
        "success": True,
        "call_request_id": vc_req.id if vc_req else None,
        "session_id": session_id,
        "call_sid": voice_res.get("call_sid"),
        "lead_id": lead.id if lead else None,
        "call_status": voice_res.get("status", "REQUESTED"),
        "consent": payload.consent,
        "consent_timestamp": vc_req.consent_timestamp if vc_req else datetime.now(timezone.utc),
        "message": voice_res.get("message", "AI callback request processed."),
        "diagnostics": voice_res.get("diagnostics", {})
    }

# -------------------------------------------------------------
# SUBSCRIPTION MANAGEMENT (PROPULSE PRO)
# -------------------------------------------------------------
@router.get("/subscriptions")
def list_admin_subscriptions(
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_user_with_role("ADMIN"))
):
    """
    Returns user subscriptions with plan, status, payment/subscription ID,
    activation and expiry dates. Zero exposure of Razorpay secret keys.
    """
    subs = db.query(Subscription).order_by(desc(Subscription.created_at)).all()
    results = []
    for s in subs:
        u = db.query(User).filter(User.id == s.user_id).first()
        results.append({
            "id": s.id,
            "user_id": s.user_id,
            "user_email": u.email if u else "N/A",
            "user_name": u.full_name if u else "N/A",
            "plan": s.plan,
            "subscription_status": s.subscription_status,
            "razorpay_payment_id": s.razorpay_payment_id,
            "razorpay_order_id": s.razorpay_order_id,
            "razorpay_subscription_id": s.razorpay_subscription_id,
            "plan_amount": s.plan_amount,
            "currency": s.currency,
            "start_date": s.start_date.isoformat() if s.start_date else None,
            "end_date": s.end_date.isoformat() if s.end_date else None,
            "created_at": s.created_at.isoformat() if s.created_at else None,
            "updated_at": s.updated_at.isoformat() if s.updated_at else None,
        })
    return {
        "total": len(results),
        "subscriptions": results
    }
