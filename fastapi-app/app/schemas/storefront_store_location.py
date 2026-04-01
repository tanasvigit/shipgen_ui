from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel


class StoreLocationBase(BaseModel):
    uuid: Optional[str] = None
    public_id: Optional[str] = None
    store_uuid: Optional[str] = None
    place_uuid: Optional[str] = None
    name: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class StoreLocationOut(StoreLocationBase):
    id: Optional[int] = None
    address: Optional[str] = None
    place: Optional[dict[str, Any]] = None
    hours: Optional[list[dict[str, Any]]] = None

    class Config:
        from_attributes = True

