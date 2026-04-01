from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    uuid: Optional[str] = None
    company_uuid: Optional[str] = None
    public_id: Optional[str] = None
    name: Optional[str] = None
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    country: Optional[str] = None
    timezone: Optional[str] = None
    avatar_url: Optional[str] = None
    meta: Optional[dict[str, Any]] = None
    type: Optional[str] = None
    locale: Optional[str] = None
    company_name: Optional[str] = None
    company_onboarding_completed: Optional[bool] = None
    session_status: Optional[str] = None
    is_admin: Optional[bool] = None
    is_online: Optional[bool] = None
    ip_address: Optional[str] = None
    date_of_birth: Optional[str] = None
    email_verified_at: Optional[datetime] = None
    phone_verified_at: Optional[datetime] = None
    last_seen_at: Optional[datetime] = None
    last_login: Optional[datetime | str] = None
    status: Optional[str] = None
    slug: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class UserCreate(BaseModel):
    name: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    password: Optional[str] = None
    company_uuid: Optional[str] = None
    timezone: Optional[str] = None
    country: Optional[str] = None


class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    timezone: Optional[str] = None
    country: Optional[str] = None
    status: Optional[str] = None


class UserOut(UserBase):
    id: Optional[int] = None

    class Config:
        from_attributes = True



