from datetime import datetime, time
from typing import Optional

from sqlalchemy import DateTime, Integer, String, Time
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class StorefrontCatalogHour(Base):
    __tablename__ = "catalog_hours"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    uuid: Mapped[Optional[str]] = mapped_column(String(36), unique=True, nullable=True)
    catalog_uuid: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    day_of_week: Mapped[str] = mapped_column(String(255), nullable=False)
    start: Mapped[Optional[time]] = mapped_column(Time, nullable=True)
    end: Mapped[Optional[time]] = mapped_column(Time, nullable=True)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

