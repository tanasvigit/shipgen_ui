"""
Fix driver profile for existing DRIVER users.

This script ensures that users with DRIVER role have a linked driver record.
Run this if you get "Driver profile not found for current user" errors.

Usage:
    python scripts/fix_driver_profiles.py
"""

import sys
import uuid
from datetime import datetime, timezone

# Add parent directory to path
sys.path.insert(0, '.')

from app.core.database import SessionLocal
from app.models.user import User
from app.models.driver import Driver
from app.core.roles import DRIVER, effective_user_role


def fix_driver_profiles():
    """Create driver records for users with DRIVER role who don't have one."""
    db = SessionLocal()
    
    try:
        # Find all users with DRIVER role
        driver_users = db.query(User).filter(
            User.role == DRIVER,
            User.deleted_at.is_(None)
        ).all()
        
        if not driver_users:
            print("⚠ No DRIVER users found in database")
            print("  Run 'python scripts/seed_rbac_demo_users.py' first to create demo users")
            return
        
        print(f"Found {len(driver_users)} DRIVER user(s)")
        print("=" * 60)
        
        fixed_count = 0
        
        for user in driver_users:
            print(f"\nChecking user: {user.email}")
            print(f"  UUID: {user.uuid}")
            print(f"  Company UUID: {user.company_uuid}")
            print(f"  Role: {user.role}")
            
            # Check if driver record exists
            existing_driver = db.query(Driver).filter(
                Driver.user_uuid == user.uuid,
                Driver.company_uuid == user.company_uuid,
                Driver.deleted_at.is_(None)
            ).first()
            
            if existing_driver:
                print(f"  ✓ Driver record already exists")
                print(f"    Driver UUID: {existing_driver.uuid}")
                print(f"    Status: {existing_driver.status}")
                print(f"    Online: {existing_driver.online}")
            else:
                print(f"  ✗ No driver record found - creating one...")
                
                # Create driver record
                new_driver = Driver(
                    uuid=str(uuid.uuid4()),
                    public_id=str(uuid.uuid4())[:8],
                    company_uuid=user.company_uuid,
                    user_uuid=user.uuid,
                    drivers_license_number=f"DL-{user.email.split('@')[0].upper()}",
                    status="active",
                    online=0,
                    created_at=datetime.now(timezone.utc),
                    updated_at=datetime.now(timezone.utc)
                )
                
                db.add(new_driver)
                db.commit()
                db.refresh(new_driver)
                
                print(f"  ✓ Created driver record")
                print(f"    Driver UUID: {new_driver.uuid}")
                print(f"    License: {new_driver.drivers_license_number}")
                print(f"    Status: {new_driver.status}")
                print(f"    Online: {new_driver.online}")
                
                fixed_count += 1
        
        print("\n" + "=" * 60)
        print(f"✓ Complete! Fixed {fixed_count} driver record(s)")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    fix_driver_profiles()
