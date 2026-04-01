from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class StorefrontFoodTruck(Base):
    __tablename__ = "food_trucks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    uuid: Mapped[Optional[str]] = mapped_column(String(36), unique=True, nullable=True)
    public_id: Mapped[Optional[str]] = mapped_column(String(191), unique=True, nullable=True)
    vehicle_uuid: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    store_uuid: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    company_uuid: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    created_by_uuid: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    service_area_uuid: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    zone_uuid: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    status: Mapped[Optional[str]] = mapped_column(String(255), default="inactive")
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

