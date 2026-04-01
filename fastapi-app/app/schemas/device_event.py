"""
Pydantic schemas for device events.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class DeviceEventBase(BaseModel):
    event_type: Optional[str] = Field(None, description="Type of event: 'location', 'status', 'alert', 'error', etc.")
    severity: Optional[str] = Field(None, description="Severity: 'low', 'medium', 'high', 'critical'")
    ident: Optional[str] = None
    protocol: Optional[str] = None
    provider: Optional[str] = None
    payload: Optional[dict] = None
    meta: Optional[dict] = None
    latitude: Optional[str] = None
    longitude: Optional[str] = None
    code: Optional[str] = None
    reason: Optional[str] = None
    comment: Optional[str] = None
    state: Optional[str] = None
    mileage: Optional[int] = None
    occurred_at: Optional[datetime] = None


class DeviceEventCreate(DeviceEventBase):
    device_uuid: Optional[str] = None
    device_id: Optional[str] = Field(None, description="Alternative: device_id or imei to identify device")


class DeviceEventUpdate(BaseModel):
    processed_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    comment: Optional[str] = None


class DeviceEventOut(DeviceEventBase):
    uuid: str
    public_id: str
    company_uuid: Optional[str] = None
    device_uuid: Optional[str] = None
    processed_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    slug: Optional[str] = None
    is_processed: bool = Field(default=False, description="Computed: whether event has been processed")
    age_minutes: int = Field(default=0, description="Computed: age of event in minutes")
    severity_level: int = Field(default=0, description="Computed: numeric severity for sorting")
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class DeviceEventIngest(BaseModel):
    """Bulk event ingestion from IoT devices."""
    device_id: Optional[str] = Field(None, description="Device identifier (device_id, imei, or uuid)")
    device_uuid: Optional[str] = None
    events: list[DeviceEventCreate] = Field(..., min_items=1, description="List of events to ingest")

