"""Storefront: reviews, food-trucks, stores, networks, checkouts, gateways, store-locations, network-stores, categories
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0011_storefront_complete"
down_revision: Union[str, None] = "0010_fleetops_expanded"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Categories table (core model, used by storefront)
    op.create_table(
        "categories",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("_key", sa.String(length=255), nullable=True),
        sa.Column("uuid", sa.String(length=191), nullable=True, index=True),
        sa.Column("public_id", sa.String(length=191), nullable=True, index=True),
        sa.Column("company_uuid", sa.String(length=36), nullable=True, index=True),
        sa.Column("parent_uuid", sa.String(length=36), nullable=True, index=True),
        sa.Column("owner_uuid", sa.String(length=36), nullable=True),
        sa.Column("owner_type", sa.String(length=255), nullable=True),
        sa.Column("name", sa.String(length=255), nullable=True),
        sa.Column("internal_id", sa.String(length=255), nullable=True),
        sa.Column("description", sa.String(length=255), nullable=True),
        sa.Column("translations", sa.JSON, nullable=True),
        sa.Column("tags", sa.JSON, nullable=True),
        sa.Column("meta", sa.JSON, nullable=True),
        sa.Column("icon", sa.String(length=255), nullable=True),
        sa.Column("icon_color", sa.String(length=255), nullable=True),
        sa.Column("icon_file_uuid", sa.String(length=36), nullable=True, index=True),
        sa.Column("for_field", sa.String(length=255), nullable=True),  # 'for' is Python keyword
        sa.Column("slug", sa.String(length=255), nullable=True),
        sa.Column("order", sa.String(length=255), nullable=True),
        sa.Column("deleted_at", sa.DateTime, nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=True, index=True),
        sa.Column("updated_at", sa.DateTime, nullable=True),
    )
    op.create_index("categories_uuid_index", "categories", ["uuid"], unique=True)

    # Reviews table
    op.create_table(
        "reviews",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("uuid", sa.String(length=36), nullable=True, unique=True),
        sa.Column("public_id", sa.String(length=191), nullable=True, unique=True),
        sa.Column("created_by_uuid", sa.String(length=36), nullable=True, index=True),
        sa.Column("customer_uuid", sa.String(length=36), nullable=True, index=True),
        sa.Column("subject_uuid", sa.String(length=36), nullable=True),
        sa.Column("subject_type", sa.String(length=255), nullable=True),
        sa.Column("rating", sa.Integer, nullable=True),
        sa.Column("content", sa.Text, nullable=True),
        sa.Column("rejected", sa.Boolean, default=False),
        sa.Column("deleted_at", sa.DateTime, nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=True),
        sa.Column("updated_at", sa.DateTime, nullable=True),
    )

    # Food trucks table
    op.create_table(
        "food_trucks",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("uuid", sa.String(length=36), nullable=True, unique=True),
        sa.Column("public_id", sa.String(length=191), nullable=True, unique=True),
        sa.Column("vehicle_uuid", sa.String(length=36), nullable=True),
        sa.Column("store_uuid", sa.String(length=36), nullable=True),
        sa.Column("company_uuid", sa.String(length=36), nullable=True),
        sa.Column("created_by_uuid", sa.String(length=36), nullable=True),
        sa.Column("service_area_uuid", sa.String(length=36), nullable=True),
        sa.Column("zone_uuid", sa.String(length=36), nullable=True),
        sa.Column("status", sa.String(length=255), default="inactive"),
        sa.Column("deleted_at", sa.DateTime, nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=True),
        sa.Column("updated_at", sa.DateTime, nullable=True),
    )

    # Stores table
    op.create_table(
        "stores",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("uuid", sa.String(length=36), nullable=True, unique=True),
        sa.Column("public_id", sa.String(length=191), nullable=True, index=True),
        sa.Column("created_by_uuid", sa.String(length=36), nullable=True, index=True),
        sa.Column("company_uuid", sa.String(length=36), nullable=True, index=True),
        sa.Column("logo_uuid", sa.String(length=36), nullable=True, index=True),
        sa.Column("backdrop_uuid", sa.String(length=36), nullable=True, index=True),
        sa.Column("order_config_uuid", sa.String(length=36), nullable=True),
        sa.Column("key", sa.Text, nullable=True),
        sa.Column("online", sa.Boolean, default=True, index=True),
        sa.Column("name", sa.String(length=255), nullable=True),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("phone", sa.String(length=255), nullable=True),
        sa.Column("email", sa.String(length=255), nullable=True),
        sa.Column("website", sa.String(length=255), nullable=True),
        sa.Column("facebook", sa.String(length=255), nullable=True),
        sa.Column("instagram", sa.String(length=255), nullable=True),
        sa.Column("twitter", sa.String(length=255), nullable=True),
        sa.Column("tags", sa.JSON, nullable=True),
        sa.Column("translations", sa.JSON, nullable=True),
        sa.Column("currency", sa.String(length=255), nullable=True),
        sa.Column("timezone", sa.String(length=255), nullable=True),
        sa.Column("pod_method", sa.String(length=255), nullable=True),
        sa.Column("options", sa.JSON, nullable=True),
        sa.Column("alertable", sa.JSON, nullable=True),
        sa.Column("meta", sa.JSON, nullable=True),
        sa.Column("slug", sa.String(length=191), nullable=True, index=True),
        sa.Column("deleted_at", sa.DateTime, nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=True),
        sa.Column("updated_at", sa.DateTime, nullable=True),
    )

    # Networks table
    op.create_table(
        "networks",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("uuid", sa.String(length=36), nullable=True, unique=True),
        sa.Column("public_id", sa.String(length=191), nullable=True, index=True),
        sa.Column("created_by_uuid", sa.String(length=36), nullable=True, index=True),
        sa.Column("company_uuid", sa.String(length=36), nullable=True, index=True),
        sa.Column("logo_uuid", sa.String(length=36), nullable=True, index=True),
        sa.Column("backdrop_uuid", sa.String(length=36), nullable=True, index=True),
        sa.Column("order_config_uuid", sa.String(length=36), nullable=True),
        sa.Column("key", sa.Text, nullable=True),
        sa.Column("online", sa.Boolean, default=True, index=True),
        sa.Column("name", sa.String(length=255), nullable=True),
        sa.Column("description", sa.String(length=255), nullable=True),
        sa.Column("phone", sa.String(length=255), nullable=True),
        sa.Column("email", sa.String(length=255), nullable=True),
        sa.Column("website", sa.String(length=255), nullable=True),
        sa.Column("facebook", sa.String(length=255), nullable=True),
        sa.Column("instagram", sa.String(length=255), nullable=True),
        sa.Column("twitter", sa.String(length=255), nullable=True),
        sa.Column("tags", sa.JSON, nullable=True),
        sa.Column("translations", sa.JSON, nullable=True),
        sa.Column("currency", sa.String(length=255), nullable=True),
        sa.Column("timezone", sa.String(length=255), nullable=True),
        sa.Column("pod_method", sa.String(length=255), nullable=True),
        sa.Column("options", sa.JSON, nullable=True),
        sa.Column("alertable", sa.JSON, nullable=True),
        sa.Column("slug", sa.String(length=191), nullable=True, index=True),
        sa.Column("deleted_at", sa.DateTime, nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=True),
        sa.Column("updated_at", sa.DateTime, nullable=True),
    )

    # Checkouts table
    op.create_table(
        "checkouts",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("uuid", sa.String(length=36), nullable=True, unique=True),
        sa.Column("public_id", sa.String(length=191), nullable=True, index=True),
        sa.Column("company_uuid", sa.String(length=36), nullable=True, index=True),
        sa.Column("order_uuid", sa.String(length=36), nullable=True, index=True),
        sa.Column("cart_uuid", sa.String(length=36), nullable=True, index=True),
        sa.Column("store_uuid", sa.String(length=36), nullable=True, index=True),
        sa.Column("network_uuid", sa.String(length=36), nullable=True, index=True),
        sa.Column("gateway_uuid", sa.String(length=36), nullable=True, index=True),
        sa.Column("service_quote_uuid", sa.String(length=36), nullable=True, index=True),
        sa.Column("owner_uuid", sa.String(length=36), nullable=True),
        sa.Column("owner_type", sa.String(length=255), nullable=True),
        sa.Column("token", sa.String(length=255), nullable=True),
        sa.Column("amount", sa.Integer, nullable=True),
        sa.Column("currency", sa.String(length=255), nullable=True),
        sa.Column("is_cod", sa.Boolean, default=False),
        sa.Column("is_pickup", sa.Boolean, default=False),
        sa.Column("options", sa.JSON, nullable=True),
        sa.Column("cart_state", sa.JSON, nullable=True),
        sa.Column("captured", sa.Boolean, default=False),
        sa.Column("deleted_at", sa.DateTime, nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=True),
        sa.Column("updated_at", sa.DateTime, nullable=True),
    )

    # Gateways table
    op.create_table(
        "gateways",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("uuid", sa.String(length=36), nullable=True, unique=True),
        sa.Column("public_id", sa.String(length=191), nullable=True, index=True),
        sa.Column("company_uuid", sa.String(length=36), nullable=True, index=True),
        sa.Column("created_by_uuid", sa.String(length=36), nullable=True, index=True),
        sa.Column("logo_file_uuid", sa.String(length=36), nullable=True, index=True),
        sa.Column("owner_uuid", sa.String(length=36), nullable=True),
        sa.Column("owner_type", sa.String(length=255), nullable=True),
        sa.Column("name", sa.String(length=255), nullable=True),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("code", sa.String(length=255), nullable=True),
        sa.Column("type", sa.String(length=255), nullable=True),
        sa.Column("sandbox", sa.Boolean, default=False, index=True),
        sa.Column("meta", sa.JSON, nullable=True),
        sa.Column("config", sa.JSON, nullable=True),
        sa.Column("return_url", sa.String(length=255), nullable=True),
        sa.Column("callback_url", sa.String(length=255), nullable=True),
        sa.Column("deleted_at", sa.DateTime, nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=True),
        sa.Column("updated_at", sa.DateTime, nullable=True),
    )

    # Store locations table
    op.create_table(
        "store_locations",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("uuid", sa.String(length=36), nullable=True, unique=True),
        sa.Column("public_id", sa.String(length=191), nullable=True, index=True),
        sa.Column("store_uuid", sa.String(length=36), nullable=True, index=True),
        sa.Column("created_by_uuid", sa.String(length=36), nullable=True, index=True),
        sa.Column("place_uuid", sa.String(length=36), nullable=True, index=True),
        sa.Column("name", sa.String(length=255), nullable=True),
        sa.Column("deleted_at", sa.DateTime, nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=True),
        sa.Column("updated_at", sa.DateTime, nullable=True),
    )

    # Network stores pivot table
    op.create_table(
        "network_stores",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("uuid", sa.String(length=36), nullable=True, unique=True),
        sa.Column("network_uuid", sa.String(length=36), nullable=True, index=True),
        sa.Column("store_uuid", sa.String(length=36), nullable=True, index=True),
        sa.Column("category_uuid", sa.String(length=36), nullable=True, index=True),
        sa.Column("deleted_at", sa.DateTime, nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=True),
        sa.Column("updated_at", sa.DateTime, nullable=True),
    )


def downgrade() -> None:
    op.drop_table("network_stores")
    op.drop_table("store_locations")
    op.drop_table("gateways")
    op.drop_table("checkouts")
    op.drop_table("networks")
    op.drop_table("stores")
    op.drop_table("food_trucks")
    op.drop_table("reviews")
    op.drop_table("categories")

