from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, Integer, String, JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    _key: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    uuid: Mapped[Optional[str]] = mapped_column(String(191), index=True, unique=False)
    public_id: Mapped[Optional[str]] = mapped_column(String(191), index=True, unique=False)
    company_uuid: Mapped[Optional[str]] = mapped_column(String(36), index=True)
    internal_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    customer_uuid: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    customer_type: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    driver_assigned_uuid: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    vehicle_assigned_uuid: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    meta: Mapped[Optional[dict]] = mapped_column(JSON)
    options: Mapped[Optional[dict]] = mapped_column(JSON)
    dispatched: Mapped[bool] = mapped_column(Boolean, default=False)
    dispatched_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    adhoc: Mapped[bool] = mapped_column(Boolean, default=False)
    adhoc_distance: Mapped[Optional[int]] = mapped_column(Integer)
    started: Mapped[bool] = mapped_column(Boolean, default=False)
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    distance: Mapped[Optional[int]] = mapped_column(Integer)
    time: Mapped[Optional[int]] = mapped_column(Integer)
    pod_required: Mapped[Optional[bool]] = mapped_column(Boolean)
    is_route_optimized: Mapped[bool] = mapped_column(Boolean, default=False)
    pod_method: Mapped[Optional[str]] = mapped_column(String(255))
    notes: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    scheduled_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    type: Mapped[Optional[str]] = mapped_column(String(255))
    status: Mapped[Optional[str]] = mapped_column(String(191), index=True)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime, index=True, default=datetime.utcnow)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)



