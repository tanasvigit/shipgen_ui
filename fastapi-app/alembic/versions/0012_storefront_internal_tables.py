"""Storefront internal tables: store-hours, product-hours, product-variants, product-variant-options, product-addons, product-addon-categories, notification-channels, votes, catalogs, catalog-hours
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0012_storefront_int"
down_revision: Union[str, None] = "0011_storefront_complete"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Store hours table
    op.create_table(
        "store_hours",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("uuid", sa.String(length=36), nullable=True, unique=True),
        sa.Column("store_location_uuid", sa.String(length=36), nullable=True, index=True),
        sa.Column("day_of_week", sa.String(length=255), nullable=True),
        sa.Column("start", sa.Time, nullable=False),
        sa.Column("end", sa.Time, nullable=False),
        sa.Column("deleted_at", sa.DateTime, nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=True),
        sa.Column("updated_at", sa.DateTime, nullable=True),
    )

    # Product hours table
    op.create_table(
        "product_hours",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("uuid", sa.String(length=36), nullable=True, unique=True),
        sa.Column("product_uuid", sa.String(length=191), nullable=True, index=True),
        sa.Column("day_of_week", sa.String(length=255), nullable=True),
        sa.Column("start", sa.Time, nullable=False),
        sa.Column("end", sa.Time, nullable=False),
        sa.Column("deleted_at", sa.DateTime, nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=True),
        sa.Column("updated_at", sa.DateTime, nullable=True),
    )

    # Product variants table
    op.create_table(
        "product_variants",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("uuid", sa.String(length=36), nullable=True, unique=True),
        sa.Column("public_id", sa.String(length=191), nullable=True, index=True),
        sa.Column("product_uuid", sa.String(length=191), nullable=True, index=True),
        sa.Column("name", sa.String(length=255), nullable=True),
        sa.Column("description", sa.String(length=255), nullable=True),
        sa.Column("translations", sa.JSON, nullable=True),
        sa.Column("meta", sa.JSON, nullable=True),
        sa.Column("is_multiselect", sa.Boolean, nullable=True, default=False),
        sa.Column("is_required", sa.Boolean, nullable=True, default=False),
        sa.Column("min", sa.Integer, nullable=True, default=0),
        sa.Column("max", sa.Integer, nullable=True, default=1),
        sa.Column("slug", sa.String(length=191), nullable=True, index=True),
        sa.Column("deleted_at", sa.DateTime, nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=True),
        sa.Column("updated_at", sa.DateTime, nullable=True),
    )

    # Product variant options table
    op.create_table(
        "product_variant_options",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("uuid", sa.String(length=36), nullable=True, unique=True),
        sa.Column("public_id", sa.String(length=191), nullable=True, index=True),
        sa.Column("product_variant_uuid", sa.String(length=191), nullable=True, index=True),
        sa.Column("name", sa.String(length=255), nullable=True),
        sa.Column("description", sa.String(length=255), nullable=True),
        sa.Column("translations", sa.JSON, nullable=True),
        sa.Column("meta", sa.JSON, nullable=True),
        sa.Column("additional_cost", sa.Integer, nullable=True, default=0),
        sa.Column("deleted_at", sa.DateTime, nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=True),
        sa.Column("updated_at", sa.DateTime, nullable=True),
    )

    # Product addons table
    op.create_table(
        "product_addons",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("uuid", sa.String(length=36), nullable=True, unique=True),
        sa.Column("public_id", sa.String(length=191), nullable=True, index=True),
        sa.Column("created_by_uuid", sa.String(length=191), nullable=True, index=True),
        sa.Column("category_uuid", sa.String(length=191), nullable=True, index=True),
        sa.Column("name", sa.String(length=255), nullable=True),
        sa.Column("description", sa.String(length=255), nullable=True),
        sa.Column("translations", sa.JSON, nullable=True),
        sa.Column("price", sa.Integer, nullable=True, default=0),
        sa.Column("sale_price", sa.Integer, nullable=True, default=0),
        sa.Column("is_on_sale", sa.Boolean, nullable=True, default=False),
        sa.Column("slug", sa.String(length=191), nullable=True, index=True),
        sa.Column("deleted_at", sa.DateTime, nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=True),
        sa.Column("updated_at", sa.DateTime, nullable=True),
    )

    # Product addon categories table
    op.create_table(
        "product_addon_categories",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("uuid", sa.String(length=36), nullable=True, unique=True),
        sa.Column("product_uuid", sa.String(length=191), nullable=True, index=True),
        sa.Column("category_uuid", sa.String(length=191), nullable=True, index=True),
        sa.Column("excluded_addons", sa.JSON, nullable=True),
        sa.Column("max_selectable", sa.Integer, nullable=True),
        sa.Column("is_required", sa.Boolean, nullable=True, default=False),
        sa.Column("deleted_at", sa.DateTime, nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=True),
        sa.Column("updated_at", sa.DateTime, nullable=True),
    )

    # Notification channels table
    op.create_table(
        "notification_channels",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("uuid", sa.String(length=36), nullable=True, index=True),
        sa.Column("company_uuid", sa.String(length=36), nullable=True, index=True),
        sa.Column("created_by_uuid", sa.String(length=36), nullable=True, index=True),
        sa.Column("owner_uuid", sa.String(length=191), nullable=True),
        sa.Column("owner_type", sa.String(length=191), nullable=True),
        sa.Column("certificate_uuid", sa.String(length=36), nullable=True, index=True),
        sa.Column("config", sa.JSON, nullable=True),
        sa.Column("options", sa.JSON, nullable=True),
        sa.Column("name", sa.String(length=255), nullable=True),
        sa.Column("scheme", sa.String(length=255), nullable=True),
        sa.Column("app_key", sa.String(length=255), nullable=True),
        sa.Column("deleted_at", sa.DateTime, nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=True),
        sa.Column("updated_at", sa.DateTime, nullable=True),
    )

    # Votes table
    op.create_table(
        "votes",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("uuid", sa.String(length=36), nullable=True, unique=True),
        sa.Column("public_id", sa.String(length=191), nullable=True, unique=True),
        sa.Column("created_by_uuid", sa.String(length=191), nullable=True, index=True),
        sa.Column("customer_uuid", sa.String(length=36), nullable=True, index=True),
        sa.Column("subject_uuid", sa.String(length=36), nullable=True),
        sa.Column("subject_type", sa.String(length=191), nullable=True),
        sa.Column("type", sa.String(length=255), nullable=True),
        sa.Column("deleted_at", sa.DateTime, nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=True),
        sa.Column("updated_at", sa.DateTime, nullable=True),
    )

    # Catalogs table
    op.create_table(
        "catalogs",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("uuid", sa.String(length=36), nullable=True, unique=True),
        sa.Column("public_id", sa.String(length=191), nullable=True, unique=True),
        sa.Column("store_uuid", sa.String(length=36), nullable=True),
        sa.Column("company_uuid", sa.String(length=36), nullable=True),
        sa.Column("created_by_uuid", sa.String(length=36), nullable=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("status", sa.String(length=255), nullable=True, default="draft"),
        sa.Column("meta", sa.JSON, nullable=True),
        sa.Column("deleted_at", sa.DateTime, nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=True),
        sa.Column("updated_at", sa.DateTime, nullable=True),
    )

    # Catalog hours table
    op.create_table(
        "catalog_hours",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("uuid", sa.String(length=36), nullable=True, unique=True),
        sa.Column("catalog_uuid", sa.String(length=36), nullable=True),
        sa.Column("day_of_week", sa.String(length=255), nullable=False),
        sa.Column("start", sa.Time, nullable=True),
        sa.Column("end", sa.Time, nullable=True),
        sa.Column("deleted_at", sa.DateTime, nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=True),
        sa.Column("updated_at", sa.DateTime, nullable=True),
    )


def downgrade() -> None:
    op.drop_table("catalog_hours")
    op.drop_table("catalogs")
    op.drop_table("votes")
    op.drop_table("notification_channels")
    op.drop_table("product_addon_categories")
    op.drop_table("product_addons")
    op.drop_table("product_variant_options")
    op.drop_table("product_variants")
    op.drop_table("product_hours")
    op.drop_table("store_hours")

