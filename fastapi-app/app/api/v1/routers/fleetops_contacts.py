from datetime import datetime
from typing import List
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.api.v1.routers.auth import _get_current_user
from app.core.database import get_db
from app.core.roles import (
    ADMIN,
    DISPATCHER,
    DRIVER,
    OPERATIONS_MANAGER,
    effective_user_role,
    require_roles,
)
from app.models.contact import Contact
from app.models.order import Order
from app.models.user import User
from app.schemas.contact import ContactCreate, ContactOut, ContactUpdate, ContactResponse, ContactsResponse
from app.services.fleet_customer_contacts import sync_fleet_customer_contacts_for_company

router = APIRouter(prefix="/fleetops/v1/contacts", tags=["fleetops-contacts"])


def _require_company_uuid(current: User) -> str:
    if not current.company_uuid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current user is not associated with a company.",
        )
    return current.company_uuid


def _deny_driver_customer_access(current: User) -> None:
    if effective_user_role(current) == DRIVER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions",
        )


@router.get("", response_model=ContactsResponse)
@router.get("/", response_model=ContactsResponse)
def list_contacts(
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    kind: str | None = Query(None, description="Filter by contact type, e.g. customer"),
    search: str | None = Query(None, description="Search name, phone, or email"),
):
    _deny_driver_customer_access(current)
    company_uuid = _require_company_uuid(current)
    if sync_fleet_customer_contacts_for_company(db, company_uuid) > 0:
        db.commit()
    q = db.query(Contact).filter(Contact.company_uuid == company_uuid, Contact.deleted_at.is_(None))
    if kind:
        q = q.filter(Contact.type == kind)
    if search and search.strip():
        s = f"%{search.strip()}%"
        q = q.filter(or_(Contact.name.ilike(s), Contact.phone.ilike(s), Contact.email.ilike(s)))
    contacts = q.offset(offset).limit(limit).all()
    return {"contacts": contacts}


@router.get("/{id}", response_model=ContactResponse)
def get_contact(
    id: str,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    _deny_driver_customer_access(current)
    company_uuid = _require_company_uuid(current)
    contact = (
        db.query(Contact)
        .filter(
            Contact.company_uuid == company_uuid,
            Contact.deleted_at.is_(None),
            (Contact.uuid == id) | (Contact.public_id == id),
        )
        .first()
    )
    if not contact:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found.")
    return {"contact": contact}


@router.post("", response_model=ContactResponse, status_code=status.HTTP_201_CREATED)
@router.post("/", response_model=ContactResponse, status_code=status.HTTP_201_CREATED)
def create_contact(
    payload: ContactCreate,
    db: Session = Depends(get_db),
    current: User = Depends(require_roles(ADMIN, OPERATIONS_MANAGER, DISPATCHER)),
):
    company_uuid = _require_company_uuid(current)
    contact = Contact()
    contact.uuid = str(uuid.uuid4())
    contact.public_id = f"contact_{uuid.uuid4().hex[:12]}"
    contact.company_uuid = company_uuid
    contact.name = payload.name
    contact.email = payload.email
    contact.phone = payload.phone
    contact.type = payload.type or "contact"
    contact.title = payload.title
    contact.meta = payload.meta
    contact.created_at = datetime.utcnow()
    contact.updated_at = datetime.utcnow()

    db.add(contact)
    db.commit()
    db.refresh(contact)
    return {"contact": contact}


@router.put("/{id}", response_model=ContactResponse)
@router.patch("/{id}", response_model=ContactResponse)
def update_contact(
    id: str,
    payload: ContactUpdate,
    db: Session = Depends(get_db),
    current: User = Depends(require_roles(ADMIN, OPERATIONS_MANAGER, DISPATCHER)),
):
    company_uuid = _require_company_uuid(current)
    contact = (
        db.query(Contact)
        .filter(
            Contact.company_uuid == company_uuid,
            Contact.deleted_at.is_(None),
            (Contact.uuid == id) | (Contact.public_id == id),
        )
        .first()
    )
    if not contact:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found.")

    for field, value in payload.dict(exclude_unset=True).items():
        setattr(contact, field, value)

    db.add(contact)
    db.commit()
    db.refresh(contact)
    return {"contact": contact}


@router.delete("/{id}", response_model=ContactResponse)
def delete_contact(
    id: str,
    db: Session = Depends(get_db),
    current: User = Depends(require_roles(ADMIN)),
):
    company_uuid = _require_company_uuid(current)
    contact = (
        db.query(Contact)
        .filter(
            Contact.company_uuid == company_uuid,
            Contact.deleted_at.is_(None),
            (Contact.uuid == id) | (Contact.public_id == id),
        )
        .first()
    )
    if not contact:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found.")

    if (contact.type or "").lower() == "customer" and contact.uuid:
        has_orders = (
            db.query(Order)
            .filter(
                Order.company_uuid == company_uuid,
                Order.customer_uuid == contact.uuid,
                Order.deleted_at.is_(None),
            )
            .first()
        )
        if has_orders:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete customer with existing orders",
            )

    contact.deleted_at = datetime.utcnow()
    db.add(contact)
    db.commit()
    return {"contact": contact}



