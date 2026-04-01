from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class FuelReport(Base):
    __tablename__ = "fuel_reports"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    _key: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    uuid: Mapped[Optional[str]] = mapped_column(String(191), index=True)
    public_id: Mapped[Optional[str]] = mapped_column(String(191), unique=True, nullable=True)
    company_uuid: Mapped[Optional[str]] = mapped_column(String(36), index=True)
    driver_uuid: Mapped[Optional[str]] = mapped_column(String(36), index=True, nullable=True)
    vehicle_uuid: Mapped[Optional[str]] = mapped_column(String(36), index=True, nullable=True)
    reported_by_uuid: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    odometer: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    location_latitude: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    location_longitude: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    latitude: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    longitude: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    amount: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    currency: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    volume: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    metric_unit: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    report: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    meta: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    status: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime, index=True, nullable=True)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

