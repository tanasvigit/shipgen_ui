from datetime import datetime
from typing import Any, List, Optional

from pydantic import BaseModel


class VehicleBase(BaseModel):
    uuid: Optional[str] = None
    public_id: Optional[str] = None
    company_uuid: Optional[str] = None
    vendor_uuid: Optional[str] = None
    photo_uuid: Optional[str] = None
    avatar_url: Optional[str] = None
    make: Optional[str] = None
    model: Optional[str] = None
    year: Optional[str] = None
    trim: Optional[str] = None
    type: Optional[str] = None
    plate_number: Optional[str] = None
    vin: Optional[str] = None
    vin_data: Optional[dict[str, Any]] = None
    meta: Optional[dict[str, Any]] = None
    status: Optional[str] = None
    slug: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class VehicleCreate(BaseModel):
    company_uuid: Optional[str] = None
    vendor_uuid: Optional[str] = None
    make: Optional[str] = None
    model: Optional[str] = None
    year: Optional[str] = None
    trim: Optional[str] = None
    type: Optional[str] = None
    plate_number: Optional[str] = None
    vin: Optional[str] = None
    status: Optional[str] = "active"


class VehicleUpdate(BaseModel):
    vendor_uuid: Optional[str] = None
    make: Optional[str] = None
    model: Optional[str] = None
    year: Optional[str] = None
    trim: Optional[str] = None
    type: Optional[str] = None
    plate_number: Optional[str] = None
    vin: Optional[str] = None
    status: Optional[str] = None
    meta: Optional[dict[str, Any]] = None




class VehicleOut(VehicleBase):
    id: Optional[int] = None

    class Config:
        from_attributes = True


class VehicleResponse(BaseModel):
    vehicle: VehicleOut


class VehiclesResponse(BaseModel):
    vehicles: List[VehicleOut]



