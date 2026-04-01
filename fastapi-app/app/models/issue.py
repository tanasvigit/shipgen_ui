from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Issue(Base):
    __tablename__ = "issues"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    _key: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    uuid: Mapped[Optional[str]] = mapped_column(String(191), index=True)
    public_id: Mapped[Optional[str]] = mapped_column(String(191), unique=True, nullable=True)
    issue_id: Mapped[Optional[str]] = mapped_column(String(191), unique=True, nullable=True)
    company_uuid: Mapped[Optional[str]] = mapped_column(String(36), index=True)
    driver_uuid: Mapped[Optional[str]] = mapped_column(String(36), index=True, nullable=True)
    vehicle_uuid: Mapped[Optional[str]] = mapped_column(String(36), index=True, nullable=True)
    assigned_to_uuid: Mapped[Optional[str]] = mapped_column(String(36), index=True, nullable=True)
    reported_by_uuid: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    location_latitude: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    location_longitude: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    latitude: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    longitude: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    category: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    type: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    report: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    title: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    tags: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    priority: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    meta: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    status: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime, index=True, nullable=True)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

