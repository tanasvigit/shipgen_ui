"""Ensure unique driver link per user/company"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0019_unique_driver_user_link"
down_revision: Union[str, None] = "0018_backfill_user_uuid_values"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_index(
        "uq_drivers_company_user_uuid",
        "drivers",
        ["company_uuid", "user_uuid"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index("uq_drivers_company_user_uuid", table_name="drivers")
