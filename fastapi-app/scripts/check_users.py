#!/usr/bin/env python3
"""Check existing users in database."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.user import User

db: Session = SessionLocal()

try:
    users = db.query(User).filter(User.deleted_at.is_(None)).all()
    
    print(f"📊 Found {len(users)} users in database:\n")
    
    for user in users:
        print(f"  - Email: {user.email}")
        print(f"    Name: {user.name}")
        print(f"    Type: {user.type}")
        print(f"    UUID: {user.uuid}")
        print(f"    Has Password: {'Yes' if user.password else 'No'}")
        print()
    
    # Check specifically for admin user
    admin_user = db.query(User).filter(
        User.email == "admin@techliv.net",
        User.deleted_at.is_(None)
    ).first()
    
    if admin_user:
        print("✅ Admin user found!")
        print(f"   Email: {admin_user.email}")
        print(f"   Password hash exists: {'Yes' if admin_user.password else 'No'}")
    else:
        print("❌ Admin user (admin@techliv.net) NOT found!")
        print("   You need to run: python scripts/create_initial_users.py")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
finally:
    db.close()

