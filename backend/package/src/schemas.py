from pydantic import BaseModel, EmailStr, constr, conint, validator
from typing import Optional, List
from datetime import datetime
import re
import bleach

class SubmissionBase(BaseModel):
    full_name: constr(strip_whitespace=True, min_length=1, max_length=255)
    email: EmailStr
    phone_number: constr(strip_whitespace=True, min_length=7, max_length=20)
    age: conint(ge=18, le=120)
    address: Optional[str] = None
    preferred_contact: constr(strip_whitespace=True)

    @validator('full_name')
    def sanitize_full_name(cls, v):
        v = bleach.clean(v, strip=True)
        if not re.match(r"^[A-Za-z\s\.'-]+$", v):
            raise ValueError("Full name contains invalid characters")
        return v

    @validator('email')
    def sanitize_email(cls, v):
        v = bleach.clean(v, strip=True)
        return v

    @validator('phone_number')
    def validate_phone_number(cls, v):
        v = bleach.clean(v, strip=True)
        # Simple international phone regex, adjust as needed
        if not re.match(r"^\+?\d{7,20}$", v):
            raise ValueError("Invalid phone number format")
        return v

    @validator('address')
    def sanitize_address(cls, v):
        if v:
            return bleach.clean(v, strip=True)
        return v

    @validator('preferred_contact')
    def sanitize_preferred_contact(cls, v):
        v = bleach.clean(v, strip=True)
        if v not in ('Email', 'Phone', 'Both'):
            raise ValueError("preferred_contact must be 'Email', 'Phone', or 'Both'")
        return v

class SubmissionCreate(SubmissionBase):
    pass

class SubmissionUpdate(SubmissionBase):
    pass

class SubmissionOut(SubmissionBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class PaginatedSubmissions(BaseModel):
    total: int
    items: List[SubmissionOut] 