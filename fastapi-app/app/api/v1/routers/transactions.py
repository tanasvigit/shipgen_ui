import uuid
from datetime import datetime, timezone
from typing import List, Optional, Any
from pydantic import BaseModel

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.v1.routers.auth import _get_current_user
from app.core.database import get_db
from app.models.transaction import Transaction
from app.models.user import User

router = APIRouter(prefix="/int/v1/transactions", tags=["transactions"])


def _serialize_transaction(tx: Transaction) -> dict:
    """Convert Transaction model to plain dict without SQLAlchemy state."""
    data = tx.__dict__.copy()
    data.pop("_sa_instance_state", None)
    return data


class TransactionCreate(BaseModel):
    owner_uuid: Optional[str] = None
    owner_type: Optional[str] = None
    customer_uuid: Optional[str] = None
    customer_type: Optional[str] = None
    gateway_transaction_id: Optional[str] = None
    gateway: Optional[str] = None
    gateway_uuid: Optional[str] = None
    amount: int
    currency: Optional[str] = "USD"
    description: Optional[str] = None
    meta: Optional[dict] = None
    type: Optional[str] = None
    status: Optional[str] = "pending"


@router.get("/", response_model=List[dict])
def list_transactions(
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    status: Optional[str] = None,
    type: Optional[str] = None,
):
    query = db.query(Transaction).filter(
        Transaction.company_uuid == current.company_uuid,
        Transaction.deleted_at.is_(None),
    )
    if status:
        query = query.filter(Transaction.status == status)
    if type:
        query = query.filter(Transaction.type == type)
    
    transactions = (
        query.order_by(Transaction.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )
    return [_serialize_transaction(t) for t in transactions]


@router.get("/{id}", response_model=dict)
def get_transaction(
    id: str,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    base_query = db.query(Transaction).filter(
        Transaction.company_uuid == current.company_uuid,
        Transaction.deleted_at.is_(None),
    )
    # Try uuid/public_id/gateway id first
    transaction = base_query.filter(
        (Transaction.uuid == id)
        | (Transaction.public_id == id)
        | (Transaction.gateway_transaction_id == id)
    ).first()
    if not transaction:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")
    return _serialize_transaction(transaction)


@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED)
def create_transaction(
    payload: TransactionCreate,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    transaction = Transaction()
    transaction.uuid = str(uuid.uuid4())
    transaction.company_uuid = current.company_uuid
    transaction.owner_uuid = payload.owner_uuid
    transaction.owner_type = payload.owner_type
    transaction.customer_uuid = payload.customer_uuid
    transaction.customer_type = payload.customer_type
    transaction.gateway_transaction_id = payload.gateway_transaction_id
    transaction.gateway = payload.gateway
    transaction.gateway_uuid = payload.gateway_uuid
    transaction.amount = payload.amount
    transaction.currency = payload.currency
    transaction.description = payload.description
    transaction.meta = payload.meta or {}
    transaction.type = payload.type
    transaction.status = payload.status
    transaction.created_at = datetime.now(timezone.utc)
    transaction.updated_at = datetime.now(timezone.utc)

    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    return _serialize_transaction(transaction)


@router.put("/{id}", response_model=dict)
@router.patch("/{id}", response_model=dict)
def update_transaction(
    id: str,
    payload: dict,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    base_query = db.query(Transaction).filter(
        Transaction.company_uuid == current.company_uuid,
        Transaction.deleted_at.is_(None),
    )
    transaction = base_query.filter(Transaction.uuid == id).first()
    if not transaction:
        transaction = base_query.filter(Transaction.public_id == id).first()
    if not transaction:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")
    
    for field, value in payload.items():
        if hasattr(transaction, field):
            setattr(transaction, field, value)
    
    transaction.updated_at = datetime.now(timezone.utc)
    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    return _serialize_transaction(transaction)


@router.delete("/{id}", status_code=status.HTTP_200_OK)
def delete_transaction(
    id: str,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    base_query = db.query(Transaction).filter(
        Transaction.company_uuid == current.company_uuid,
        Transaction.deleted_at.is_(None),
    )
    transaction = base_query.filter(Transaction.uuid == id).first()
    if not transaction:
        transaction = base_query.filter(Transaction.public_id == id).first()
    if not transaction:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")
    
    transaction.deleted_at = datetime.now(timezone.utc)
    db.add(transaction)
    db.commit()
    return {"status": "ok", "message": "Transaction deleted"}

