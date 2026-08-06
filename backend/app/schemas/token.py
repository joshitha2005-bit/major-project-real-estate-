from pydantic import BaseModel
from typing import Optional
from app.schemas.user import UserOut

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut

class TokenData(BaseModel):
    user_id: Optional[int] = None
