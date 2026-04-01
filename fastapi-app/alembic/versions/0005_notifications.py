"""Core notifications table
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0005_notifications"
down_revision: Union[str, None] = "0004_twofa"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "notifications",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("type", sa.String(length=255), nullable=False),
        sa.Column("notifiable_type", sa.String(length=255), nullable=False),
        sa.Column("notifiable_id", sa.String(length=36), nullable=False, index=True),
        sa.Column("data", sa.Text, nullable=False),
        sa.Column("read_at", sa.DateTime, nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=True),
        sa.Column("updated_at", sa.DateTime, nullable=True),
    )
    op.create_index(
        "notifications_notifiable_index",
        "notifications",
        ["notifiable_type", "notifiable_id"],
    )


def downgrade() -> None:
    op.drop_table("notifications")



