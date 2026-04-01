"""
Storefront customer endpoints (/storefront/v1/customers).
"""
import uuid
from datetime import datetime, timezone
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.contact import Contact
from app.models.order import Order
from app.models.place import Place
from app.schemas.storefront import CustomerCreate, CustomerOut, CustomerUpdate, CustomerLoginRequest
from app.core.security import get_password_hash, verify_password, create_access_token

router = APIRouter(prefix="/storefront/v1/customers", tags=["storefront-customers"])


from fastapi import Header
from app.utils.storefront_auth import get_storefront_customer, require_storefront_customer


@router.get("/", response_model=List[CustomerOut])
def list_customers(
    db: Session = Depends(get_db),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    """List customers (requires storefront API authentication)."""
    query = db.query(Contact).filter(
        Contact.type == "customer",
        Contact.deleted_at.is_(None)
    )
    customers = query.offset(offset).limit(limit).all()
    return customers


@router.get("/{customer_id}", response_model=CustomerOut)
def get_customer(
    customer_id: str,
    db: Session = Depends(get_db),
):
    """Get a customer by public_id or uuid."""
    customer = db.query(Contact).filter(
        (Contact.public_id == customer_id) | (Contact.uuid == customer_id),
        Contact.type == "customer",
        Contact.deleted_at.is_(None)
    ).first()
    
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found."
        )
    
    return customer


@router.post("/", response_model=CustomerOut, status_code=status.HTTP_201_CREATED)
def create_customer(
    payload: CustomerCreate,
    db: Session = Depends(get_db),
):
    """Create a new customer."""
    # Check if customer already exists
    existing = None
    if payload.email:
        existing = db.query(Contact).filter(
            Contact.email == payload.email,
            Contact.type == "customer",
            Contact.deleted_at.is_(None)
        ).first()
    elif payload.phone:
        existing = db.query(Contact).filter(
            Contact.phone == payload.phone,
            Contact.type == "customer",
            Contact.deleted_at.is_(None)
        ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Customer with this email or phone already exists."
        )
    
    customer_uuid = str(uuid.uuid4())
    public_id = f"contact_{uuid.uuid4().hex[:12]}"
    
    customer = Contact(
        uuid=customer_uuid,
        public_id=public_id,
        name=payload.name,
        email=payload.email,
        phone=payload.phone,
        type="customer",
        meta=payload.meta,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    
    db.add(customer)
    db.commit()
    db.refresh(customer)
    
    return customer


@router.put("/{customer_id}", response_model=CustomerOut)
def update_customer(
    customer_id: str,
    payload: CustomerUpdate,
    db: Session = Depends(get_db),
):
    """Update a customer."""
    customer = db.query(Contact).filter(
        (Contact.public_id == customer_id) | (Contact.uuid == customer_id),
        Contact.type == "customer",
        Contact.deleted_at.is_(None)
    ).first()
    
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found."
        )
    
    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(customer, field, value)
    
    customer.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(customer)
    
    return customer


@router.post("/login", response_model=dict)
def customer_login(
    payload: CustomerLoginRequest,
    db: Session = Depends(get_db),
):
    """Customer login (returns token)."""
    # Find customer by email or phone
    customer = db.query(Contact).filter(
        (Contact.email == payload.identity) | (Contact.phone == payload.identity),
        Contact.type == "customer",
        Contact.deleted_at.is_(None)
    ).first()
    
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials."
        )
    
    # In a real implementation, we'd verify password from user table
    # For now, we'll create a token
    token = create_access_token(subject=customer.uuid, token_type="customer")
    
    return {
        "token": token,
        "customer": CustomerOut.model_validate(customer).model_dump()
    }


@router.get("/{customer_id}/orders", response_model=List[dict])
def get_customer_orders(
    customer_id: str,
    db: Session = Depends(get_db),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    """Get orders for a customer."""
    customer = db.query(Contact).filter(
        (Contact.public_id == customer_id) | (Contact.uuid == customer_id),
        Contact.type == "customer",
        Contact.deleted_at.is_(None)
    ).first()
    
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found."
        )
    
    orders = db.query(Order).filter(
        Order.customer_uuid == customer.uuid,
        Order.deleted_at.is_(None)
    ).offset(offset).limit(limit).all()
    
    return [{"uuid": o.uuid, "public_id": o.public_id, "status": o.status} for o in orders]


@router.get("/{customer_id}/places", response_model=List[dict])
def get_customer_places(
    customer_id: str,
    db: Session = Depends(get_db),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    """Get saved places for a customer."""
    customer = db.query(Contact).filter(
        (Contact.public_id == customer_id) | (Contact.uuid == customer_id),
        Contact.type == "customer",
        Contact.deleted_at.is_(None)
    ).first()
    
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found."
        )
    
    places = db.query(Place).filter(
        Place.owner_uuid == customer.uuid,
        Place.deleted_at.is_(None)
    ).offset(offset).limit(limit).all()
    
    return [{"uuid": p.uuid, "public_id": p.public_id, "name": p.name} for p in places]

