from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, Integer, String, JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class StorefrontNotificationChannel(Base):
    __tablename__ = "notification_channels"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    uuid: Mapped[Optional[str]] = mapped_column(String(36), index=True, nullable=True)
    company_uuid: Mapped[Optional[str]] = mapped_column(String(36), index=True, nullable=True)
    created_by_uuid: Mapped[Optional[str]] = mapped_column(String(36), index=True, nullable=True)
    owner_uuid: Mapped[Optional[str]] = mapped_column(String(191), nullable=True)
    owner_type: Mapped[Optional[str]] = mapped_column(String(191), nullable=True)
    certificate_uuid: Mapped[Optional[str]] = mapped_column(String(36), index=True, nullable=True)
    config: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    options: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    scheme: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    app_key: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

