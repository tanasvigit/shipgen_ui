"""FleetOps core tables: orders, drivers, vehicles (subset matching Laravel migrations)
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0002_fleetops_core"
down_revision: Union[str, None] = "0001_core_users_companies"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "orders",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("_key", sa.String(length=255), nullable=True),
        sa.Column("uuid", sa.String(length=191), nullable=True),
        sa.Column("public_id", sa.String(length=191), nullable=True),
        sa.Column("company_uuid", sa.String(length=36), nullable=True, index=True),
        sa.Column("created_by_uuid", sa.String(length=36), nullable=True),
        sa.Column("updated_by_uuid", sa.String(length=36), nullable=True),
        sa.Column("internal_id", sa.String(length=255), nullable=True),
        sa.Column("customer_uuid", sa.String(length=36), nullable=True),
        sa.Column("customer_type", sa.String(length=255), nullable=True),
        sa.Column("facilitator_uuid", sa.String(length=36), nullable=True),
        sa.Column("facilitator_type", sa.String(length=255), nullable=True),
        sa.Column("session_uuid", sa.String(length=36), nullable=True),
        sa.Column("payload_uuid", sa.String(length=36), nullable=True),
        sa.Column("route_uuid", sa.String(length=36), nullable=True),
        sa.Column("transaction_uuid", sa.String(length=36), nullable=True),
        sa.Column("purchase_rate_uuid", sa.String(length=36), nullable=True),
        sa.Column("tracking_number_uuid", sa.String(length=36), nullable=True),
        sa.Column("driver_assigned_uuid", sa.String(length=36), nullable=True),
        sa.Column("meta", sa.JSON, nullable=True),
        sa.Column("options", sa.JSON, nullable=True),
        sa.Column("dispatched", sa.Boolean, nullable=False, server_default=sa.text("FALSE")),
        sa.Column("dispatched_at", sa.DateTime, nullable=True),
        sa.Column("adhoc", sa.Boolean, nullable=False, server_default=sa.text("FALSE")),
        sa.Column("adhoc_distance", sa.Integer, nullable=True),
        sa.Column("started", sa.Boolean, nullable=False, server_default=sa.text("FALSE")),
        sa.Column("started_at", sa.DateTime, nullable=True),
        sa.Column("distance", sa.Integer, nullable=True),
        sa.Column("time", sa.Integer, nullable=True),
        sa.Column("pod_required", sa.Boolean, nullable=True),
        sa.Column("is_route_optimized", sa.Boolean, nullable=False, server_default=sa.text("FALSE")),
        sa.Column("pod_method", sa.String(length=255), nullable=True),
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column("scheduled_at", sa.DateTime, nullable=True),
        sa.Column("type", sa.String(length=255), nullable=True),
        sa.Column("status", sa.String(length=191), nullable=True),
        sa.Column("deleted_at", sa.DateTime, nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=True),
        sa.Column("updated_at", sa.DateTime, nullable=True),
    )
    op.create_index("orders_uuid_index", "orders", ["uuid"], unique=False)
    op.create_index("orders_public_id_index", "orders", ["public_id"], unique=False)
    op.create_index("orders_company_uuid_index", "orders", ["company_uuid"], unique=False)
    op.create_index("orders_status_index", "orders", ["status"], unique=False)
    op.create_index("orders_dispatched_at_index", "orders", ["dispatched_at"], unique=False)
    op.create_index("orders_scheduled_at_index", "orders", ["scheduled_at"], unique=False)

    op.create_table(
        "drivers",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("_key", sa.String(length=255), nullable=True),
        sa.Column("uuid", sa.String(length=191), nullable=True),
        sa.Column("public_id", sa.String(length=191), nullable=True),
        sa.Column("internal_id", sa.String(length=255), nullable=True),
        sa.Column("company_uuid", sa.String(length=36), nullable=True),
        sa.Column("vehicle_uuid", sa.String(length=36), nullable=True),
        sa.Column("vendor_uuid", sa.String(length=36), nullable=True),
        sa.Column("vendor_type", sa.String(length=255), nullable=True),
        sa.Column("current_job_uuid", sa.String(length=36), nullable=True),
        sa.Column("user_uuid", sa.String(length=36), nullable=True),
        sa.Column("auth_token", sa.String(length=255), nullable=True),
        sa.Column("drivers_license_number", sa.String(length=255), nullable=True),
        sa.Column("signup_token_used", sa.String(length=255), nullable=True),
        sa.Column("latitude", sa.String(length=255), nullable=True),
        sa.Column("longitude", sa.String(length=255), nullable=True),
        sa.Column("heading", sa.String(length=255), nullable=True),
        sa.Column("bearing", sa.String(length=255), nullable=True),
        sa.Column("speed", sa.String(length=255), nullable=True),
        sa.Column("altitude", sa.String(length=255), nullable=True),
        sa.Column("country", sa.String(length=255), nullable=True),
        sa.Column("city", sa.String(length=255), nullable=True),
        sa.Column("currency", sa.String(length=255), nullable=True),
        sa.Column("online", sa.Integer, nullable=False, server_default="0"),
        sa.Column("status", sa.String(length=191), nullable=True),
        sa.Column("slug", sa.String(length=191), nullable=True),
        sa.Column("deleted_at", sa.DateTime, nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=True),
        sa.Column("updated_at", sa.DateTime, nullable=True),
    )
    op.create_index("drivers_uuid_index", "drivers", ["uuid"], unique=False)
    op.create_index("drivers_public_id_unique", "drivers", ["public_id"], unique=True)
    op.create_index("drivers_company_uuid_index", "drivers", ["company_uuid"], unique=False)
    op.create_index("drivers_status_index", "drivers", ["status"], unique=False)
    op.create_index("drivers_slug_index", "drivers", ["slug"], unique=False)

    op.create_table(
        "vehicles",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("_key", sa.String(length=255), nullable=True),
        sa.Column("uuid", sa.String(length=191), nullable=True),
        sa.Column("public_id", sa.String(length=191), nullable=True),
        sa.Column("company_uuid", sa.String(length=36), nullable=True),
        sa.Column("vendor_uuid", sa.String(length=36), nullable=True),
        sa.Column("photo_uuid", sa.String(length=36), nullable=True),
        sa.Column("avatar_url", sa.String(length=300), nullable=True),
        sa.Column("make", sa.String(length=191), nullable=True),
        sa.Column("model", sa.String(length=191), nullable=True),
        sa.Column("year", sa.String(length=191), nullable=True),
        sa.Column("trim", sa.String(length=191), nullable=True),
        sa.Column("type", sa.String(length=255), nullable=True),
        sa.Column("plate_number", sa.String(length=255), nullable=True),
        sa.Column("vin", sa.String(length=255), nullable=True),
        sa.Column("vin_data", sa.Text, nullable=True),
        sa.Column("meta", sa.JSON, nullable=True),
        sa.Column("status", sa.String(length=255), nullable=True),
        sa.Column("slug", sa.String(length=191), nullable=True),
        sa.Column("deleted_at", sa.DateTime, nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=True),
        sa.Column("updated_at", sa.DateTime, nullable=True),
    )
    op.create_index("vehicles_uuid_index", "vehicles", ["uuid"], unique=False)
    op.create_index("vehicles_public_id_unique", "vehicles", ["public_id"], unique=True)
    op.create_index("vehicles_company_uuid_index", "vehicles", ["company_uuid"], unique=False)
    op.create_index("vehicles_slug_index", "vehicles", ["slug"], unique=False)


def downgrade() -> None:
    op.drop_table("vehicles")
    op.drop_table("drivers")
    op.drop_table("orders")



