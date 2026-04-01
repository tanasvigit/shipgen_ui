from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel


class FoodTruckBase(BaseModel):
    uuid: Optional[str] = None
    public_id: Optional[str] = None
    vehicle_uuid: Optional[str] = None
    store_uuid: Optional[str] = None
    company_uuid: Optional[str] = None
    service_area_uuid: Optional[str] = None
    zone_uuid: Optional[str] = None
    status: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class FoodTruckOut(FoodTruckBase):
    id: Optional[int] = None
    location: Optional[dict[str, Any]] = None

    class Config:
        from_attributes = True

