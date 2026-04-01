from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Entity(Base):
    __tablename__ = "entities"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    _key: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    uuid: Mapped[Optional[str]] = mapped_column(String(191), index=True)
    public_id: Mapped[Optional[str]] = mapped_column(String(191), index=True)
    payload_uuid: Mapped[Optional[str]] = mapped_column(String(36), index=True, nullable=True)
    company_uuid: Mapped[Optional[str]] = mapped_column(String(36), index=True)
    driver_assigned_uuid: Mapped[Optional[str]] = mapped_column(String(36), index=True, nullable=True)
    destination_uuid: Mapped[Optional[str]] = mapped_column(String(36), index=True, nullable=True)
    customer_uuid: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    customer_type: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    tracking_number_uuid: Mapped[Optional[str]] = mapped_column(String(36), index=True, nullable=True)
    photo_uuid: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    supplier_uuid: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    category_uuid: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    _import_id: Mapped[Optional[str]] = mapped_column(String(191), index=True, nullable=True)
    internal_id: Mapped[Optional[str]] = mapped_column(String(191), index=True, nullable=True)
    name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    type: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    currency: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    barcode: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    qr_code: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    weight: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    weight_unit: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    length: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    width: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    height: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    dimensions_unit: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    declared_value: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    sku: Mapped[Optional[str]] = mapped_column(String(191), index=True, nullable=True)
    price: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    sale_price: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    meta: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    slug: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime, index=True, nullable=True)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

