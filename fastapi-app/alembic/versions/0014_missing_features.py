"""Missing features: API events, logs, activities, extensions, custom fields, transactions, schedules, groups, user devices
Note: api_credentials table is created in 0001_core_users_companies migration
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0014_missing_features"
down_revision: Union[str, None] = "0013_core_utilities"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Note: api_credentials table already created in 0001_core_users_companies migration
    
    # API Events table
    op.create_table(
        "api_events",
        sa.Column("id", sa.Integer, primary_key=True, index=True),
        sa.Column("uuid", sa.String(length=36), nullable=True, unique=True),
        sa.Column("public_id", sa.String(length=191), nullable=True, index=True),
        sa.Column("company_uuid", sa.String(length=36), nullable=True, index=True),
        sa.Column("api_credential_uuid", sa.String(length=36), nullable=True, index=True),
        sa.Column("access_token_id", sa.String(length=36), nullable=True),
        sa.Column("event", sa.String(length=255), nullable=True),
        sa.Column("source", sa.String(length=255), nullable=True),
        sa.Column("data", sa.JSON, nullable=True),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("method", sa.String(length=10), nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=True),
        sa.Column("updated_at", sa.DateTime, nullable=True),
    )

    # API Request Logs table
    op.create_table(
        "api_request_logs",
        sa.Column("id", sa.Integer, primary_key=True, index=True),
        sa.Column("uuid", sa.String(length=36), nullable=True, unique=True),
        sa.Column("public_id", sa.String(length=191), nullable=True, index=True),
        sa.Column("company_uuid", sa.String(length=36), nullable=True, index=True),
        sa.Column("api_credential_uuid", sa.String(length=36), nullable=True, index=True),
        sa.Column("access_token_id", sa.String(length=36), nullable=True),
        sa.Column("method", sa.String(length=10), nullable=False),
        sa.Column("path", sa.String(length=255), nullable=True),
        sa.Column("full_url", sa.Text, nullable=True),
        sa.Column("status_code", sa.Integer, nullable=True),
        sa.Column("reason_phrase", sa.String(length=255), nullable=True),
        sa.Column("duration", sa.Float, nullable=True),
        sa.Column("ip_address", sa.String(length=255), nullable=True),
        sa.Column("version", sa.String(length=255), nullable=True),
        sa.Column("source", sa.String(length=255), nullable=True),
        sa.Column("content_type", sa.String(length=255), nullable=True),
        sa.Column("related", sa.JSON, nullable=True),
        sa.Column("query_params", sa.JSON, nullable=True),
        sa.Column("request_headers", sa.JSON, nullable=True),
        sa.Column("request_body", sa.JSON, nullable=True),
        sa.Column("request_raw_body", sa.Text, nullable=True),
        sa.Column("response_headers", sa.JSON, nullable=True),
        sa.Column("response_body", sa.JSON, nullable=True),
        sa.Column("response_raw_body", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=True),
        sa.Column("updated_at", sa.DateTime, nullable=True),
    )

    # Activity Log table (extends Spatie ActivityLog)
    op.create_table(
        "activity_log",
        sa.Column("id", sa.Integer, primary_key=True, index=True),
        sa.Column("uuid", sa.String(length=36), nullable=True, unique=True),
        sa.Column("log_name", sa.String(length=255), nullable=True, index=True),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("subject_type", sa.String(length=255), nullable=True, index=True),
        sa.Column("subject_id", sa.String(length=36), nullable=True, index=True),
        sa.Column("event", sa.String(length=255), nullable=True),
        sa.Column("causer_type", sa.String(length=255), nullable=True, index=True),
        sa.Column("causer_id", sa.String(length=36), nullable=True, index=True),
        sa.Column("properties", sa.JSON, nullable=True),
        sa.Column("batch_uuid", sa.String(length=36), nullable=True, index=True),
        sa.Column("created_at", sa.DateTime, nullable=True),
        sa.Column("updated_at", sa.DateTime, nullable=True),
    )

    # Extensions table
    op.create_table(
        "extensions",
        sa.Column("id", sa.Integer, primary_key=True, index=True),
        sa.Column("uuid", sa.String(length=36), nullable=True, unique=True),
        sa.Column("public_id", sa.String(length=191), nullable=True, index=True),
        sa.Column("extension_id", sa.String(length=255), nullable=True),
        sa.Column("author_uuid", sa.String(length=36), nullable=True, index=True),
        sa.Column("category_uuid", sa.String(length=36), nullable=True, index=True),
        sa.Column("type_uuid", sa.String(length=36), nullable=True, index=True),
        sa.Column("icon_uuid", sa.String(length=36), nullable=True, index=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("display_name", sa.String(length=255), nullable=True),
        sa.Column("key", sa.String(length=255), nullable=True, index=True),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("tags", sa.JSON, nullable=True),
        sa.Column("namespace", sa.String(length=255), nullable=True),
        sa.Column("internal_route", sa.String(length=255), nullable=True),
        sa.Column("fa_icon", sa.String(length=255), nullable=True),
        sa.Column("version", sa.String(length=255), nullable=True),
        sa.Column("website_url", sa.Text, nullable=True),
        sa.Column("privacy_policy_url", sa.Text, nullable=True),
        sa.Column("tos_url", sa.Text, nullable=True),
        sa.Column("contact_email", sa.String(length=255), nullable=True),
        sa.Column("domains", sa.JSON, nullable=True),
        sa.Column("core_service", sa.Boolean, nullable=True, default=False),
        sa.Column("meta", sa.JSON, nullable=True),
        sa.Column("meta_type", sa.String(length=255), nullable=True),
        sa.Column("config", sa.JSON, nullable=True),
        sa.Column("secret", sa.Text, nullable=True),
        sa.Column("client_token", sa.String(length=255), nullable=True),
        sa.Column("status", sa.String(length=255), nullable=True),
        sa.Column("slug", sa.String(length=255), nullable=True, index=True),
        sa.Column("deleted_at", sa.DateTime, nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=True),
        sa.Column("updated_at", sa.DateTime, nullable=True),
    )

    # Extension Installs table
    op.create_table(
        "extension_installs",
        sa.Column("id", sa.Integer, primary_key=True, index=True),
        sa.Column("uuid", sa.String(length=36), nullable=True, unique=True),
        sa.Column("extension_uuid", sa.String(length=36), nullable=True, index=True),
        sa.Column("company_uuid", sa.String(length=36), nullable=True, index=True),
        sa.Column("config", sa.JSON, nullable=True),
        sa.Column("meta", sa.JSON, nullable=True),
        sa.Column("deleted_at", sa.DateTime, nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=True),
        sa.Column("updated_at", sa.DateTime, nullable=True),
    )

    # Custom Fields table
    op.create_table(
        "custom_fields",
        sa.Column("id", sa.Integer, primary_key=True, index=True),
        sa.Column("uuid", sa.String(length=36), nullable=True, unique=True),
        sa.Column("company_uuid", sa.String(length=36), nullable=True, index=True),
        sa.Column("category_uuid", sa.String(length=36), nullable=True, index=True),
        sa.Column("subject_uuid", sa.String(length=36), nullable=True),
        sa.Column("subject_type", sa.String(length=255), nullable=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("label", sa.String(length=255), nullable=True),
        sa.Column("type", sa.String(length=255), nullable=True),
        sa.Column("for_field", sa.String(length=255), nullable=True),
        sa.Column("component", sa.String(length=255), nullable=True),
        sa.Column("options", sa.JSON, nullable=True),
        sa.Column("required", sa.Boolean, nullable=True, default=False),
        sa.Column("editable", sa.Boolean, nullable=True, default=True),
        sa.Column("default_value", sa.Text, nullable=True),
        sa.Column("validation_rules", sa.JSON, nullable=True),
        sa.Column("meta", sa.JSON, nullable=True),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("help_text", sa.Text, nullable=True),
        sa.Column("order", sa.Integer, nullable=True),
        sa.Column("deleted_at", sa.DateTime, nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=True),
        sa.Column("updated_at", sa.DateTime, nullable=True),
    )

    # Custom Field Values table
    op.create_table(
        "custom_field_values",
        sa.Column("id", sa.Integer, primary_key=True, index=True),
        sa.Column("uuid", sa.String(length=36), nullable=True, unique=True),
        sa.Column("company_uuid", sa.String(length=36), nullable=True, index=True),
        sa.Column("custom_field_uuid", sa.String(length=36), nullable=True, index=True),
        sa.Column("subject_uuid", sa.String(length=36), nullable=True),
        sa.Column("subject_type", sa.String(length=255), nullable=True),
        sa.Column("value", sa.Text, nullable=True),
        sa.Column("value_type", sa.String(length=255), nullable=True),
        sa.Column("deleted_at", sa.DateTime, nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=True),
        sa.Column("updated_at", sa.DateTime, nullable=True),
    )

    # Transactions table
    op.create_table(
        "transactions",
        sa.Column("id", sa.Integer, primary_key=True, index=True),
        sa.Column("uuid", sa.String(length=36), nullable=True, unique=True),
        sa.Column("public_id", sa.String(length=191), nullable=True, index=True),
        sa.Column("owner_uuid", sa.String(length=36), nullable=True),
        sa.Column("owner_type", sa.String(length=255), nullable=True),
        sa.Column("customer_uuid", sa.String(length=36), nullable=True),
        sa.Column("customer_type", sa.String(length=255), nullable=True),
        sa.Column("company_uuid", sa.String(length=36), nullable=True, index=True),
        sa.Column("gateway_transaction_id", sa.String(length=255), nullable=True, index=True),
        sa.Column("gateway", sa.String(length=255), nullable=True),
        sa.Column("gateway_uuid", sa.String(length=36), nullable=True),
        sa.Column("amount", sa.Integer, nullable=False, default=0),
        sa.Column("currency", sa.String(length=10), nullable=True),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("meta", sa.JSON, nullable=True),
        sa.Column("type", sa.String(length=255), nullable=True),
        sa.Column("status", sa.String(length=255), nullable=True),
        sa.Column("deleted_at", sa.DateTime, nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=True),
        sa.Column("updated_at", sa.DateTime, nullable=True),
    )

    # Transaction Items table
    op.create_table(
        "transaction_items",
        sa.Column("id", sa.Integer, primary_key=True, index=True),
        sa.Column("uuid", sa.String(length=36), nullable=True, unique=True),
        sa.Column("transaction_uuid", sa.String(length=36), nullable=True, index=True),
        sa.Column("amount", sa.Integer, nullable=False, default=0),
        sa.Column("currency", sa.String(length=10), nullable=True),
        sa.Column("details", sa.Text, nullable=True),
        sa.Column("code", sa.String(length=255), nullable=True),
        sa.Column("meta", sa.JSON, nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=True),
        sa.Column("updated_at", sa.DateTime, nullable=True),
    )

    # Schedules table
    op.create_table(
        "schedules",
        sa.Column("id", sa.Integer, primary_key=True, index=True),
        sa.Column("uuid", sa.String(length=36), nullable=True, unique=True),
        sa.Column("public_id", sa.String(length=191), nullable=True, index=True),
        sa.Column("company_uuid", sa.String(length=36), nullable=True, index=True),
        sa.Column("subject_uuid", sa.String(length=36), nullable=True),
        sa.Column("subject_type", sa.String(length=255), nullable=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("start_date", sa.Date, nullable=True),
        sa.Column("end_date", sa.Date, nullable=True),
        sa.Column("timezone", sa.String(length=255), nullable=True),
        sa.Column("status", sa.String(length=255), nullable=True),
        sa.Column("meta", sa.JSON, nullable=True),
        sa.Column("deleted_at", sa.DateTime, nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=True),
        sa.Column("updated_at", sa.DateTime, nullable=True),
    )

    # Schedule Items table
    op.create_table(
        "schedule_items",
        sa.Column("id", sa.Integer, primary_key=True, index=True),
        sa.Column("uuid", sa.String(length=36), nullable=True, unique=True),
        sa.Column("public_id", sa.String(length=191), nullable=True, index=True),
        sa.Column("schedule_uuid", sa.String(length=36), nullable=True, index=True),
        sa.Column("assignee_uuid", sa.String(length=36), nullable=True),
        sa.Column("assignee_type", sa.String(length=255), nullable=True),
        sa.Column("resource_uuid", sa.String(length=36), nullable=True),
        sa.Column("resource_type", sa.String(length=255), nullable=True),
        sa.Column("start_at", sa.DateTime, nullable=True),
        sa.Column("end_at", sa.DateTime, nullable=True),
        sa.Column("duration", sa.Integer, nullable=True),
        sa.Column("break_start_at", sa.DateTime, nullable=True),
        sa.Column("break_end_at", sa.DateTime, nullable=True),
        sa.Column("status", sa.String(length=255), nullable=True),
        sa.Column("meta", sa.JSON, nullable=True),
        sa.Column("deleted_at", sa.DateTime, nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=True),
        sa.Column("updated_at", sa.DateTime, nullable=True),
    )

    # Schedule Templates table
    op.create_table(
        "schedule_templates",
        sa.Column("id", sa.Integer, primary_key=True, index=True),
        sa.Column("uuid", sa.String(length=36), nullable=True, unique=True),
        sa.Column("public_id", sa.String(length=191), nullable=True, index=True),
        sa.Column("company_uuid", sa.String(length=36), nullable=True, index=True),
        sa.Column("subject_uuid", sa.String(length=36), nullable=True),
        sa.Column("subject_type", sa.String(length=255), nullable=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("start_time", sa.Time, nullable=True),
        sa.Column("end_time", sa.Time, nullable=True),
        sa.Column("duration", sa.Integer, nullable=True),
        sa.Column("break_duration", sa.Integer, nullable=True),
        sa.Column("rrule", sa.Text, nullable=True),
        sa.Column("meta", sa.JSON, nullable=True),
        sa.Column("deleted_at", sa.DateTime, nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=True),
        sa.Column("updated_at", sa.DateTime, nullable=True),
    )

    # Schedule Availability table
    op.create_table(
        "schedule_availability",
        sa.Column("id", sa.Integer, primary_key=True, index=True),
        sa.Column("uuid", sa.String(length=36), nullable=True, unique=True),
        sa.Column("subject_uuid", sa.String(length=36), nullable=True),
        sa.Column("subject_type", sa.String(length=255), nullable=True),
        sa.Column("start_at", sa.DateTime, nullable=True),
        sa.Column("end_at", sa.DateTime, nullable=True),
        sa.Column("is_available", sa.Boolean, nullable=True, default=True),
        sa.Column("preference_level", sa.Integer, nullable=True),
        sa.Column("rrule", sa.Text, nullable=True),
        sa.Column("reason", sa.String(length=255), nullable=True),
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column("meta", sa.JSON, nullable=True),
        sa.Column("deleted_at", sa.DateTime, nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=True),
        sa.Column("updated_at", sa.DateTime, nullable=True),
    )

    # Schedule Constraints table
    op.create_table(
        "schedule_constraints",
        sa.Column("id", sa.Integer, primary_key=True, index=True),
        sa.Column("uuid", sa.String(length=36), nullable=True, unique=True),
        sa.Column("company_uuid", sa.String(length=36), nullable=True, index=True),
        sa.Column("subject_uuid", sa.String(length=36), nullable=True),
        sa.Column("subject_type", sa.String(length=255), nullable=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("type", sa.String(length=255), nullable=True),
        sa.Column("category", sa.String(length=255), nullable=True),
        sa.Column("constraint_key", sa.String(length=255), nullable=True),
        sa.Column("constraint_value", sa.Text, nullable=True),
        sa.Column("jurisdiction", sa.String(length=255), nullable=True),
        sa.Column("priority", sa.Integer, nullable=True),
        sa.Column("is_active", sa.Boolean, nullable=True, default=True),
        sa.Column("meta", sa.JSON, nullable=True),
        sa.Column("deleted_at", sa.DateTime, nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=True),
        sa.Column("updated_at", sa.DateTime, nullable=True),
    )

    # Groups table
    op.create_table(
        "groups",
        sa.Column("id", sa.Integer, primary_key=True, index=True),
        sa.Column("uuid", sa.String(length=36), nullable=True, unique=True),
        sa.Column("public_id", sa.String(length=191), nullable=True, index=True),
        sa.Column("company_uuid", sa.String(length=36), nullable=True, index=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("slug", sa.String(length=255), nullable=True, index=True),
        sa.Column("deleted_at", sa.DateTime, nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=True),
        sa.Column("updated_at", sa.DateTime, nullable=True),
    )

    # Group Users table (pivot)
    op.create_table(
        "group_users",
        sa.Column("id", sa.Integer, primary_key=True, index=True),
        sa.Column("uuid", sa.String(length=36), nullable=True, unique=True),
        sa.Column("company_uuid", sa.String(length=36), nullable=True, index=True),
        sa.Column("user_uuid", sa.String(length=36), nullable=True, index=True),
        sa.Column("group_uuid", sa.String(length=36), nullable=True, index=True),
        sa.Column("created_at", sa.DateTime, nullable=True),
        sa.Column("updated_at", sa.DateTime, nullable=True),
    )

    # User Devices table
    op.create_table(
        "user_devices",
        sa.Column("id", sa.Integer, primary_key=True, index=True),
        sa.Column("uuid", sa.String(length=36), nullable=True, unique=True),
        sa.Column("public_id", sa.String(length=191), nullable=True, index=True),
        sa.Column("user_uuid", sa.String(length=36), nullable=True, index=True),
        sa.Column("platform", sa.String(length=255), nullable=True),
        sa.Column("token", sa.Text, nullable=True),
        sa.Column("status", sa.String(length=255), nullable=True),
        sa.Column("deleted_at", sa.DateTime, nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=True),
        sa.Column("updated_at", sa.DateTime, nullable=True),
    )


def downgrade() -> None:
    op.drop_table("user_devices")
    op.drop_table("group_users")
    op.drop_table("groups")
    op.drop_table("schedule_constraints")
    op.drop_table("schedule_availability")
    op.drop_table("schedule_templates")
    op.drop_table("schedule_items")
    op.drop_table("schedules")
    op.drop_table("transaction_items")
    op.drop_table("transactions")
    op.drop_table("custom_field_values")
    op.drop_table("custom_fields")
    op.drop_table("extension_installs")
    op.drop_table("extensions")
    op.drop_table("activity_log")
    op.drop_table("api_request_logs")
    op.drop_table("api_events")
    # Note: api_credentials table is dropped in 0001_core_users_companies migration

