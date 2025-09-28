# app/schemas/vendor.py
from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

class VendorCreate(BaseModel):
    name: str
    email: Optional[EmailStr] = None

class VendorResponse(BaseModel):
    id: int
    name: str
    email: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True
