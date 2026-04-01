from datetime import datetime
from typing import Any, List, Optional

from pydantic import BaseModel


class ServiceAreaBase(BaseModel):
    uuid: Optional[str] = None
    public_id: Optional[str] = None
    company_uuid: Optional[str] = None
    parent_uuid: Optional[str] = None
    name: Optional[str] = None
    type: Optional[str] = None
    country: Optional[str] = None
    border: Optional[dict[str, Any]] = None
    color: Optional[str] = None
    stroke_color: Optional[str] = None
    status: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class ServiceAreaCreate(BaseModel):
    name: str
    type: Optional[str] = None
    status: Optional[str] = None
    country: Optional[str] = None
    parent: Optional[str] = None  # public_id
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    location: Optional[dict[str, Any]] = None
    radius: Optional[int] = 500  # meters


class ServiceAreaUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = None
    status: Optional[str] = None
    country: Optional[str] = None
    parent: Optional[str] = None  # public_id
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    location: Optional[dict[str, Any]] = None
    radius: Optional[int] = 500  # meters




class ServiceAreaOut(ServiceAreaBase):
    id: Optional[int] = None

    class Config:
        from_attributes = True


class ServiceAreaResponse(BaseModel):
    service_area: ServiceAreaOut


class ServiceAreasResponse(BaseModel):
    service_areas: List[ServiceAreaOut]

