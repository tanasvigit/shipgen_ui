from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, Integer, JSON, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class OrderEvent(Base):
    __tablename__ = "order_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    uuid: Mapped[Optional[str]] = mapped_column(String(36), nullable=True, unique=True)
    public_id: Mapped[Optional[str]] = mapped_column(String(191), nullable=True, index=True)
    company_uuid: Mapped[Optional[str]] = mapped_column(String(36), nullable=True, index=True)
    order_uuid: Mapped[Optional[str]] = mapped_column(String(36), nullable=True, index=True)
    actor_uuid: Mapped[Optional[str]] = mapped_column(String(36), nullable=True, index=True)
    event_type: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    from_status: Mapped[Optional[str]] = mapped_column(String(64), nullable=True, index=True)
    to_status: Mapped[Optional[str]] = mapped_column(String(64), nullable=True, index=True)
    payload: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True, index=True)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

