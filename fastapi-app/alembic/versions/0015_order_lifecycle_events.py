"""Order lifecycle events table for orchestration flow"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0015_order_lifecycle_events"
down_revision: Union[str, None] = "0014_missing_features"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "order_events",
        sa.Column("id", sa.Integer, primary_key=True, index=True),
        sa.Column("uuid", sa.String(length=36), nullable=True, unique=True),
        sa.Column("public_id", sa.String(length=191), nullable=True, index=True),
        sa.Column("company_uuid", sa.String(length=36), nullable=True, index=True),
        sa.Column("order_uuid", sa.String(length=36), nullable=True, index=True),
        sa.Column("actor_uuid", sa.String(length=36), nullable=True, index=True),
        sa.Column("event_type", sa.String(length=64), nullable=False, index=True),
        sa.Column("from_status", sa.String(length=64), nullable=True, index=True),
        sa.Column("to_status", sa.String(length=64), nullable=True, index=True),
        sa.Column("payload", sa.JSON, nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=True, index=True),
        sa.Column("updated_at", sa.DateTime, nullable=True),
    )


def downgrade() -> None:
    op.drop_table("order_events")

