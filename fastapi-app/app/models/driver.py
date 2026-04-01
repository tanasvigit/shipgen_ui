from datetime import datetime
from typing import Optional

from sqlalchemy import Integer, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Driver(Base):
    __tablename__ = "drivers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    _key: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    uuid: Mapped[Optional[str]] = mapped_column(String(191), index=True)
    public_id: Mapped[Optional[str]] = mapped_column(String(191), index=True)
    internal_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    company_uuid: Mapped[Optional[str]] = mapped_column(String(36), index=True)
    vehicle_uuid: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    vendor_uuid: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    current_job_uuid: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    user_uuid: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    drivers_license_number: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    latitude: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    longitude: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    heading: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    speed: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    altitude: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    country: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    city: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    currency: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    online: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[Optional[str]] = mapped_column(String(191), index=True)
    slug: Mapped[Optional[str]] = mapped_column(String(191), index=True)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime, index=True)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime)



