from datetime import datetime
from typing import Any, List, Optional

from pydantic import BaseModel, ConfigDict, EmailStr


class ContactBase(BaseModel):
    uuid: Optional[str] = None
    public_id: Optional[str] = None
    company_uuid: Optional[str] = None
    user_uuid: Optional[str] = None
    name: Optional[str] = None
    title: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    type: Optional[str] = None
    slug: Optional[str] = None
    meta: Optional[dict[str, Any]] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class ContactCreate(BaseModel):
    name: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    type: Optional[str] = "contact"
    title: Optional[str] = None
    meta: Optional[dict[str, Any]] = None


class ContactUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    type: Optional[str] = None
    title: Optional[str] = None
    meta: Optional[dict[str, Any]] = None


class ContactOut(ContactBase):
    """Read model: `email` is plain str so invalid/legacy values in DB cannot break responses."""

    id: Optional[int] = None
    email: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class ContactResponse(BaseModel):
    contact: ContactOut


class ContactsResponse(BaseModel):
    contacts: List[ContactOut]



