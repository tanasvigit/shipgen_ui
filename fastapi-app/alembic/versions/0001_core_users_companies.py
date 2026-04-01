"""Core tables: users, companies, company_users, api_credentials

This file is generated from the corresponding Laravel migrations:
- 2023_04_25_094301_create_users_table.php
- 2023_04_25_094305_create_companies_table.php
- 2023_04_25_094311_create_company_users_table.php
- 2023_04_25_094311_create_api_credentials_table.php
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0001_core_users_companies"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("_key", sa.String(length=255), nullable=True),
        sa.Column("uuid", sa.String(length=191), nullable=True),
        sa.Column("public_id", sa.String(length=191), nullable=True),
        sa.Column("company_uuid", sa.String(length=191), nullable=True),
        sa.Column("avatar_uuid", sa.String(length=191), nullable=True),
        sa.Column("username", sa.String(length=191), nullable=True),
        sa.Column("email", sa.String(length=255), nullable=True),
        sa.Column("phone", sa.String(length=255), nullable=True),
        sa.Column("password", sa.String(length=255), nullable=True),
        sa.Column("name", sa.String(length=255), nullable=True),
        sa.Column("date_of_birth", sa.String(length=255), nullable=True),
        sa.Column("timezone", sa.String(length=255), nullable=True),
        sa.Column("country", sa.String(length=255), nullable=True),
        sa.Column("ip_address", sa.String(length=255), nullable=True),
        sa.Column("last_login", sa.String(length=255), nullable=True),
        sa.Column("slug", sa.String(length=255), nullable=True),
        sa.Column("type", sa.String(length=191), nullable=True),
        sa.Column("status", sa.String(length=255), nullable=True),
        sa.Column("meta", sa.JSON, nullable=True),
        sa.Column("remember_token", sa.String(length=100), nullable=True),
        sa.Column("email_verified_at", sa.DateTime, nullable=True),
        sa.Column("phone_verified_at", sa.DateTime, nullable=True),
        sa.Column("deleted_at", sa.DateTime, nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=True),
        sa.Column("updated_at", sa.DateTime, nullable=True),
    )
    op.create_index("users_uuid_index", "users", ["uuid"], unique=False)
    op.create_index("users_public_id_unique", "users", ["public_id"], unique=True)
    op.create_index("users_type_index", "users", ["type"], unique=False)
    op.create_index("users_email_verified_at_index", "users", ["email_verified_at"], unique=False)
    op.create_index("users_created_at_index", "users", ["created_at"], unique=False)
    op.create_index("users_uuid_unique", "users", ["uuid"], unique=True)

    op.create_table(
        "companies",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("_key", sa.String(length=255), nullable=True),
        sa.Column("uuid", sa.String(length=191), nullable=True),
        sa.Column("public_id", sa.String(length=191), nullable=True),
        sa.Column("stripe_id", sa.String(length=191), nullable=True),
        sa.Column("stripe_connect_id", sa.String(length=191), nullable=True),
        sa.Column("trial_ends_at", sa.DateTime, nullable=True),
        sa.Column("card_last_four", sa.String(length=4), nullable=True),
        sa.Column("card_brand", sa.String(length=255), nullable=True),
        sa.Column("owner_uuid", sa.String(length=191), nullable=True),
        sa.Column("logo_uuid", sa.String(length=191), nullable=True),
        sa.Column("backdrop_uuid", sa.String(length=191), nullable=True),
        sa.Column("name", sa.String(length=255), nullable=True),
        sa.Column("website_url", sa.String(length=255), nullable=True),
        sa.Column("description", sa.String(length=255), nullable=True),
        sa.Column("options", sa.JSON, nullable=True),
        sa.Column("phone", sa.String(length=255), nullable=True),
        sa.Column("currency", sa.String(length=255), nullable=True),
        sa.Column("country", sa.String(length=255), nullable=True),
        sa.Column("timezone", sa.String(length=255), nullable=True),
        sa.Column("place_uuid", sa.String(length=191), nullable=True),
        sa.Column("plan", sa.String(length=255), nullable=True),
        sa.Column("status", sa.String(length=255), nullable=True),
        sa.Column("type", sa.String(length=191), nullable=True),
        sa.Column("slug", sa.String(length=255), nullable=True),
        sa.Column("deleted_at", sa.DateTime, nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=True),
        sa.Column("updated_at", sa.DateTime, nullable=True),
    )
    op.create_index("companies_uuid_index", "companies", ["uuid"], unique=False)
    op.create_index("companies_public_id_unique", "companies", ["public_id"], unique=True)
    op.create_index("companies_stripe_id_index", "companies", ["stripe_id"], unique=False)
    op.create_index("companies_owner_uuid_index", "companies", ["owner_uuid"], unique=False)
    op.create_index("companies_logo_uuid_foreign", "companies", ["logo_uuid"], unique=False)
    op.create_index("companies_backdrop_uuid_foreign", "companies", ["backdrop_uuid"], unique=False)
    op.create_index("companies_place_uuid_foreign", "companies", ["place_uuid"], unique=False)
    op.create_index("companies_type_index", "companies", ["type"], unique=False)
    op.create_index("companies_created_at_index", "companies", ["created_at"], unique=False)
    op.create_index("companies_uuid_unique", "companies", ["uuid"], unique=True)

    op.create_table(
        "company_users",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("_key", sa.String(length=255), nullable=True),
        sa.Column("uuid", sa.String(length=36), nullable=False),
        sa.Column("company_uuid", sa.String(length=36), nullable=True),
        sa.Column("user_uuid", sa.String(length=36), nullable=True),
        sa.Column("status", sa.String(length=255), nullable=False, server_default="active"),
        sa.Column("deleted_at", sa.DateTime, nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=True),
        sa.Column("updated_at", sa.DateTime, nullable=True),
    )
    op.create_index("company_users_company_uuid_index", "company_users", ["company_uuid"], unique=False)
    op.create_index("company_users_user_uuid_index", "company_users", ["user_uuid"], unique=False)
    op.create_index("company_users_created_at_index", "company_users", ["created_at"], unique=False)
    op.create_index("company_users_uuid_unique", "company_users", ["uuid"], unique=True)

    op.create_table(
        "api_credentials",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("_key", sa.String(length=255), nullable=True),
        sa.Column("uuid", sa.String(length=191), nullable=True),
        sa.Column("user_uuid", sa.String(length=191), nullable=True),
        sa.Column("company_uuid", sa.String(length=191), nullable=True),
        sa.Column("name", sa.String(length=255), nullable=True),
        sa.Column("key", sa.String(length=255), nullable=True),
        sa.Column("secret", sa.String(length=255), nullable=True),
        sa.Column("test_mode", sa.Integer, nullable=False, server_default="0"),
        sa.Column("api", sa.String(length=191), nullable=True),
        sa.Column("browser_origins", sa.JSON, nullable=True),
        sa.Column("last_used_at", sa.DateTime, nullable=True),
        sa.Column("expires_at", sa.DateTime, nullable=True),
        sa.Column("deleted_at", sa.DateTime, nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=True),
        sa.Column("updated_at", sa.DateTime, nullable=True),
    )
    op.create_index("api_credentials_uuid_index", "api_credentials", ["uuid"], unique=False)
    op.create_index("api_credentials_user_uuid_foreign", "api_credentials", ["user_uuid"], unique=False)
    op.create_index("api_credentials_company_uuid_foreign", "api_credentials", ["company_uuid"], unique=False)
    op.create_index("api_credentials_test_mode_index", "api_credentials", ["test_mode"], unique=False)
    op.create_index("api_credentials_api_index", "api_credentials", ["api"], unique=False)
    op.create_index("api_credentials_deleted_at_index", "api_credentials", ["deleted_at"], unique=False)
    op.create_index("api_credentials_created_at_index", "api_credentials", ["created_at"], unique=False)
    op.create_index("api_credentials_uuid_unique", "api_credentials", ["uuid"], unique=True)


def downgrade() -> None:
    op.drop_table("api_credentials")
    op.drop_table("company_users")
    op.drop_table("companies")
    op.drop_table("users")



