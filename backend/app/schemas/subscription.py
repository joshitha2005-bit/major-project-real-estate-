from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Dict, Any


class SubscriptionBase(BaseModel):
    plan_name: str = "PRO_299"
    status: str = "FREE"


class SubscriptionCreate(SubscriptionBase):
    payment_reference: Optional[str] = None
    razorpay_payment_id: Optional[str] = None
    duration_days: Optional[int] = 30


class SubscriptionOut(SubscriptionBase):
    id: int
    user_id: int
    plan: Optional[str] = "FREE"
    subscription_status: Optional[str] = "FREE"
    start_date: datetime
    end_date: Optional[datetime] = None
    payment_reference: Optional[str] = None
    razorpay_payment_id: Optional[str] = None

    class Config:
        from_attributes = True


class CreateOrderResponse(BaseModel):
    order_id: str
    amount: int
    currency: str
    key_id: str
    plan: str
    plan_name: str
    plan_display_price: str


class VerifyPaymentRequest(BaseModel):
    razorpay_order_id: str = Field(..., description="Razorpay order identifier")
    razorpay_payment_id: str = Field(..., description="Razorpay payment identifier")
    razorpay_signature: str = Field(..., description="Cryptographic HMAC-SHA256 signature")


class SubscriptionProfileResponse(BaseModel):
    user_id: int
    user_email: str
    user_name: str
    role: str
    plan: str
    subscription_status: str
    is_pro: bool
    is_active: bool = False
    plan_name: str
    plan_amount: float
    currency: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    payment_reference: Optional[str] = None
    razorpay_payment_id: Optional[str] = None
    order_id: Optional[str] = None
    gateway_configured: bool
    razorpay_key_id: str
