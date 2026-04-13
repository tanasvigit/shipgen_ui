"""Add fleet customer order creator and trips table"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# Keep <= 32 chars: default alembic_version.version_num is VARCHAR(32).
revision: str = "0021_fleet_cust_orders"
down_revision: Union[str, None] = "0020_add_driver_last_seen"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("orders", sa.Column("created_by", sa.String(length=36), nullable=True))
    op.create_index("ix_orders_created_by", "orders", ["created_by"], unique=False)
    op.create_foreign_key(
        "fk_orders_created_by_users_uuid",
        "orders",
        "users",
        ["created_by"],
        ["uuid"],
        ondelete="SET NULL",
    )

    op.create_table(
        "trips",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("order_id", sa.Integer(), nullable=False),
        sa.Column("driver_id", sa.Integer(), nullable=False),
        sa.Column("start_time", sa.DateTime(), nullable=True),
        sa.Column("end_time", sa.DateTime(), nullable=True),
        sa.Column("status", sa.String(length=64), nullable=True),
        sa.Column("current_location", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["order_id"], ["orders.id"]),
        sa.ForeignKeyConstraint(["driver_id"], ["drivers.id"]),
    )
    op.create_index("ix_trips_order_id", "trips", ["order_id"], unique=False)
    op.create_index("ix_trips_driver_id", "trips", ["driver_id"], unique=False)
    op.create_index("ix_trips_status", "trips", ["status"], unique=False)
    op.create_index("ix_trips_created_at", "trips", ["created_at"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_trips_created_at", table_name="trips")
    op.drop_index("ix_trips_status", table_name="trips")
    op.drop_index("ix_trips_driver_id", table_name="trips")
    op.drop_index("ix_trips_order_id", table_name="trips")
    op.drop_table("trips")

    op.drop_constraint("fk_orders_created_by_users_uuid", "orders", type_="foreignkey")
    op.drop_index("ix_orders_created_by", table_name="orders")
    op.drop_column("orders", "created_by")
