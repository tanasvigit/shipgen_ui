from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    _key: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    uuid: Mapped[Optional[str]] = mapped_column(String(191), index=True)
    public_id: Mapped[Optional[str]] = mapped_column(String(191), index=True)
    company_uuid: Mapped[Optional[str]] = mapped_column(String(36), index=True)
    parent_uuid: Mapped[Optional[str]] = mapped_column(String(36), index=True, nullable=True)
    owner_uuid: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    owner_type: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    internal_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    translations: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    tags: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    meta: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    icon: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    icon_color: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    icon_file_uuid: Mapped[Optional[str]] = mapped_column(String(36), index=True, nullable=True)
    for_field: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)  # 'for' is a Python keyword
    slug: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    order: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime, index=True, nullable=True)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

