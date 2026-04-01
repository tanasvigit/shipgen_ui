from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel


class AssignOrderRequest(BaseModel):
    driver_id: Optional[str] = None
    driver_uuid: Optional[str] = None
    vehicle_id: Optional[str] = None
    vehicle_uuid: Optional[str] = None
    mode: str = "auto"  # auto | manual
    note: Optional[str] = None


class TransitionOrderRequest(BaseModel):
    to_status: str
    note: Optional[str] = None
    meta: Optional[dict[str, Any]] = None


class CreateExceptionRequest(BaseModel):
    title: str
    category: str = "operations"
    type: str = "delivery_exception"
    report: str
    priority: str = "medium"
    status: str = "open"
    reassign_driver_uuid: Optional[str] = None
    meta: Optional[dict[str, Any]] = None


class OrderEventOut(BaseModel):
    uuid: Optional[str] = None
    event_type: str
    from_status: Optional[str] = None
    to_status: Optional[str] = None
    actor_uuid: Optional[str] = None
    payload: Optional[dict[str, Any]] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

