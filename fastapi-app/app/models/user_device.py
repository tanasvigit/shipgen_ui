from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class UserDevice(Base):
    __tablename__ = "user_devices"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    uuid: Mapped[Optional[str]] = mapped_column(String(36), unique=True, nullable=True)
    public_id: Mapped[Optional[str]] = mapped_column(String(191), index=True, nullable=True)
    user_uuid: Mapped[Optional[str]] = mapped_column(String(36), index=True, nullable=True)
    platform: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    token: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

