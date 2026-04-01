from typing import List
import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.v1.routers.auth import _get_current_user
from app.core.database import get_db
from app.models.tracking_number import TrackingNumber
from app.models.order import Order
from app.models.entity import Entity
from app.models.user import User
from app.schemas.tracking_number import TrackingNumberCreate, TrackingNumberOut, TrackingNumberResponse, TrackingNumbersResponse

router = APIRouter(prefix="/fleetops/v1/tracking-numbers", tags=["fleetops-tracking-numbers"])


@router.get("/", response_model=TrackingNumbersResponse)
def list_tracking_numbers(
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    q = db.query(TrackingNumber).filter(TrackingNumber.company_uuid == current.company_uuid, TrackingNumber.deleted_at.is_(None))
    numbers = q.offset(offset).limit(limit).all()
    return {"tracking_numbers": numbers}


@router.get("/{id}", response_model=TrackingNumberResponse)
def get_tracking_number(
    id: str,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    tracking = (
        db.query(TrackingNumber)
        .filter(
            TrackingNumber.company_uuid == current.company_uuid,
            (TrackingNumber.uuid == id) | (TrackingNumber.public_id == id) | (TrackingNumber.tracking_number == id)
        )
        .first()
    )
    if not tracking:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tracking number not found.")
    return {"tracking_number": tracking}


@router.post("/", response_model=TrackingNumberResponse, status_code=status.HTTP_201_CREATED)
def create_tracking_number(
    payload: TrackingNumberCreate,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    tracking = TrackingNumber()
    tracking.uuid = str(uuid.uuid4())
    tracking.public_id = f"tracking_number_{uuid.uuid4().hex[:12]}"
    tracking.company_uuid = current.company_uuid
    tracking.region = payload.region
    tracking.type = payload.type

    # Handle owner assignment (order or entity)
    if payload.owner:
        owner = (
            db.query(Order)
            .filter(Order.company_uuid == current.company_uuid, (Order.uuid == payload.owner) | (Order.public_id == payload.owner))
            .first()
        )
        if owner:
            tracking.owner_uuid = owner.uuid
            tracking.owner_type = "Order"
        else:
            owner = (
                db.query(Entity)
                .filter(Entity.company_uuid == current.company_uuid, (Entity.uuid == payload.owner) | (Entity.public_id == payload.owner))
                .first()
            )
            if owner:
                tracking.owner_uuid = owner.uuid
                tracking.owner_type = "Entity"

    # Generate tracking number
    if not tracking.tracking_number:
        tracking.tracking_number = f"TN{tracking.uuid[:8].upper()}"

    db.add(tracking)
    db.commit()
    db.refresh(tracking)
    return {"tracking_number": tracking}


def _to_dict(obj):
    """Convert SQLAlchemy model to dict for JSON serialization."""
    data = {}
    for key, value in obj.__dict__.items():
        if key.startswith("_"):
            continue
        if hasattr(value, "isoformat"):
            data[key] = value.isoformat()
        else:
            data[key] = value
    return data


@router.post("/from-qr", response_model=dict)
def from_qr(
    code: str,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    entity = (
        db.query(Entity)
        .filter((Entity.uuid == code) | (Entity.public_id == code))
        .first()
    )
    if entity:
        return {"type": "Entity", "data": _to_dict(entity)}

    order = (
        db.query(Order)
        .filter((Order.uuid == code) | (Order.public_id == code))
        .first()
    )
    if order:
        return {"type": "Order", "data": _to_dict(order)}

    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unable to find QR code value")


@router.delete("/{id}", response_model=TrackingNumberResponse)
def delete_tracking_number(
    id: str,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    tracking = (
        db.query(TrackingNumber)
        .filter(
            TrackingNumber.company_uuid == current.company_uuid,
            (TrackingNumber.uuid == id) | (TrackingNumber.public_id == id) | (TrackingNumber.tracking_number == id)
        )
        .first()
    )
    if not tracking:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tracking number not found.")

    tracking.deleted_at = datetime.utcnow()
    db.add(tracking)
    db.commit()
    return {"tracking_number": tracking}

