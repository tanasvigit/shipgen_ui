from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class TwoFaSetting(Base):
    __tablename__ = "twofa_settings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    subject_type: Mapped[str] = mapped_column(String(50))  # 'system' | 'user' | 'company'
    subject_uuid: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    method: Mapped[str] = mapped_column(String(50), default="email")
    enforced: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)


class TwoFaSession(Base):
    __tablename__ = "twofa_sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    identity: Mapped[str] = mapped_column(String(255), index=True)
    session_token: Mapped[str] = mapped_column(String(255), unique=True)
    client_token: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    code: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    validated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)



