import os
import hmac
import hashlib
import time
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from dotenv import dotenv_values

from app.core.config import settings
from app.models.user import User
from app.models.subscription import Subscription

try:
    import razorpay
except ImportError:
    razorpay = None


class SubscriptionService:
    """
    Core Payment & Access Control Service for PropPulse Pro.
    Integrates with Razorpay for order creation, signature verification, and webhook handling.
    Enforces server-side authority over plan pricing, duration, and subscription status.
    """

    PLAN_CODE = "PRO"
    PLAN_NAME = "PROPULSE_PRO_299"
    PLAN_AMOUNT_PAISE = 29900  # ₹299.00 INR
    PLAN_AMOUNT_INR = 299.00
    CURRENCY = "INR"
    DURATION_DAYS = 30

    @classmethod
    def _get_credentials(cls) -> Dict[str, str]:
        """Fetch fresh Razorpay credentials, checking live .env if modified."""
        env_file = os.path.join(os.path.dirname(__file__), "..", "..", ".env")
        env_vals = dotenv_values(env_file) if os.path.exists(env_file) else {}

        key_id = (env_vals.get("RAZORPAY_KEY_ID") or os.getenv("RAZORPAY_KEY_ID") or settings.RAZORPAY_KEY_ID or "").strip()
        key_secret = (env_vals.get("RAZORPAY_KEY_SECRET") or os.getenv("RAZORPAY_KEY_SECRET") or settings.RAZORPAY_KEY_SECRET or "").strip()
        webhook_secret = (env_vals.get("RAZORPAY_WEBHOOK_SECRET") or os.getenv("RAZORPAY_WEBHOOK_SECRET") or settings.RAZORPAY_WEBHOOK_SECRET or "").strip()

        return {
            "key_id": key_id,
            "key_secret": key_secret,
            "webhook_secret": webhook_secret
        }

    @classmethod
    def is_gateway_configured(cls) -> bool:
        """Verify if real, valid Razorpay credentials are configured."""
        creds = cls._get_credentials()
        key_id = creds["key_id"]
        key_secret = creds["key_secret"]
        return bool(
            key_id and key_secret and
            not key_id.startswith("rzp_test_placeholder") and
            len(key_id) >= 10 and len(key_secret) >= 10
        )

    @classmethod
    def get_public_key_id(cls) -> str:
        """Return public Razorpay Key ID safe for frontend checkout."""
        creds = cls._get_credentials()
        return creds["key_id"] if cls.is_gateway_configured() else ""

    @classmethod
    def create_order(cls, user: User, db: Session) -> Dict[str, Any]:
        """
        Create a server-authenticated Razorpay payment order for PropPulse Pro.
        Never trusts client-supplied amount or plan.
        """
        if not cls.is_gateway_configured():
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail={
                    "code": "PAYMENT_GATEWAY_NOT_CONFIGURED",
                    "message": "Payment gateway not configured. PropPulse Pro subscription requires valid Razorpay credentials."
                }
            )

        creds = cls._get_credentials()
        key_id = creds["key_id"]
        key_secret = creds["key_secret"]

        receipt = f"sub_{user.id}_{int(time.time())}"
        order_data = {
            "amount": cls.PLAN_AMOUNT_PAISE,
            "currency": cls.CURRENCY,
            "receipt": receipt,
            "notes": {
                "user_id": str(user.id),
                "user_email": user.email,
                "plan": cls.PLAN_CODE
            }
        }

        try:
            if razorpay:
                client = razorpay.Client(auth=(key_id, key_secret))
                razorpay_order = client.order.create(data=order_data)
            else:
                import urllib.request
                import json
                import base64
                auth_str = base64.b64encode(f"{key_id}:{key_secret}".encode()).decode()
                req = urllib.request.Request(
                    "https://api.razorpay.com/v1/orders",
                    data=json.dumps(order_data).encode("utf-8"),
                    headers={
                        "Authorization": f"Basic {auth_str}",
                        "Content-Type": "application/json"
                    }
                )
                with urllib.request.urlopen(req, timeout=10) as resp:
                    razorpay_order = json.loads(resp.read().decode())
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Razorpay order creation failed: {str(e)}"
            )

        order_id = razorpay_order.get("id")

        # Create or update pending subscription record in DB
        pending_sub = Subscription(
            user_id=user.id,
            plan=cls.PLAN_CODE,
            plan_name=cls.PLAN_NAME,
            subscription_status="PENDING",
            status="PENDING",
            razorpay_order_id=order_id,
            plan_amount=cls.PLAN_AMOUNT_INR,
            currency=cls.CURRENCY,
            start_date=datetime.now(timezone.utc),
            end_date=None,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        db.add(pending_sub)
        db.commit()
        db.refresh(pending_sub)

        return {
            "order_id": order_id,
            "amount": cls.PLAN_AMOUNT_PAISE,
            "currency": cls.CURRENCY,
            "key_id": key_id,
            "plan": cls.PLAN_CODE,
            "plan_name": "PropPulse Pro",
            "plan_display_price": f"₹{int(cls.PLAN_AMOUNT_INR)}/month"
        }

    @classmethod
    def verify_payment(
        cls,
        user: User,
        order_id: str,
        payment_id: str,
        signature: str,
        db: Session
    ) -> Dict[str, Any]:
        """
        Verify Razorpay signature server-side using HMAC-SHA256 with key secret.
        Activates PRO subscription only after cryptographic proof.
        """
        creds = cls._get_credentials()
        key_secret = creds["key_secret"]
        if not key_secret:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail={"code": "PAYMENT_GATEWAY_NOT_CONFIGURED", "message": "Payment gateway not configured."}
            )

        # Cryptographic Signature Verification
        payload = f"{order_id}|{payment_id}"
        expected_signature = hmac.new(
            key_secret.encode("utf-8"),
            payload.encode("utf-8"),
            hashlib.sha256
        ).hexdigest()

        if not hmac.compare_digest(expected_signature, signature):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"code": "INVALID_SIGNATURE", "message": "Payment verification failed: Invalid signature."}
            )

        # Find the user's subscription record for this order
        sub = db.query(Subscription).filter(
            Subscription.user_id == user.id,
            Subscription.razorpay_order_id == order_id
        ).first()

        now = datetime.now(timezone.utc)
        end_date = now + timedelta(days=cls.DURATION_DAYS)

        if not sub:
            # Fallback: check if user has an existing subscription record to update
            sub = db.query(Subscription).filter(Subscription.user_id == user.id).first()
            if not sub:
                sub = Subscription(user_id=user.id)
                db.add(sub)

        # Activate PRO status
        sub.plan = cls.PLAN_CODE
        sub.plan_name = cls.PLAN_NAME
        sub.subscription_status = "ACTIVE"
        sub.status = "ACTIVE"
        sub.razorpay_order_id = order_id
        sub.razorpay_payment_id = payment_id
        sub.payment_reference = payment_id
        sub.plan_amount = cls.PLAN_AMOUNT_INR
        sub.currency = cls.CURRENCY
        sub.start_date = now
        sub.end_date = end_date
        sub.updated_at = now

        db.commit()
        db.refresh(sub)

        return {
            "status": "ok",
            "plan": "PRO",
            "subscription_status": "ACTIVE",
            "message": "PropPulse Pro subscription activated successfully!",
            "subscription": cls._format_subscription(sub, user)
        }

    @classmethod
    def verify_webhook(cls, raw_body: bytes, signature: str) -> bool:
        """Cryptographically verify Razorpay webhook signature."""
        creds = cls._get_credentials()
        webhook_secret = creds["webhook_secret"] or creds["key_secret"]
        if not webhook_secret or not signature:
            return False

        expected = hmac.new(
            webhook_secret.encode("utf-8"),
            raw_body,
            hashlib.sha256
        ).hexdigest()
        return hmac.compare_digest(expected, signature)

    @classmethod
    def process_webhook_event(cls, event_data: Dict[str, Any], db: Session) -> Dict[str, Any]:
        """Process verified Razorpay webhook payload for subscription state updates."""
        event_name = event_data.get("event")
        payload = event_data.get("payload", {})

        now = datetime.now(timezone.utc)

        if event_name in ("payment.captured", "order.paid"):
            payment_entity = payload.get("payment", {}).get("entity", {})
            order_id = payment_entity.get("order_id")
            payment_id = payment_entity.get("id")

            if order_id:
                sub = db.query(Subscription).filter(Subscription.razorpay_order_id == order_id).first()
                if sub:
                    sub.plan = cls.PLAN_CODE
                    sub.plan_name = cls.PLAN_NAME
                    sub.subscription_status = "ACTIVE"
                    sub.status = "ACTIVE"
                    sub.razorpay_payment_id = payment_id
                    sub.payment_reference = payment_id
                    sub.start_date = now
                    sub.end_date = now + timedelta(days=cls.DURATION_DAYS)
                    sub.updated_at = now
                    db.commit()
                    return {"status": "ok", "action": "subscription_activated", "order_id": order_id}

        elif event_name in ("subscription.cancelled", "payment.failed"):
            payment_entity = payload.get("payment", {}).get("entity", {})
            order_id = payment_entity.get("order_id")
            if order_id:
                sub = db.query(Subscription).filter(Subscription.razorpay_order_id == order_id).first()
                if sub:
                    sub.subscription_status = "CANCELLED"
                    sub.status = "CANCELLED"
                    sub.updated_at = now
                    db.commit()
                    return {"status": "ok", "action": "subscription_cancelled", "order_id": order_id}

        return {"status": "ok", "action": "ignored", "event": event_name}

    @classmethod
    def cancel_subscription(cls, user: User, db: Session) -> Dict[str, Any]:
        """Cancel an active subscription for the current user."""
        sub = db.query(Subscription).filter(
            Subscription.user_id == user.id,
            Subscription.subscription_status == "ACTIVE"
        ).first()

        if not sub:
            sub = db.query(Subscription).filter(
                Subscription.user_id == user.id,
                Subscription.status == "ACTIVE"
            ).first()

        if not sub:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No active subscription found to cancel."
            )

        sub.subscription_status = "CANCELLED"
        sub.status = "CANCELLED"
        sub.updated_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(sub)

        return {
            "status": "ok",
            "message": "Subscription cancelled successfully.",
            "subscription": cls._format_subscription(sub, user)
        }

    @classmethod
    def get_user_subscription(cls, user: User, db: Session) -> Dict[str, Any]:
        """Return comprehensive subscription profile for current authenticated user."""
        sub = db.query(Subscription).filter(
            Subscription.user_id == user.id
        ).order_by(Subscription.id.desc()).first()

        return cls._format_subscription(sub, user)

    @classmethod
    def _format_subscription(cls, sub: Optional[Subscription], user: User) -> Dict[str, Any]:
        """Format subscription record into standardized, non-sensitive dictionary."""
        is_pro = user.is_pro_active()
        plan = user.current_plan
        sub_status = user.subscription_status

        start_date = None
        end_date = None
        payment_ref = None
        order_id = None

        if sub:
            start_date = sub.start_date.isoformat() if sub.start_date else None
            end_date = sub.end_date.isoformat() if sub.end_date else None
            payment_ref = sub.razorpay_payment_id or sub.payment_reference
            order_id = sub.razorpay_order_id

        return {
            "user_id": user.id,
            "user_email": user.email,
            "user_name": user.full_name,
            "role": user.role,
            "plan": plan,
            "subscription_status": sub_status,
            "is_pro": is_pro,
            "is_active": is_pro,
            "plan_name": "PropPulse Pro" if plan == "PRO" else "Free Plan",
            "plan_amount": cls.PLAN_AMOUNT_INR,
            "currency": cls.CURRENCY,
            "start_date": start_date,
            "end_date": end_date,
            "payment_reference": payment_ref,
            "razorpay_payment_id": payment_ref,
            "order_id": order_id,
            "gateway_configured": cls.is_gateway_configured(),
            "razorpay_key_id": cls.get_public_key_id()
        }
