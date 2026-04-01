"""
ServiceRate model for distance-based pricing.
"""
from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, Integer, String, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class ServiceRate(Base):
    __tablename__ = "service_rates"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    _key: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    uuid: Mapped[Optional[str]] = mapped_column(String(191), unique=True, index=True)
    public_id: Mapped[Optional[str]] = mapped_column(String(191), unique=True, index=True)
    company_uuid: Mapped[Optional[str]] = mapped_column(String(36), index=True)
    service_area_uuid: Mapped[Optional[str]] = mapped_column(String(36), index=True)
    zone_uuid: Mapped[Optional[str]] = mapped_column(String(36), index=True)
    service_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    service_type: Mapped[Optional[str]] = mapped_column(String(191), index=True, nullable=True)
    
    # Pricing fields
    base_fee: Mapped[int] = mapped_column(Integer, default=0, nullable=True)  # in cents
    per_meter_flat_rate_fee: Mapped[int] = mapped_column(Integer, default=0, nullable=True)  # in cents
    per_meter_unit: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # 'm' or 'km'
    algorithm: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    rate_calculation_method: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # 'per_meter', 'fixed_meter', 'fixed_rate', 'per_drop', 'algo'
    
    # COD (Cash on Delivery) fields
    has_cod_fee: Mapped[bool] = mapped_column(Boolean, default=False, nullable=True)
    cod_calculation_method: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # 'flat' or 'percentage'
    cod_flat_fee: Mapped[int] = mapped_column(Integer, default=0, nullable=True)  # in cents
    cod_percent: Mapped[int] = mapped_column(Integer, default=0, nullable=True)  # percentage (0-100)
    
    # Peak hours fields
    has_peak_hours_fee: Mapped[bool] = mapped_column(Boolean, default=False, nullable=True)
    peak_hours_calculation_method: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # 'flat' or 'percentage'
    peak_hours_flat_fee: Mapped[int] = mapped_column(Integer, default=0, nullable=True)  # in cents
    peak_hours_percent: Mapped[int] = mapped_column(Integer, default=0, nullable=True)  # percentage (0-100)
    peak_hours_start: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # 'HH:MM' format
    peak_hours_end: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # 'HH:MM' format
    
    # Distance limits
    max_distance: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # in meters
    max_distance_unit: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # 'm' or 'km'
    
    # Other fields
    currency: Mapped[Optional[str]] = mapped_column(String(10), nullable=True, default="USD")
    duration_terms: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    estimated_days: Mapped[int] = mapped_column(Integer, default=0, nullable=True)
    meta: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime, index=True, nullable=True)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Relationships
    rate_fees: Mapped[list["ServiceRateFee"]] = relationship(
        "ServiceRateFee",
        back_populates="service_rate",
        cascade="all, delete-orphan",
    )
    
    def is_per_meter(self) -> bool:
        """Check if rate calculation method is per_meter."""
        return self.rate_calculation_method == "per_meter"
    
    def is_fixed_meter(self) -> bool:
        """Check if rate calculation method is fixed_meter or fixed_rate."""
        return self.rate_calculation_method in ["fixed_meter", "fixed_rate"]
    
    def has_cod(self) -> bool:
        """Check if COD fee is enabled."""
        return bool(self.has_cod_fee)
    
    def has_peak_hours(self) -> bool:
        """Check if peak hours fee is enabled."""
        return bool(self.has_peak_hours_fee)

