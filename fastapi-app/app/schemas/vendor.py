from datetime import datetime
from typing import Any, List, Optional

from pydantic import BaseModel, EmailStr


class VendorBase(BaseModel):
    uuid: Optional[str] = None
    public_id: Optional[str] = None
    company_uuid: Optional[str] = None
    place_uuid: Optional[str] = None
    name: Optional[str] = None
    internal_id: Optional[str] = None
    business_id: Optional[str] = None
    connected: Optional[int] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    website_url: Optional[str] = None
    country: Optional[str] = None
    meta: Optional[dict[str, Any]] = None
    type: Optional[str] = None
    status: Optional[str] = None
    slug: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class VendorCreate(BaseModel):
    name: str
    type: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    meta: Optional[dict[str, Any]] = None


class VendorUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    meta: Optional[dict[str, Any]] = None




class VendorOut(VendorBase):
    id: Optional[int] = None

    class Config:
        from_attributes = True


class VendorResponse(BaseModel):
    vendor: VendorOut


class VendorsResponse(BaseModel):
    vendors: List[VendorOut]



