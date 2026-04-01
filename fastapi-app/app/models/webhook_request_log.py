from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, Integer, String, Text, JSON, Float
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class WebhookRequestLog(Base):
    __tablename__ = "webhook_request_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    uuid: Mapped[Optional[str]] = mapped_column(String(36), unique=True, nullable=True)
    public_id: Mapped[Optional[str]] = mapped_column(String(191), index=True, nullable=True)
    company_uuid: Mapped[Optional[str]] = mapped_column(String(36), index=True, nullable=True)
    webhook_uuid: Mapped[Optional[str]] = mapped_column(String(36), index=True, nullable=True)
    api_credential_uuid: Mapped[Optional[str]] = mapped_column(String(36), index=True, nullable=True)
    access_token_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    api_event_uuid: Mapped[Optional[str]] = mapped_column(String(36), index=True, nullable=True)
    method: Mapped[str] = mapped_column(String(10), nullable=False)
    status_code: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    reason_phrase: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    duration: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    attempt: Mapped[int] = mapped_column(Integer, default=1, nullable=True)
    response: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    status: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    headers: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    meta: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    sent_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

