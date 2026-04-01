from datetime import datetime
from typing import Any, List, Optional

from pydantic import BaseModel


class PayloadBase(BaseModel):
    uuid: Optional[str] = None
    public_id: Optional[str] = None
    company_uuid: Optional[str] = None
    pickup_uuid: Optional[str] = None
    dropoff_uuid: Optional[str] = None
    return_uuid: Optional[str] = None
    current_waypoint_uuid: Optional[str] = None
    provider: Optional[str] = None
    payment_method: Optional[str] = None
    cod_amount: Optional[int] = None
    cod_currency: Optional[str] = None
    cod_payment_method: Optional[str] = None
    type: Optional[str] = None
    meta: Optional[dict[str, Any]] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class PayloadCreate(BaseModel):
    type: Optional[str] = None
    provider: Optional[str] = None
    meta: Optional[dict[str, Any]] = None
    cod_amount: Optional[int] = None
    cod_currency: Optional[str] = None
    cod_payment_method: Optional[str] = None
    entities: Optional[list[dict[str, Any]]] = None
    waypoints: Optional[list[dict[str, Any]]] = None
    pickup: Optional[dict[str, Any]] = None
    dropoff: Optional[dict[str, Any]] = None
    return_location: Optional[dict[str, Any]] = None


class PayloadUpdate(BaseModel):
    type: Optional[str] = None
    provider: Optional[str] = None
    meta: Optional[dict[str, Any]] = None
    cod_amount: Optional[int] = None
    cod_currency: Optional[str] = None
    cod_payment_method: Optional[str] = None
    entities: Optional[list[dict[str, Any]]] = None
    waypoints: Optional[list[dict[str, Any]]] = None
    pickup: Optional[dict[str, Any]] = None
    dropoff: Optional[dict[str, Any]] = None
    return_location: Optional[dict[str, Any]] = None




class PayloadOut(PayloadBase):
    id: Optional[int] = None
    pickup_name: Optional[str] = None
    dropoff_name: Optional[str] = None
    return_name: Optional[str] = None
    entities: Optional[list[dict[str, Any]]] = None
    waypoints: Optional[list[dict[str, Any]]] = None
    pickup: Optional[dict[str, Any]] = None
    dropoff: Optional[dict[str, Any]] = None
    return_location: Optional[dict[str, Any]] = None

    class Config:
        from_attributes = True


class PayloadResponse(BaseModel):
    payload: PayloadOut


class PayloadsResponse(BaseModel):
    payloads: List[PayloadOut]

