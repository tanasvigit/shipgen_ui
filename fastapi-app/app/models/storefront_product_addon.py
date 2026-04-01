from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, Integer, String, JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class StorefrontProductAddon(Base):
    __tablename__ = "product_addons"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    uuid: Mapped[Optional[str]] = mapped_column(String(36), unique=True, nullable=True)
    public_id: Mapped[Optional[str]] = mapped_column(String(191), index=True, nullable=True)
    created_by_uuid: Mapped[Optional[str]] = mapped_column(String(191), index=True, nullable=True)
    category_uuid: Mapped[Optional[str]] = mapped_column(String(191), index=True, nullable=True)
    name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    translations: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    price: Mapped[int] = mapped_column(Integer, default=0, nullable=True)
    sale_price: Mapped[int] = mapped_column(Integer, default=0, nullable=True)
    is_on_sale: Mapped[bool] = mapped_column(Boolean, nullable=True, default=False)
    slug: Mapped[Optional[str]] = mapped_column(String(191), index=True, nullable=True)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

