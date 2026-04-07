from datetime import datetime
from typing import Any, List, Optional

from pydantic import BaseModel, Field


class OrderBase(BaseModel):
    uuid: Optional[str] = None
    public_id: Optional[str] = None
    company_uuid: Optional[str] = None
    internal_id: Optional[str] = None
    customer_uuid: Optional[str] = None
    customer_type: Optional[str] = None
    customer_display_name: Optional[str] = Field(
        default=None, description="Resolved from Contact in API responses; not persisted on Order row."
    )
    driver_assigned_uuid: Optional[str] = None
    vehicle_assigned_uuid: Optional[str] = None
    meta: Optional[dict[str, Any]] = None
    options: Optional[dict[str, Any]] = None
    dispatched: Optional[bool] = None
    dispatched_at: Optional[datetime] = None
    adhoc: Optional[bool] = None
    adhoc_distance: Optional[int] = None
    started: Optional[bool] = None
    started_at: Optional[datetime] = None
    distance: Optional[int] = None
    time: Optional[int] = None
    pod_required: Optional[bool] = None
    is_route_optimized: Optional[bool] = None
    pod_method: Optional[str] = None
    notes: Optional[str] = None
    scheduled_at: Optional[datetime] = None
    type: Optional[str] = None
    status: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class OrderCreate(BaseModel):
    type: str
    customer_uuid: str
    internal_id: Optional[str] = None
    notes: Optional[str] = None
    scheduled_at: Optional[datetime] = None
    meta: Optional[dict[str, Any]] = None
    options: Optional[dict[str, Any]] = None


class OrderUpdate(BaseModel):
    """Partial update. When `customer_uuid` is sent (including explicit null), it is validated; omit the field to leave the link unchanged."""

    customer_uuid: Optional[str] = None
    internal_id: Optional[str] = None
    notes: Optional[str] = None
    scheduled_at: Optional[datetime] = None
    status: Optional[str] = None
    type: Optional[str] = None
    meta: Optional[dict[str, Any]] = None
    options: Optional[dict[str, Any]] = None




class OrderOut(OrderBase):
    id: Optional[int] = None

    class Config:
        from_attributes = True


class OrderResponse(BaseModel):
    order: OrderOut


class OrdersResponse(BaseModel):
    orders: List[OrderOut]



