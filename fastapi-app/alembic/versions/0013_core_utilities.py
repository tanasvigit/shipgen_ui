"""Core utilities: files, comments, settings, webhooks, dashboards, reports, chat
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0013_core_utilities"
down_revision: Union[str, None] = "0012_storefront_int"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Files table
    op.create_table(
        "files",
        sa.Column("id", sa.Integer, primary_key=True, index=True),
        sa.Column("uuid", sa.String(length=36), nullable=True, unique=True),
        sa.Column("public_id", sa.String(length=191), nullable=True, index=True),
        sa.Column("company_uuid", sa.String(length=36), nullable=True, index=True),
        sa.Column("uploader_uuid", sa.String(length=36), nullable=True, index=True),
        sa.Column("subject_uuid", sa.String(length=36), nullable=True),
        sa.Column("subject_type", sa.String(length=255), nullable=True),
        sa.Column("disk", sa.String(length=255), nullable=True),
        sa.Column("path", sa.Text, nullable=True),
        sa.Column("bucket", sa.String(length=255), nullable=True),
        sa.Column("folder", sa.String(length=255), nullable=True),
        sa.Column("meta", sa.JSON, nullable=True),
        sa.Column("etag", sa.String(length=255), nullable=True),
        sa.Column("original_filename", sa.String(length=255), nullable=True),
        sa.Column("type", sa.String(length=255), nullable=True),
        sa.Column("content_type", sa.String(length=255), nullable=True),
        sa.Column("file_size", sa.Integer, nullable=True),
        sa.Column("slug", sa.String(length=255), nullable=True, index=True),
        sa.Column("caption", sa.Text, nullable=True),
        sa.Column("deleted_at", sa.DateTime, nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=True),
        sa.Column("updated_at", sa.DateTime, nullable=True),
    )

    # Comments table
    op.create_table(
        "comments",
        sa.Column("id", sa.Integer, primary_key=True, index=True),
        sa.Column("uuid", sa.String(length=36), nullable=True, unique=True),
        sa.Column("public_id", sa.String(length=191), nullable=True, index=True),
        sa.Column("company_uuid", sa.String(length=36), nullable=True, index=True),
        sa.Column("subject_uuid", sa.String(length=36), nullable=True),
        sa.Column("subject_type", sa.String(length=255), nullable=True),
        sa.Column("author_uuid", sa.String(length=36), nullable=True, index=True),
        sa.Column("parent_comment_uuid", sa.String(length=36), nullable=True, index=True),
        sa.Column("content", sa.Text, nullable=True),
        sa.Column("tags", sa.JSON, nullable=True),
        sa.Column("meta", sa.JSON, nullable=True),
        sa.Column("deleted_at", sa.DateTime, nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=True),
        sa.Column("updated_at", sa.DateTime, nullable=True),
    )

    # Settings table
    op.create_table(
        "settings",
        sa.Column("id", sa.Integer, primary_key=True, index=True),
        sa.Column("key", sa.String(length=255), nullable=False, unique=True, index=True),
        sa.Column("value", sa.JSON, nullable=True),
    )

    # Webhook endpoints table
    op.create_table(
        "webhook_endpoints",
        sa.Column("id", sa.Integer, primary_key=True, index=True),
        sa.Column("uuid", sa.String(length=36), nullable=True, unique=True),
        sa.Column("company_uuid", sa.String(length=36), nullable=True, index=True),
        sa.Column("created_by_uuid", sa.String(length=36), nullable=True, index=True),
        sa.Column("updated_by_uuid", sa.String(length=36), nullable=True),
        sa.Column("api_credential_uuid", sa.String(length=36), nullable=True, index=True),
        sa.Column("url", sa.Text, nullable=False),
        sa.Column("mode", sa.String(length=255), nullable=True),
        sa.Column("version", sa.String(length=255), nullable=True),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("events", sa.JSON, nullable=True),
        sa.Column("status", sa.String(length=255), nullable=True, default="enabled"),
        sa.Column("deleted_at", sa.DateTime, nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=True),
        sa.Column("updated_at", sa.DateTime, nullable=True),
    )

    # Webhook request logs table
    op.create_table(
        "webhook_request_logs",
        sa.Column("id", sa.Integer, primary_key=True, index=True),
        sa.Column("uuid", sa.String(length=36), nullable=True, unique=True),
        sa.Column("public_id", sa.String(length=191), nullable=True, index=True),
        sa.Column("company_uuid", sa.String(length=36), nullable=True, index=True),
        sa.Column("webhook_uuid", sa.String(length=36), nullable=True, index=True),
        sa.Column("api_credential_uuid", sa.String(length=36), nullable=True, index=True),
        sa.Column("access_token_id", sa.String(length=36), nullable=True),
        sa.Column("api_event_uuid", sa.String(length=36), nullable=True, index=True),
        sa.Column("method", sa.String(length=10), nullable=False),
        sa.Column("status_code", sa.Integer, nullable=True),
        sa.Column("reason_phrase", sa.String(length=255), nullable=True),
        sa.Column("duration", sa.Float, nullable=True),
        sa.Column("url", sa.Text, nullable=True),
        sa.Column("attempt", sa.Integer, nullable=True, default=1),
        sa.Column("response", sa.JSON, nullable=True),
        sa.Column("status", sa.String(length=255), nullable=True),
        sa.Column("headers", sa.JSON, nullable=True),
        sa.Column("meta", sa.JSON, nullable=True),
        sa.Column("sent_at", sa.DateTime, nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=True),
        sa.Column("updated_at", sa.DateTime, nullable=True),
    )

    # Dashboards table
    op.create_table(
        "dashboards",
        sa.Column("id", sa.Integer, primary_key=True, index=True),
        sa.Column("uuid", sa.String(length=36), nullable=True, unique=True),
        sa.Column("user_uuid", sa.String(length=36), nullable=True, index=True),
        sa.Column("company_uuid", sa.String(length=36), nullable=True, index=True),
        sa.Column("extension", sa.String(length=255), nullable=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("is_default", sa.Boolean, nullable=True, default=False),
        sa.Column("tags", sa.JSON, nullable=True),
        sa.Column("meta", sa.JSON, nullable=True),
        sa.Column("options", sa.JSON, nullable=True),
        sa.Column("deleted_at", sa.DateTime, nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=True),
        sa.Column("updated_at", sa.DateTime, nullable=True),
    )

    # Dashboard widgets table
    op.create_table(
        "dashboard_widgets",
        sa.Column("id", sa.Integer, primary_key=True, index=True),
        sa.Column("uuid", sa.String(length=36), nullable=True, unique=True),
        sa.Column("dashboard_uuid", sa.String(length=36), nullable=True, index=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("component", sa.String(length=255), nullable=True),
        sa.Column("grid_options", sa.JSON, nullable=True),
        sa.Column("options", sa.JSON, nullable=True),
        sa.Column("deleted_at", sa.DateTime, nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=True),
        sa.Column("updated_at", sa.DateTime, nullable=True),
    )

    # Reports table
    op.create_table(
        "reports",
        sa.Column("id", sa.Integer, primary_key=True, index=True),
        sa.Column("uuid", sa.String(length=36), nullable=True, unique=True),
        sa.Column("public_id", sa.String(length=191), nullable=True, index=True),
        sa.Column("company_uuid", sa.String(length=36), nullable=True, index=True),
        sa.Column("category_uuid", sa.String(length=36), nullable=True, index=True),
        sa.Column("created_by_uuid", sa.String(length=36), nullable=True, index=True),
        sa.Column("updated_by_uuid", sa.String(length=36), nullable=True),
        sa.Column("subject_uuid", sa.String(length=36), nullable=True),
        sa.Column("subject_type", sa.String(length=255), nullable=True),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("period_start", sa.DateTime, nullable=True),
        sa.Column("period_end", sa.DateTime, nullable=True),
        sa.Column("result_columns", sa.JSON, nullable=True),
        sa.Column("last_executed_at", sa.DateTime, nullable=True),
        sa.Column("execution_time", sa.Float, nullable=True),
        sa.Column("row_count", sa.Integer, nullable=True),
        sa.Column("is_scheduled", sa.Boolean, nullable=True, default=False),
        sa.Column("schedule_config", sa.JSON, nullable=True),
        sa.Column("export_formats", sa.JSON, nullable=True),
        sa.Column("is_generated", sa.Boolean, nullable=True, default=False),
        sa.Column("generation_progress", sa.Integer, nullable=True),
        sa.Column("options", sa.JSON, nullable=True),
        sa.Column("tags", sa.JSON, nullable=True),
        sa.Column("query_config", sa.JSON, nullable=True),
        sa.Column("data", sa.JSON, nullable=True),
        sa.Column("meta", sa.JSON, nullable=True),
        sa.Column("status", sa.String(length=255), nullable=True),
        sa.Column("type", sa.String(length=255), nullable=True),
        sa.Column("deleted_at", sa.DateTime, nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=True),
        sa.Column("updated_at", sa.DateTime, nullable=True),
    )

    # Chat channels table
    op.create_table(
        "chat_channels",
        sa.Column("id", sa.Integer, primary_key=True, index=True),
        sa.Column("uuid", sa.String(length=36), nullable=True, unique=True),
        sa.Column("public_id", sa.String(length=191), nullable=True, index=True),
        sa.Column("company_uuid", sa.String(length=36), nullable=True, index=True),
        sa.Column("created_by_uuid", sa.String(length=36), nullable=True, index=True),
        sa.Column("name", sa.String(length=255), nullable=True),
        sa.Column("slug", sa.String(length=255), nullable=True, index=True),
        sa.Column("meta", sa.JSON, nullable=True),
        sa.Column("deleted_at", sa.DateTime, nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=True),
        sa.Column("updated_at", sa.DateTime, nullable=True),
    )

    # Chat messages table
    op.create_table(
        "chat_messages",
        sa.Column("id", sa.Integer, primary_key=True, index=True),
        sa.Column("uuid", sa.String(length=36), nullable=True, unique=True),
        sa.Column("public_id", sa.String(length=191), nullable=True, index=True),
        sa.Column("company_uuid", sa.String(length=36), nullable=True, index=True),
        sa.Column("chat_channel_uuid", sa.String(length=36), nullable=True, index=True),
        sa.Column("sender_uuid", sa.String(length=36), nullable=True, index=True),
        sa.Column("content", sa.Text, nullable=True),
        sa.Column("deleted_at", sa.DateTime, nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=True),
        sa.Column("updated_at", sa.DateTime, nullable=True),
    )

    # Chat participants table
    op.create_table(
        "chat_participants",
        sa.Column("id", sa.Integer, primary_key=True, index=True),
        sa.Column("uuid", sa.String(length=36), nullable=True, unique=True),
        sa.Column("public_id", sa.String(length=191), nullable=True, index=True),
        sa.Column("company_uuid", sa.String(length=36), nullable=True, index=True),
        sa.Column("chat_channel_uuid", sa.String(length=36), nullable=True, index=True),
        sa.Column("user_uuid", sa.String(length=36), nullable=True, index=True),
        sa.Column("deleted_at", sa.DateTime, nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=True),
        sa.Column("updated_at", sa.DateTime, nullable=True),
    )

    # Chat attachments table
    op.create_table(
        "chat_attachments",
        sa.Column("id", sa.Integer, primary_key=True, index=True),
        sa.Column("uuid", sa.String(length=36), nullable=True, unique=True),
        sa.Column("public_id", sa.String(length=191), nullable=True, index=True),
        sa.Column("company_uuid", sa.String(length=36), nullable=True, index=True),
        sa.Column("chat_channel_uuid", sa.String(length=36), nullable=True, index=True),
        sa.Column("chat_message_uuid", sa.String(length=36), nullable=True, index=True),
        sa.Column("sender_uuid", sa.String(length=36), nullable=True, index=True),
        sa.Column("file_uuid", sa.String(length=36), nullable=True, index=True),
        sa.Column("deleted_at", sa.DateTime, nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=True),
        sa.Column("updated_at", sa.DateTime, nullable=True),
    )

    # Chat receipts table
    op.create_table(
        "chat_receipts",
        sa.Column("id", sa.Integer, primary_key=True, index=True),
        sa.Column("uuid", sa.String(length=36), nullable=True, unique=True),
        sa.Column("public_id", sa.String(length=191), nullable=True, index=True),
        sa.Column("company_uuid", sa.String(length=36), nullable=True, index=True),
        sa.Column("chat_message_uuid", sa.String(length=36), nullable=True, index=True),
        sa.Column("participant_uuid", sa.String(length=36), nullable=True, index=True),
        sa.Column("read_at", sa.DateTime, nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=True),
        sa.Column("updated_at", sa.DateTime, nullable=True),
    )


def downgrade() -> None:
    op.drop_table("chat_receipts")
    op.drop_table("chat_attachments")
    op.drop_table("chat_participants")
    op.drop_table("chat_messages")
    op.drop_table("chat_channels")
    op.drop_table("reports")
    op.drop_table("dashboard_widgets")
    op.drop_table("dashboards")
    op.drop_table("webhook_request_logs")
    op.drop_table("webhook_endpoints")
    op.drop_table("settings")
    op.drop_table("comments")
    op.drop_table("files")

