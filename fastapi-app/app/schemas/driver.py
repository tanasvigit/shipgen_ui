from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class DriverBase(BaseModel):
    uuid: Optional[str] = None
    public_id: Optional[str] = None
    company_uuid: Optional[str] = None
    user_uuid: Optional[str] = None
    vehicle_uuid: Optional[str] = None
    vendor_uuid: Optional[str] = None
    current_job_uuid: Optional[str] = None
    drivers_license_number: Optional[str] = None
    latitude: Optional[str] = None
    longitude: Optional[str] = None
    heading: Optional[str] = None
    speed: Optional[str] = None
    altitude: Optional[str] = None
    country: Optional[str] = None
    city: Optional[str] = None
    currency: Optional[str] = None
    online: Optional[int] = None
    status: Optional[str] = None
    slug: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class DriverCreate(BaseModel):
    company_uuid: Optional[str] = None
    user_uuid: Optional[str] = None
    drivers_license_number: Optional[str] = None
    status: Optional[str] = "active"


class DriverUpdate(BaseModel):
    drivers_license_number: Optional[str] = None
    status: Optional[str] = None
    online: Optional[int] = None
    latitude: Optional[str] = None
    longitude: Optional[str] = None
    heading: Optional[str] = None
    speed: Optional[str] = None
    altitude: Optional[str] = None




class DriverOut(DriverBase):
    id: Optional[int] = None

    class Config:
        from_attributes = True


class DriverResponse(BaseModel):
    driver: DriverOut


class DriversResponse(BaseModel):
    drivers: List[DriverOut]



