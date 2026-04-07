from datetime import datetime
from typing import Any, List, Optional

from pydantic import BaseModel, ConfigDict, model_validator


def _meta_coord(meta: Optional[dict[str, Any]], key: str) -> Optional[float]:
    if not meta or not isinstance(meta, dict):
        return None
    raw = meta.get(key)
    if raw is None:
        return None
    if isinstance(raw, (int, float)) and not isinstance(raw, bool):
        return float(raw)
    try:
        return float(str(raw).strip())
    except (TypeError, ValueError):
        return None


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
    model_config = ConfigDict(from_attributes=True)

    id: Optional[int] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None

    @model_validator(mode="after")
    def fill_coords_from_meta(self) -> "VehicleOut":
        meta = self.meta if isinstance(self.meta, dict) else None
        if self.latitude is None:
            self.latitude = _meta_coord(meta, "latitude")
        if self.longitude is None:
            self.longitude = _meta_coord(meta, "longitude")
        return self


class VehicleResponse(BaseModel):
    vehicle: VehicleOut


class VehiclesListResponse(BaseModel):
    data: List[VehicleOut]
    total: int
    limit: int
    offset: int
