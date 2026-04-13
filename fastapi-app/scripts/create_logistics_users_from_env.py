#!/usr/bin/env python3
"""
Create or update logistics users using DB credentials from .env.

Usage:
  cd fastapi-app
  python scripts/create_logistics_users_from_env.py

Optional env vars:
  DEMO_USERS_PASSWORD=YourStrongPassword
  DEMO_USERS_COMPANY_UUID=<existing-company-uuid>

Notes:
  - Reads DB config from app.core.config -> .env
  - Idempotent: re-running updates existing users by email
  - Ensures DRIVER has a driver profile
  - Includes FLEET_CUSTOMER role user
"""

from __future__ import annotations

import os
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy import text
from sqlalchemy.orm import Session

# Allow "python scripts/..." to import app modules.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.core.database import SessionLocal
from app.core.security import get_password_hash
from app.models.company import Company
from app.models.company_user import CompanyUser
from app.models.driver import Driver
from app.models.user import User

# Same as dashboard demo + seed_rbac_demo_users.py (override with DEMO_USERS_PASSWORD).
DEFAULT_PASSWORD = "RbacDemo123"
DEMO_USERS: list[tuple[str, str, str]] = [
    ("admin@demo.local", "ADMIN", "Demo Admin"),
    ("operations@demo.local", "OPERATIONS_MANAGER", "Demo Operations Manager"),
    ("dispatcher@demo.local", "DISPATCHER", "Demo Dispatcher"),
    ("driver@demo.local", "DRIVER", "Demo Driver"),
    ("viewer@demo.local", "VIEWER", "Demo Viewer"),
    ("fleet.customer@demo.local", "FLEET_CUSTOMER", "Demo Fleet Customer"),
]


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _ensure_company(db: Session, forced_company_uuid: str | None = None) -> str:
    if forced_company_uuid:
        existing = (
            db.query(Company)
            .filter(Company.uuid == forced_company_uuid, Company.deleted_at.is_(None))
            .first()
        )
        if existing and existing.uuid:
            return str(existing.uuid)
        raise ValueError(f"Company with uuid '{forced_company_uuid}' was not found.")

    existing = db.query(Company).filter(Company.deleted_at.is_(None)).first()
    if existing and existing.uuid:
        return str(existing.uuid)

    company_uuid = str(uuid.uuid4())
    ts = _now()
    company = Company(
        uuid=company_uuid,
        public_id=f"comp_{uuid.uuid4().hex[:12]}",
        name="Demo Logistics Company",
        phone="+10000000000",
        timezone="UTC",
        country="US",
        currency="USD",
        status="active",
        created_at=ts,
        updated_at=ts,
    )
    db.add(company)
    db.flush()
    return company_uuid


def _ensure_company_user(db: Session, company_uuid: str, user_uuid: str) -> None:
    row = (
        db.query(CompanyUser)
        .filter(
            CompanyUser.company_uuid == company_uuid,
            CompanyUser.user_uuid == user_uuid,
            CompanyUser.deleted_at.is_(None),
        )
        .first()
    )
    if row:
        return
    ts = _now()
    db.add(
        CompanyUser(
            uuid=str(uuid.uuid4()),
            company_uuid=company_uuid,
            user_uuid=user_uuid,
            status="active",
            created_at=ts,
            updated_at=ts,
        )
    )


def _ensure_driver_profile(db: Session, company_uuid: str, user_uuid: str) -> None:
    existing = (
        db.query(Driver)
        .filter(
            Driver.company_uuid == company_uuid,
            Driver.user_uuid == user_uuid,
            Driver.deleted_at.is_(None),
        )
        .first()
    )
    if existing:
        if existing.status != "active":
            existing.status = "active"
            existing.updated_at = _now()
            db.add(existing)
        return

    ts = _now()
    db.add(
        Driver(
            uuid=str(uuid.uuid4()),
            public_id=f"drv_{uuid.uuid4().hex[:12]}",
            company_uuid=company_uuid,
            user_uuid=user_uuid,
            drivers_license_number="DEMO-DRV-001",
            status="active",
            online=0,
            created_at=ts,
            updated_at=ts,
        )
    )


def _drivers_table_has_last_seen_at(db: Session) -> bool:
    """Guard against partially-migrated DB schemas."""
    row = db.execute(
        text(
            """
            SELECT 1
            FROM information_schema.columns
            WHERE table_name = 'drivers' AND column_name = 'last_seen_at'
            LIMIT 1
            """
        )
    ).first()
    return bool(row)


def main() -> None:
    password = os.getenv("DEMO_USERS_PASSWORD", DEFAULT_PASSWORD)
    forced_company_uuid = os.getenv("DEMO_USERS_COMPANY_UUID")

    db: Session = SessionLocal()
    try:
        company_uuid = _ensure_company(db, forced_company_uuid)
        ts = _now()
        password_hash = get_password_hash(password)
        can_manage_driver_profile = _drivers_table_has_last_seen_at(db)
        if not can_manage_driver_profile:
            print(
                "WARN: drivers.last_seen_at is missing in DB schema; "
                "skipping DRIVER profile provisioning. Run Alembic migrations (upgrade head)."
            )

        for email, role, name in DEMO_USERS:
            user = db.query(User).filter(User.email == email, User.deleted_at.is_(None)).first()
            if user:
                user.name = name
                user.role = role
                user.password = password_hash
                user.company_uuid = company_uuid
                user.status = "active"
                user.type = user.type or "user"
                user.updated_at = ts
                if not user.public_id:
                    user.public_id = f"user_{uuid.uuid4().hex[:12]}"
                if not user.uuid:
                    user.uuid = str(uuid.uuid4())
                db.add(user)
            else:
                user = User(
                    uuid=str(uuid.uuid4()),
                    public_id=f"user_{uuid.uuid4().hex[:12]}",
                    name=name,
                    email=email,
                    password=password_hash,
                    company_uuid=company_uuid,
                    timezone="UTC",
                    country="US",
                    type="user",
                    status="active",
                    role=role,
                    email_verified_at=ts,
                    created_at=ts,
                    updated_at=ts,
                )
                db.add(user)
                db.flush()

            _ensure_company_user(db, company_uuid, str(user.uuid))
            if role == "DRIVER" and can_manage_driver_profile:
                _ensure_driver_profile(db, company_uuid, str(user.uuid))

        db.commit()

        print("OK: logistics demo users created/updated using .env DB credentials.")
        print(f"Company UUID: {company_uuid}")
        print(f"Password: {password}")
        print("\nRole                    Email")
        print("-" * 56)
        for email, role, _ in DEMO_USERS:
            print(f"{role:<23} {email}")

    except Exception as exc:
        db.rollback()
        print(f"ERROR: {exc}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
