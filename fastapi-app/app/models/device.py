"""
Device model for IoT devices and telematics tracking.
"""
from datetime import datetime, date
from typing import Optional

from sqlalchemy import Boolean, DateTime, Integer, String, Date, JSON, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Device(Base):
    __tablename__ = "devices"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    _key: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)
    uuid: Mapped[Optional[str]] = mapped_column(String(191), unique=True, index=True)
    public_id: Mapped[Optional[str]] = mapped_column(String(191), unique=True, index=True)
    company_uuid: Mapped[Optional[str]] = mapped_column(String(36), index=True)
    
    # Telematic provider relationship
    telematic_uuid: Mapped[Optional[str]] = mapped_column(String(36), index=True, nullable=True)
    
    # Polymorphic attachment (can attach to Vehicle, Driver, etc.)
    attachable_type: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    attachable_uuid: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    
    # Device identification
    device_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    imei: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)
    imsi: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    provider: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    type: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # Device details
    name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    model: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    manufacturer: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    serial_number: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    firmware_version: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # Location tracking
    latitude: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    longitude: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    heading: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    speed: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    altitude: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # Status and lifecycle
    status: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)
    online: Mapped[bool] = mapped_column(Boolean, default=False, nullable=True)
    last_online_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True, index=True)
    data_frequency: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # Dates
    installation_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    last_maintenance_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    
    # Metadata
    meta: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    data: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    options: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    slug: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)
    
    # Photo
    photo_uuid: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    
    # Warranty
    warranty_uuid: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime, index=True, nullable=True)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Relationships
    events: Mapped[list["DeviceEvent"]] = relationship(
        "DeviceEvent",
        back_populates="device",
        cascade="all, delete-orphan",
    )
    
    def is_online(self) -> bool:
        """Check if device is currently online (last seen within 10 minutes)."""
        if not self.last_online_at:
            return False
        from datetime import timedelta
        return datetime.now() - self.last_online_at < timedelta(minutes=10)
    
    def get_connection_status(self) -> str:
        """Get connection status based on last online time."""
        if not self.last_online_at:
            return "never_connected"
        
        minutes_offline = (datetime.now() - self.last_online_at).total_seconds() / 60
        
        if minutes_offline <= 10:
            return "online"
        elif minutes_offline <= 60:
            return "recently_offline"
        elif minutes_offline <= 1440:  # 24 hours
            return "offline"
        else:
            return "long_offline"

