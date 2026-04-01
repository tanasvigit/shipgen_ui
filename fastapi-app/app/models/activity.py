from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, Integer, String, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Activity(Base):
    __tablename__ = "activity_log"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    uuid: Mapped[Optional[str]] = mapped_column(String(36), unique=True, nullable=True)
    log_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    subject_type: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)
    subject_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True, index=True)
    event: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    causer_type: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)
    causer_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True, index=True)
    properties: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    batch_uuid: Mapped[Optional[str]] = mapped_column(String(36), nullable=True, index=True)
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

