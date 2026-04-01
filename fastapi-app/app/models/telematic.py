"""
Telematic model for telematics provider integrations.
"""
from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, Integer, String, JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Telematic(Base):
    __tablename__ = "telematics"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    _key: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)
    uuid: Mapped[Optional[str]] = mapped_column(String(191), unique=True, index=True)
    public_id: Mapped[Optional[str]] = mapped_column(String(191), unique=True, index=True)
    company_uuid: Mapped[Optional[str]] = mapped_column(String(36), index=True)
    
    # Provider information
    name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)
    provider: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)  # 'samsara', 'geotab', 'custom', etc.
    model: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    serial_number: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)
    firmware_version: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    status: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, index=True, default="initialized")
    type: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)
    
    # Connectivity identifiers
    imei: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)
    iccid: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)
    imsi: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)
    msisdn: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)
    
    # Last heartbeat / metrics
    last_seen_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True, index=True)
    last_metrics: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)  # { lat, lng, speed, heading, signal_strength, ... }
    
    # Configuration
    config: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    credentials: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)  # Encrypted provider credentials
    meta: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    # Warranty
    warranty_uuid: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    
    # Audit
    created_by_uuid: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    updated_by_uuid: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime, index=True, nullable=True)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    def is_online(self) -> bool:
        """Check if telematic is currently online (last seen within 5 minutes)."""
        if not self.last_seen_at:
            return False
        from datetime import timedelta
        return datetime.now() - self.last_seen_at < timedelta(minutes=5)
    
    def get_connection_status(self) -> str:
        """Get connection status based on last seen time."""
        if not self.last_seen_at:
            return "never_connected"
        
        minutes_offline = (datetime.now() - self.last_seen_at).total_seconds() / 60
        
        if minutes_offline <= 5:
            return "online"
        elif minutes_offline <= 60:
            return "recently_offline"
        elif minutes_offline <= 1440:  # 24 hours
            return "offline"
        else:
            return "long_offline"
    
    def get_signal_strength(self) -> Optional[int]:
        """Get signal strength from last metrics."""
        if self.last_metrics and "signal_strength" in self.last_metrics:
            return self.last_metrics["signal_strength"]
        return None
    
    def get_last_location(self) -> Optional[dict]:
        """Get last known location from metrics."""
        if not self.last_metrics:
            return None
        
        metrics = self.last_metrics
        if "lat" in metrics and "lng" in metrics:
            return {
                "latitude": metrics["lat"],
                "longitude": metrics["lng"],
                "timestamp": self.last_seen_at.isoformat() if self.last_seen_at else None,
            }
        return None

