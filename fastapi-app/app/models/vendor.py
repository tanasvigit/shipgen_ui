from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, Integer, JSON, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Vendor(Base):
    __tablename__ = "vendors"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    _key: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    uuid: Mapped[Optional[str]] = mapped_column(String(191), index=True)
    public_id: Mapped[Optional[str]] = mapped_column(String(191), index=True)
    company_uuid: Mapped[Optional[str]] = mapped_column(String(36), index=True)
    place_uuid: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    type_uuid: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    connect_company_uuid: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    logo_uuid: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    internal_id: Mapped[Optional[str]] = mapped_column(String(191), nullable=True)
    business_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    connected: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    website_url: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    country: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    meta: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    callbacks: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    type: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    status: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    slug: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)



