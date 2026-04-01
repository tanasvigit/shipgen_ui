"""
Storefront Product model.
"""
from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, Integer, String, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class StorefrontProduct(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    uuid: Mapped[Optional[str]] = mapped_column(String(36), unique=True, index=True)
    public_id: Mapped[Optional[str]] = mapped_column(String(191), unique=True, index=True)
    company_uuid: Mapped[Optional[str]] = mapped_column(String(191), index=True)
    created_by_uuid: Mapped[Optional[str]] = mapped_column(String(191), index=True, nullable=True)
    primary_image_uuid: Mapped[Optional[str]] = mapped_column(String(191), index=True, nullable=True)
    store_uuid: Mapped[Optional[str]] = mapped_column(String(191), index=True, nullable=True)
    category_uuid: Mapped[Optional[str]] = mapped_column(String(191), index=True, nullable=True)
    
    # Product details
    name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    tags: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    meta: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    translations: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    youtube_urls: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    
    # Barcodes
    qr_code: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    barcode: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Pricing
    sku: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    price: Mapped[int] = mapped_column(Integer, default=0, nullable=True)  # in cents
    sale_price: Mapped[int] = mapped_column(Integer, default=0, nullable=True)  # in cents
    currency: Mapped[Optional[str]] = mapped_column(String(10), nullable=True, index=True)
    
    # Flags
    is_on_sale: Mapped[bool] = mapped_column(Boolean, nullable=True, default=False)
    is_service: Mapped[bool] = mapped_column(Boolean, nullable=True, default=False, index=True)
    is_bookable: Mapped[bool] = mapped_column(Boolean, default=False, nullable=True)
    is_available: Mapped[bool] = mapped_column(Boolean, default=True, nullable=True, index=True)
    is_recommended: Mapped[bool] = mapped_column(Boolean, nullable=True, default=False)
    can_pickup: Mapped[bool] = mapped_column(Boolean, default=False, nullable=True)
    
    # Status
    status: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, index=True)  # 'available', 'draft'
    slug: Mapped[Optional[str]] = mapped_column(String(191), nullable=True, index=True)
    
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

