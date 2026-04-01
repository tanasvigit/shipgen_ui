from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class StorefrontStore(Base):
    __tablename__ = "stores"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    uuid: Mapped[Optional[str]] = mapped_column(String(36), unique=True, nullable=True)
    public_id: Mapped[Optional[str]] = mapped_column(String(191), index=True, nullable=True)
    created_by_uuid: Mapped[Optional[str]] = mapped_column(String(36), index=True, nullable=True)
    company_uuid: Mapped[Optional[str]] = mapped_column(String(36), index=True, nullable=True)
    logo_uuid: Mapped[Optional[str]] = mapped_column(String(36), index=True, nullable=True)
    backdrop_uuid: Mapped[Optional[str]] = mapped_column(String(36), index=True, nullable=True)
    order_config_uuid: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    key: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    online: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    website: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    facebook: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    instagram: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    twitter: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    tags: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    translations: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    currency: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    timezone: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    pod_method: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    options: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    alertable: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    meta: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    slug: Mapped[Optional[str]] = mapped_column(String(191), index=True, nullable=True)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

