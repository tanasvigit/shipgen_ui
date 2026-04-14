from datetime import datetime
from typing import Optional

from sqlalchemy import JSON, DateTime, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class DispatchTrip(Base):
    __tablename__ = "dispatch_trips"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    uuid: Mapped[Optional[str]] = mapped_column(String(36), unique=True, index=True, nullable=True)
    public_id: Mapped[Optional[str]] = mapped_column(String(191), unique=True, index=True, nullable=True)
    company_uuid: Mapped[str] = mapped_column(String(36), index=True, nullable=False)
    vehicle_uuid: Mapped[str] = mapped_column(String(36), index=True, nullable=False)
    driver_uuid: Mapped[str] = mapped_column(String(36), index=True, nullable=False)
    start_location: Mapped[str] = mapped_column(String(255), nullable=False)
    end_location: Mapped[str] = mapped_column(String(255), nullable=False)
    total_capacity: Mapped[int] = mapped_column(Integer, nullable=False)
    current_load: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    available_capacity: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    status: Mapped[str] = mapped_column(String(32), index=True, nullable=False, default="PLANNED")
    current_lat: Mapped[Optional[float]] = mapped_column(nullable=True)
    current_lng: Mapped[Optional[float]] = mapped_column(nullable=True)
    last_location_update: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime, index=True, default=datetime.utcnow)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class DispatchTripOrder(Base):
    __tablename__ = "dispatch_trip_orders"
    __table_args__ = (
        UniqueConstraint("trip_id", "order_id", name="uq_dispatch_trip_order"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    trip_id: Mapped[int] = mapped_column(Integer, ForeignKey("dispatch_trips.id"), index=True, nullable=False)
    order_id: Mapped[int] = mapped_column(Integer, ForeignKey("orders.id"), index=True, nullable=False)
    pickup_location: Mapped[str] = mapped_column(String(255), nullable=False)
    drop_location: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(32), index=True, nullable=False, default="LOADED")
    load_units: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime, index=True, default=datetime.utcnow)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class DispatchTripStop(Base):
    __tablename__ = "dispatch_trip_stops"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    trip_id: Mapped[int] = mapped_column(Integer, ForeignKey("dispatch_trips.id"), index=True, nullable=False)
    location_name: Mapped[str] = mapped_column(String(255), nullable=False)
    type: Mapped[str] = mapped_column(String(16), nullable=False)  # PICKUP | DROPOFF
    sequence: Mapped[int] = mapped_column(Integer, nullable=False)
    is_completed: Mapped[bool] = mapped_column(nullable=False, default=False)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime, index=True, default=datetime.utcnow)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class DispatchTripEvent(Base):
    __tablename__ = "dispatch_trip_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    trip_id: Mapped[int] = mapped_column(Integer, ForeignKey("dispatch_trips.id"), index=True, nullable=False)
    event_type: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    event_metadata: Mapped[Optional[dict]] = mapped_column("metadata", JSON, nullable=True)
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime, index=True, default=datetime.utcnow)
