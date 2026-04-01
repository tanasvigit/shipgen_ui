from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class GroupUser(Base):
    __tablename__ = "group_users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    uuid: Mapped[Optional[str]] = mapped_column(String(36), unique=True, nullable=True)
    company_uuid: Mapped[Optional[str]] = mapped_column(String(36), index=True, nullable=True)
    user_uuid: Mapped[Optional[str]] = mapped_column(String(36), index=True, nullable=True)
    group_uuid: Mapped[Optional[str]] = mapped_column(String(36), index=True, nullable=True)
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

