from datetime import datetime
from typing import Any, List, Optional

from pydantic import BaseModel


class ZoneBase(BaseModel):
    uuid: Optional[str] = None
    public_id: Optional[str] = None
    company_uuid: Optional[str] = None
    service_area_uuid: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    border: Optional[dict[str, Any]] = None
    color: Optional[str] = None
    stroke_color: Optional[str] = None
    status: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class ZoneCreate(BaseModel):
    name: str
    description: Optional[str] = None
    border: Optional[dict[str, Any]] = None
    status: Optional[str] = None
    color: Optional[str] = None
    stroke_color: Optional[str] = None
    service_area: Optional[str] = None  # public_id
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    location: Optional[dict[str, Any]] = None
    radius: Optional[int] = 500  # meters


class ZoneUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    border: Optional[dict[str, Any]] = None
    status: Optional[str] = None
    color: Optional[str] = None
    stroke_color: Optional[str] = None
    service_area: Optional[str] = None  # public_id
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    location: Optional[dict[str, Any]] = None
    radius: Optional[int] = 500  # meters




class ZoneOut(ZoneBase):
    id: Optional[int] = None

    class Config:
        from_attributes = True


class ZoneResponse(BaseModel):
    zone: ZoneOut


class ZonesResponse(BaseModel):
    zones: List[ZoneOut]

