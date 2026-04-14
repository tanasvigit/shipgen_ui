from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field


TripStatus = Literal["PLANNED", "IN_PROGRESS", "COMPLETED"]
TripOrderStatus = Literal["LOADED", "IN_TRANSIT", "DELIVERED"]
StopType = Literal["PICKUP", "DROPOFF"]


class TripStopIn(BaseModel):
    location_name: str = Field(min_length=2, max_length=255)
    type: StopType
    sequence: int = Field(ge=1)


class CreateTripRequest(BaseModel):
    vehicle_id: str
    driver_id: str
    start_location: str = Field(min_length=2, max_length=255)
    end_location: str = Field(min_length=2, max_length=255)
    total_capacity: int = Field(gt=0)
    stops: list[TripStopIn] = Field(default_factory=list)


class AssignTripOrderRequest(BaseModel):
    order_id: str
    pickup_location: str = Field(min_length=2, max_length=255)
    drop_location: str = Field(min_length=2, max_length=255)
    load_units: int = Field(default=1, gt=0)


class StartTripRequest(BaseModel):
    pass


class UpdateTripLocationRequest(BaseModel):
    current_lat: float
    current_lng: float


class StopPickupIn(BaseModel):
    order_id: str
    pickup_location: str = Field(min_length=2, max_length=255)
    drop_location: str = Field(min_length=2, max_length=255)
    load_units: int = Field(default=1, gt=0)


class CompleteStopRequest(BaseModel):
    stop_sequence: int = Field(ge=1)
    new_pickups: list[StopPickupIn] = Field(default_factory=list)


class TripOrderOut(BaseModel):
    order_id: int
    pickup_location: str
    drop_location: str
    status: TripOrderStatus
    load_units: int


class TripStopOut(BaseModel):
    location_name: str
    type: StopType
    sequence: int
    is_completed: bool = False
    completed_at: Optional[datetime] = None


class TripEventOut(BaseModel):
    event_type: str
    metadata: Optional[dict] = None
    created_at: Optional[datetime] = None


class TripDashboardOut(BaseModel):
    total_capacity: int
    current_load: int
    available_capacity: int
    delivered_orders_count: int
    pending_orders_count: int


class TripOut(BaseModel):
    id: int
    uuid: Optional[str] = None
    public_id: Optional[str] = None
    vehicle_id: str
    driver_id: str
    vehicle_plate_number: Optional[str] = None
    driver_name: Optional[str] = None
    start_location: str
    end_location: str
    status: TripStatus
    total_capacity: int
    current_load: int
    available_capacity: int
    current_lat: Optional[float] = None
    current_lng: Optional[float] = None
    last_location_update: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    orders: list[TripOrderOut]
    stops: list[TripStopOut]
    events: list[TripEventOut] = Field(default_factory=list)
    dashboard: TripDashboardOut


class TripResponse(BaseModel):
    trip: TripOut


class TripsResponse(BaseModel):
    trips: list[TripOut]
