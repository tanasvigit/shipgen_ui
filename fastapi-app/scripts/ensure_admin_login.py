#!/usr/bin/env python3
"""
Ensure admin@techliv.net can login with password admin123.
- Creates admin user (and company) if missing
- Resets admin password to admin123
- Disables system-wide 2FA so login works without 2FA step
Run: docker compose -f fastapi-app/docker-compose.yml exec api python scripts/ensure_admin_login.py
"""

import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.core.security import get_password_hash, verify_password
from app.models.user import User
from app.models.company import Company
from app.models.company_user import CompanyUser
from app.models.twofa import TwoFaSetting

EMAIL = "admin@techliv.net"
PASSWORD = "admin123"


def ensure_admin_login():
    db: Session = SessionLocal()
    try:
        # 1. Disable system 2FA so login doesn't require 2FA
        twofa = (
            db.query(TwoFaSetting)
            .filter(TwoFaSetting.subject_type == "system", TwoFaSetting.subject_uuid.is_(None))
            .first()
        )
        if twofa is None:
            twofa = TwoFaSetting(
                subject_type="system",
                subject_uuid=None,
                enabled=False,
                method="email",
                enforced=False,
            )
            db.add(twofa)
            db.flush()
        if twofa.enabled:
            twofa.enabled = False
            twofa.enforced = False
            db.add(twofa)
            print("  Disabled system 2FA (so login works without 2FA).")

        # 2. Find or create admin user
        admin = (
            db.query(User)
            .filter(User.email == EMAIL, User.deleted_at.is_(None))
            .first()
        )

        if not admin:
            # Create company and admin (minimal create_initial_users)
            company = db.query(Company).filter(Company.name == "ShipGen Company").first()
            if not company:
                company = Company(
                    uuid=str(uuid.uuid4()),
                    public_id=f"comp_{uuid.uuid4().hex[:12]}",
                    name="ShipGen Company",
                    description="Default company",
                    phone="+1234567890",
                    timezone="UTC",
                    country="US",
                    currency="USD",
                    status="active",
                    owner_uuid=None,
                )
                db.add(company)
                db.flush()

            admin_uuid = str(uuid.uuid4())
            admin = User(
                uuid=admin_uuid,
                public_id=f"user_{uuid.uuid4().hex[:12]}",
                name="Super Admin",
                email=EMAIL,
                phone="+1234567890",
                password=get_password_hash(PASSWORD),
                company_uuid=company.uuid,
                timezone="UTC",
                country="US",
                type="admin",
                status="active",
                email_verified_at=datetime.now(timezone.utc),
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
            )
            db.add(admin)
            db.flush()
            if not company.owner_uuid:
                company.owner_uuid = admin.uuid
                db.add(company)
            cu = CompanyUser(
                uuid=str(uuid.uuid4()),
                company_uuid=company.uuid,
                user_uuid=admin.uuid,
                status="active",
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
            )
            db.add(cu)
            print("  Created admin user and company.")
        else:
            # Reset password to admin123
            admin.password = get_password_hash(PASSWORD)
            admin.updated_at = datetime.now(timezone.utc)
            db.add(admin)
            print("  Reset admin password to admin123.")

        # 3. Ensure admin has at least one organization (frontend requires it or logs out)
        company = db.query(Company).filter(Company.name == "ShipGen Company").first()
        if not company:
            company = Company(
                uuid=str(uuid.uuid4()),
                public_id=f"comp_{uuid.uuid4().hex[:12]}",
                name="ShipGen Company",
                description="Default company",
                phone="+1234567890",
                timezone="UTC",
                country="US",
                currency="USD",
                status="active",
                owner_uuid=admin.uuid,
            )
            db.add(company)
            db.flush()
            print("  Created default company.")
        if not company.owner_uuid:
            company.owner_uuid = admin.uuid
            db.add(company)
        if not admin.company_uuid:
            admin.company_uuid = company.uuid
            db.add(admin)
        existing_cu = (
            db.query(CompanyUser)
            .filter(
                CompanyUser.company_uuid == company.uuid,
                CompanyUser.user_uuid == admin.uuid,
            )
            .first()
        )
        if not existing_cu:
            cu = CompanyUser(
                uuid=str(uuid.uuid4()),
                company_uuid=company.uuid,
                user_uuid=admin.uuid,
                status="active",
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
            )
            db.add(cu)
            print("  Linked admin to company (organizations will no longer be empty).")

        # Verify password works
        ok = verify_password(PASSWORD, admin.password)
        db.commit()
        if ok:
            print("  Verified: password hash is valid.")
        else:
            print("  Warning: password verification failed after reset (unexpected).")

        print("\n  Login with:")
        print(f"    Email:    {EMAIL}")
        print(f"    Password: {PASSWORD}")
        print("\n  Then open http://localhost:4200 and sign in.")
        return 0
    except Exception as e:
        db.rollback()
        print(f"  Error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        db.close()


if __name__ == "__main__":
    print("Ensuring admin can login...")
    sys.exit(ensure_admin_login())
