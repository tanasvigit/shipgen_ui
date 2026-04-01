from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel


class StoreBase(BaseModel):
    uuid: Optional[str] = None
    public_id: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None
    facebook: Optional[str] = None
    instagram: Optional[str] = None
    twitter: Optional[str] = None
    tags: Optional[list[str]] = None
    currency: Optional[str] = None
    timezone: Optional[str] = None
    online: Optional[bool] = True
    slug: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class StoreOut(StoreBase):
    id: Optional[int] = None
    logo_url: Optional[str] = None
    backdrop_url: Optional[str] = None
    rating: Optional[float] = None

    class Config:
        from_attributes = True

