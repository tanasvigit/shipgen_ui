"""add last_seen_at to drivers table

Revision ID: 0020_add_driver_last_seen
Revises: 0019_unique_driver_user_link
Create Date: 2026-04-08 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "0020_add_driver_last_seen"
down_revision: Union[str, None] = "0019_unique_driver_user_link"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("drivers", sa.Column("last_seen_at", sa.DateTime(), nullable=True))


def downgrade() -> None:
    op.drop_column("drivers", "last_seen_at")
