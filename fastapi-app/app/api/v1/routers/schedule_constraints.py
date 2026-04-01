import uuid
from datetime import datetime, timezone
from typing import List, Optional, Any
from pydantic import BaseModel

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.v1.routers.auth import _get_current_user
from app.core.database import get_db
from app.models.schedule_constraint import ScheduleConstraint
from app.models.user import User

router = APIRouter(prefix="/int/v1/schedules-constraints", tags=["schedule-constraints"])


def _serialize_constraint(c: ScheduleConstraint) -> dict:
    data = c.__dict__.copy()
    data.pop("_sa_instance_state", None)
    return data


class ScheduleConstraintCreate(BaseModel):
    name: str
    description: Optional[str] = None
    subject_uuid: Optional[str] = None
    subject_type: Optional[str] = None
    type: Optional[str] = None
    category: Optional[str] = None
    constraint_key: Optional[str] = None
    constraint_value: Optional[str] = None
    jurisdiction: Optional[str] = None
    priority: Optional[int] = None
    is_active: Optional[bool] = True
    meta: Optional[dict] = None


@router.get("/", response_model=List[dict])
def list_schedule_constraints(
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    subject_type: Optional[str] = None,
    subject_uuid: Optional[str] = None,
    type: Optional[str] = None,
    is_active: Optional[bool] = None,
):
    query = db.query(ScheduleConstraint).filter(
        ScheduleConstraint.company_uuid == current.company_uuid,
        ScheduleConstraint.deleted_at.is_(None),
    )
    if subject_type:
        query = query.filter(ScheduleConstraint.subject_type == subject_type)
    if subject_uuid:
        query = query.filter(ScheduleConstraint.subject_uuid == subject_uuid)
    if type:
        query = query.filter(ScheduleConstraint.type == type)
    if is_active is not None:
        query = query.filter(ScheduleConstraint.is_active == is_active)
    
    constraints = (
        query.order_by(ScheduleConstraint.priority.desc().nullslast())
        .offset(offset)
        .limit(limit)
        .all()
    )
    return [_serialize_constraint(c) for c in constraints]


@router.get("/{id}", response_model=dict)
def get_schedule_constraint(
    id: str,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    constraint = (
        db.query(ScheduleConstraint)
        .filter(
            ScheduleConstraint.uuid == id,
            ScheduleConstraint.company_uuid == current.company_uuid,
            ScheduleConstraint.deleted_at.is_(None),
        )
        .first()
    )

    if not constraint and id.isdigit():
        constraint = (
            db.query(ScheduleConstraint)
            .filter(
                ScheduleConstraint.id == int(id),
                ScheduleConstraint.company_uuid == current.company_uuid,
                ScheduleConstraint.deleted_at.is_(None),
            )
            .first()
        )
    if not constraint:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Schedule constraint not found"
        )
    return _serialize_constraint(constraint)


@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED)
def create_schedule_constraint(
    payload: ScheduleConstraintCreate,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    constraint = ScheduleConstraint()
    constraint.uuid = str(uuid.uuid4())
    constraint.company_uuid = current.company_uuid
    constraint.name = payload.name
    constraint.description = payload.description
    constraint.subject_uuid = payload.subject_uuid
    constraint.subject_type = payload.subject_type
    constraint.type = payload.type
    constraint.category = payload.category
    constraint.constraint_key = payload.constraint_key
    constraint.constraint_value = payload.constraint_value
    constraint.jurisdiction = payload.jurisdiction
    constraint.priority = payload.priority
    constraint.is_active = payload.is_active
    constraint.meta = payload.meta or {}
    constraint.created_at = datetime.now(timezone.utc)
    constraint.updated_at = datetime.now(timezone.utc)

    db.add(constraint)
    db.commit()
    db.refresh(constraint)
    return _serialize_constraint(constraint)


@router.put("/{id}", response_model=dict)
@router.patch("/{id}", response_model=dict)
def update_schedule_constraint(
    id: str,
    payload: dict,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    constraint = (
        db.query(ScheduleConstraint)
        .filter(
            ScheduleConstraint.uuid == id,
            ScheduleConstraint.company_uuid == current.company_uuid,
            ScheduleConstraint.deleted_at.is_(None),
        )
        .first()
    )

    if not constraint and id.isdigit():
        constraint = (
            db.query(ScheduleConstraint)
            .filter(
                ScheduleConstraint.id == int(id),
                ScheduleConstraint.company_uuid == current.company_uuid,
                ScheduleConstraint.deleted_at.is_(None),
            )
            .first()
        )
    if not constraint:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Schedule constraint not found"
        )
    
    for field, value in payload.items():
        if hasattr(constraint, field):
            setattr(constraint, field, value)
    
    constraint.updated_at = datetime.now(timezone.utc)
    db.add(constraint)
    db.commit()
    db.refresh(constraint)
    return _serialize_constraint(constraint)


@router.delete("/{id}", status_code=status.HTTP_200_OK)
def delete_schedule_constraint(
    id: str,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    constraint = (
        db.query(ScheduleConstraint)
        .filter(
            ScheduleConstraint.uuid == id,
            ScheduleConstraint.company_uuid == current.company_uuid,
            ScheduleConstraint.deleted_at.is_(None),
        )
        .first()
    )

    if not constraint and id.isdigit():
        constraint = (
            db.query(ScheduleConstraint)
            .filter(
                ScheduleConstraint.id == int(id),
                ScheduleConstraint.company_uuid == current.company_uuid,
                ScheduleConstraint.deleted_at.is_(None),
            )
            .first()
        )
    if not constraint:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Schedule constraint not found")
    
    constraint.deleted_at = datetime.now(timezone.utc)
    db.add(constraint)
    db.commit()
    return {"status": "ok", "message": "Schedule constraint deleted"}

