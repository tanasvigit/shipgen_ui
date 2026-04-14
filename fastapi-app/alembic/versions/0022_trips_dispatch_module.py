"""Trips & Dispatch module tables

Revision ID: 0022_trips_dispatch_module
Revises: 0021_fleet_cust_orders
Create Date: 2026-04-13
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0022_trips_dispatch_module"
down_revision: Union[str, None] = "0021_fleet_cust_orders"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "dispatch_trips",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("uuid", sa.String(length=36), nullable=True),
        sa.Column("public_id", sa.String(length=191), nullable=True),
        sa.Column("company_uuid", sa.String(length=36), nullable=False),
        sa.Column("vehicle_uuid", sa.String(length=36), nullable=False),
        sa.Column("driver_uuid", sa.String(length=36), nullable=False),
        sa.Column("start_location", sa.String(length=255), nullable=False),
        sa.Column("end_location", sa.String(length=255), nullable=False),
        sa.Column("total_capacity", sa.Integer(), nullable=False),
        sa.Column("current_load", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("available_capacity", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="PLANNED"),
        sa.Column("started_at", sa.DateTime(), nullable=True),
        sa.Column("completed_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
    )
    op.create_index("ix_dispatch_trips_uuid", "dispatch_trips", ["uuid"], unique=True)
    op.create_index("ix_dispatch_trips_public_id", "dispatch_trips", ["public_id"], unique=True)
    op.create_index("ix_dispatch_trips_company_uuid", "dispatch_trips", ["company_uuid"], unique=False)
    op.create_index("ix_dispatch_trips_vehicle_uuid", "dispatch_trips", ["vehicle_uuid"], unique=False)
    op.create_index("ix_dispatch_trips_driver_uuid", "dispatch_trips", ["driver_uuid"], unique=False)
    op.create_index("ix_dispatch_trips_status", "dispatch_trips", ["status"], unique=False)
    op.create_index("ix_dispatch_trips_created_at", "dispatch_trips", ["created_at"], unique=False)

    op.create_table(
        "dispatch_trip_orders",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("trip_id", sa.Integer(), nullable=False),
        sa.Column("order_id", sa.Integer(), nullable=False),
        sa.Column("pickup_location", sa.String(length=255), nullable=False),
        sa.Column("drop_location", sa.String(length=255), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="LOADED"),
        sa.Column("load_units", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["trip_id"], ["dispatch_trips.id"]),
        sa.ForeignKeyConstraint(["order_id"], ["orders.id"]),
        sa.UniqueConstraint("trip_id", "order_id", name="uq_dispatch_trip_order"),
    )
    op.create_index("ix_dispatch_trip_orders_trip_id", "dispatch_trip_orders", ["trip_id"], unique=False)
    op.create_index("ix_dispatch_trip_orders_order_id", "dispatch_trip_orders", ["order_id"], unique=False)
    op.create_index("ix_dispatch_trip_orders_status", "dispatch_trip_orders", ["status"], unique=False)
    op.create_index("ix_dispatch_trip_orders_created_at", "dispatch_trip_orders", ["created_at"], unique=False)

    op.create_table(
        "dispatch_trip_stops",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("trip_id", sa.Integer(), nullable=False),
        sa.Column("location_name", sa.String(length=255), nullable=False),
        sa.Column("type", sa.String(length=16), nullable=False),
        sa.Column("sequence", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["trip_id"], ["dispatch_trips.id"]),
    )
    op.create_index("ix_dispatch_trip_stops_trip_id", "dispatch_trip_stops", ["trip_id"], unique=False)
    op.create_index("ix_dispatch_trip_stops_created_at", "dispatch_trip_stops", ["created_at"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_dispatch_trip_stops_created_at", table_name="dispatch_trip_stops")
    op.drop_index("ix_dispatch_trip_stops_trip_id", table_name="dispatch_trip_stops")
    op.drop_table("dispatch_trip_stops")

    op.drop_index("ix_dispatch_trip_orders_created_at", table_name="dispatch_trip_orders")
    op.drop_index("ix_dispatch_trip_orders_status", table_name="dispatch_trip_orders")
    op.drop_index("ix_dispatch_trip_orders_order_id", table_name="dispatch_trip_orders")
    op.drop_index("ix_dispatch_trip_orders_trip_id", table_name="dispatch_trip_orders")
    op.drop_table("dispatch_trip_orders")

    op.drop_index("ix_dispatch_trips_created_at", table_name="dispatch_trips")
    op.drop_index("ix_dispatch_trips_status", table_name="dispatch_trips")
    op.drop_index("ix_dispatch_trips_driver_uuid", table_name="dispatch_trips")
    op.drop_index("ix_dispatch_trips_vehicle_uuid", table_name="dispatch_trips")
    op.drop_index("ix_dispatch_trips_company_uuid", table_name="dispatch_trips")
    op.drop_index("ix_dispatch_trips_public_id", table_name="dispatch_trips")
    op.drop_index("ix_dispatch_trips_uuid", table_name="dispatch_trips")
    op.drop_table("dispatch_trips")
