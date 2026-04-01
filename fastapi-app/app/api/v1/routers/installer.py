from typing import Optional, Any
from pydantic import BaseModel
import subprocess
import os

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.core.database import get_db, engine
from app.models.user import User
from app.models.company import Company
from alembic.config import Config
from alembic import command

router = APIRouter(prefix="/int/v1/installer", tags=["installer"])


class CreateDatabaseRequest(BaseModel):
    host: str
    port: int = 3306
    database: str
    username: str
    password: str


@router.get("/initialize", response_model=dict)
def initialize_installer(
    db: Session = Depends(get_db),
):
    """Check if installation is needed."""
    try:
        # Check database connection
        db.execute(text("SELECT 1"))
        database_configured = True
    except Exception:
        database_configured = False
    
    # Check if migrations have been run (check for users table)
    migrations_run = False
    if database_configured:
        try:
            db.execute(text("SELECT 1 FROM users LIMIT 1"))
            migrations_run = True
        except Exception:
            migrations_run = False
    
    # Check if seeded (check for users)
    seeded = False
    if migrations_run:
        user_count = db.query(User).count()
        seeded = user_count > 0
    
    needs_installation = not database_configured or not migrations_run or not seeded
    
    return {
        "needs_installation": needs_installation,
        "database_configured": database_configured,
        "migrations_run": migrations_run,
        "seeded": seeded
    }


@router.post("/createdb", response_model=dict)
def create_database(
    payload: CreateDatabaseRequest,
    db: Session = Depends(get_db),
):
    """Create database (for MySQL/MariaDB - PostgreSQL handled differently)."""
    # Note: For PostgreSQL, database creation is typically done by admin user
    # This endpoint is mainly for MySQL/MariaDB compatibility
    try:
        # For PostgreSQL, we can't create database from within a transaction
        # Database should be created manually or via init script
        return {
            "status": "ok",
            "message": "Database creation should be done via PostgreSQL admin or init script",
            "database": payload.database,
            "note": "For PostgreSQL, use CREATE DATABASE command or docker init script"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating database: {str(e)}"
        )


@router.post("/migrate", response_model=dict)
def run_migrations(
    db: Session = Depends(get_db),
):
    """Run Alembic migrations."""
    try:
        # Get Alembic config
        alembic_cfg = Config("alembic.ini")
        
        # Run migrations
        command.upgrade(alembic_cfg, "head")
        
        return {
            "status": "ok",
            "message": "Migrations completed successfully"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error running migrations: {str(e)}"
        )


@router.post("/seed", response_model=dict)
def seed_database(
    db: Session = Depends(get_db),
):
    """Seed database with initial data."""
    try:
        from app.models.role import Role
        from datetime import datetime, timezone
        import uuid
        
        # Check if already seeded
        role_count = db.query(Role).count()
        if role_count > 0:
            return {
                "status": "ok",
                "message": "Database already seeded",
                "skipped": True
            }
        
        # Create default roles
        roles = [
            {"name": "super-admin", "guard_name": "web"},
            {"name": "admin", "guard_name": "web"},
            {"name": "manager", "guard_name": "web"},
            {"name": "driver", "guard_name": "web"},
            {"name": "user", "guard_name": "web"},
        ]
        
        for role_data in roles:
            role = Role(
                id=str(uuid.uuid4()),
                name=role_data["name"],
                guard_name=role_data["guard_name"],
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
            )
            db.add(role)
        
        db.commit()
        
        return {
            "status": "ok",
            "message": "Database seeded successfully",
            "roles_created": len(roles)
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error seeding database: {str(e)}"
        )

