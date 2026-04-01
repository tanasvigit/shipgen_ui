"""FleetOps: contacts, vendors, places (minimal columns)
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0006_fleetops_contacts"
down_revision: Union[str, None] = "0005_notifications"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "contacts",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("_key", sa.String(length=255), nullable=True),
        sa.Column("uuid", sa.String(length=191), nullable=True, index=True),
        sa.Column("public_id", sa.String(length=191), nullable=True, index=True),
        sa.Column("internal_id", sa.String(length=255), nullable=True),
        sa.Column("company_uuid", sa.String(length=36), nullable=True, index=True),
        sa.Column("user_uuid", sa.String(length=36), nullable=True),
        sa.Column("photo_uuid", sa.String(length=36), nullable=True),
        sa.Column("name", sa.String(length=255), nullable=True),
        sa.Column("title", sa.String(length=255), nullable=True),
        sa.Column("email", sa.String(length=191), nullable=True, index=True),
        sa.Column("phone", sa.String(length=255), nullable=True),
        sa.Column("type", sa.String(length=255), nullable=True),
        sa.Column("slug", sa.String(length=255), nullable=True),
        sa.Column("meta", sa.JSON, nullable=True),
        sa.Column("deleted_at", sa.DateTime, nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=True),
        sa.Column("updated_at", sa.DateTime, nullable=True),
    )
    op.create_index("contacts_uuid_index", "contacts", ["uuid"])
    op.create_index("contacts_public_id_index", "contacts", ["public_id"])
    op.create_index("contacts_email_index", "contacts", ["email"])

    op.create_table(
        "vendors",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("_key", sa.String(length=255), nullable=True),
        sa.Column("uuid", sa.String(length=191), nullable=True, index=True),
        sa.Column("public_id", sa.String(length=191), nullable=True, index=True),
        sa.Column("company_uuid", sa.String(length=36), nullable=True, index=True),
        sa.Column("place_uuid", sa.String(length=36), nullable=True),
        sa.Column("type_uuid", sa.String(length=36), nullable=True),
        sa.Column("connect_company_uuid", sa.String(length=36), nullable=True),
        sa.Column("logo_uuid", sa.String(length=36), nullable=True),
        sa.Column("name", sa.String(length=255), nullable=True),
        sa.Column("internal_id", sa.String(length=191), nullable=True),
        sa.Column("business_id", sa.String(length=255), nullable=True),
        sa.Column("connected", sa.Integer, nullable=True),
        sa.Column("email", sa.String(length=255), nullable=True),
        sa.Column("phone", sa.String(length=255), nullable=True),
        sa.Column("website_url", sa.String(length=255), nullable=True),
        sa.Column("country", sa.String(length=255), nullable=True),
        sa.Column("meta", sa.JSON, nullable=True),
        sa.Column("callbacks", sa.JSON, nullable=True),
        sa.Column("type", sa.String(length=255), nullable=True),
        sa.Column("status", sa.String(length=255), nullable=True),
        sa.Column("slug", sa.String(length=255), nullable=True),
        sa.Column("deleted_at", sa.DateTime, nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=True),
        sa.Column("updated_at", sa.DateTime, nullable=True),
    )
    op.create_index("vendors_uuid_index", "vendors", ["uuid"])
    op.create_index("vendors_public_id_index", "vendors", ["public_id"])
    op.create_index("vendors_company_uuid_index", "vendors", ["company_uuid"])

    op.create_table(
        "places",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("_key", sa.String(length=255), nullable=True),
        sa.Column("uuid", sa.String(length=191), nullable=True, index=True),
        sa.Column("public_id", sa.String(length=191), nullable=True, index=True),
        sa.Column("_import_id", sa.String(length=191), nullable=True),
        sa.Column("company_uuid", sa.String(length=36), nullable=True, index=True),
        sa.Column("owner_uuid", sa.String(length=36), nullable=True),
        sa.Column("owner_type", sa.String(length=255), nullable=True),
        sa.Column("name", sa.String(length=255), nullable=True),
        sa.Column("street1", sa.String(length=255), nullable=True),
        sa.Column("street2", sa.String(length=255), nullable=True),
        sa.Column("city", sa.String(length=191), nullable=True),
        sa.Column("province", sa.String(length=255), nullable=True),
        sa.Column("postal_code", sa.String(length=191), nullable=True),
        sa.Column("neighborhood", sa.String(length=191), nullable=True),
        sa.Column("district", sa.String(length=191), nullable=True),
        sa.Column("building", sa.String(length=191), nullable=True),
        sa.Column("security_access_code", sa.String(length=255), nullable=True),
        sa.Column("country", sa.String(length=191), nullable=True),
        sa.Column("latitude", sa.String(length=255), nullable=True),
        sa.Column("longitude", sa.String(length=255), nullable=True),
        sa.Column("meta", sa.JSON, nullable=True),
        sa.Column("phone", sa.String(length=255), nullable=True),
        sa.Column("remarks", sa.Text, nullable=True),
        sa.Column("type", sa.String(length=191), nullable=True),
        sa.Column("deleted_at", sa.DateTime, nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=True),
        sa.Column("updated_at", sa.DateTime, nullable=True),
    )
    op.create_index("places_uuid_index", "places", ["uuid"])
    op.create_index("places_public_id_index", "places", ["public_id"])
    op.create_index("places_company_uuid_index", "places", ["company_uuid"])


def downgrade() -> None:
    op.drop_table("places")
    op.drop_table("vendors")
    op.drop_table("contacts")



