from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, Integer, String, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class CustomField(Base):
    __tablename__ = "custom_fields"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    uuid: Mapped[Optional[str]] = mapped_column(String(36), unique=True, nullable=True)
    company_uuid: Mapped[Optional[str]] = mapped_column(String(36), index=True, nullable=True)
    category_uuid: Mapped[Optional[str]] = mapped_column(String(36), index=True, nullable=True)
    subject_uuid: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    subject_type: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    label: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    type: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    for_field: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)  # 'for' is Python keyword
    component: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    options: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    required: Mapped[bool] = mapped_column(Boolean, default=False, nullable=True)
    editable: Mapped[bool] = mapped_column(Boolean, default=True, nullable=True)
    default_value: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    validation_rules: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    meta: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    help_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    order: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

