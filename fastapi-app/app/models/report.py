from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, Integer, String, Text, JSON, Float
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Report(Base):
    __tablename__ = "reports"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    uuid: Mapped[Optional[str]] = mapped_column(String(36), unique=True, nullable=True)
    public_id: Mapped[Optional[str]] = mapped_column(String(191), index=True, nullable=True)
    company_uuid: Mapped[Optional[str]] = mapped_column(String(36), index=True, nullable=True)
    category_uuid: Mapped[Optional[str]] = mapped_column(String(36), index=True, nullable=True)
    created_by_uuid: Mapped[Optional[str]] = mapped_column(String(36), index=True, nullable=True)
    updated_by_uuid: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    subject_uuid: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    subject_type: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    period_start: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    period_end: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    result_columns: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    last_executed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    execution_time: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    row_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    is_scheduled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=True)
    schedule_config: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    export_formats: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    is_generated: Mapped[bool] = mapped_column(Boolean, default=False, nullable=True)
    generation_progress: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    options: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    tags: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    query_config: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    data: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    meta: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    status: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    type: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

