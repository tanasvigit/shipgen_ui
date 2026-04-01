import uuid
from datetime import datetime, timezone
from typing import List, Optional, Any
from pydantic import BaseModel

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.v1.routers.auth import _get_current_user
from app.core.database import get_db
from app.models.schedule_availability import ScheduleAvailability
from app.models.user import User

router = APIRouter(prefix="/int/v1/schedules-availability", tags=["schedule-availability"])


def _serialize_availability(a: ScheduleAvailability) -> dict:
    data = a.__dict__.copy()
    data.pop("_sa_instance_state", None)
    return data


class ScheduleAvailabilityCreate(BaseModel):
    subject_uuid: str
    subject_type: str
    start_at: Optional[datetime] = None
    end_at: Optional[datetime] = None
    is_available: Optional[bool] = True
    preference_level: Optional[int] = None
    rrule: Optional[str] = None
    reason: Optional[str] = None
    notes: Optional[str] = None
    meta: Optional[dict] = None


@router.get("/", response_model=List[dict])
def list_schedule_availability(
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    subject_type: Optional[str] = None,
    subject_uuid: Optional[str] = None,
    is_available: Optional[bool] = None,
):
    query = db.query(ScheduleAvailability).filter(ScheduleAvailability.deleted_at.is_(None))
    if subject_type:
        query = query.filter(ScheduleAvailability.subject_type == subject_type)
    if subject_uuid:
        query = query.filter(ScheduleAvailability.subject_uuid == subject_uuid)
    if is_available is not None:
        query = query.filter(ScheduleAvailability.is_available == is_available)
    
    availability = (
        query.order_by(ScheduleAvailability.start_at.asc().nullslast())
        .offset(offset)
        .limit(limit)
        .all()
    )
    return [_serialize_availability(a) for a in availability]


@router.get("/{id}", response_model=dict)
def get_schedule_availability(
    id: str,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    # First try lookup by UUID
    availability = (
        db.query(ScheduleAvailability)
        .filter(
            ScheduleAvailability.uuid == id,
            ScheduleAvailability.deleted_at.is_(None),
        )
        .first()
    )

    # If not found and the id looks like an integer, try numeric primary key
    if not availability and id.isdigit():
        availability = (
            db.query(ScheduleAvailability)
            .filter(
                ScheduleAvailability.id == int(id),
                ScheduleAvailability.deleted_at.is_(None),
            )
            .first()
        )
    if not availability:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Schedule availability not found")
    return _serialize_availability(availability)


@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED)
def create_schedule_availability(
    payload: ScheduleAvailabilityCreate,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    availability = ScheduleAvailability()
    availability.uuid = str(uuid.uuid4())
    availability.subject_uuid = payload.subject_uuid
    availability.subject_type = payload.subject_type
    availability.start_at = payload.start_at
    availability.end_at = payload.end_at
    availability.is_available = payload.is_available
    availability.preference_level = payload.preference_level
    availability.rrule = payload.rrule
    availability.reason = payload.reason
    availability.notes = payload.notes
    availability.meta = payload.meta or {}
    availability.created_at = datetime.now(timezone.utc)
    availability.updated_at = datetime.now(timezone.utc)

    db.add(availability)
    db.commit()
    db.refresh(availability)
    return _serialize_availability(availability)


@router.put("/{id}", response_model=dict)
@router.patch("/{id}", response_model=dict)
def update_schedule_availability(
    id: str,
    payload: dict,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    availability = (
        db.query(ScheduleAvailability)
        .filter(
            ScheduleAvailability.uuid == id,
            ScheduleAvailability.deleted_at.is_(None),
        )
        .first()
    )

    if not availability and id.isdigit():
        availability = (
            db.query(ScheduleAvailability)
            .filter(
                ScheduleAvailability.id == int(id),
                ScheduleAvailability.deleted_at.is_(None),
            )
            .first()
        )
    if not availability:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Schedule availability not found")
    
    for field, value in payload.items():
        if hasattr(availability, field):
            setattr(availability, field, value)
    
    availability.updated_at = datetime.now(timezone.utc)
    db.add(availability)
    db.commit()
    db.refresh(availability)
    return _serialize_availability(availability)


@router.delete("/{id}", status_code=status.HTTP_200_OK)
def delete_schedule_availability(
    id: str,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    availability = (
        db.query(ScheduleAvailability)
        .filter(
            ScheduleAvailability.uuid == id,
            ScheduleAvailability.deleted_at.is_(None),
        )
        .first()
    )

    if not availability and id.isdigit():
        availability = (
            db.query(ScheduleAvailability)
            .filter(
                ScheduleAvailability.id == int(id),
                ScheduleAvailability.deleted_at.is_(None),
            )
            .first()
        )
    if not availability:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Schedule availability not found")
    
    availability.deleted_at = datetime.now(timezone.utc)
    db.add(availability)
    db.commit()
    return {"status": "ok", "message": "Schedule availability deleted"}

