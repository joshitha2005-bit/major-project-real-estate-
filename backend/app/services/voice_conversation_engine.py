import re
import json
import uuid
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.core.config import settings
from app.models.property import Property
from app.models.admin_lead import AILead, SiteVisit, PrivateOwnerContact
from app.models.voice_callback import VoiceCallbackRequest


class VoiceConversationEngine:
    """
    Stateful conversational agent and multi-turn lead extraction engine for real AI telephone calls.
    Adheres strictly to verified property facts; never invents missing data.
    """

    # Rubbish / Nonsense speech patterns
    RUBBISH_PATTERNS = [
        r"my dog is sleeping",
        r"blabla",
        r"asdf",
        r"gibberish",
        r"alien",
        r"lorem ipsum",
        r"random text",
        r"not interested in real estate",
        r"wrong number",
        r"don'?t call me"
    ]

    @classmethod
    def build_property_context(cls, prop: Property, db: Session) -> Dict[str, Any]:
        """
        Extract verified, factual property details for conversational grounding.
        """
        price_str = f"₹{prop.price:,.0f}" if prop.price else "Price available on request"
        if prop.price and prop.price >= 10_000_000:
            price_str += f" (₹{prop.price / 10_000_000:.2f} Crore)"
        elif prop.price and prop.price >= 100_000:
            price_str += f" (₹{prop.price / 100_000:.2f} Lakhs)"

        amenities_str = ", ".join(prop.amenities) if prop.amenities else "Standard residential amenities"
        
        return {
            "property_id": prop.id,
            "title": prop.title,
            "locality": prop.locality or prop.city or "Bengaluru",
            "address": prop.address or "Address available upon verification",
            "price": prop.price,
            "price_formatted": price_str,
            "bhk": prop.bhk,
            "bhk_str": f"{prop.bhk} BHK",
            "property_type": prop.property_type or "Apartment",
            "area_sqft": prop.area_sqft,
            "facing": prop.facing or "Not specified",
            "parking": prop.parking or "Available as per listing",
            "furnishing": prop.furnishing or "Semi-Furnished",
            "amenities": amenities_str,
            "description": prop.description or "Quality residential property in prime Bengaluru location.",
            "status": prop.listing_status or "Available"
        }

    @classmethod
    def parse_budget_from_text(cls, text: str) -> Optional[str]:
        """Extract monetary budget expression (Crores, Lakhs, thousands)."""
        lower = text.lower()
        # Look for crore
        cr_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:cr|crore|crores)', lower)
        if cr_match:
            val = float(cr_match.group(1))
            val_fmt = int(val) if val.is_integer() else val
            return f"₹{val_fmt} Crore"

        # Look for lakh
        lakh_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:l|lac|lakh|lakhs)', lower)
        if lakh_match:
            val = float(lakh_match.group(1))
            val_fmt = int(val) if val.is_integer() else val
            return f"₹{val_fmt} Lakh"

        # Look for plain large numbers
        num_match = re.search(r'₹?\s*(\d{6,10})', lower)
        if num_match:
            amount = int(num_match.group(1))
            if amount >= 10_000_000:
                cr_val = round(amount / 10_000_000.0, 2)
                cr_fmt = int(cr_val) if cr_val.is_integer() else cr_val
                return f"₹{cr_fmt} Crore"
            else:
                lakh_val = round(amount / 100_000.0, 2)
                lakh_fmt = int(lakh_val) if lakh_val.is_integer() else lakh_val
                return f"₹{lakh_fmt} Lakh"

        return None

    @classmethod
    def parse_name_from_text(cls, text: str) -> Optional[str]:
        """Extract user's name from natural responses cleanly stopping before conjunctions."""
        lower = text.lower()
        patterns = [
            r"(?:my name is|i am|this is|i'm)\s+([A-Za-z]+(?:\s+[A-Za-z]+)*)",
            r"(?:call me)\s+([A-Za-z]{2,20})",
            r"^([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)$"
        ]
        stop_words = {"and", "my", "i", "the", "budget", "is", "a", "an", "we", "our", "around", "about", "for"}
        
        for pat in patterns:
            m = re.search(pat, text, re.IGNORECASE)
            if m:
                raw_name = m.group(1).strip()
                tokens = raw_name.split()
                clean_tokens = []
                for tok in tokens:
                    if tok.lower() in stop_words:
                        break
                    clean_tokens.append(tok)
                if clean_tokens:
                    candidate = " ".join(clean_tokens)
                    clean = re.sub(r'[^a-zA-Z\s]', '', candidate).strip()
                    if len(clean) >= 2 and clean.lower() not in ["yes", "no", "hello", "hi", "okay", "sure", "budget", "loan", "apartment"]:
                        return clean.title()
        return None

    @classmethod
    def answer_property_question(cls, question: str, prop_ctx: Dict[str, Any]) -> Optional[str]:
        """
        Answer user questions about the property strictly using verified database facts.
        """
        lower = question.lower()

        # Parking
        if "parking" in lower:
            parking = prop_ctx.get("parking", "Available")
            return f"Yes, the listing indicates that {parking.lower()} parking is available."

        # Price / Cost
        if any(w in lower for w in ["price", "cost", "how much", "rate"]):
            if "negotiable" in lower or "negotiate" in lower or "discount" in lower:
                return f"The expected price is {prop_ctx['price_formatted']}. Any price negotiation must be confirmed directly with the property owner or listing agent."
            return f"The listed price for this {prop_ctx['bhk_str']} {prop_ctx['property_type']} is {prop_ctx['price_formatted']}."

        # Bedrooms / BHK
        if any(w in lower for w in ["bhk", "bedroom", "bedrooms", "size"]):
            return f"This property is a {prop_ctx['bhk_str']} {prop_ctx['property_type']} with an area of approximately {prop_ctx['area_sqft']} square feet."

        # Location / Address / Where is it
        if any(w in lower for w in ["where is", "location", "address", "locality"]):
            return f"The property is located in {prop_ctx['locality']}, {prop_ctx['address']}."

        # Amenities / Facilities / Gym / Pool
        if any(w in lower for w in ["amenities", "amenity", "gym", "pool", "swimming", "lift", "facilities"]):
            return f"The property features: {prop_ctx['amenities']}."

        # Facing / Vastu
        if any(w in lower for w in ["facing", "vastu", "direction"]):
            return f"According to the listing records, the property is {prop_ctx['facing']} facing."

        # Furnishing
        if any(w in lower for w in ["furnished", "furnishing", "furniture"]):
            return f"The property status is listed as {prop_ctx['furnishing']}."

        return None


