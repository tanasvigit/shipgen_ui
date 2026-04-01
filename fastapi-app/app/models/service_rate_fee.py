"""
ServiceRateFee model for distance-based pricing tiers.
"""
from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class ServiceRateFee(Base):
    __tablename__ = "service_rate_fees"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    _key: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    uuid: Mapped[Optional[str]] = mapped_column(String(191), unique=True, index=True)
    service_rate_uuid: Mapped[Optional[str]] = mapped_column(
        String(36),
        ForeignKey("service_rates.uuid"),
        index=True,
        nullable=True
    )
    
    # Distance-based pricing (for fixed_meter method)
    distance: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # in km for distance-based
    distance_unit: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # 'km' or 'm'
    
    # Min/Max range pricing (for per_drop method)
    min: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    max: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    unit: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    
    # Fee amount
    fee: Mapped[int] = mapped_column(Integer, nullable=True)  # in cents
    currency: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime, index=True, nullable=True)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Relationships
    service_rate: Mapped["ServiceRate"] = relationship(
        "ServiceRate",
        back_populates="rate_fees",
    )
    
    def is_within_min_max(self, number: int) -> bool:
        """Check if number is within min and max range."""
        if self.min is None or self.max is None:
            return False
        return self.min <= number <= self.max

