"""Service rates and service quotes tables for distance-based pricing
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0007_service_rates_and_quotes"
down_revision: Union[str, None] = "0006_fleetops_contacts"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Service rates table
    op.create_table(
        "service_rates",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("_key", sa.String(length=255), nullable=True),
        sa.Column("uuid", sa.String(length=191), nullable=True, unique=True, index=True),
        sa.Column("public_id", sa.String(length=191), nullable=True, unique=True, index=True),
        sa.Column("company_uuid", sa.String(length=36), nullable=True, index=True),
        sa.Column("service_area_uuid", sa.String(length=36), nullable=True, index=True),
        sa.Column("zone_uuid", sa.String(length=36), nullable=True, index=True),
        sa.Column("service_name", sa.String(length=255), nullable=True),
        sa.Column("service_type", sa.String(length=191), nullable=True, index=True),
        
        # Pricing fields
        sa.Column("base_fee", sa.Integer, nullable=True, default=0),
        sa.Column("per_meter_flat_rate_fee", sa.Integer, nullable=True, default=0),
        sa.Column("per_meter_unit", sa.String(length=50), nullable=True),
        sa.Column("algorithm", sa.String(length=255), nullable=True),
        sa.Column("rate_calculation_method", sa.String(length=50), nullable=True),
        
        # COD fields
        sa.Column("has_cod_fee", sa.Boolean, nullable=True, default=False),
        sa.Column("cod_calculation_method", sa.String(length=50), nullable=True),
        sa.Column("cod_flat_fee", sa.Integer, nullable=True, default=0),
        sa.Column("cod_percent", sa.Integer, nullable=True, default=0),
        
        # Peak hours fields
        sa.Column("has_peak_hours_fee", sa.Boolean, nullable=True, default=False),
        sa.Column("peak_hours_calculation_method", sa.String(length=50), nullable=True),
        sa.Column("peak_hours_flat_fee", sa.Integer, nullable=True, default=0),
        sa.Column("peak_hours_percent", sa.Integer, nullable=True, default=0),
        sa.Column("peak_hours_start", sa.String(length=50), nullable=True),
        sa.Column("peak_hours_end", sa.String(length=50), nullable=True),
        
        # Distance limits
        sa.Column("max_distance", sa.Integer, nullable=True),
        sa.Column("max_distance_unit", sa.String(length=50), nullable=True),
        
        # Other fields
        sa.Column("currency", sa.String(length=10), nullable=True, default="USD"),
        sa.Column("duration_terms", sa.String(length=255), nullable=True),
        sa.Column("estimated_days", sa.Integer, nullable=True, default=0),
        sa.Column("meta", sa.JSON, nullable=True),
        
        sa.Column("deleted_at", sa.DateTime, nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=True, index=True),
        sa.Column("updated_at", sa.DateTime, nullable=True),
    )
    
    # Service rate fees table (distance tiers)
    op.create_table(
        "service_rate_fees",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("_key", sa.String(length=255), nullable=True),
        sa.Column("uuid", sa.String(length=191), nullable=True, unique=True, index=True),
        sa.Column("service_rate_uuid", sa.String(length=36), nullable=True, index=True),
        sa.Column("distance", sa.Integer, nullable=True),
        sa.Column("distance_unit", sa.String(length=50), nullable=True),
        sa.Column("min", sa.Integer, nullable=True),
        sa.Column("max", sa.Integer, nullable=True),
        sa.Column("unit", sa.String(length=50), nullable=True),
        sa.Column("fee", sa.Integer, nullable=True),
        sa.Column("currency", sa.String(length=10), nullable=True),
        sa.Column("deleted_at", sa.DateTime, nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=True, index=True),
        sa.Column("updated_at", sa.DateTime, nullable=True),
    )
    
    # Service quotes table
    op.create_table(
        "service_quotes",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("_key", sa.String(length=255), nullable=True),
        sa.Column("uuid", sa.String(length=191), nullable=True, unique=True, index=True),
        sa.Column("public_id", sa.String(length=191), nullable=True, unique=True, index=True),
        sa.Column("request_id", sa.String(length=191), nullable=True, index=True),
        sa.Column("company_uuid", sa.String(length=36), nullable=True, index=True),
        sa.Column("service_rate_uuid", sa.String(length=36), nullable=True, index=True),
        sa.Column("amount", sa.Integer, nullable=True),
        sa.Column("currency", sa.String(length=10), nullable=True),
        sa.Column("meta", sa.JSON, nullable=True),
        sa.Column("expired_at", sa.DateTime, nullable=True),
        sa.Column("deleted_at", sa.DateTime, nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=True, index=True),
        sa.Column("updated_at", sa.DateTime, nullable=True),
    )
    
    # Service quote items table
    op.create_table(
        "service_quote_items",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("_key", sa.String(length=255), nullable=True),
        sa.Column("uuid", sa.String(length=191), nullable=True, unique=True, index=True),
        sa.Column("service_quote_uuid", sa.String(length=36), nullable=True, index=True),
        sa.Column("amount", sa.Integer, nullable=True),
        sa.Column("currency", sa.String(length=10), nullable=True),
        sa.Column("details", sa.String(length=500), nullable=True),
        sa.Column("code", sa.String(length=50), nullable=True),
        sa.Column("deleted_at", sa.DateTime, nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=True, index=True),
        sa.Column("updated_at", sa.DateTime, nullable=True),
    )


def downgrade() -> None:
    op.drop_table("service_quote_items")
    op.drop_table("service_quotes")
    op.drop_table("service_rate_fees")
    op.drop_table("service_rates")

