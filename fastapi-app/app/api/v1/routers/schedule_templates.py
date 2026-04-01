import uuid
from datetime import datetime, timezone, time
from typing import List, Optional, Any
from pydantic import BaseModel

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.v1.routers.auth import _get_current_user
from app.core.database import get_db
from app.models.schedule_template import ScheduleTemplate
from app.models.user import User

router = APIRouter(prefix="/int/v1/schedules-templates", tags=["schedule-templates"])


def _serialize_template(t: ScheduleTemplate) -> dict:
    """Convert ScheduleTemplate model to plain dict without SQLAlchemy state."""
    data = t.__dict__.copy()
    data.pop("_sa_instance_state", None)
    return data


class ScheduleTemplateCreate(BaseModel):
    name: str
    description: Optional[str] = None
    subject_uuid: Optional[str] = None
    subject_type: Optional[str] = None
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    duration: Optional[int] = None
    break_duration: Optional[int] = None
    rrule: Optional[str] = None
    meta: Optional[dict] = None


@router.get("/", response_model=List[dict])
def list_schedule_templates(
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    subject_type: Optional[str] = None,
    subject_uuid: Optional[str] = None,
):
    query = db.query(ScheduleTemplate).filter(
        ScheduleTemplate.company_uuid == current.company_uuid,
        ScheduleTemplate.deleted_at.is_(None)
    )
    if subject_type:
        query = query.filter(ScheduleTemplate.subject_type == subject_type)
    if subject_uuid:
        query = query.filter(ScheduleTemplate.subject_uuid == subject_uuid)
    
    templates = (
        query.order_by(ScheduleTemplate.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )
    return [_serialize_template(t) for t in templates]


@router.get("/{id}", response_model=dict)
def get_schedule_template(
    id: str,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    template = (
        db.query(ScheduleTemplate)
        .filter(
            (ScheduleTemplate.uuid == id) | (ScheduleTemplate.public_id == id),
            ScheduleTemplate.company_uuid == current.company_uuid,
            ScheduleTemplate.deleted_at.is_(None),
        )
        .first()
    )
    if not template:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Schedule template not found")
    return _serialize_template(template)


@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED)
def create_schedule_template(
    payload: ScheduleTemplateCreate,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    template = ScheduleTemplate()
    template.uuid = str(uuid.uuid4())
    template.company_uuid = current.company_uuid
    template.name = payload.name
    template.description = payload.description
    template.subject_uuid = payload.subject_uuid
    template.subject_type = payload.subject_type
    template.start_time = payload.start_time
    template.end_time = payload.end_time
    template.duration = payload.duration
    template.break_duration = payload.break_duration
    template.rrule = payload.rrule
    template.meta = payload.meta or {}
    template.created_at = datetime.now(timezone.utc)
    template.updated_at = datetime.now(timezone.utc)

    db.add(template)
    db.commit()
    db.refresh(template)
    return _serialize_template(template)


@router.put("/{id}", response_model=dict)
@router.patch("/{id}", response_model=dict)
def update_schedule_template(
    id: str,
    payload: dict,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    template = (
        db.query(ScheduleTemplate)
        .filter(
            (ScheduleTemplate.uuid == id) | (ScheduleTemplate.public_id == id),
            ScheduleTemplate.company_uuid == current.company_uuid,
            ScheduleTemplate.deleted_at.is_(None),
        )
        .first()
    )
    if not template:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Schedule template not found")
    
    for field, value in payload.items():
        if hasattr(template, field):
            setattr(template, field, value)
    
    template.updated_at = datetime.now(timezone.utc)
    db.add(template)
    db.commit()
    db.refresh(template)
    return _serialize_template(template)


@router.delete("/{id}", status_code=status.HTTP_200_OK)
def delete_schedule_template(
    id: str,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    template = db.query(ScheduleTemplate).filter(
        (ScheduleTemplate.uuid == id) | (ScheduleTemplate.public_id == id),
        ScheduleTemplate.company_uuid == current.company_uuid,
        ScheduleTemplate.deleted_at.is_(None)
    ).first()
    if not template:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Schedule template not found")
    
    template.deleted_at = datetime.now(timezone.utc)
    db.add(template)
    db.commit()
    return {"status": "ok", "message": "Schedule template deleted"}

