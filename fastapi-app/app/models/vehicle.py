from datetime import datetime
from typing import Optional

from sqlalchemy import Integer, String, DateTime, JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Vehicle(Base):
    __tablename__ = "vehicles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    _key: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    uuid: Mapped[Optional[str]] = mapped_column(String(191), index=True)
    public_id: Mapped[Optional[str]] = mapped_column(String(191), index=True)
    company_uuid: Mapped[Optional[str]] = mapped_column(String(36), index=True)
    vendor_uuid: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    photo_uuid: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    avatar_url: Mapped[Optional[str]] = mapped_column(String(300), nullable=True)
    make: Mapped[Optional[str]] = mapped_column(String(191), nullable=True)
    model: Mapped[Optional[str]] = mapped_column(String(191), nullable=True)
    year: Mapped[Optional[str]] = mapped_column(String(191), nullable=True)
    trim: Mapped[Optional[str]] = mapped_column(String(191), nullable=True)
    type: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    plate_number: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    vin: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    vin_data: Mapped[Optional[dict]] = mapped_column(JSON)
    meta: Mapped[Optional[dict]] = mapped_column(JSON)
    status: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    slug: Mapped[Optional[str]] = mapped_column(String(191), index=True)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime, index=True)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime)



