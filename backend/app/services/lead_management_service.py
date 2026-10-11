import uuid
import os
import re
import io
from typing import Optional, Dict, Any, Tuple
from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from app.core.config import settings
from app.models.admin_lead import AILead, PrivateOwnerContact, SiteVisit, AdminAuditLog
from app.models.property import Property
from app.models.user import User

# ReportLab imports for lead report PDF generation
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT


class LeadManagementService:
    """
    Core service handling AI lead extraction, rubbish/spam detection,
    factual summarization, duplicate checking, owner dispatch, and PDF generation.
    """

    RUBBISH_PATTERNS = [
        r"my dog is sleeping",
        r"blabla",
        r"asdf",
        r"gibberish",
        r"alien",
        r"lorem ipsum",
        r"random text",
        r"test test test",
        r"not interested in real estate",
        r"wrong number",
        r"don'?t call me"
    ]

    @classmethod
    def evaluate_text_validity(cls, text: str) -> Tuple[str, str]:
        """
        Evaluate if transcription or user notes contain rubbish or spam.
        Returns (validation_status, lead_status)
        """
        if not text or len(text.strip()) < 3:
            return ("NEEDS_REVIEW", "NEW")

        lower = text.lower()
        for pat in cls.RUBBISH_PATTERNS:
            if re.search(pat, lower):
                return ("INVALID", "SPAM")

        return ("VALID", "NEW")

    @classmethod
    def detect_duplicate(cls, db: Session, phone: str, property_id: int, window_days: int = 7) -> Optional[AILead]:
        """
        Detect if a recent lead exists for the same user phone & property.
        """
        cutoff = datetime.now(timezone.utc) - timedelta(days=window_days)
        clean_phone = re.sub(r"[^\d+]", "", phone)
        # Look for existing leads in window
        existing = db.query(AILead).filter(
            AILead.property_id == property_id,
            AILead.created_at >= cutoff
        ).all()

        for lead in existing:
            lead_clean_phone = re.sub(r"[^\d+]", "", lead.phone)
            if lead_clean_phone == clean_phone or lead_clean_phone[-10:] == clean_phone[-10:]:
                return lead
        return None

    @classmethod
    def generate_factual_summary(
        cls,
        name: str,
        property_name: str,
        buy_or_rent: str,
        budget: str,
        loan_required: str,
        bhk: str,
        site_visit_requested: bool,
        site_visit_date: Optional[str] = None,
        site_visit_time: Optional[str] = None,
        owner_callback_requested: bool = True,
        notes: Optional[str] = None
    ) -> str:
        """
        Generates a strictly factual summary containing ONLY verified and user-supplied data.
        Never hallucinates missing numbers.
        """
        parts = [f"Lead '{name}' inquired regarding {property_name}."]
        parts.append(f"Intent: {buy_or_rent.upper()} ({bhk}).")
        if budget and budget.lower() != "unknown":
            parts.append(f"Budget indicated: {budget}.")
        
        loan_str = "Home loan required" if loan_required == "YES" else ("Self-financed (No loan)" if loan_required == "NO" else "Loan requirement undecided")
        parts.append(f"{loan_str}.")

        if site_visit_requested and site_visit_date:
            visit_str = f"Requested on-site visit for {site_visit_date}"
            if site_visit_time:
                visit_str += f" at {site_visit_time}"
            parts.append(f"{visit_str}.")

        if owner_callback_requested:
            parts.append("Requested direct contact from property owner/agent.")

        if notes and notes.strip():
            parts.append(f"Additional requirements: {notes.strip()}.")

        return " ".join(parts)

    @classmethod
    def create_or_process_call_lead(
        cls,
        db: Session,
        phone: str,
        property_id: int,
        name: Optional[str] = None,
        inquiry_text: Optional[str] = None,
        session_id: Optional[str] = None,
        buy_or_rent: str = "BUY",
        budget: str = "₹80–90 Lakh",
        bhk: str = "3 BHK",
        loan_required: str = "YES",
        site_visit_requested: bool = False,
        site_visit_date: Optional[str] = None,
        site_visit_time: Optional[str] = None,
        owner_callback_requested: bool = True,
        call_duration_seconds: int = 60
    ) -> AILead:
        """
        Create structured lead after voice call / request, checking duplicates and spam.
        """
        prop = db.query(Property).filter(Property.id == property_id).first()
        prop_name = prop.title if prop else f"Property #{property_id}"
        if not name or not name.strip():
            name = f"Inquirer {phone[-4:]}"

        validation_status, lead_status = cls.evaluate_text_validity(inquiry_text or "")
        
        # Check duplicate
        duplicate_lead = cls.detect_duplicate(db, phone, property_id)
        is_dup = duplicate_lead is not None
        dup_id = duplicate_lead.id if duplicate_lead else None

        if is_dup:
            lead_status = "FOLLOW_UP"

        if validation_status == "INVALID":
            lead_status = "SPAM"

        summary = cls.generate_factual_summary(
            name=name,
            property_name=prop_name,
            buy_or_rent=buy_or_rent,
            budget=budget,
            loan_required=loan_required,
            bhk=bhk,
            site_visit_requested=site_visit_requested,
            site_visit_date=site_visit_date,
            site_visit_time=site_visit_time,
            owner_callback_requested=owner_callback_requested,
            notes=inquiry_text
        )

        lead_code = f"LEAD-{property_id}-{uuid.uuid4().hex[:6].upper()}"

        new_lead = AILead(
            lead_code=lead_code,
            name=name,
            phone=phone,
            property_id=property_id,
            property_name=prop_name,
            buy_or_rent=buy_or_rent,
            property_type=prop.property_type if prop else "Apartment",
            bhk=bhk,
            budget=budget,
            loan_required=loan_required,
            purchase_timeline="Within 1-3 months",
            location_preference=prop.locality if prop else "Bengaluru",
            additional_requirements=inquiry_text,
            owner_callback_requested=owner_callback_requested,
            site_visit_requested=site_visit_requested,
            site_visit_date=site_visit_date,
            site_visit_time=site_visit_time,
            call_summary=summary,
            call_duration_seconds=call_duration_seconds,
            call_session_id=session_id,
            lead_status=lead_status,
            validation_status=validation_status,
            is_duplicate=is_dup,
            duplicate_of_id=dup_id,
            owner_sent_status="NOT_SENT"
        )
        db.add(new_lead)
        db.commit()
        db.refresh(new_lead)

        # Create SiteVisit record if requested and not spam
        if site_visit_requested and site_visit_date and validation_status != "INVALID":
            appointment_code = f"VISIT-{new_lead.id:04d}"
            site_visit = SiteVisit(
                appointment_code=appointment_code,
                lead_id=new_lead.id,
                property_id=property_id,
                user_name=name,
                user_phone=phone,
                visit_date=site_visit_date,
                visit_time=site_visit_time or "11:00 AM",
                status="REQUESTED",
                admin_notes=f"Created via AI Callback Session {session_id or ''}"
            )
            db.add(site_visit)
            db.commit()

        return new_lead

    @classmethod
    def generate_lead_pdf(cls, db: Session, lead_id: int) -> bytes:
        """
        Builds a comprehensive, confidential AI Property Lead Report PDF.
        """
        lead = db.query(AILead).filter(AILead.id == lead_id).first()
        if not lead:
            raise ValueError(f"Lead ID #{lead_id} not found.")

        prop = db.query(Property).filter(Property.id == lead.property_id).first() if lead.property_id else None
        private_contact = db.query(PrivateOwnerContact).filter(PrivateOwnerContact.property_id == lead.property_id).first() if lead.property_id else None

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=36,
            leftMargin=36,
            topMargin=36,
            bottomMargin=36
        )

        styles = getSampleStyleSheet()
        primary_color = colors.HexColor("#4338ca")    # Indigo
        accent_color = colors.HexColor("#0284c7")     # Blue
        dark_text = colors.HexColor("#0f172a")        # Slate-900
        muted_text = colors.HexColor("#475569")       # Slate-600
        bg_light = colors.HexColor("#f8fafc")         # Slate-50

        title_style = ParagraphStyle(
            "DocTitle",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=18,
            leading=22,
            textColor=primary_color,
            alignment=TA_LEFT
        )
        subtitle_style = ParagraphStyle(
            "DocSubtitle",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=9,
            leading=12,
            textColor=muted_text,
            alignment=TA_LEFT
        )
        section_style = ParagraphStyle(
            "SectionTitle",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=11,
            leading=14,
            textColor=dark_text,
            spaceBefore=10,
            spaceAfter=4
        )
        cell_bold = ParagraphStyle(
            "CellBold",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=8.5,
            leading=11,
            textColor=dark_text
        )
        cell_val = ParagraphStyle(
            "CellVal",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=8.5,
            leading=11,
            textColor=dark_text
        )
        summary_style = ParagraphStyle(
            "SummaryText",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=8.5,
            leading=12,
            textColor=dark_text
        )

        elements = []

        # 1. Header Banner
        header_table = Table([
            [
                Paragraph("<b>Cloud-Based Real Estate Analysis</b><br/><font size=7 color='#64748b'>PRIVATE PROPERTY & LEAD MANAGEMENT SYSTEM</font>", title_style),
                Paragraph(f"<b>CONFIDENTIAL REPORT</b><br/><font size=7 color='#64748b'>Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}</font>", subtitle_style)
            ]
        ], colWidths=[340, 200])
        header_table.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('ALIGN', (1,0), (1,0), 'RIGHT'),
        ]))
        elements.append(header_table)
        elements.append(Spacer(1, 10))
        elements.append(HRFlowable(width="100%", thickness=1.5, color=primary_color, spaceBefore=2, spaceAfter=10))

        # 2. Executive Badge Row
        val_color = "#16a34a" if lead.validation_status == "VALID" else ("#dc2626" if lead.validation_status in ["INVALID", "SPAM"] else "#d97706")
        status_color = "#2563eb"
        badge_text = f"<b>Lead Code:</b> {lead.lead_code} &nbsp;|&nbsp; <b>Validation:</b> <font color='{val_color}'><b>{lead.validation_status}</b></font> &nbsp;|&nbsp; <b>Status:</b> <b>{lead.lead_status}</b>"
        elements.append(Paragraph(badge_text, cell_bold))
        elements.append(Spacer(1, 8))

        # 3. Lead & Property Data Grid
        prop_title = prop.title if prop else lead.property_name
        prop_loc = prop.locality if prop else lead.location_preference
        prop_price = f"₹{prop.price:,.0f}" if prop and prop.price else "On Request"

        grid_data = [
            [Paragraph("<b>Lead Name</b>", cell_bold), Paragraph(lead.name, cell_val), Paragraph("<b>Property ID</b>", cell_bold), Paragraph(str(lead.property_id or "N/A"), cell_val)],
            [Paragraph("<b>Lead Phone</b>", cell_bold), Paragraph(lead.phone, cell_val), Paragraph("<b>Property Title</b>", cell_bold), Paragraph(prop_title, cell_val)],
            [Paragraph("<b>Intent</b>", cell_bold), Paragraph(lead.buy_or_rent, cell_val), Paragraph("<b>Location</b>", cell_bold), Paragraph(prop_loc, cell_val)],
            [Paragraph("<b>BHK Requirement</b>", cell_bold), Paragraph(lead.bhk, cell_val), Paragraph("<b>Listing Price</b>", cell_bold), Paragraph(prop_price, cell_val)],
            [Paragraph("<b>Budget Range</b>", cell_bold), Paragraph(lead.budget or "N/A", cell_val), Paragraph("<b>Loan Required</b>", cell_bold), Paragraph(lead.loan_required, cell_val)],
            [Paragraph("<b>Timeline</b>", cell_bold), Paragraph(lead.purchase_timeline or "Immediate", cell_val), Paragraph("<b>Duplicate Flag</b>", cell_bold), Paragraph("YES (Possible Duplicate)" if lead.is_duplicate else "NO (Original)", cell_val)],
            [Paragraph("<b>Call Status</b>", cell_bold), Paragraph(getattr(lead, "call_status", "COMPLETED") or "COMPLETED", cell_val), Paragraph("<b>Call Duration / SID</b>", cell_bold), Paragraph(f"{lead.call_duration_seconds or 0}s | {getattr(lead, 'call_sid', None) or 'Direct Registered'}", cell_val)],
        ]
        grid_table = Table(grid_data, colWidths=[110, 160, 110, 160])
        grid_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), bg_light),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('TOPPADDING', (0,0), (-1,-1), 4),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ]))
        elements.append(grid_table)
        elements.append(Spacer(1, 10))

        # 4. AI Call Consultation & Factual Summary
        elements.append(Paragraph("AI Consultation & Voice Call Summary", section_style))
        summary_p = Paragraph(lead.call_summary or "No summary recorded.", summary_style)
        summary_box = Table([[summary_p]], colWidths=[540])
        summary_box.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#f1f5f9")),
            ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#94a3b8")),
            ('TOPPADDING', (0,0), (-1,-1), 6),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
            ('LEFTPADDING', (0,0), (-1,-1), 8),
            ('RIGHTPADDING', (0,0), (-1,-1), 8),
        ]))
        elements.append(summary_box)
        elements.append(Spacer(1, 10))

        # 5. Site Visit & Callback Information
        elements.append(Paragraph("Site Visit & Follow-Up Requirements", section_style))
        sv_req = "YES" if lead.site_visit_requested else "NO"
        sv_date = f"{lead.site_visit_date or ''} {lead.site_visit_time or ''}".strip() or "Not Scheduled"
        cb_req = "YES" if lead.owner_callback_requested else "NO"

        sv_data = [
            [Paragraph("<b>Site Visit Requested:</b>", cell_bold), Paragraph(sv_req, cell_val), Paragraph("<b>Preferred Schedule:</b>", cell_bold), Paragraph(sv_date, cell_val)],
            [Paragraph("<b>Owner Callback Requested:</b>", cell_bold), Paragraph(cb_req, cell_val), Paragraph("<b>Owner Notification Status:</b>", cell_bold), Paragraph(str(lead.owner_sent_status or "PENDING_REVIEW"), cell_val)],
        ]
        sv_table = Table(sv_data, colWidths=[140, 130, 140, 130])
        sv_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.white),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#e2e8f0")),
            ('TOPPADDING', (0,0), (-1,-1), 4),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ]))
        elements.append(sv_table)
        elements.append(Spacer(1, 10))

        # 6. Confidential Owner & Admin Review Section
        elements.append(Paragraph("Confidential Verified Contact Information (Admin Only)", section_style))
        owner_name = str(private_contact.contact_name or "Not Assigned") if private_contact else "Not Assigned"
        owner_phone = str(private_contact.phone or "N/A") if private_contact else "N/A"
        owner_email = str(private_contact.email or "N/A") if private_contact else "N/A"
        owner_ver = str(private_contact.verification_status or "UNVERIFIED") if private_contact else "UNVERIFIED"
        owner_type = str(private_contact.contact_type or "N/A") if private_contact else "N/A"
        owner_src = str(private_contact.source or "N/A") if private_contact else "N/A"

        owner_data = [
            [Paragraph("<b>Contact Name:</b>", cell_bold), Paragraph(owner_name, cell_val), Paragraph("<b>Contact Type:</b>", cell_bold), Paragraph(owner_type, cell_val)],
            [Paragraph("<b>Contact Phone:</b>", cell_bold), Paragraph(owner_phone, cell_val), Paragraph("<b>Verification:</b>", cell_bold), Paragraph(owner_ver, cell_val)],
            [Paragraph("<b>Contact Email:</b>", cell_bold), Paragraph(owner_email, cell_val), Paragraph("<b>Source:</b>", cell_bold), Paragraph(owner_src, cell_val)],
        ]
        owner_table = Table(owner_data, colWidths=[110, 160, 110, 160])
        owner_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#fef2f2")),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#fecaca")),
            ('TOPPADDING', (0,0), (-1,-1), 4),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ]))
        elements.append(owner_table)
        elements.append(Spacer(1, 15))

        # 7. Security & Verification Footer
        footer_text = "<font size=7 color='#64748b'>NOTICE: This document contains strictly confidential real estate lead intelligence. Access is restricted to authorized administrative personnel. Any unauthorized distribution, reproduction, or disclosure is strictly prohibited under data privacy policies.</font>"
        elements.append(Paragraph(footer_text, ParagraphStyle("Footer", parent=styles["Normal"], alignment=TA_CENTER)))

        doc.build(elements)
        buffer.seek(0)
        return buffer.getvalue()

    @classmethod
    def send_to_owner(cls, db: Session, lead_id: int, admin_user: User) -> Dict[str, Any]:
        """
        Dispatch lead information to verified owner/agent.
        Honest handling: If provider is not configured, records NOT_CONFIGURED without false claims.
        """
        lead = db.query(AILead).filter(AILead.id == lead_id).first()
        if not lead:
            return {"success": False, "status": "NOT_FOUND", "message": "Lead not found."}

        if lead.validation_status in ["INVALID", "SPAM"]:
            return {"success": False, "status": "INVALID_LEAD", "message": "Cannot send SPAM or INVALID leads to property owners."}

        if not lead.property_id:
            return {"success": False, "status": "NO_PROPERTY", "message": "Lead is not associated with an active property."}

        private_contact = db.query(PrivateOwnerContact).filter(PrivateOwnerContact.property_id == lead.property_id).first()
        if not private_contact or private_contact.verification_status != "VERIFIED":
            return {
                "success": False,
                "status": "UNVERIFIED_CONTACT",
                "message": "Cannot send to unverified contact. Please verify owner contact credentials before dispatch."
            }

        # Check notification channel configuration
        provider = settings.OWNER_NOTIFICATION_PROVIDER
        if not provider or provider.strip() == "":
            lead.owner_sent_status = "NOT_CONFIGURED"
            db.commit()
            
            # Log action in audit
            log = AdminAuditLog(
                admin_id=admin_user.id,
                admin_email=admin_user.email,
                action="LEAD_SEND_ATTEMPTED",
                entity_type="LEAD",
                entity_id=lead.id,
                details=f"Notification channel not configured. Lead #{lead.id} held safely in database."
            )
            db.add(log)
            db.commit()

            return {
                "success": False,
                "status": "NOT_CONFIGURED",
                "message": "Owner notification not configured (stored safely in database). No external notification was sent.",
                "owner_contact": {
                    "name": private_contact.contact_name,
                    "phone": private_contact.phone,
                    "type": private_contact.contact_type
                }
            }

        # If a live provider is configured (e.g. Email / SMS / WhatsApp)
        lead.owner_sent_status = "SENT"
        lead.owner_sent_at = datetime.now(timezone.utc)
        if lead.lead_status == "NEW":
            lead.lead_status = "CONTACTED"
        db.commit()

        log = AdminAuditLog(
            admin_id=admin_user.id,
            admin_email=admin_user.email,
            action="LEAD_SENT_TO_OWNER",
            entity_type="LEAD",
            entity_id=lead.id,
            details=f"Lead dispatched to verified owner {private_contact.contact_name} via {provider}."
        )
        db.add(log)
        db.commit()

        return {
            "success": True,
            "status": "SENT",
            "message": f"Lead successfully dispatched to owner via {provider}.",
            "owner_contact": {
                "name": private_contact.contact_name,
                "phone": private_contact.phone,
                "type": private_contact.contact_type
            }
        }
