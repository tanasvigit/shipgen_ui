"""
Pydantic schemas for telematics providers.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class TelematicBase(BaseModel):
    name: Optional[str] = None
    provider: Optional[str] = Field(None, description="Provider: 'samsara', 'geotab', 'custom', etc.")
    model: Optional[str] = None
    serial_number: Optional[str] = None
    firmware_version: Optional[str] = None
    status: Optional[str] = Field("initialized", description="Status: 'initialized', 'active', 'disconnected', etc.")
    type: Optional[str] = None
    imei: Optional[str] = None
    iccid: Optional[str] = None
    imsi: Optional[str] = None
    msisdn: Optional[str] = None
    config: Optional[dict] = None
    credentials: Optional[dict] = None
    meta: Optional[dict] = None
    warranty_uuid: Optional[str] = None


class TelematicCreate(TelematicBase):
    pass


class TelematicUpdate(BaseModel):
    name: Optional[str] = None
    provider: Optional[str] = None
    model: Optional[str] = None
    serial_number: Optional[str] = None
    firmware_version: Optional[str] = None
    status: Optional[str] = None
    type: Optional[str] = None
    imei: Optional[str] = None
    iccid: Optional[str] = None
    imsi: Optional[str] = None
    msisdn: Optional[str] = None
    config: Optional[dict] = None
    credentials: Optional[dict] = None
    meta: Optional[dict] = None
    warranty_uuid: Optional[str] = None


class TelematicOut(TelematicBase):
    uuid: str
    public_id: str
    company_uuid: Optional[str] = None
    last_seen_at: Optional[datetime] = None
    last_metrics: Optional[dict] = None
    is_online: bool = Field(default=False, description="Computed: telematic online status")
    connection_status: str = Field(default="never_connected", description="Computed: connection status")
    signal_strength: Optional[int] = Field(None, description="Computed: signal strength from metrics")
    last_location: Optional[dict] = Field(None, description="Computed: last known location")
    created_by_uuid: Optional[str] = None
    updated_by_uuid: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class TelematicHeartbeat(BaseModel):
    """Telematic heartbeat/metrics update."""
    metrics: Optional[dict] = Field(None, description="Metrics: { lat, lng, speed, heading, signal_strength, ... }")
    timestamp: Optional[datetime] = None

