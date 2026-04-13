"""Ensure FLEET_CUSTOMER users have Contact rows (type customer) for admin Customers + order linking."""
from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.company_scope import require_company_uuid
from app.core.roles import FLEET_CUSTOMER
from app.models.contact import Contact
from app.models.user import User


def ensure_fleet_customer_contact(db: Session, user: User) -> Contact:
    """Get or create a customer Contact for this fleet customer user (same transaction)."""
    company_uuid = require_company_uuid(user)
    if not user.uuid:
        raise ValueError("User uuid required")

    existing = (
        db.query(Contact)
        .filter(
            Contact.company_uuid == company_uuid,
            Contact.user_uuid == user.uuid,
            Contact.deleted_at.is_(None),
        )
        .first()
    )
    if existing:
        if (existing.type or "").lower() != "customer":
            existing.type = "customer"
            existing.updated_at = datetime.utcnow()
            db.add(existing)
        return existing

    now = datetime.utcnow()
    c = Contact(
        uuid=str(uuid.uuid4()),
        public_id=f"contact_{uuid.uuid4().hex[:12]}",
        company_uuid=company_uuid,
        user_uuid=user.uuid,
        name=(user.name or user.email or "Fleet customer").strip() or "Fleet customer",
        email=user.email,
        phone=user.phone,
        type="customer",
        meta={"source": "fleet_customer_account"},
        created_at=now,
        updated_at=now,
    )
    db.add(c)
    db.flush()
    return c


def sync_fleet_customer_contacts_for_company(db: Session, company_uuid: str) -> int:
    """Create missing customer contacts for all fleet-customer users in the company. Returns rows created."""
    rows = (
        db.query(User)
        .filter(
            User.company_uuid == company_uuid,
            User.uuid.isnot(None),
            User.deleted_at.is_(None),
            User.role.isnot(None),
            func.upper(User.role) == FLEET_CUSTOMER,
        )
        .all()
    )
    created = 0
    for u in rows:
        has = (
            db.query(Contact)
            .filter(
                Contact.company_uuid == company_uuid,
                Contact.user_uuid == u.uuid,
                Contact.deleted_at.is_(None),
            )
            .first()
        )
        if has:
            continue
        ensure_fleet_customer_contact(db, u)
        created += 1
    return created
