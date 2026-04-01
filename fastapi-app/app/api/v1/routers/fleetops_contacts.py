from typing import List
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.v1.routers.auth import _get_current_user
from app.core.database import get_db
from app.models.contact import Contact
from app.models.user import User
from app.schemas.contact import ContactCreate, ContactOut, ContactUpdate, ContactResponse, ContactsResponse

router = APIRouter(prefix="/fleetops/v1/contacts", tags=["fleetops-contacts"])


@router.get("/", response_model=ContactsResponse)
def list_contacts(
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    q = db.query(Contact).filter(Contact.company_uuid == current.company_uuid, Contact.deleted_at.is_(None))
    contacts = q.offset(offset).limit(limit).all()
    return {"contacts": contacts}


@router.get("/{id}", response_model=ContactResponse)
def get_contact(
    id: str,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    contact = (
        db.query(Contact)
        .filter(Contact.company_uuid == current.company_uuid, (Contact.uuid == id) | (Contact.public_id == id))
        .first()
    )
    if not contact:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found.")
    return {"contact": contact}


@router.post("/", response_model=ContactResponse, status_code=status.HTTP_201_CREATED)
def create_contact(
    payload: ContactCreate,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    contact = Contact()
    contact.uuid = str(uuid.uuid4())
    contact.public_id = f"contact_{uuid.uuid4().hex[:12]}"
    contact.company_uuid = current.company_uuid
    contact.name = payload.name
    contact.email = payload.email
    contact.phone = payload.phone
    contact.type = payload.type or "contact"
    contact.title = payload.title
    contact.meta = payload.meta

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
    current: User = Depends(_get_current_user),
):
    contact = (
        db.query(Contact)
        .filter(Contact.company_uuid == current.company_uuid, (Contact.uuid == id) | (Contact.public_id == id))
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
    current: User = Depends(_get_current_user),
):
    contact = (
        db.query(Contact)
        .filter(Contact.company_uuid == current.company_uuid, (Contact.uuid == id) | (Contact.public_id == id))
        .first()
    )
    if not contact:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found.")

    contact.deleted_at = datetime.utcnow()
    db.add(contact)
    db.commit()
    return {"contact": contact}