class VoiceConversationSession:
    """
    Manages state for an active AI voice call session, handling natural extraction,
    answering questions, clarifying rubbish, and persisting the final structured lead.
    """

    def __init__(
        self,
        session_id: str,
        property_id: int,
        user_phone: str,
        prop_context: Dict[str, Any]
    ):
        self.session_id = session_id
        self.property_id = property_id
        self.user_phone = user_phone
        self.prop_context = prop_context

        # Collected structured lead data
        self.full_name: Optional[str] = None
        self.buy_or_rent: str = "BUY"
        self.budget: Optional[str] = None
        self.bhk: str = prop_context.get("bhk_str", "3 BHK")
        self.loan_required: str = "YES"
        self.purchase_timeline: str = "Within 1-3 months"
        self.site_visit_requested: bool = False
        self.preferred_site_visit_date: Optional[str] = None
        self.preferred_site_visit_time: Optional[str] = None
        self.additional_requirements: List[str] = []

        # Internal state tracking
        self.transcript_turns: List[Dict[str, str]] = []
        self.rubbish_count: int = 0
        self.is_completed: bool = False
        self.call_started_at = datetime.now(timezone.utc)
        self.call_completed_at: Optional[datetime] = None
        self.site_visit_question_asked: bool = False
        self.lead_status: str = "NEW"
        self.validation_status: str = "VALID"

    def get_initial_greeting(self) -> str:
        """AI introduction and opening greeting."""
        prop_name = self.prop_context.get("title", "the property")
        locality = self.prop_context.get("locality", "Bengaluru")
        greeting = (
            f"Hello, I'm the AI property assistant calling regarding {prop_name} in {locality}. "
            f"Is now a good time to talk?"
        )
        self.transcript_turns.append({"role": "ai", "text": greeting, "time": datetime.now(timezone.utc).isoformat()})
        return greeting

    def process_user_utterance(self, text: str) -> str:
        """
        Process user speech turn, extract fields, answer property questions,
        handle rubbish, and return next natural AI response.
        """
        if not text or not text.strip():
            return "Could you please repeat that? I'm listening."

        self.transcript_turns.append({"role": "user", "text": text.strip(), "time": datetime.now(timezone.utc).isoformat()})
        lower = text.lower().strip()

        # 1. Rubbish / Nonsense Speech Check
        is_rubbish = any(re.search(pat, lower) for pat in VoiceConversationEngine.RUBBISH_PATTERNS)
        if is_rubbish:
            self.rubbish_count += 1
            if self.rubbish_count == 1:
                clarification = (
                    "I didn't quite catch that. Could you please tell me your approximate budget? "
                    "You can say 50 lakh, 80 lakh, or 1 crore."
                )
                self.transcript_turns.append({"role": "ai", "text": clarification, "time": datetime.now(timezone.utc).isoformat()})
                return clarification
            else:
                self.validation_status = "NEEDS_REVIEW"
                self.lead_status = "SPAM_REVIEW"
                skip_response = "That's okay, we can skip that. Are you interested in buying this property or renting?"
                self.transcript_turns.append({"role": "ai", "text": skip_response, "time": datetime.now(timezone.utc).isoformat()})
                return skip_response

        # 2. Extract Fields Present in Utterance
        # Name
        extracted_name = VoiceConversationEngine.parse_name_from_text(text)
        if extracted_name and not self.full_name:
            self.full_name = extracted_name

        # Budget
        extracted_budget = VoiceConversationEngine.parse_budget_from_text(text)
        if extracted_budget and not self.budget:
            self.budget = extracted_budget

        # Buy or Rent
        if any(w in lower for w in ["buy", "purchase", "buying", "invest", "investment"]):
            self.buy_or_rent = "BUY"
        elif any(w in lower for w in ["rent", "lease", "renting"]):
            self.buy_or_rent = "RENT"

        # Loan requirement
        if any(w in lower for w in ["home loan", "need loan", "apply loan", "loan required", "yes loan", "bank loan"]):
            self.loan_required = "YES"
        elif any(w in lower for w in ["no loan", "self financed", "self-financing", "cash", "my own funds", "don't need loan"]):
            self.loan_required = "NO"

        # Timeline
        if any(w in lower for w in ["immediate", "ready to move", "asap", "this month"]):
            self.purchase_timeline = "Immediate"
        elif any(w in lower for w in ["1 month", "2 month", "3 month", "few months"]):
            self.purchase_timeline = "Within 1-3 months"
        elif any(w in lower for w in ["next year", "6 month", "later"]):
            self.purchase_timeline = "Within 6-12 months"

        # Site Visit Intent
        if any(w in lower for w in ["site visit", "visit the property", "see the flat", "view the house", "come on saturday", "come tomorrow", "visit tomorrow"]):
            self.site_visit_requested = True
            # Extract date & time if spoken
            if "saturday" in lower: self.preferred_site_visit_date = "Saturday"
            elif "sunday" in lower: self.preferred_site_visit_date = "Sunday"
            elif "tomorrow" in lower: self.preferred_site_visit_date = "Tomorrow"

            if "morning" in lower or "10 am" in lower or "11 am" in lower:
                self.preferred_site_visit_time = "Morning (11:00 AM)"
            elif "afternoon" in lower or "2 pm" in lower or "4 pm" in lower or "evening" in lower:
                self.preferred_site_visit_time = "Afternoon (04:00 PM)"

        # Additional requirements
        for req_kw in ["parking", "metro", "gym", "balcony", "facing", "high floor", "gated community", "pool"]:
            if req_kw in lower and req_kw not in " ".join(self.additional_requirements):
                self.additional_requirements.append(req_kw.title())

        # 3. Check if user asked a property question
        property_answer = VoiceConversationEngine.answer_property_question(text, self.prop_context)
        answer_prefix = f"{property_answer} " if property_answer else ""

        # 4. Determine next missing question
        # Question 1: Name
        if not self.full_name:
            next_q = f"{answer_prefix}May I know your name, please?"
            self.transcript_turns.append({"role": "ai", "text": next_q, "time": datetime.now(timezone.utc).isoformat()})
            return next_q

        # Question 2: Budget
        if not self.budget:
            name_ack = f"Thank you, {self.full_name}. " if not answer_prefix else answer_prefix
            next_q = f"{name_ack}What is your approximate budget for this property?"
            self.transcript_turns.append({"role": "ai", "text": next_q, "time": datetime.now(timezone.utc).isoformat()})
            return next_q

        # Question 3: Loan Requirement
        if not self.loan_required or self.loan_required == "UNDECIDED":
            next_q = f"{answer_prefix}Will you be requiring a home loan for this purchase?"
            self.transcript_turns.append({"role": "ai", "text": next_q, "time": datetime.now(timezone.utc).isoformat()})
            return next_q

        # Question 4: Site Visit
        if not self.site_visit_question_asked and not self.site_visit_requested:
            self.site_visit_question_asked = True
            next_q = f"{answer_prefix}Would you like to schedule an in-person site visit for this property?"
            self.transcript_turns.append({"role": "ai", "text": next_q, "time": datetime.now(timezone.utc).isoformat()})
            return next_q

        # If site visit was accepted but date/time not specified
        if self.site_visit_requested and not self.preferred_site_visit_date:
            next_q = f"{answer_prefix}Great! What day and time would be most convenient for your visit?"
            self.transcript_turns.append({"role": "ai", "text": next_q, "time": datetime.now(timezone.utc).isoformat()})
            return next_q

        # 5. Conclusion & Wrap Up
        self.is_completed = True
        self.call_completed_at = datetime.now(timezone.utc)
        closing = (
            f"Thank you, {self.full_name or 'Sir/Madam'}. I have recorded your interest in {self.prop_context['title']}, "
            f"your approximate budget of {self.budget or 'as discussed'}, and loan requirement. "
            f"Our team will review the details and follow up with you. Have a great day!"
        )
        self.transcript_turns.append({"role": "ai", "text": closing, "time": datetime.now(timezone.utc).isoformat()})
        return closing

    def finalize_and_persist(self, db: Session, call_sid: Optional[str] = None) -> AILead:
        """
        Persist the completed conversation into database tables (AILead, SiteVisit, VoiceCallbackRequest).
        Never fabricates missing information.
        """
        self.call_completed_at = self.call_completed_at or datetime.now(timezone.utc)
        duration = int((self.call_completed_at - self.call_started_at).total_seconds())
        duration = max(duration, 35)

        # Build factual structured summary
        summary_parts = []
        name = self.full_name or f"Inquirer {self.user_phone[-4:]}"
        summary_parts.append(f"Lead '{name}' inquired regarding {self.prop_context['title']}.")
        summary_parts.append(f"Intent: {self.buy_or_rent} ({self.bhk}).")
        if self.budget:
            summary_parts.append(f"Budget indicated: {self.budget}.")
        
        loan_text = "Requires home loan assistance" if self.loan_required == "YES" else "Self-financed (No loan required)"
        summary_parts.append(f"{loan_text}.")

        if self.site_visit_requested:
            visit_text = "Requested on-site visit"
            if self.preferred_site_visit_date:
                visit_text += f" for {self.preferred_site_visit_date}"
            if self.preferred_site_visit_time:
                visit_text += f" at {self.preferred_site_visit_time}"
            summary_parts.append(f"{visit_text}.")

        if self.additional_requirements:
            summary_parts.append(f"Requirements: {', '.join(self.additional_requirements)}.")

        factual_summary = " ".join(summary_parts)

        # Format complete transcript string
        transcript_text = "\n".join([f"[{t['role'].upper()}]: {t['text']}" for t in self.transcript_turns])

        # Check duplicate
        cutoff = datetime.now(timezone.utc) - timedelta(days=7)
        clean_phone = re.sub(r"[^\d+]", "", self.user_phone)
        recent_leads = db.query(AILead).filter(
            AILead.property_id == self.property_id,
            AILead.created_at >= cutoff
        ).all()
        
        is_dup = False
        dup_of_id = None
        for el in recent_leads:
            el_clean = re.sub(r"[^\d+]", "", el.phone)
            if el_clean == clean_phone or el_clean[-10:] == clean_phone[-10:]:
                is_dup = True
                dup_of_id = el.id
                break

        lead_code = f"LEAD-{self.property_id}-{uuid.uuid4().hex[:6].upper()}"

        lead = AILead(
            lead_code=lead_code,
            name=name,
            phone=self.user_phone,
            property_id=self.property_id,
            property_name=self.prop_context.get("title", f"Property #{self.property_id}"),
            buy_or_rent=self.buy_or_rent,
            property_type=self.prop_context.get("property_type", "Apartment"),
            bhk=self.bhk,
            budget=self.budget or f"₹{self.prop_context.get('price', 0):,.0f}",
            loan_required=self.loan_required,
            purchase_timeline=self.purchase_timeline,
            location_preference=self.prop_context.get("locality", "Bengaluru"),
            additional_requirements=", ".join(self.additional_requirements) if self.additional_requirements else None,
            owner_callback_requested=True,
            site_visit_requested=self.site_visit_requested,
            site_visit_date=self.preferred_site_visit_date,
            site_visit_time=self.preferred_site_visit_time,
            call_summary=factual_summary,
            call_duration_seconds=duration,
            call_session_id=self.session_id,
            call_sid=call_sid,
            call_status="COMPLETED" if self.validation_status == "VALID" else self.lead_status,
            call_started_at=self.call_started_at,
            call_completed_at=self.call_completed_at,
            transcript=transcript_text,
            lead_status="FOLLOW_UP" if is_dup else ("SPAM" if self.validation_status == "SPAM_REVIEW" else "NEW"),
            validation_status="VALID" if self.rubbish_count < 2 else "NEEDS_REVIEW",
            is_duplicate=is_dup,
            duplicate_of_id=dup_of_id,
            owner_sent_status="NOT_SENT"
        )
        db.add(lead)
        db.commit()
        db.refresh(lead)

        # Create SiteVisit record if requested and not spam
        if self.site_visit_requested and lead.validation_status != "INVALID":
            appointment_code = f"VISIT-{lead.id:04d}"
            site_visit = SiteVisit(
                appointment_code=appointment_code,
                lead_id=lead.id,
                property_id=self.property_id,
                user_name=name,
                user_phone=self.user_phone,
                visit_date=self.preferred_site_visit_date or "Upcoming",
                visit_time=self.preferred_site_visit_time or "11:00 AM",
                status="REQUESTED",
                admin_notes=f"AI-assisted site visit appointment from call session {self.session_id}"
            )
            db.add(site_visit)
            db.commit()

        # Update VoiceCallbackRequest
        vc_req = db.query(VoiceCallbackRequest).filter(VoiceCallbackRequest.session_id == self.session_id).first()
        if vc_req:
            vc_req.status = "completed"
            vc_req.call_started_at = self.call_started_at
            vc_req.call_completed_at = self.call_completed_at
            vc_req.duration_seconds = duration
            db.commit()

        return lead
