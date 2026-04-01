from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Place(Base):
    __tablename__ = "places"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    _key: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    uuid: Mapped[Optional[str]] = mapped_column(String(191), index=True)
    public_id: Mapped[Optional[str]] = mapped_column(String(191), index=True)
    _import_id: Mapped[Optional[str]] = mapped_column(String(191), nullable=True)
    company_uuid: Mapped[Optional[str]] = mapped_column(String(36), index=True)
    owner_uuid: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    owner_type: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    street1: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    street2: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    city: Mapped[Optional[str]] = mapped_column(String(191), nullable=True)
    province: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    postal_code: Mapped[Optional[str]] = mapped_column(String(191), nullable=True)
    neighborhood: Mapped[Optional[str]] = mapped_column(String(191), nullable=True)
    district: Mapped[Optional[str]] = mapped_column(String(191), nullable=True)
    building: Mapped[Optional[str]] = mapped_column(String(191), nullable=True)
    security_access_code: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    country: Mapped[Optional[str]] = mapped_column(String(191), nullable=True)
    latitude: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    longitude: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    meta: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    remarks: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    type: Mapped[Optional[str]] = mapped_column(String(191), nullable=True)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)



