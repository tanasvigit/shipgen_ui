from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class TrackingStatus(Base):
    __tablename__ = "tracking_statuses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    _key: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    uuid: Mapped[Optional[str]] = mapped_column(String(191), index=True)
    public_id: Mapped[Optional[str]] = mapped_column(String(191), index=True)
    company_uuid: Mapped[Optional[str]] = mapped_column(String(36), index=True)
    tracking_number_uuid: Mapped[Optional[str]] = mapped_column(String(36), index=True, nullable=True)
    proof_uuid: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    meta: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    status: Mapped[Optional[str]] = mapped_column(String(191), index=True, nullable=True)
    details: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    code: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    city: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    province: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    postal_code: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    country: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    location_latitude: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    location_longitude: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    latitude: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    longitude: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    completed: Mapped[Optional[bool]] = mapped_column(Integer, nullable=True)  # Stored as 0/1
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime, index=True, nullable=True)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

