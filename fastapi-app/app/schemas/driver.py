from datetime import datetime
from typing import Any, List, Optional

from pydantic import BaseModel, ConfigDict, field_validator


def _coerce_optional_float(v: Any) -> Optional[float]:
    if v is None:
        return None
    if isinstance(v, (int, float)) and not isinstance(v, bool):
        return float(v)
    s = str(v).strip()
    if not s:
        return None
    try:
        return float(s)
    except ValueError:
        return None


class DriverBase(BaseModel):
    uuid: Optional[str] = None
    public_id: Optional[str] = None
    company_uuid: Optional[str] = None
    user_uuid: Optional[str] = None
    vehicle_uuid: Optional[str] = None
    vendor_uuid: Optional[str] = None
    current_job_uuid: Optional[str] = None
    drivers_license_number: Optional[str] = None
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
    user_uuid: Optional[str] = None
    drivers_license_number: Optional[str] = None
    status: Optional[str] = None
    online: Optional[int] = None
    latitude: Optional[str] = None
    longitude: Optional[str] = None
    heading: Optional[str] = None
    speed: Optional[str] = None
    altitude: Optional[str] = None


class DriverOut(DriverBase):
    """API driver shape; latitude/longitude are always floats or null in JSON."""

    model_config = ConfigDict(from_attributes=True)

    id: Optional[int] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None

    @field_validator("latitude", "longitude", mode="before")
    @classmethod
    def _coerce_lat_lng(cls, v: Any) -> Optional[float]:
        return _coerce_optional_float(v)


class DriverResponse(BaseModel):
    driver: DriverOut


class DriversListResponse(BaseModel):
    data: List[DriverOut]
    total: int
    limit: int
    offset: int
