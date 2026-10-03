from datetime import datetime, timezone
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.subscription import Subscription


def require_pro_subscription(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> User:
    """
    Reusable FastAPI dependency that guards premium PropPulse Pro endpoints.
    Allows administrators and active Pro subscribers within their valid subscription window.
    Blocks FREE users with HTTP 403 Forbidden and machine-readable payload:
    {
      "code": "PRO_REQUIRED",
      "message": "This feature requires an active PropPulse Pro subscription."
    }
    """
    # Administrators automatically inherit full platform feature privileges
    if current_user.role == "ADMIN":
        return current_user

    now = datetime.now(timezone.utc)

    # Check for active subscription
    active_sub = db.query(Subscription).filter(
        Subscription.user_id == current_user.id,
        Subscription.subscription_status == "ACTIVE"
    ).first()

    # Fallback to legacy status column if subscription_status was not set
    if not active_sub:
        active_sub = db.query(Subscription).filter(
            Subscription.user_id == current_user.id,
            Subscription.status == "ACTIVE"
        ).first()

    if active_sub:
        # Check plan
        plan = (getattr(active_sub, "plan", "") or getattr(active_sub, "plan_name", "") or "").upper()
        if "PRO" in plan or plan == "PROPULSE_PRO_299":
            # Check end_date validity
            if not active_sub.end_date:
                return current_user
            end_dt = active_sub.end_date if active_sub.end_date.tzinfo else active_sub.end_date.replace(tzinfo=timezone.utc)
            if end_dt > now:
                return current_user

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail={
            "code": "PRO_REQUIRED",
            "message": "This feature requires an active PropPulse Pro subscription."
        }
    )
