from typing import List
import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.v1.routers.auth import _get_current_user
from app.core.database import get_db
from app.models.payload import Payload
from app.models.place import Place
from app.models.user import User
from app.schemas.payload import PayloadCreate, PayloadOut, PayloadUpdate, PayloadResponse, PayloadsResponse

router = APIRouter(prefix="/fleetops/v1/payloads", tags=["fleetops-payloads"])


@router.get("/", response_model=PayloadsResponse)
def list_payloads(
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    q = db.query(Payload).filter(Payload.company_uuid == current.company_uuid, Payload.deleted_at.is_(None))
    payloads = q.offset(offset).limit(limit).all()
    return {"payloads": payloads}


@router.get("/{id}", response_model=PayloadResponse)
def get_payload(
    id: str,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    payload_obj = (
        db.query(Payload)
        .filter(Payload.company_uuid == current.company_uuid, (Payload.uuid == id) | (Payload.public_id == id))
        .first()
    )
    if not payload_obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payload not found.")
    return {"payload": payload_obj}


@router.post("/", response_model=PayloadResponse, status_code=status.HTTP_201_CREATED)
def create_payload(
    payload: PayloadCreate,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    payload_obj = Payload()
    payload_obj.uuid = str(uuid.uuid4())
    payload_obj.public_id = f"payload_{uuid.uuid4().hex[:12]}"
    payload_obj.company_uuid = current.company_uuid
    payload_obj.type = payload.type
    payload_obj.provider = payload.provider
    payload_obj.meta = payload.meta
    payload_obj.cod_amount = payload.cod_amount
    payload_obj.cod_currency = payload.cod_currency
    payload_obj.cod_payment_method = payload.cod_payment_method

    db.add(payload_obj)
    db.commit()
    db.refresh(payload_obj)
    return {"payload": payload_obj}


@router.put("/{id}", response_model=PayloadResponse)
def update_payload(
    id: str,
    payload: PayloadUpdate,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    payload_obj = (
        db.query(Payload)
        .filter(Payload.company_uuid == current.company_uuid, (Payload.uuid == id) | (Payload.public_id == id))
        .first()
    )
    if not payload_obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payload not found.")

    update_data = payload.dict(exclude_unset=True, exclude={"entities", "waypoints", "pickup", "dropoff", "return_location"})
    for field, value in update_data.items():
        setattr(payload_obj, field, value)

    db.add(payload_obj)
    db.commit()
    db.refresh(payload_obj)
    return {"payload": payload_obj}


@router.delete("/{id}", response_model=PayloadResponse)
def delete_payload(
    id: str,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    payload_obj = (
        db.query(Payload)
        .filter(Payload.company_uuid == current.company_uuid, (Payload.uuid == id) | (Payload.public_id == id))
        .first()
    )
    if not payload_obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payload not found.")

    payload_obj.deleted_at = datetime.utcnow()
    db.add(payload_obj)
    db.commit()
    return {"payload": payload_obj}

