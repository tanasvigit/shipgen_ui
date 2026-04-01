"""Add vehicle assignment column to orders"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0016_order_vehicle_assignment"
down_revision: Union[str, None] = "0015_order_lifecycle_events"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("orders", sa.Column("vehicle_assigned_uuid", sa.String(length=36), nullable=True))
    op.create_index("ix_orders_vehicle_assigned_uuid", "orders", ["vehicle_assigned_uuid"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_orders_vehicle_assigned_uuid", table_name="orders")
    op.drop_column("orders", "vehicle_assigned_uuid")

