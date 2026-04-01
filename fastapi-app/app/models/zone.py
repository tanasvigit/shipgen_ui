from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Zone(Base):
    __tablename__ = "zones"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    _key: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    uuid: Mapped[Optional[str]] = mapped_column(String(191), index=True)
    public_id: Mapped[Optional[str]] = mapped_column(String(191), unique=True, nullable=True)
    company_uuid: Mapped[Optional[str]] = mapped_column(String(36), index=True)
    service_area_uuid: Mapped[Optional[str]] = mapped_column(String(36), index=True, nullable=True)
    name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    # Border stored as JSON (polygon coordinates)
    border: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    color: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    stroke_color: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    status: Mapped[Optional[str]] = mapped_column(String(191), index=True, nullable=True)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime, index=True, nullable=True)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

