"""Add role column to users for logistics RBAC"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0017_user_role_rbac"
down_revision: Union[str, None] = "0016_order_vehicle_assignment"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column("role", sa.String(length=64), nullable=True),
    )
    op.create_index("ix_users_role", "users", ["role"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_users_role", table_name="users")
    op.drop_column("users", "role")
