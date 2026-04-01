"""
Pydantic schemas for devices.
"""
from datetime import datetime, date
from typing import Optional
from pydantic import BaseModel, Field


class DeviceBase(BaseModel):
    name: Optional[str] = None
    model: Optional[str] = None
    manufacturer: Optional[str] = None
    serial_number: Optional[str] = None
    device_id: Optional[str] = None
    imei: Optional[str] = None
    imsi: Optional[str] = None
    provider: Optional[str] = None
    type: Optional[str] = None
    firmware_version: Optional[str] = None
    telematic_uuid: Optional[str] = None
    attachable_type: Optional[str] = None
    attachable_uuid: Optional[str] = None
    status: Optional[str] = None
    online: bool = False
    data_frequency: Optional[str] = None
    installation_date: Optional[date] = None
    last_maintenance_date: Optional[date] = None
    meta: Optional[dict] = None
    data: Optional[dict] = None
    options: Optional[dict] = None
    notes: Optional[str] = None
    photo_uuid: Optional[str] = None
    warranty_uuid: Optional[str] = None


class DeviceCreate(DeviceBase):
    pass


class DeviceUpdate(BaseModel):
    name: Optional[str] = None
    model: Optional[str] = None
    manufacturer: Optional[str] = None
    serial_number: Optional[str] = None
    device_id: Optional[str] = None
    imei: Optional[str] = None
    imsi: Optional[str] = None
    provider: Optional[str] = None
    type: Optional[str] = None
    firmware_version: Optional[str] = None
    telematic_uuid: Optional[str] = None
    attachable_type: Optional[str] = None
    attachable_uuid: Optional[str] = None
    status: Optional[str] = None
    online: Optional[bool] = None
    data_frequency: Optional[str] = None
    installation_date: Optional[date] = None
    last_maintenance_date: Optional[date] = None
    meta: Optional[dict] = None
    data: Optional[dict] = None
    options: Optional[dict] = None
    notes: Optional[str] = None
    photo_uuid: Optional[str] = None
    warranty_uuid: Optional[str] = None


class DeviceOut(DeviceBase):
    uuid: str
    public_id: str
    company_uuid: Optional[str] = None
    latitude: Optional[str] = None
    longitude: Optional[str] = None
    heading: Optional[str] = None
    speed: Optional[str] = None
    altitude: Optional[str] = None
    last_online_at: Optional[datetime] = None
    slug: Optional[str] = None
    is_online: bool = Field(default=False, description="Computed: device online status")
    connection_status: str = Field(default="never_connected", description="Computed: connection status")
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class DeviceLocationUpdate(BaseModel):
    """Update device location from telemetry."""
    latitude: float
    longitude: float
    heading: Optional[float] = None
    speed: Optional[float] = None
    altitude: Optional[float] = None
    timestamp: Optional[datetime] = None


class DeviceHeartbeat(BaseModel):
    """Device heartbeat/status update."""
    online: bool = True
    timestamp: Optional[datetime] = None
    metrics: Optional[dict] = None

