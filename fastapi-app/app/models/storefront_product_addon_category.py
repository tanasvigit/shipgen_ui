from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, Integer, String, JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class StorefrontProductAddonCategory(Base):
    __tablename__ = "product_addon_categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    uuid: Mapped[Optional[str]] = mapped_column(String(36), unique=True, nullable=True)
    product_uuid: Mapped[Optional[str]] = mapped_column(String(191), index=True, nullable=True)
    category_uuid: Mapped[Optional[str]] = mapped_column(String(191), index=True, nullable=True)
    excluded_addons: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    max_selectable: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    is_required: Mapped[bool] = mapped_column(Boolean, nullable=True, default=False)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

