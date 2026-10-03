from fastapi import APIRouter, Depends, HTTPException, Header, Request, status
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional

from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.subscription import (
    CreateOrderResponse,
    VerifyPaymentRequest,
    SubscriptionProfileResponse
)
from app.services.subscription_service import SubscriptionService

router = APIRouter()


@router.get("/config")
def get_subscription_config():
    """
    Public configuration endpoint reporting whether Razorpay is configured
    and providing the public Razorpay Key ID for client checkout.
    Never exposes secrets.
    """
    return {
        "gateway_configured": SubscriptionService.is_gateway_configured(),
        "razorpay_key_id": SubscriptionService.get_public_key_id(),
        "plan_code": SubscriptionService.PLAN_CODE,
        "plan_name": "PropPulse Pro",
        "plan_amount_inr": SubscriptionService.PLAN_AMOUNT_INR,
        "currency": SubscriptionService.CURRENCY,
        "display_price": f"₹{int(SubscriptionService.PLAN_AMOUNT_INR)}/month"
    }


@router.get("/me", response_model=SubscriptionProfileResponse)
def get_my_subscription(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get current authenticated user's subscription profile, plan, and active status.
    """
    return SubscriptionService.get_user_subscription(current_user, db)


@router.post("/create-order", response_model=CreateOrderResponse)
def create_subscription_order(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Initiate a server-authenticated order for PropPulse Pro (₹299/mo).
    Plan amount and currency are strictly enforced server-side.
    """
    return SubscriptionService.create_order(current_user, db)


@router.post("/verify-payment")
def verify_subscription_payment(
    payload: VerifyPaymentRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Verify payment signature cryptographically using Razorpay secret.
    Activates PRO subscription only upon successful mathematical verification.
    """
    return SubscriptionService.verify_payment(
        user=current_user,
        order_id=payload.razorpay_order_id,
        payment_id=payload.razorpay_payment_id,
        signature=payload.razorpay_signature,
        db=db
    )


@router.post("/webhook")
async def razorpay_webhook(
    request: Request,
    x_razorpay_signature: Optional[str] = Header(None, alias="X-Razorpay-Signature"),
    db: Session = Depends(get_db)
):
    """
    Public Razorpay webhook endpoint for asynchronous payment and subscription lifecycle events.
    Verifies authenticity using webhook secret.
    """
    if not x_razorpay_signature:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing X-Razorpay-Signature header."
        )

    body = await request.body()
    if not SubscriptionService.verify_webhook(body, x_razorpay_signature):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid webhook signature."
        )

    import json
    try:
        event_data = json.loads(body.decode("utf-8"))
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Malformed JSON.")

    return SubscriptionService.process_webhook_event(event_data, db)


@router.post("/cancel")
def cancel_subscription(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Cancel an active PropPulse Pro subscription for the current user.
    """
    return SubscriptionService.cancel_subscription(current_user, db)
