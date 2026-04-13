from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


# Lowercase statuses align with fleetops / dashboard lifecycle.
ORDER_CREATED = "created"
ASSIGNED = "assigned"
IN_PROGRESS = "in_progress"


class FleetCustomerOrderCreate(BaseModel):
    internal_id: Optional[str] = Field(default=None, max_length=255)
    pickup_location: str = Field(min_length=3, max_length=255)
    drop_location: str = Field(min_length=3, max_length=255)
    goods_description: str = Field(min_length=3, max_length=1000)


class OrderAssignmentRequest(BaseModel):
    driver_id: str
    vehicle_id: str


class TripStartRequest(BaseModel):
    order_id: str
    current_location: Optional[dict] = None


class DriverSummary(BaseModel):
    uuid: Optional[str] = None
    public_id: Optional[str] = None
    user_uuid: Optional[str] = None
    status: Optional[str] = None


class VehicleSummary(BaseModel):
    uuid: Optional[str] = None
    public_id: Optional[str] = None
    make: Optional[str] = None
    model: Optional[str] = None
    plate_number: Optional[str] = None
    status: Optional[str] = None


class TripSummary(BaseModel):
    id: int
    status: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    current_location: Optional[dict] = None


class FleetCustomerOrderOut(BaseModel):
    id: int
    uuid: Optional[str] = None
    public_id: Optional[str] = None
    status: Optional[str] = None
    type: Optional[str] = None
    internal_id: Optional[str] = None
    customer_uuid: Optional[str] = None
    customer_type: Optional[str] = None
    customer_display_name: Optional[str] = None
    created_by: Optional[str] = None
    created_by_display_name: Optional[str] = None
    notes: Optional[str] = None
    scheduled_at: Optional[datetime] = None
    driver_assigned_uuid: Optional[str] = None
    vehicle_assigned_uuid: Optional[str] = None
    meta: Optional[dict] = None
    options: Optional[dict] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    driver: Optional[DriverSummary] = None
    vehicle: Optional[VehicleSummary] = None
    trip: Optional[TripSummary] = None

    class Config:
        from_attributes = True


class FleetCustomerOrdersResponse(BaseModel):
    orders: list[FleetCustomerOrderOut]


class FleetCustomerOrderResponse(BaseModel):
    order: FleetCustomerOrderOut
