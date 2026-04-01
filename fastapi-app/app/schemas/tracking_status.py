from datetime import datetime
from typing import Any, List, Optional

from pydantic import BaseModel


class TrackingStatusBase(BaseModel):
    uuid: Optional[str] = None
    public_id: Optional[str] = None
    company_uuid: Optional[str] = None
    tracking_number_uuid: Optional[str] = None
    proof_uuid: Optional[str] = None
    meta: Optional[dict[str, Any]] = None
    status: Optional[str] = None
    details: Optional[str] = None
    code: Optional[str] = None
    city: Optional[str] = None
    province: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = None
    location: Optional[dict[str, Any]] = None
    latitude: Optional[str] = None
    longitude: Optional[str] = None
    completed: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class TrackingStatusCreate(BaseModel):
    tracking_number: Optional[str] = None  # public_id
    order: Optional[str] = None  # public_id (alternative to tracking_number)
    status: str
    details: Optional[str] = None
    code: Optional[str] = None
    city: Optional[str] = None
    province: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = None
    location: Optional[dict[str, Any]] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    meta: Optional[dict[str, Any]] = None


class TrackingStatusUpdate(BaseModel):
    status: Optional[str] = None
    details: Optional[str] = None
    code: Optional[str] = None
    city: Optional[str] = None
    province: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = None
    location: Optional[dict[str, Any]] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    meta: Optional[dict[str, Any]] = None




class TrackingStatusOut(TrackingStatusBase):
    id: Optional[int] = None

    class Config:
        from_attributes = True


class TrackingStatusResponse(BaseModel):
    tracking_status: TrackingStatusOut


class TrackingStatusesResponse(BaseModel):
    tracking_statuses: List[TrackingStatusOut]

