"""
ServiceQuote model for storing calculated quotes.
"""
from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Integer, String, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class ServiceQuote(Base):
    __tablename__ = "service_quotes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    _key: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    uuid: Mapped[Optional[str]] = mapped_column(String(191), unique=True, index=True)
    public_id: Mapped[Optional[str]] = mapped_column(String(191), unique=True, index=True)
    request_id: Mapped[Optional[str]] = mapped_column(String(191), index=True, nullable=True)
    company_uuid: Mapped[Optional[str]] = mapped_column(String(36), index=True, nullable=True)
    service_rate_uuid: Mapped[Optional[str]] = mapped_column(String(36), index=True, nullable=True)
    
    # Quote amount
    amount: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # in cents
    currency: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    
    # Metadata
    meta: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    expired_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime, index=True, nullable=True)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Relationships
    items: Mapped[list["ServiceQuoteItem"]] = relationship(
        "ServiceQuoteItem",
        back_populates="service_quote",
        cascade="all, delete-orphan",
    )


class ServiceQuoteItem(Base):
    __tablename__ = "service_quote_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    _key: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    uuid: Mapped[Optional[str]] = mapped_column(String(191), unique=True, index=True)
    service_quote_uuid: Mapped[Optional[str]] = mapped_column(
        String(36),
        ForeignKey("service_quotes.uuid"),
        index=True,
        nullable=True
    )
    
    # Line item details
    amount: Mapped[int] = mapped_column(Integer, nullable=True)  # in cents
    currency: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    details: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    code: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # 'BASE_FEE', 'SERVICE_FEE', 'COD_FEE', etc.
    
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime, index=True, nullable=True)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Relationships
    service_quote: Mapped["ServiceQuote"] = relationship(
        "ServiceQuote",
        back_populates="items",
    )

