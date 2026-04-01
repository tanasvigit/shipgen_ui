from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class StorefrontReview(Base):
    __tablename__ = "reviews"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    uuid: Mapped[Optional[str]] = mapped_column(String(36), unique=True, nullable=True)
    public_id: Mapped[Optional[str]] = mapped_column(String(191), unique=True, nullable=True)
    created_by_uuid: Mapped[Optional[str]] = mapped_column(String(36), index=True, nullable=True)
    customer_uuid: Mapped[Optional[str]] = mapped_column(String(36), index=True, nullable=True)
    subject_uuid: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    subject_type: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    rating: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    content: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    rejected: Mapped[bool] = mapped_column(Boolean, default=False)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

