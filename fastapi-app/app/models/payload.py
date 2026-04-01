from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, Integer, JSON, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Payload(Base):
    __tablename__ = "payloads"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    _key: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    uuid: Mapped[Optional[str]] = mapped_column(String(191), index=True)
    public_id: Mapped[Optional[str]] = mapped_column(String(191), index=True)
    company_uuid: Mapped[Optional[str]] = mapped_column(String(36), index=True)
    pickup_uuid: Mapped[Optional[str]] = mapped_column(String(36), index=True, nullable=True)
    dropoff_uuid: Mapped[Optional[str]] = mapped_column(String(36), index=True, nullable=True)
    return_uuid: Mapped[Optional[str]] = mapped_column(String(36), index=True, nullable=True)
    current_waypoint_uuid: Mapped[Optional[str]] = mapped_column(String(36), index=True, nullable=True)
    provider: Mapped[Optional[str]] = mapped_column(String(191), index=True, nullable=True)
    payment_method: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    cod_amount: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    cod_currency: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    cod_payment_method: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    type: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    meta: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime, index=True, nullable=True)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

