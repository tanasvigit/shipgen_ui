from datetime import datetime
from typing import Any, List, Optional

from pydantic import BaseModel


class PlaceBase(BaseModel):
    uuid: Optional[str] = None
    public_id: Optional[str] = None
    company_uuid: Optional[str] = None
    owner_uuid: Optional[str] = None
    owner_type: Optional[str] = None
    name: Optional[str] = None
    street1: Optional[str] = None
    street2: Optional[str] = None
    city: Optional[str] = None
    province: Optional[str] = None
    postal_code: Optional[str] = None
    neighborhood: Optional[str] = None
    district: Optional[str] = None
    building: Optional[str] = None
    security_access_code: Optional[str] = None
    country: Optional[str] = None
    latitude: Optional[str] = None
    longitude: Optional[str] = None
    meta: Optional[dict[str, Any]] = None
    phone: Optional[str] = None
    remarks: Optional[str] = None
    type: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class PlaceCreate(BaseModel):
    name: Optional[str] = None
    street1: Optional[str] = None
    street2: Optional[str] = None
    city: Optional[str] = None
    province: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = None
    latitude: Optional[str] = None
    longitude: Optional[str] = None
    phone: Optional[str] = None
    type: Optional[str] = None
    meta: Optional[dict[str, Any]] = None


class PlaceUpdate(BaseModel):
    name: Optional[str] = None
    street1: Optional[str] = None
    street2: Optional[str] = None
    city: Optional[str] = None
    province: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = None
    latitude: Optional[str] = None
    longitude: Optional[str] = None
    phone: Optional[str] = None
    type: Optional[str] = None
    meta: Optional[dict[str, Any]] = None




class PlaceOut(PlaceBase):
    id: Optional[int] = None

    class Config:
        from_attributes = True


class PlaceResponse(BaseModel):
    place: PlaceOut


class PlacesResponse(BaseModel):
    places: List[PlaceOut]



