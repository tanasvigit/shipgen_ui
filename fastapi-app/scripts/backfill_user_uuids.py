#!/usr/bin/env python3
"""
Backfill missing users.uuid/public_id values.

Run from fastapi-app:
  python scripts/backfill_user_uuids.py
"""
from __future__ import annotations

import sys
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.models.user import User


def main() -> None:
    db: Session = SessionLocal()
    try:
        rows = db.query(User).all()
        changed = 0
        for user in rows:
            touched = False
            if not user.uuid:
                user.uuid = str(uuid.uuid4())
                touched = True
            if not user.public_id:
                user.public_id = f"user_{uuid.uuid4().hex[:12]}"
                touched = True
            if touched:
                db.add(user)
                changed += 1
        db.commit()
        print(f"OK: updated {changed} user row(s).")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
