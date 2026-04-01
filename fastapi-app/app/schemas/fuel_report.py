from datetime import datetime
from typing import Any, List, Optional

from pydantic import BaseModel


class FuelReportBase(BaseModel):
    uuid: Optional[str] = None
    public_id: Optional[str] = None
    company_uuid: Optional[str] = None
    driver_uuid: Optional[str] = None
    vehicle_uuid: Optional[str] = None
    reported_by_uuid: Optional[str] = None
    odometer: Optional[str] = None
    location: Optional[dict[str, Any]] = None
    latitude: Optional[str] = None
    longitude: Optional[str] = None
    amount: Optional[str] = None
    currency: Optional[str] = None
    volume: Optional[str] = None
    metric_unit: Optional[str] = None
    report: Optional[str] = None
    meta: Optional[dict[str, Any]] = None
    status: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class FuelReportCreate(BaseModel):
    driver: Optional[str] = None  # public_id
    location: Optional[dict[str, Any]] = None
    odometer: Optional[str] = None
    volume: Optional[str] = None
    metric_unit: Optional[str] = None
    amount: Optional[str] = None
    currency: Optional[str] = None
    status: Optional[str] = None
    report: Optional[str] = None
    meta: Optional[dict[str, Any]] = None


class FuelReportUpdate(BaseModel):
    odometer: Optional[str] = None
    volume: Optional[str] = None
    metric_unit: Optional[str] = None
    amount: Optional[str] = None
    currency: Optional[str] = None
    status: Optional[str] = None
    report: Optional[str] = None
    meta: Optional[dict[str, Any]] = None




class FuelReportOut(FuelReportBase):
    id: Optional[int] = None
    vehicle_name: Optional[str] = None
    driver_name: Optional[str] = None
    reporter_name: Optional[str] = None

    class Config:
        from_attributes = True


class FuelReportResponse(BaseModel):
    fuel_report: FuelReportOut


class FuelReportsResponse(BaseModel):
    fuel_reports: List[FuelReportOut]

