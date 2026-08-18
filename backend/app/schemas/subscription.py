from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class SubscriptionBase(BaseModel):
    plan_name: str = "PRO_299"
    status: str = "FREE"

class SubscriptionCreate(SubscriptionBase):
    payment_reference: Optional[str] = None
    duration_days: Optional[int] = 30

class SubscriptionOut(SubscriptionBase):
    id: int
    user_id: int
    start_date: datetime
    end_date: Optional[datetime]
    payment_reference: Optional[str]

    class Config:
        from_attributes = True
