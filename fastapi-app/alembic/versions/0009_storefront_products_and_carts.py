"""Storefront products and carts tables
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0009_storefront_core"
down_revision: Union[str, None] = "0008_telematics_and_devices"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Products table
    op.create_table(
        "products",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("uuid", sa.String(length=36), nullable=True, unique=True, index=True),
        sa.Column("public_id", sa.String(length=191), nullable=True, unique=True, index=True),
        sa.Column("company_uuid", sa.String(length=191), nullable=True, index=True),
        sa.Column("created_by_uuid", sa.String(length=191), nullable=True, index=True),
        sa.Column("primary_image_uuid", sa.String(length=191), nullable=True, index=True),
        sa.Column("store_uuid", sa.String(length=191), nullable=True, index=True),
        sa.Column("category_uuid", sa.String(length=191), nullable=True, index=True),
        sa.Column("name", sa.String(length=255), nullable=True),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("tags", sa.JSON, nullable=True),
        sa.Column("meta", sa.JSON, nullable=True),
        sa.Column("translations", sa.JSON, nullable=True),
        sa.Column("youtube_urls", sa.JSON, nullable=True),
        sa.Column("qr_code", sa.Text, nullable=True),
        sa.Column("barcode", sa.Text, nullable=True),
        sa.Column("sku", sa.String(length=255), nullable=True),
        sa.Column("price", sa.Integer, nullable=True, default=0),
        sa.Column("sale_price", sa.Integer, nullable=True, default=0),
        sa.Column("currency", sa.String(length=10), nullable=True, index=True),
        sa.Column("is_on_sale", sa.Boolean, nullable=True, default=False),
        sa.Column("is_service", sa.Boolean, nullable=True, default=False, index=True),
        sa.Column("is_bookable", sa.Boolean, nullable=True, default=False),
        sa.Column("is_available", sa.Boolean, nullable=True, default=True, index=True),
        sa.Column("is_recommended", sa.Boolean, nullable=True, default=False),
        sa.Column("can_pickup", sa.Boolean, nullable=True, default=False),
        sa.Column("status", sa.String(length=50), nullable=True, index=True),
        sa.Column("slug", sa.String(length=191), nullable=True, index=True),
        sa.Column("deleted_at", sa.DateTime, nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=True),
        sa.Column("updated_at", sa.DateTime, nullable=True),
    )
    
    # Carts table
    op.create_table(
        "carts",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("uuid", sa.String(length=36), nullable=True, unique=True, index=True),
        sa.Column("public_id", sa.String(length=191), nullable=True, unique=True, index=True),
        sa.Column("company_uuid", sa.String(length=36), nullable=True, index=True),
        sa.Column("user_uuid", sa.String(length=36), nullable=True, index=True),
        sa.Column("checkout_uuid", sa.String(length=36), nullable=True, index=True),
        sa.Column("customer_id", sa.String(length=255), nullable=True),
        sa.Column("unique_identifier", sa.String(length=255), nullable=True, index=True),
        sa.Column("currency", sa.String(length=10), nullable=True),
        sa.Column("discount_code", sa.String(length=255), nullable=True),
        sa.Column("items", sa.JSON, nullable=True),
        sa.Column("events", sa.JSON, nullable=True),
        sa.Column("expires_at", sa.DateTime, nullable=True, index=True),
        sa.Column("deleted_at", sa.DateTime, nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=True),
        sa.Column("updated_at", sa.DateTime, nullable=True),
    )


def downgrade() -> None:
    op.drop_table("carts")
    op.drop_table("products")

