#!/usr/bin/env python3
"""
Set alembic_version to `head` without executing any migration SQL.

Use this when:
  - The database already has tables (created manually, restored, or from an older flow).
  - `alembic upgrade head` fails on 0001 with DuplicateTable (users already exists).
  - You have confirmed the live schema matches the migration chain through `head`.

This does NOT add missing columns or tables. If something is missing, apply the right
migration SQL, or run `python scripts/hotfix_missing_columns.py`, then stamp.

Usage (from fastapi-app, with venv active and .env pointing at this DB):

  python scripts/stamp_alembic_head.py

After stamping, use `alembic upgrade head` only for *new* migrations added later.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def main() -> None:
    os.chdir(ROOT)
    sys.path.insert(0, str(ROOT))

    ini = ROOT / "alembic.ini"
    if not ini.exists():
        print(f"ERROR: {ini} not found.")
        sys.exit(1)

    from alembic import command
    from alembic.config import Config

    cfg = Config(str(ini))
    command.stamp(cfg, "head")
    print("OK: alembic_version set to head (no DDL was executed).")


if __name__ == "__main__":
    main()
