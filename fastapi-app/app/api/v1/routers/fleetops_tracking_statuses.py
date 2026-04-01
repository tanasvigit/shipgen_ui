from typing import List
import uuid
from datetime import datetime
import re

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.v1.routers.auth import _get_current_user
from app.core.database import get_db
from app.models.tracking_status import TrackingStatus
from app.models.tracking_number import TrackingNumber
from app.models.order import Order
from app.models.user import User
from app.schemas.tracking_status import TrackingStatusCreate, TrackingStatusOut, TrackingStatusUpdate, TrackingStatusResponse, TrackingStatusesResponse

router = APIRouter(prefix="/fleetops/v1/tracking-statuses", tags=["fleetops-tracking-statuses"])


def prepare_code(status: str) -> str:
    """Convert status to code format."""
    if not status:
        return ""
    code = re.sub(r'[^a-z0-9]+', '_', status.lower())
    return code.strip('_')


@router.get("/", response_model=TrackingStatusesResponse)
def list_tracking_statuses(
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    q = db.query(TrackingStatus).filter(TrackingStatus.company_uuid == current.company_uuid, TrackingStatus.deleted_at.is_(None))
    statuses = q.offset(offset).limit(limit).all()
    return {"tracking_statuses": statuses}


@router.get("/{id}", response_model=TrackingStatusResponse)
def get_tracking_status(
    id: str,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    status_obj = (
        db.query(TrackingStatus)
        .filter(TrackingStatus.company_uuid == current.company_uuid, (TrackingStatus.uuid == id) | (TrackingStatus.public_id == id))
        .first()
    )
    if not status_obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tracking status not found.")
    return {"tracking_status": status_obj}


@router.post("/", response_model=TrackingStatusResponse, status_code=status.HTTP_201_CREATED)
def create_tracking_status(
    payload: TrackingStatusCreate,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    status_obj = TrackingStatus()
    status_obj.uuid = str(uuid.uuid4())
    status_obj.public_id = f"tracking_status_{uuid.uuid4().hex[:12]}"
    status_obj.company_uuid = current.company_uuid
    status_obj.status = payload.status
    status_obj.details = payload.details
    status_obj.code = payload.code or prepare_code(payload.status)
    status_obj.city = payload.city
    status_obj.province = payload.province
    status_obj.postal_code = payload.postal_code
    status_obj.country = payload.country
    status_obj.meta = payload.meta

    # Handle location
    if payload.location:
        if isinstance(payload.location, dict):
            status_obj.latitude = str(payload.location.get("latitude") or payload.location.get("lat"))
            status_obj.longitude = str(payload.location.get("longitude") or payload.location.get("lng"))
            status_obj.location_latitude = status_obj.latitude
            status_obj.location_longitude = status_obj.longitude
    elif payload.latitude and payload.longitude:
        status_obj.latitude = str(payload.latitude)
        status_obj.longitude = str(payload.longitude)
        status_obj.location_latitude = status_obj.latitude
        status_obj.location_longitude = status_obj.longitude

    # Handle tracking number assignment
    if payload.tracking_number:
        tracking = (
            db.query(TrackingNumber)
            .filter(TrackingNumber.company_uuid == current.company_uuid, (TrackingNumber.uuid == payload.tracking_number) | (TrackingNumber.public_id == payload.tracking_number))
            .first()
        )
        if tracking:
            status_obj.tracking_number_uuid = tracking.uuid
    elif payload.order:
        # Get tracking number from order
        order = (
            db.query(Order)
            .filter(Order.company_uuid == current.company_uuid, (Order.uuid == payload.order) | (Order.public_id == payload.order))
            .first()
        )
        if order:
            # In a full implementation, orders would have tracking_number_uuid
            # For now, we'll try to find a tracking number by owner
            tracking = (
                db.query(TrackingNumber)
                .filter(TrackingNumber.company_uuid == current.company_uuid, TrackingNumber.owner_uuid == order.uuid)
                .first()
            )
            if tracking:
                status_obj.tracking_number_uuid = tracking.uuid

    db.add(status_obj)
    db.commit()
    db.refresh(status_obj)
    return {"tracking_status": status_obj}


@router.put("/{id}", response_model=TrackingStatusResponse)
def update_tracking_status(
    id: str,
    payload: TrackingStatusUpdate,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    status_obj = (
        db.query(TrackingStatus)
        .filter(TrackingStatus.company_uuid == current.company_uuid, (TrackingStatus.uuid == id) | (TrackingStatus.public_id == id))
        .first()
    )
    if not status_obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tracking status not found.")

    update_data = payload.dict(exclude_unset=True, exclude={"location", "latitude", "longitude"})
    for field, value in update_data.items():
        setattr(status_obj, field, value)

    # Handle code generation if status changed
    if payload.status and not status_obj.code:
        status_obj.code = prepare_code(payload.status)

    # Handle location
    if payload.location:
        if isinstance(payload.location, dict):
            status_obj.latitude = str(payload.location.get("latitude") or payload.location.get("lat"))
            status_obj.longitude = str(payload.location.get("longitude") or payload.location.get("lng"))
            status_obj.location_latitude = status_obj.latitude
            status_obj.location_longitude = status_obj.longitude
    elif payload.latitude and payload.longitude:
        status_obj.latitude = str(payload.latitude)
        status_obj.longitude = str(payload.longitude)
        status_obj.location_latitude = status_obj.latitude
        status_obj.location_longitude = status_obj.longitude

    db.add(status_obj)
    db.commit()
    db.refresh(status_obj)
    return {"tracking_status": status_obj}


@router.delete("/{id}", response_model=TrackingStatusResponse)
def delete_tracking_status(
    id: str,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    status_obj = (
        db.query(TrackingStatus)
        .filter(TrackingStatus.company_uuid == current.company_uuid, (TrackingStatus.uuid == id) | (TrackingStatus.public_id == id))
        .first()
    )
    if not status_obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tracking status not found.")

    status_obj.deleted_at = datetime.utcnow()
    db.add(status_obj)
    db.commit()
    return {"tracking_status": status_obj}

