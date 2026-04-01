from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class FleetBase(BaseModel):
    uuid: Optional[str] = None
    public_id: Optional[str] = None
    company_uuid: Optional[str] = None
    service_area_uuid: Optional[str] = None
    zone_uuid: Optional[str] = None
    image_uuid: Optional[str] = None
    name: Optional[str] = None
    color: Optional[str] = None
    task: Optional[str] = None
    status: Optional[str] = None
    slug: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class FleetCreate(BaseModel):
    name: str
    service_area: Optional[str] = None  # public_id
    color: Optional[str] = None
    task: Optional[str] = None
    status: Optional[str] = None


class FleetUpdate(BaseModel):
    name: Optional[str] = None
    service_area: Optional[str] = None  # public_id
    color: Optional[str] = None
    task: Optional[str] = None
    status: Optional[str] = None




class FleetOut(FleetBase):
    id: Optional[int] = None

    class Config:
        from_attributes = True


class FleetResponse(BaseModel):
    fleet: FleetOut


class FleetsResponse(BaseModel):
    fleets: List[FleetOut]

