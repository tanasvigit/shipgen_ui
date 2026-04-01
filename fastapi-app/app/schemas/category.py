from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel


class CategoryBase(BaseModel):
    uuid: Optional[str] = None
    public_id: Optional[str] = None
    parent_uuid: Optional[str] = None
    owner_uuid: Optional[str] = None
    owner_type: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    icon: Optional[str] = None
    icon_color: Optional[str] = None
    slug: Optional[str] = None
    tags: Optional[list[str]] = None
    translations: Optional[dict[str, Any]] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class CategoryOut(CategoryBase):
    id: Optional[str] = None  # Using public_id as id
    icon_url: Optional[str] = None
    products: Optional[list[dict[str, Any]]] = None
    stores: Optional[list[dict[str, Any]]] = None

    class Config:
        from_attributes = True

