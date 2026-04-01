from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, Integer, JSON, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class StorefrontCheckout(Base):
    __tablename__ = "checkouts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    uuid: Mapped[Optional[str]] = mapped_column(String(36), unique=True, nullable=True)
    public_id: Mapped[Optional[str]] = mapped_column(String(191), index=True, nullable=True)
    company_uuid: Mapped[Optional[str]] = mapped_column(String(36), index=True, nullable=True)
    order_uuid: Mapped[Optional[str]] = mapped_column(String(36), index=True, nullable=True)
    cart_uuid: Mapped[Optional[str]] = mapped_column(String(36), index=True, nullable=True)
    store_uuid: Mapped[Optional[str]] = mapped_column(String(36), index=True, nullable=True)
    network_uuid: Mapped[Optional[str]] = mapped_column(String(36), index=True, nullable=True)
    gateway_uuid: Mapped[Optional[str]] = mapped_column(String(36), index=True, nullable=True)
    service_quote_uuid: Mapped[Optional[str]] = mapped_column(String(36), index=True, nullable=True)
    owner_uuid: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    owner_type: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    token: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    amount: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    currency: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    is_cod: Mapped[bool] = mapped_column(Boolean, default=False)
    is_pickup: Mapped[bool] = mapped_column(Boolean, default=False)
    options: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    cart_state: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    captured: Mapped[bool] = mapped_column(Boolean, default=False)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

