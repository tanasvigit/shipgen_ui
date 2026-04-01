from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, Integer, String, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    uuid: Mapped[Optional[str]] = mapped_column(String(36), unique=True, nullable=True)
    public_id: Mapped[Optional[str]] = mapped_column(String(191), index=True, nullable=True)
    owner_uuid: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    owner_type: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    customer_uuid: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    customer_type: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    company_uuid: Mapped[Optional[str]] = mapped_column(String(36), index=True, nullable=True)
    gateway_transaction_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)
    gateway: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    gateway_uuid: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    amount: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    currency: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    meta: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    type: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    status: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

