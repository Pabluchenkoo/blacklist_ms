from pydantic import BaseModel, EmailStr, constr
from typing import Optional
from uuid import UUID

class BlacklistCreate(BaseModel):
    email: EmailStr
    app_uuid: UUID
    blocked_reason: Optional[constr(max_length=255)]

class BlacklistResponse(BaseModel):
    email: EmailStr
    blocked_reason: Optional[str]
    blacklisted: bool
