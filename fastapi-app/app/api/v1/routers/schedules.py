import uuid
from datetime import datetime, timezone, date
from typing import List, Optional, Any
from pydantic import BaseModel

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.v1.routers.auth import _get_current_user
from app.core.database import get_db
from app.models.schedule import Schedule
from app.models.user import User

router = APIRouter(prefix="/int/v1/schedules", tags=["schedules"])


def _serialize_schedule(s: Schedule) -> dict:
    """Convert Schedule model to plain dict without SQLAlchemy state."""
    data = s.__dict__.copy()
    data.pop("_sa_instance_state", None)
    return data


class ScheduleCreate(BaseModel):
    name: str
    description: Optional[str] = None
    subject_uuid: Optional[str] = None
    subject_type: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    timezone: Optional[str] = None
    status: Optional[str] = "active"
    meta: Optional[dict] = None


@router.get("/", response_model=List[dict])
def list_schedules(
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    subject_type: Optional[str] = None,
    subject_uuid: Optional[str] = None,
    status: Optional[str] = None,
):
    query = db.query(Schedule).filter(
        Schedule.company_uuid == current.company_uuid,
        Schedule.deleted_at.is_(None),
    )
    if subject_type:
        query = query.filter(Schedule.subject_type == subject_type)
    if subject_uuid:
        query = query.filter(Schedule.subject_uuid == subject_uuid)
    if status:
        query = query.filter(Schedule.status == status)
    
    schedules = (
        query.order_by(Schedule.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )
    return [_serialize_schedule(s) for s in schedules]


@router.get("/{id}", response_model=dict)
def get_schedule(
    id: str,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    schedule = (
        db.query(Schedule)
        .filter(
            (Schedule.uuid == id) | (Schedule.public_id == id),
            Schedule.company_uuid == current.company_uuid,
            Schedule.deleted_at.is_(None),
        )
        .first()
    )
    if not schedule:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Schedule not found")
    return _serialize_schedule(schedule)


@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED)
def create_schedule(
    payload: ScheduleCreate,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    schedule = Schedule()
    schedule.uuid = str(uuid.uuid4())
    schedule.company_uuid = current.company_uuid
    schedule.name = payload.name
    schedule.description = payload.description
    schedule.subject_uuid = payload.subject_uuid
    schedule.subject_type = payload.subject_type
    schedule.start_date = payload.start_date
    schedule.end_date = payload.end_date
    schedule.timezone = payload.timezone
    schedule.status = payload.status
    schedule.meta = payload.meta or {}
    schedule.created_at = datetime.now(timezone.utc)
    schedule.updated_at = datetime.now(timezone.utc)

    db.add(schedule)
    db.commit()
    db.refresh(schedule)
    return _serialize_schedule(schedule)


@router.put("/{id}", response_model=dict)
@router.patch("/{id}", response_model=dict)
def update_schedule(
    id: str,
    payload: dict,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    schedule = (
        db.query(Schedule)
        .filter(
            (Schedule.uuid == id) | (Schedule.public_id == id),
            Schedule.company_uuid == current.company_uuid,
            Schedule.deleted_at.is_(None),
        )
        .first()
    )
    if not schedule:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Schedule not found")
    
    for field, value in payload.items():
        if hasattr(schedule, field):
            setattr(schedule, field, value)
    
    schedule.updated_at = datetime.now(timezone.utc)
    db.add(schedule)
    db.commit()
    db.refresh(schedule)
    return _serialize_schedule(schedule)


@router.delete("/{id}", status_code=status.HTTP_200_OK)
def delete_schedule(
    id: str,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    schedule = db.query(Schedule).filter(
        (Schedule.uuid == id) | (Schedule.public_id == id),
        Schedule.company_uuid == current.company_uuid,
        Schedule.deleted_at.is_(None)
    ).first()
    if not schedule:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Schedule not found")
    
    schedule.deleted_at = datetime.now(timezone.utc)
    db.add(schedule)
    db.commit()
    return {"status": "ok", "message": "Schedule deleted"}

