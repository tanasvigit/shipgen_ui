from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel


class CompanyBase(BaseModel):
    uuid: Optional[str] = None
    public_id: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    phone: Optional[str] = None
    website_url: Optional[str] = None
    currency: Optional[str] = None
    country: Optional[str] = None
    timezone: Optional[str] = None
    status: Optional[str] = None
    slug: Optional[str] = None
    options: Optional[dict[str, Any]] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class CompanyCreate(BaseModel):
    name: str
    description: Optional[str] = None
    phone: Optional[str] = None
    website_url: Optional[str] = None
    currency: Optional[str] = None
    country: Optional[str] = None
    timezone: Optional[str] = None


class CompanyUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    phone: Optional[str] = None
    website_url: Optional[str] = None
    currency: Optional[str] = None
    country: Optional[str] = None
    timezone: Optional[str] = None
    status: Optional[str] = None


class CompanyOut(CompanyBase):
    id: Optional[int] = None

    class Config:
        from_attributes = True



