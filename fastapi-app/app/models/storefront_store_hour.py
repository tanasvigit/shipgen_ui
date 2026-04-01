from datetime import datetime, time
from typing import Optional

from sqlalchemy import DateTime, Integer, String, Time
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class StorefrontStoreHour(Base):
    __tablename__ = "store_hours"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    uuid: Mapped[Optional[str]] = mapped_column(String(36), unique=True, nullable=True)
    store_location_uuid: Mapped[Optional[str]] = mapped_column(String(36), index=True, nullable=True)
    day_of_week: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    start: Mapped[time] = mapped_column(Time, nullable=False)
    end: Mapped[time] = mapped_column(Time, nullable=False)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

