"""
DeviceEvent model for IoT telemetry and event ingestion.
"""
from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Integer, String, JSON, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class DeviceEvent(Base):
    __tablename__ = "device_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    _key: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)
    uuid: Mapped[Optional[str]] = mapped_column(String(191), unique=True, index=True)
    public_id: Mapped[Optional[str]] = mapped_column(String(191), unique=True, index=True)
    company_uuid: Mapped[Optional[str]] = mapped_column(String(36), index=True)
    device_uuid: Mapped[Optional[str]] = mapped_column(
        String(36),
        ForeignKey("devices.uuid"),
        index=True,
        nullable=True
    )
    
    # Event identification
    ident: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    event_type: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)
    severity: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, index=True)  # 'low', 'medium', 'high', 'critical'
    protocol: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    provider: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # Event data
    payload: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    meta: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    # Location data (if event includes location)
    latitude: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    longitude: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # Event details
    code: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    reason: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    comment: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    state: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    mileage: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    # Processing status
    processed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True, index=True)
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    occurred_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True, index=True)
    
    slug: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime, index=True, nullable=True)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Relationships
    device: Mapped[Optional["Device"]] = relationship(
        "Device",
        back_populates="events",
    )
    
    def is_processed(self) -> bool:
        """Check if event has been processed."""
        return self.processed_at is not None
    
    def get_age_minutes(self) -> int:
        """Get age of event in minutes."""
        start_time = self.occurred_at or self.created_at
        if not start_time:
            return 0
        return int((datetime.now() - start_time).total_seconds() / 60)
    
    def get_severity_level(self) -> int:
        """Get severity as numeric value for sorting."""
        severity_map = {
            "critical": 4,
            "high": 3,
            "medium": 2,
            "low": 1,
        }
        return severity_map.get(self.severity or "", 0)

