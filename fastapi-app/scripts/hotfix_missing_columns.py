#!/usr/bin/env python3
"""
Apply idempotent DB fixes when the live schema is behind SQLAlchemy models
but Alembic upgrade is not an option (e.g. version table out of sync).

Matches alembic/versions/0020_add_driver_last_seen.py and
0021_fleet_cust_orders (file 0021_*.py) where possible.

Run from fastapi-app:
  python scripts/hotfix_missing_columns.py

Prefer when possible:
  alembic upgrade head
"""
import sys
from pathlib import Path

from sqlalchemy import text

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.core.database import SessionLocal


def column_exists(db, table: str, column: str) -> bool:
    row = db.execute(
        text(
            """
            SELECT 1
            FROM information_schema.columns
            WHERE table_schema = 'public'
              AND table_name = :table_name
              AND column_name = :column_name
            LIMIT 1
            """
        ),
        {"table_name": table, "column_name": column},
    ).first()
    return bool(row)


def table_exists(db, table: str) -> bool:
    row = db.execute(
        text(
            """
            SELECT 1
            FROM information_schema.tables
            WHERE table_schema = 'public' AND table_name = :t
            LIMIT 1
            """
        ),
        {"t": table},
    ).first()
    return bool(row)


def pg_constraint_exists(db, name: str) -> bool:
    row = db.execute(
        text("SELECT 1 FROM pg_constraint WHERE conname = :n LIMIT 1"),
        {"n": name},
    ).first()
    return bool(row)


def main() -> None:
    db = SessionLocal()
    try:
        if not column_exists(db, "drivers", "last_seen_at"):
            db.execute(text("ALTER TABLE drivers ADD COLUMN last_seen_at TIMESTAMP NULL"))
            print("Added: drivers.last_seen_at")
        else:
            print("Exists: drivers.last_seen_at")

        if not column_exists(db, "orders", "created_by"):
            db.execute(text("ALTER TABLE orders ADD COLUMN created_by VARCHAR(36) NULL"))
            print("Added: orders.created_by")
        else:
            print("Exists: orders.created_by")

        db.execute(text("CREATE INDEX IF NOT EXISTS ix_orders_created_by ON orders (created_by)"))

        if not pg_constraint_exists(db, "fk_orders_created_by_users_uuid"):
            db.execute(
                text(
                    """
                    ALTER TABLE orders
                    ADD CONSTRAINT fk_orders_created_by_users_uuid
                    FOREIGN KEY (created_by) REFERENCES users (uuid) ON DELETE SET NULL
                    """
                )
            )
            print("Added: fk_orders_created_by_users_uuid")
        else:
            print("Exists: fk_orders_created_by_users_uuid")

        if not table_exists(db, "trips"):
            db.execute(
                text(
                    """
                    CREATE TABLE trips (
                        id SERIAL PRIMARY KEY,
                        order_id INTEGER NOT NULL REFERENCES orders (id),
                        driver_id INTEGER NOT NULL REFERENCES drivers (id),
                        start_time TIMESTAMP NULL,
                        end_time TIMESTAMP NULL,
                        status VARCHAR(64) NULL,
                        current_location JSON NULL,
                        created_at TIMESTAMP NULL,
                        updated_at TIMESTAMP NULL
                    )
                    """
                )
            )
            print("Added: trips table")
        else:
            print("Exists: trips")

        db.execute(text("CREATE INDEX IF NOT EXISTS ix_trips_order_id ON trips (order_id)"))
        db.execute(text("CREATE INDEX IF NOT EXISTS ix_trips_driver_id ON trips (driver_id)"))
        db.execute(text("CREATE INDEX IF NOT EXISTS ix_trips_status ON trips (status)"))
        db.execute(text("CREATE INDEX IF NOT EXISTS ix_trips_created_at ON trips (created_at)"))

        db.commit()
        print("OK: hotfix committed.")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
