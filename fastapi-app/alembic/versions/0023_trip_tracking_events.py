"""Trip tracking + events enhancements

Revision ID: 0023_trip_tracking_events
Revises: 0022_trips_dispatch_module
Create Date: 2026-04-13
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0023_trip_tracking_events"
down_revision: Union[str, None] = "0022_trips_dispatch_module"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("dispatch_trips", sa.Column("current_lat", sa.Float(), nullable=True))
    op.add_column("dispatch_trips", sa.Column("current_lng", sa.Float(), nullable=True))
    op.add_column("dispatch_trips", sa.Column("last_location_update", sa.DateTime(), nullable=True))

    op.add_column("dispatch_trip_stops", sa.Column("is_completed", sa.Boolean(), nullable=False, server_default=sa.false()))
    op.add_column("dispatch_trip_stops", sa.Column("completed_at", sa.DateTime(), nullable=True))

    op.create_table(
        "dispatch_trip_events",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("trip_id", sa.Integer(), nullable=False),
        sa.Column("event_type", sa.String(length=64), nullable=False),
        sa.Column("metadata", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["trip_id"], ["dispatch_trips.id"]),
    )
    op.create_index("ix_dispatch_trip_events_trip_id", "dispatch_trip_events", ["trip_id"], unique=False)
    op.create_index("ix_dispatch_trip_events_event_type", "dispatch_trip_events", ["event_type"], unique=False)
    op.create_index("ix_dispatch_trip_events_created_at", "dispatch_trip_events", ["created_at"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_dispatch_trip_events_created_at", table_name="dispatch_trip_events")
    op.drop_index("ix_dispatch_trip_events_event_type", table_name="dispatch_trip_events")
    op.drop_index("ix_dispatch_trip_events_trip_id", table_name="dispatch_trip_events")
    op.drop_table("dispatch_trip_events")

    op.drop_column("dispatch_trip_stops", "completed_at")
    op.drop_column("dispatch_trip_stops", "is_completed")

    op.drop_column("dispatch_trips", "last_location_update")
    op.drop_column("dispatch_trips", "current_lng")
    op.drop_column("dispatch_trips", "current_lat")
