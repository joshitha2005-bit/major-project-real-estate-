from typing import Generator, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.database import get_db
from app.models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")

def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
        
    user = db.query(User).filter(User.id == int(user_id)).first()
    if user is None:
        raise credentials_exception
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user account")
    return user

def get_current_user_optional(
    db: Session = Depends(get_db),
    token: Optional[str] = Depends(OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login", auto_error=False))
) -> Optional[User]:
    if not token:
        return None
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            return None
        return db.query(User).filter(User.id == int(user_id)).first()
    except Exception:
        return None

def get_current_user_with_role(required_role: str):
    def dependency(current_user: User = Depends(get_current_user)):
        if current_user.role != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Requires {required_role} role."
            )
        return current_user
    return dependency

def verify_pro_access(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> User:
    from app.models.subscription import Subscription
    from datetime import datetime, timezone
    sub = db.query(Subscription).filter(
        Subscription.user_id == current_user.id,
        Subscription.status == "ACTIVE"
    ).first()
    if not sub or (sub.end_date and sub.end_date.replace(tzinfo=timezone.utc) < datetime.now(timezone.utc)):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Pro Subscription required. Please upgrade to Pro for Rs.299/month."
        )
    return current_user

