#!/usr/bin/env python3
"""
Script to create initial users for TechLiv API.
Creates:
1. A super admin user
2. A regular user
3. A company
4. Assigns super admin role to the first user
"""

import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import text
from sqlalchemy.orm import Session
from app.core.database import SessionLocal, engine
from app.core.security import get_password_hash
from app.models.user import User
from app.models.company import Company
from app.models.company_user import CompanyUser
from app.models.role import Role


def create_initial_users():
    """Create initial users and company."""
    db: Session = SessionLocal()
    
    try:
        # Check if admin user already exists
        admin_user = db.query(User).filter(
            User.email == "admin@techliv.net",
            User.deleted_at.is_(None)
        ).first()
        
        if admin_user:
            print("[WARN] Admin user (admin@techliv.net) already exists. Skipping creation.")
            print("   If you want to recreate, delete the user first.")
            return
        
        # Check if regular user already exists
        regular_user = db.query(User).filter(
            User.email == "user@techliv.net",
            User.deleted_at.is_(None)
        ).first()
        
        if regular_user:
            print("[WARN] Regular user (user@techliv.net) already exists. Skipping creation.")
            print("   If you want to recreate, delete the user first.")
            return
        
        # Get or create company (use existing if available)
        company = db.query(Company).filter(Company.name == "ShipGen Company").first()
        if not company:
            company_uuid = str(uuid.uuid4())
            company = Company(
                uuid=company_uuid,
                public_id=f"comp_{uuid.uuid4().hex[:12]}",
                name="ShipGen Company",
                description="Default company for ShipGen",
                phone="+1234567890",
                timezone="UTC",
                country="US",
                currency="USD",
                status="active",
                owner_uuid=None,  # Will be set after user creation
            )
            db.add(company)
            db.flush()
        else:
            company_uuid = company.uuid
        
        # Create Super Admin user
        admin_uuid = str(uuid.uuid4())
        admin_user = User(
            uuid=admin_uuid,
            public_id=f"user_{uuid.uuid4().hex[:12]}",
            name="Super Admin",
            email="admin@techliv.net",
            phone="+1234567890",
            password=get_password_hash("admin123"),
            company_uuid=company_uuid,
            timezone="UTC",
            country="US",
            type="admin",
            status="active",
            email_verified_at=datetime.now(timezone.utc),
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        db.add(admin_user)
        db.flush()
        
        # Set company owner if not set
        if not company.owner_uuid:
            company.owner_uuid = admin_uuid
            db.add(company)
        
        # Create CompanyUser relationship for admin (if not exists)
        existing_company_user = db.query(CompanyUser).filter(
            CompanyUser.company_uuid == company_uuid,
            CompanyUser.user_uuid == admin_uuid
        ).first()
        
        if not existing_company_user:
            company_user_admin = CompanyUser(
                uuid=str(uuid.uuid4()),
                company_uuid=company_uuid,
                user_uuid=admin_uuid,
                status="active",
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
            )
            db.add(company_user_admin)
        
        # Create Regular User (if not exists)
        regular_user_existing = db.query(User).filter(
            User.email == "user@techliv.net",
            User.deleted_at.is_(None)
        ).first()
        
        if not regular_user_existing:
            regular_uuid = str(uuid.uuid4())
            regular_user = User(
                uuid=regular_uuid,
                public_id=f"user_{uuid.uuid4().hex[:12]}",
                name="Regular User",
                email="user@techliv.net",
                phone="+1234567891",
                password=get_password_hash("user123"),
                company_uuid=company_uuid,
                timezone="UTC",
                country="US",
                type="user",
                status="active",
                email_verified_at=datetime.now(timezone.utc),
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
            )
            db.add(regular_user)
            db.flush()
            
            # Create CompanyUser relationship for regular user
            company_user_regular = CompanyUser(
                uuid=str(uuid.uuid4()),
                company_uuid=company_uuid,
                user_uuid=regular_uuid,
                status="active",
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
            )
            db.add(company_user_regular)
        
        # Create or get Super Admin role
        super_admin_role = db.query(Role).filter(
            Role.name == "super-admin",
            Role.guard_name == "web"
        ).first()
        
        if not super_admin_role:
            super_admin_role = Role(
                id=str(uuid.uuid4()),
                name="super-admin",
                guard_name="web",
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
            )
            db.add(super_admin_role)
            db.flush()
        
        # Assign super admin role to admin user via model_has_roles
        # Check if role assignment already exists
        existing_assignment = db.execute(
            text("""
                SELECT 1 FROM model_has_roles
                WHERE role_id = :role_id AND model_uuid = :model_uuid AND model_type = :model_type
            """),
            {
                "role_id": super_admin_role.id,
                "model_uuid": admin_uuid,
                "model_type": "App\\Models\\User"
            }
        ).first()
        
        if not existing_assignment:
            db.execute(
                text("""
                    INSERT INTO model_has_roles (role_id, model_type, model_uuid)
                    VALUES (:role_id, :model_type, :model_uuid)
                """),
                {
                    "role_id": super_admin_role.id,
                    "model_type": "App\\Models\\User",
                    "model_uuid": admin_uuid
                }
            )
        
        db.commit()
        
        print("OK: Successfully created initial users!")
        print("\nUser Credentials:")
        print("=" * 50)
        print("Super Admin:")
        print(f"  Email: admin@techliv.net")
        print(f"  Password: admin123")
        print(f"  UUID: {admin_uuid}")
        print("\nRegular User:")
        print(f"  Email: user@techliv.net")
        print(f"  Password: user123")
        print(f"  UUID: {regular_uuid}")
        print("\nCompany:")
        print(f"  Name: ShipGen Company")
        print(f"  UUID: {company_uuid}")
        print("=" * 50)
        print("\nYou can now login using these credentials at:")
        print("   POST http://localhost:9001/int/v1/auth/login")
        print("\n   Body: {")
        print('     "identity": "admin@techliv.net",')
        print('     "password": "admin123"')
        print("   }")
        
    except Exception as e:
        db.rollback()
        print(f"ERROR creating users: {e}")
        import traceback
        traceback.print_exc()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    create_initial_users()

