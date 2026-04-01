from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, Integer, String, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Extension(Base):
    __tablename__ = "extensions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    uuid: Mapped[Optional[str]] = mapped_column(String(36), unique=True, nullable=True)
    public_id: Mapped[Optional[str]] = mapped_column(String(191), index=True, nullable=True)
    extension_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    author_uuid: Mapped[Optional[str]] = mapped_column(String(36), index=True, nullable=True)
    category_uuid: Mapped[Optional[str]] = mapped_column(String(36), index=True, nullable=True)
    type_uuid: Mapped[Optional[str]] = mapped_column(String(36), index=True, nullable=True)
    icon_uuid: Mapped[Optional[str]] = mapped_column(String(36), index=True, nullable=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    display_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    key: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    tags: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    namespace: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    internal_route: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    fa_icon: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    version: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    website_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    privacy_policy_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    tos_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    contact_email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    domains: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    core_service: Mapped[bool] = mapped_column(Boolean, default=False, nullable=True)
    meta: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    meta_type: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    config: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    secret: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    client_token: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    status: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    slug: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

