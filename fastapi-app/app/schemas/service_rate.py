"""
Pydantic schemas for service rates.
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class ServiceRateFeeBase(BaseModel):
    distance: Optional[int] = None
    distance_unit: Optional[str] = None
    min: Optional[int] = None
    max: Optional[int] = None
    unit: Optional[str] = None
    fee: int = Field(..., description="Fee in cents")
    currency: Optional[str] = "USD"


class ServiceRateFeeCreate(ServiceRateFeeBase):
    pass


class ServiceRateFeeOut(ServiceRateFeeBase):
    uuid: str
    service_rate_uuid: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ServiceRateBase(BaseModel):
    service_name: Optional[str] = None
    service_type: Optional[str] = None
    base_fee: int = Field(default=0, description="Base fee in cents")
    per_meter_flat_rate_fee: int = Field(default=0, description="Per meter fee in cents")
    per_meter_unit: Optional[str] = Field(None, description="'m' or 'km'")
    rate_calculation_method: Optional[str] = Field(
        None, description="'per_meter', 'fixed_meter', 'fixed_rate', 'per_drop', 'algo'"
    )
    has_cod_fee: bool = False
    cod_calculation_method: Optional[str] = Field(None, description="'flat' or 'percentage'")
    cod_flat_fee: int = Field(default=0, description="COD flat fee in cents")
    cod_percent: int = Field(default=0, description="COD percentage (0-100)")
    has_peak_hours_fee: bool = False
    peak_hours_calculation_method: Optional[str] = Field(None, description="'flat' or 'percentage'")
    peak_hours_flat_fee: int = Field(default=0, description="Peak hours flat fee in cents")
    peak_hours_percent: int = Field(default=0, description="Peak hours percentage (0-100)")
    peak_hours_start: Optional[str] = Field(None, description="'HH:MM' format")
    peak_hours_end: Optional[str] = Field(None, description="'HH:MM' format")
    max_distance: Optional[int] = None
    max_distance_unit: Optional[str] = None
    currency: Optional[str] = "USD"
    duration_terms: Optional[str] = None
    estimated_days: int = 0


class ServiceRateCreate(ServiceRateBase):
    rate_fees: Optional[List[ServiceRateFeeCreate]] = []


class ServiceRateUpdate(BaseModel):
    service_name: Optional[str] = None
    service_type: Optional[str] = None
    base_fee: Optional[int] = None
    per_meter_flat_rate_fee: Optional[int] = None
    per_meter_unit: Optional[str] = None
    rate_calculation_method: Optional[str] = None
    has_cod_fee: Optional[bool] = None
    cod_calculation_method: Optional[str] = None
    cod_flat_fee: Optional[int] = None
    cod_percent: Optional[int] = None
    has_peak_hours_fee: Optional[bool] = None
    peak_hours_calculation_method: Optional[str] = None
    peak_hours_flat_fee: Optional[int] = None
    peak_hours_percent: Optional[int] = None
    peak_hours_start: Optional[str] = None
    peak_hours_end: Optional[str] = None
    max_distance: Optional[int] = None
    max_distance_unit: Optional[str] = None
    currency: Optional[str] = None
    duration_terms: Optional[str] = None
    estimated_days: Optional[int] = None


class ServiceRateOut(ServiceRateBase):
    uuid: str
    public_id: str
    company_uuid: Optional[str] = None
    rate_fees: List[ServiceRateFeeOut] = []
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

