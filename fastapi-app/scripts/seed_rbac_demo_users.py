#!/usr/bin/env python3
"""
Create (or update) demo users—one per logistics RBAC role—for manual UI/API testing.

Prerequisites:
  - Database running and migrated (including 0017_user_role_rbac for users.role).
  - Run from fastapi-app:  python scripts/seed_rbac_demo_users.py

Idempotent: re-running updates password hash and role for the same emails.
"""
from __future__ import annotations

import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.core.security import get_password_hash
from app.models.company import Company
from app.models.company_user import CompanyUser
from app.models.driver import Driver
from app.models.user import User

# Shared password for all demo accounts (change in production).
DEMO_PASSWORD = "RbacDemo123"

DEMO_ACCOUNTS: list[tuple[str, str, str]] = [
    # email, logistics role, display name — short addresses for local testing only
    ("admin@demo.local", "ADMIN", "Demo Admin"),
    ("operations@demo.local", "OPERATIONS_MANAGER", "Demo Operations Manager"),
    ("dispatcher@demo.local", "DISPATCHER", "Demo Dispatcher"),
    ("driver@demo.local", "DRIVER", "Demo Driver"),
    ("viewer@demo.local", "VIEWER", "Demo Viewer"),
    ("fleet.customer@demo.local", "FLEET_CUSTOMER", "Demo Fleet Customer"),
]


def _ensure_company(db: Session) -> str:
    company = db.query(Company).filter(Company.deleted_at.is_(None)).first()
    if company and company.uuid:
        return company.uuid
    company_uuid = str(uuid.uuid4())
    c = Company(
        uuid=company_uuid,
        public_id=f"comp_{uuid.uuid4().hex[:12]}",
        name="RBAC Demo Company",
        phone="+10000000000",
        timezone="UTC",
        country="US",
        currency="USD",
        status="active",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    db.add(c)
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
    db.add(
        CompanyUser(
            uuid=str(uuid.uuid4()),
            company_uuid=company_uuid,
            user_uuid=user_uuid,
            status="active",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
    )


def _ensure_driver_profile(db: Session, *, company_uuid: str, user_uuid: str) -> None:
    existing = (
        db.query(Driver)
        .filter(
            Driver.user_uuid == user_uuid,
            Driver.company_uuid == company_uuid,
            Driver.deleted_at.is_(None),
        )
        .first()
    )
    if existing:
        return
    now = datetime.now(timezone.utc)
    db.add(
        Driver(
            uuid=str(uuid.uuid4()),
            public_id=f"drv_{uuid.uuid4().hex[:12]}",
            company_uuid=company_uuid,
            user_uuid=user_uuid,
            drivers_license_number="DEMO-RBAC-DRV",
            status="active",
            online=0,
            created_at=now,
            updated_at=now,
        )
    )


def main() -> None:
    db: Session = SessionLocal()
    try:
        company_uuid = _ensure_company(db)
        now = datetime.now(timezone.utc)
        pwd_hash = get_password_hash(DEMO_PASSWORD)

        for email, role, name in DEMO_ACCOUNTS:
            user = db.query(User).filter(User.email == email, User.deleted_at.is_(None)).first()
            if user:
                user.name = name
                user.role = role
                user.password = pwd_hash
                user.company_uuid = company_uuid
                user.updated_at = now
            else:
                user_uuid = str(uuid.uuid4())
                user = User(
                    uuid=user_uuid,
                    public_id=f"user_{uuid.uuid4().hex[:12]}",
                    name=name,
                    email=email,
                    password=pwd_hash,
                    company_uuid=company_uuid,
                    timezone="UTC",
                    country="US",
                    type="user",
                    status="active",
                    role=role,
                    email_verified_at=now,
                    created_at=now,
                    updated_at=now,
                )
                db.add(user)
                db.flush()

            _ensure_company_user(db, company_uuid, user.uuid or "")
            if role == "DRIVER":
                _ensure_driver_profile(db, company_uuid=company_uuid, user_uuid=user.uuid or "")

        db.commit()
        print("OK: RBAC demo users are ready.\n")
        print("Use the same password for every account:")
        print(f"  Password: {DEMO_PASSWORD}\n")
        print(f"{'Role':<22} {'Email'}")
        print("-" * 56)
        for email, role, _ in DEMO_ACCOUNTS:
            print(f"{role:<22} {email}")
        print("\nLogin in the dashboard with Email + Password (identity field = email).")
    except Exception as e:
        db.rollback()
        print(f"ERROR: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
