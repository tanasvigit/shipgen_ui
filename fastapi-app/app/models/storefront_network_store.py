from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class StorefrontNetworkStore(Base):
    __tablename__ = "network_stores"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    uuid: Mapped[Optional[str]] = mapped_column(String(36), unique=True, nullable=True)
    network_uuid: Mapped[Optional[str]] = mapped_column(String(36), index=True, nullable=True)
    store_uuid: Mapped[Optional[str]] = mapped_column(String(36), index=True, nullable=True)
    category_uuid: Mapped[Optional[str]] = mapped_column(String(36), index=True, nullable=True)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

