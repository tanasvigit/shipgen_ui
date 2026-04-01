from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class TrackingNumberBase(BaseModel):
    uuid: Optional[str] = None
    public_id: Optional[str] = None
    company_uuid: Optional[str] = None
    owner_uuid: Optional[str] = None
    owner_type: Optional[str] = None
    status_uuid: Optional[str] = None
    tracking_number: Optional[str] = None
    region: Optional[str] = None
    type: Optional[str] = None
    qr_code: Optional[str] = None
    barcode: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class TrackingNumberCreate(BaseModel):
    region: Optional[str] = None
    type: Optional[str] = None
    owner: Optional[str] = None  # public_id (order or entity)




class TrackingNumberOut(TrackingNumberBase):
    id: Optional[int] = None

    class Config:
        from_attributes = True


class TrackingNumberResponse(BaseModel):
    tracking_number: TrackingNumberOut


class TrackingNumbersResponse(BaseModel):
    tracking_numbers: List[TrackingNumberOut]

