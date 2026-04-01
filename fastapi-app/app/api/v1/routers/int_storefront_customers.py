from typing import List, Optional
import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.api.v1.routers.auth import _get_current_user
from app.core.database import get_db
from app.models.contact import Contact
from app.models.user import User

router = APIRouter(prefix="/int/v1/customers", tags=["int-storefront-customers"])


class CustomerCreate(BaseModel):
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    type: str = "customer"


class CustomerUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None


@router.get("/", response_model=List[dict])
def list_customers(
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    customers = db.query(Contact).filter(
        Contact.company_uuid == current.company_uuid,
        Contact.type == "customer",
        Contact.deleted_at.is_(None)
    ).offset(offset).limit(limit).all()
    return [c.__dict__ for c in customers]


@router.get("/{id}", response_model=dict)
def get_customer(
    id: str,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    customer = db.query(Contact).filter(
        Contact.company_uuid == current.company_uuid,
        Contact.type == "customer",
        (Contact.uuid == id) | (Contact.public_id == id),
        Contact.deleted_at.is_(None)
    ).first()
    if not customer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")
    return customer.__dict__


@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED)
def create_customer(
    payload: CustomerCreate,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    customer = Contact()
    customer.uuid = str(uuid.uuid4())
    customer.company_uuid = current.company_uuid
    customer.created_by_uuid = current.uuid
    customer.name = payload.name
    customer.email = payload.email
    customer.phone = payload.phone
    customer.type = payload.type
    
    db.add(customer)
    db.commit()
    db.refresh(customer)
    return customer.__dict__


@router.put("/{id}", response_model=dict)
@router.patch("/{id}", response_model=dict)
def update_customer(
    id: str,
    payload: CustomerUpdate,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    customer = db.query(Contact).filter(
        Contact.company_uuid == current.company_uuid,
        Contact.type == "customer",
        (Contact.uuid == id) | (Contact.public_id == id),
        Contact.deleted_at.is_(None)
    ).first()
    if not customer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")
    
    for field, value in payload.dict(exclude_unset=True).items():
        if hasattr(customer, field):
            setattr(customer, field, value)
    
    db.add(customer)
    db.commit()
    db.refresh(customer)
    return customer.__dict__


@router.delete("/{id}", status_code=status.HTTP_200_OK)
def delete_customer(
    id: str,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    customer = db.query(Contact).filter(
        Contact.company_uuid == current.company_uuid,
        Contact.type == "customer",
        (Contact.uuid == id) | (Contact.public_id == id),
        Contact.deleted_at.is_(None)
    ).first()
    if not customer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")
    
    customer.deleted_at = datetime.utcnow()
    db.add(customer)
    db.commit()
    return customer.__dict__

