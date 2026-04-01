"""Telematics and devices tables for IoT tracking
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0008_telematics_and_devices"
down_revision: Union[str, None] = "0007_service_rates_and_quotes"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Telematics table (provider integrations)
    op.create_table(
        "telematics",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("_key", sa.String(length=255), nullable=True, index=True),
        sa.Column("uuid", sa.String(length=191), nullable=True, unique=True, index=True),
        sa.Column("public_id", sa.String(length=191), nullable=True, unique=True, index=True),
        sa.Column("company_uuid", sa.String(length=36), nullable=True, index=True),
        sa.Column("name", sa.String(length=255), nullable=True, index=True),
        sa.Column("provider", sa.String(length=255), nullable=True, index=True),
        sa.Column("model", sa.String(length=255), nullable=True),
        sa.Column("serial_number", sa.String(length=255), nullable=True, index=True),
        sa.Column("firmware_version", sa.String(length=255), nullable=True),
        sa.Column("status", sa.String(length=50), nullable=True, index=True),
        sa.Column("type", sa.String(length=255), nullable=True, index=True),
        sa.Column("imei", sa.String(length=255), nullable=True, index=True),
        sa.Column("iccid", sa.String(length=255), nullable=True, index=True),
        sa.Column("imsi", sa.String(length=255), nullable=True, index=True),
        sa.Column("msisdn", sa.String(length=255), nullable=True, index=True),
        sa.Column("last_seen_at", sa.DateTime, nullable=True, index=True),
        sa.Column("last_metrics", sa.JSON, nullable=True),
        sa.Column("config", sa.JSON, nullable=True),
        sa.Column("credentials", sa.JSON, nullable=True),
        sa.Column("meta", sa.JSON, nullable=True),
        sa.Column("warranty_uuid", sa.String(length=36), nullable=True),
        sa.Column("created_by_uuid", sa.String(length=36), nullable=True),
        sa.Column("updated_by_uuid", sa.String(length=36), nullable=True),
        sa.Column("deleted_at", sa.DateTime, nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=True, index=True),
        sa.Column("updated_at", sa.DateTime, nullable=True),
    )
    
    # Devices table (IoT devices)
    op.create_table(
        "devices",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("_key", sa.String(length=255), nullable=True, index=True),
        sa.Column("uuid", sa.String(length=191), nullable=True, unique=True, index=True),
        sa.Column("public_id", sa.String(length=191), nullable=True, unique=True, index=True),
        sa.Column("company_uuid", sa.String(length=36), nullable=True, index=True),
        sa.Column("telematic_uuid", sa.String(length=36), nullable=True, index=True),
        sa.Column("attachable_type", sa.String(length=255), nullable=True),
        sa.Column("attachable_uuid", sa.String(length=36), nullable=True),
        sa.Column("device_id", sa.String(length=255), nullable=True),
        sa.Column("imei", sa.String(length=255), nullable=True, index=True),
        sa.Column("imsi", sa.String(length=255), nullable=True),
        sa.Column("provider", sa.String(length=255), nullable=True),
        sa.Column("type", sa.String(length=255), nullable=True),
        sa.Column("name", sa.String(length=255), nullable=True),
        sa.Column("model", sa.String(length=255), nullable=True),
        sa.Column("manufacturer", sa.String(length=255), nullable=True),
        sa.Column("serial_number", sa.String(length=255), nullable=True),
        sa.Column("firmware_version", sa.String(length=255), nullable=True),
        sa.Column("latitude", sa.String(length=255), nullable=True),
        sa.Column("longitude", sa.String(length=255), nullable=True),
        sa.Column("heading", sa.String(length=255), nullable=True),
        sa.Column("speed", sa.String(length=255), nullable=True),
        sa.Column("altitude", sa.String(length=255), nullable=True),
        sa.Column("status", sa.String(length=255), nullable=True, index=True),
        sa.Column("online", sa.Boolean, nullable=True, default=False),
        sa.Column("last_online_at", sa.DateTime, nullable=True, index=True),
        sa.Column("data_frequency", sa.String(length=255), nullable=True),
        sa.Column("installation_date", sa.Date, nullable=True),
        sa.Column("last_maintenance_date", sa.Date, nullable=True),
        sa.Column("meta", sa.JSON, nullable=True),
        sa.Column("data", sa.JSON, nullable=True),
        sa.Column("options", sa.JSON, nullable=True),
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column("slug", sa.String(length=255), nullable=True, index=True),
        sa.Column("photo_uuid", sa.String(length=36), nullable=True),
        sa.Column("warranty_uuid", sa.String(length=36), nullable=True),
        sa.Column("deleted_at", sa.DateTime, nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=True, index=True),
        sa.Column("updated_at", sa.DateTime, nullable=True),
    )
    op.create_index("devices_attachable_idx", "devices", ["attachable_type", "attachable_uuid"])
    
    # Device events table (telemetry ingestion)
    op.create_table(
        "device_events",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("_key", sa.String(length=255), nullable=True, index=True),
        sa.Column("uuid", sa.String(length=191), nullable=True, unique=True, index=True),
        sa.Column("public_id", sa.String(length=191), nullable=True, unique=True, index=True),
        sa.Column("company_uuid", sa.String(length=36), nullable=True, index=True),
        sa.Column("device_uuid", sa.String(length=36), nullable=True, index=True),
        sa.Column("ident", sa.String(length=255), nullable=True),
        sa.Column("event_type", sa.String(length=255), nullable=True, index=True),
        sa.Column("severity", sa.String(length=50), nullable=True, index=True),
        sa.Column("protocol", sa.String(length=255), nullable=True),
        sa.Column("provider", sa.String(length=255), nullable=True),
        sa.Column("payload", sa.JSON, nullable=True),
        sa.Column("meta", sa.JSON, nullable=True),
        sa.Column("latitude", sa.String(length=255), nullable=True),
        sa.Column("longitude", sa.String(length=255), nullable=True),
        sa.Column("code", sa.String(length=255), nullable=True),
        sa.Column("reason", sa.String(length=500), nullable=True),
        sa.Column("comment", sa.Text, nullable=True),
        sa.Column("state", sa.String(length=255), nullable=True),
        sa.Column("mileage", sa.Integer, nullable=True),
        sa.Column("processed_at", sa.DateTime, nullable=True, index=True),
        sa.Column("resolved_at", sa.DateTime, nullable=True),
        sa.Column("occurred_at", sa.DateTime, nullable=True, index=True),
        sa.Column("slug", sa.String(length=255), nullable=True),
        sa.Column("deleted_at", sa.DateTime, nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=True, index=True),
        sa.Column("updated_at", sa.DateTime, nullable=True),
    )


def downgrade() -> None:
    op.drop_table("device_events")
    op.drop_table("devices")
    op.drop_table("telematics")

