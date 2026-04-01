"""FleetOps: issues, fuel-reports, entities, payloads, zones, service-areas, fleets, tracking-numbers, tracking-statuses
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0010_fleetops_expanded"
down_revision: Union[str, None] = "0009_storefront_core"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Issues table
    op.create_table(
        "issues",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("_key", sa.String(length=255), nullable=True),
        sa.Column("uuid", sa.String(length=191), nullable=True, index=True),
        sa.Column("public_id", sa.String(length=191), nullable=True, unique=True),
        sa.Column("issue_id", sa.String(length=191), nullable=True, unique=True),
        sa.Column("company_uuid", sa.String(length=36), nullable=True, index=True),
        sa.Column("driver_uuid", sa.String(length=36), nullable=True, index=True),
        sa.Column("vehicle_uuid", sa.String(length=36), nullable=True, index=True),
        sa.Column("assigned_to_uuid", sa.String(length=36), nullable=True, index=True),
        sa.Column("reported_by_uuid", sa.String(length=36), nullable=True),
        sa.Column("location_latitude", sa.String(length=255), nullable=True),
        sa.Column("location_longitude", sa.String(length=255), nullable=True),
        sa.Column("latitude", sa.String(length=255), nullable=True),
        sa.Column("longitude", sa.String(length=255), nullable=True),
        sa.Column("category", sa.String(length=255), nullable=True),
        sa.Column("type", sa.String(length=255), nullable=True),
        sa.Column("report", sa.Text, nullable=True),
        sa.Column("title", sa.String(length=255), nullable=True),
        sa.Column("tags", sa.JSON, nullable=True),
        sa.Column("priority", sa.String(length=255), nullable=True),
        sa.Column("meta", sa.JSON, nullable=True),
        sa.Column("resolved_at", sa.DateTime, nullable=True),
        sa.Column("status", sa.String(length=255), nullable=True),
        sa.Column("deleted_at", sa.DateTime, nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=True, index=True),
        sa.Column("updated_at", sa.DateTime, nullable=True),
    )
    op.create_index("issues_uuid_index", "issues", ["uuid"], unique=True)

    # Fuel reports table
    op.create_table(
        "fuel_reports",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("_key", sa.String(length=255), nullable=True),
        sa.Column("uuid", sa.String(length=191), nullable=True, index=True),
        sa.Column("public_id", sa.String(length=191), nullable=True, unique=True),
        sa.Column("company_uuid", sa.String(length=36), nullable=True, index=True),
        sa.Column("driver_uuid", sa.String(length=36), nullable=True, index=True),
        sa.Column("vehicle_uuid", sa.String(length=36), nullable=True, index=True),
        sa.Column("reported_by_uuid", sa.String(length=36), nullable=True),
        sa.Column("odometer", sa.String(length=255), nullable=True),
        sa.Column("location_latitude", sa.String(length=255), nullable=True),
        sa.Column("location_longitude", sa.String(length=255), nullable=True),
        sa.Column("latitude", sa.String(length=255), nullable=True),
        sa.Column("longitude", sa.String(length=255), nullable=True),
        sa.Column("amount", sa.String(length=255), nullable=True),
        sa.Column("currency", sa.String(length=255), nullable=True),
        sa.Column("volume", sa.String(length=255), nullable=True),
        sa.Column("metric_unit", sa.String(length=255), nullable=True),
        sa.Column("report", sa.Text, nullable=True),
        sa.Column("meta", sa.JSON, nullable=True),
        sa.Column("status", sa.String(length=255), nullable=True),
        sa.Column("deleted_at", sa.DateTime, nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=True, index=True),
        sa.Column("updated_at", sa.DateTime, nullable=True),
    )
    op.create_index("fuel_reports_uuid_index", "fuel_reports", ["uuid"], unique=True)

    # Entities table
    op.create_table(
        "entities",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("_key", sa.String(length=255), nullable=True),
        sa.Column("uuid", sa.String(length=191), nullable=True, index=True),
        sa.Column("public_id", sa.String(length=191), nullable=True, index=True),
        sa.Column("payload_uuid", sa.String(length=36), nullable=True, index=True),
        sa.Column("company_uuid", sa.String(length=36), nullable=True, index=True),
        sa.Column("driver_assigned_uuid", sa.String(length=36), nullable=True, index=True),
        sa.Column("destination_uuid", sa.String(length=36), nullable=True, index=True),
        sa.Column("customer_uuid", sa.String(length=36), nullable=True),
        sa.Column("customer_type", sa.String(length=255), nullable=True),
        sa.Column("tracking_number_uuid", sa.String(length=36), nullable=True, index=True),
        sa.Column("photo_uuid", sa.Text, nullable=True),
        sa.Column("supplier_uuid", sa.String(length=36), nullable=True),
        sa.Column("category_uuid", sa.String(length=36), nullable=True),
        sa.Column("_import_id", sa.String(length=191), nullable=True, index=True),
        sa.Column("internal_id", sa.String(length=191), nullable=True, index=True),
        sa.Column("name", sa.String(length=255), nullable=True),
        sa.Column("type", sa.String(length=255), nullable=True),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("currency", sa.String(length=255), nullable=True),
        sa.Column("barcode", sa.Text, nullable=True),
        sa.Column("qr_code", sa.Text, nullable=True),
        sa.Column("weight", sa.String(length=255), nullable=True),
        sa.Column("weight_unit", sa.String(length=255), nullable=True),
        sa.Column("length", sa.String(length=255), nullable=True),
        sa.Column("width", sa.String(length=255), nullable=True),
        sa.Column("height", sa.String(length=255), nullable=True),
        sa.Column("dimensions_unit", sa.String(length=255), nullable=True),
        sa.Column("declared_value", sa.Integer, nullable=True),
        sa.Column("sku", sa.String(length=191), nullable=True, index=True),
        sa.Column("price", sa.String(length=255), nullable=True),
        sa.Column("sale_price", sa.String(length=255), nullable=True),
        sa.Column("meta", sa.JSON, nullable=True),
        sa.Column("slug", sa.String(length=255), nullable=True),
        sa.Column("deleted_at", sa.DateTime, nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=True, index=True),
        sa.Column("updated_at", sa.DateTime, nullable=True),
    )
    op.create_index("entities_uuid_index", "entities", ["uuid"], unique=True)
    op.create_index("entities_public_id_index", "entities", ["public_id"], unique=True)

    # Payloads table
    op.create_table(
        "payloads",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("_key", sa.String(length=255), nullable=True),
        sa.Column("uuid", sa.String(length=191), nullable=True, index=True),
        sa.Column("public_id", sa.String(length=191), nullable=True, index=True),
        sa.Column("company_uuid", sa.String(length=36), nullable=True, index=True),
        sa.Column("pickup_uuid", sa.String(length=36), nullable=True, index=True),
        sa.Column("dropoff_uuid", sa.String(length=36), nullable=True, index=True),
        sa.Column("return_uuid", sa.String(length=36), nullable=True, index=True),
        sa.Column("current_waypoint_uuid", sa.String(length=36), nullable=True, index=True),
        sa.Column("provider", sa.String(length=191), nullable=True, index=True),
        sa.Column("payment_method", sa.String(length=255), nullable=True),
        sa.Column("cod_amount", sa.Integer, nullable=True),
        sa.Column("cod_currency", sa.String(length=255), nullable=True),
        sa.Column("cod_payment_method", sa.String(length=255), nullable=True),
        sa.Column("type", sa.String(length=255), nullable=True),
        sa.Column("meta", sa.JSON, nullable=True),
        sa.Column("deleted_at", sa.DateTime, nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=True, index=True),
        sa.Column("updated_at", sa.DateTime, nullable=True),
    )
    op.create_index("payloads_uuid_index", "payloads", ["uuid"], unique=True)
    op.create_index("payloads_public_id_index", "payloads", ["public_id"], unique=True)

    # Zones table
    op.create_table(
        "zones",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("_key", sa.String(length=255), nullable=True),
        sa.Column("uuid", sa.String(length=191), nullable=True, index=True),
        sa.Column("public_id", sa.String(length=191), nullable=True, unique=True),
        sa.Column("company_uuid", sa.String(length=36), nullable=True, index=True),
        sa.Column("service_area_uuid", sa.String(length=36), nullable=True, index=True),
        sa.Column("name", sa.String(length=255), nullable=True),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("border", sa.JSON, nullable=True),
        sa.Column("color", sa.String(length=255), nullable=True),
        sa.Column("stroke_color", sa.String(length=255), nullable=True),
        sa.Column("status", sa.String(length=191), nullable=True, index=True),
        sa.Column("deleted_at", sa.DateTime, nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=True, index=True),
        sa.Column("updated_at", sa.DateTime, nullable=True),
    )
    op.create_index("zones_uuid_index", "zones", ["uuid"], unique=True)

    # Service areas table
    op.create_table(
        "service_areas",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("_key", sa.String(length=255), nullable=True),
        sa.Column("uuid", sa.String(length=191), nullable=True, index=True),
        sa.Column("public_id", sa.String(length=191), nullable=True, unique=True),
        sa.Column("company_uuid", sa.String(length=36), nullable=True, index=True),
        sa.Column("parent_uuid", sa.String(length=36), nullable=True, index=True),
        sa.Column("name", sa.String(length=255), nullable=True),
        sa.Column("type", sa.String(length=255), nullable=True),
        sa.Column("country", sa.String(length=255), nullable=True),
        sa.Column("border", sa.JSON, nullable=True),
        sa.Column("color", sa.String(length=255), nullable=True),
        sa.Column("stroke_color", sa.String(length=255), nullable=True),
        sa.Column("status", sa.String(length=255), nullable=True),
        sa.Column("deleted_at", sa.DateTime, nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=True, index=True),
        sa.Column("updated_at", sa.DateTime, nullable=True),
    )
    op.create_index("service_areas_uuid_index", "service_areas", ["uuid"], unique=True)

    # Fleets table
    op.create_table(
        "fleets",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("_key", sa.String(length=255), nullable=True),
        sa.Column("uuid", sa.String(length=191), nullable=True, index=True),
        sa.Column("public_id", sa.String(length=191), nullable=True, unique=True),
        sa.Column("company_uuid", sa.String(length=36), nullable=True, index=True),
        sa.Column("service_area_uuid", sa.String(length=36), nullable=True, index=True),
        sa.Column("zone_uuid", sa.String(length=36), nullable=True, index=True),
        sa.Column("image_uuid", sa.String(length=36), nullable=True),
        sa.Column("name", sa.String(length=255), nullable=True),
        sa.Column("color", sa.String(length=255), nullable=True),
        sa.Column("task", sa.String(length=255), nullable=True),
        sa.Column("status", sa.String(length=191), nullable=True, index=True),
        sa.Column("slug", sa.String(length=191), nullable=True, index=True),
        sa.Column("deleted_at", sa.DateTime, nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=True, index=True),
        sa.Column("updated_at", sa.DateTime, nullable=True),
    )
    op.create_index("fleets_uuid_index", "fleets", ["uuid"], unique=True)

    # Tracking numbers table
    op.create_table(
        "tracking_numbers",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("_key", sa.String(length=255), nullable=True),
        sa.Column("uuid", sa.String(length=191), nullable=True, index=True),
        sa.Column("public_id", sa.String(length=191), nullable=True, unique=True),
        sa.Column("company_uuid", sa.String(length=36), nullable=True, index=True),
        sa.Column("owner_uuid", sa.String(length=36), nullable=True, index=True),
        sa.Column("owner_type", sa.String(length=255), nullable=True),
        sa.Column("status_uuid", sa.String(length=36), nullable=True, index=True),
        sa.Column("tracking_number", sa.String(length=191), nullable=True, index=True),
        sa.Column("region", sa.String(length=255), nullable=True),
        sa.Column("type", sa.String(length=255), nullable=True),
        sa.Column("qr_code", sa.Text, nullable=True),
        sa.Column("barcode", sa.Text, nullable=True),
        sa.Column("deleted_at", sa.DateTime, nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=True, index=True),
        sa.Column("updated_at", sa.DateTime, nullable=True),
    )
    op.create_index("tracking_numbers_uuid_index", "tracking_numbers", ["uuid"], unique=True)

    # Tracking statuses table
    op.create_table(
        "tracking_statuses",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("_key", sa.String(length=255), nullable=True),
        sa.Column("uuid", sa.String(length=191), nullable=True, index=True),
        sa.Column("public_id", sa.String(length=191), nullable=True, index=True),
        sa.Column("company_uuid", sa.String(length=36), nullable=True, index=True),
        sa.Column("tracking_number_uuid", sa.String(length=36), nullable=True, index=True),
        sa.Column("proof_uuid", sa.String(length=36), nullable=True),
        sa.Column("meta", sa.JSON, nullable=True),
        sa.Column("status", sa.String(length=191), nullable=True, index=True),
        sa.Column("details", sa.Text, nullable=True),
        sa.Column("code", sa.String(length=255), nullable=True),
        sa.Column("city", sa.String(length=255), nullable=True),
        sa.Column("province", sa.String(length=255), nullable=True),
        sa.Column("postal_code", sa.String(length=255), nullable=True),
        sa.Column("country", sa.String(length=255), nullable=True),
        sa.Column("location_latitude", sa.String(length=255), nullable=True),
        sa.Column("location_longitude", sa.String(length=255), nullable=True),
        sa.Column("latitude", sa.String(length=255), nullable=True),
        sa.Column("longitude", sa.String(length=255), nullable=True),
        sa.Column("completed", sa.Integer, nullable=True),
        sa.Column("deleted_at", sa.DateTime, nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=True, index=True),
        sa.Column("updated_at", sa.DateTime, nullable=True),
    )
    op.create_index("tracking_statuses_uuid_index", "tracking_statuses", ["uuid"], unique=True)
    op.create_index("tracking_statuses_public_id_index", "tracking_statuses", ["public_id"], unique=True)


def downgrade() -> None:
    op.drop_table("tracking_statuses")
    op.drop_table("tracking_numbers")
    op.drop_table("fleets")
    op.drop_table("service_areas")
    op.drop_table("zones")
    op.drop_table("payloads")
    op.drop_table("entities")
    op.drop_table("fuel_reports")
    op.drop_table("issues")

