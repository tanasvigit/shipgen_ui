import uuid
from datetime import datetime, timezone
from typing import List, Optional, Any
from pydantic import BaseModel

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.v1.routers.auth import _get_current_user
from app.core.database import get_db
from app.models.schedule_item import ScheduleItem
from app.models.user import User

router = APIRouter(prefix="/int/v1/schedules-items", tags=["schedule-items"])


def _serialize_item(item: ScheduleItem) -> dict:
    """Convert ScheduleItem model to plain dict without SQLAlchemy state."""
    data = item.__dict__.copy()
    data.pop("_sa_instance_state", None)
    return data


class ScheduleItemCreate(BaseModel):
    schedule_uuid: str
    assignee_uuid: Optional[str] = None
    assignee_type: Optional[str] = None
    resource_uuid: Optional[str] = None
    resource_type: Optional[str] = None
    start_at: Optional[datetime] = None
    end_at: Optional[datetime] = None
    duration: Optional[int] = None
    break_start_at: Optional[datetime] = None
    break_end_at: Optional[datetime] = None
    status: Optional[str] = "pending"
    meta: Optional[dict] = None


@router.get("/", response_model=List[dict])
def list_schedule_items(
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    schedule_uuid: Optional[str] = None,
    assignee_uuid: Optional[str] = None,
    status: Optional[str] = None,
):
    query = db.query(ScheduleItem).filter(ScheduleItem.deleted_at.is_(None))
    if schedule_uuid:
        query = query.filter(ScheduleItem.schedule_uuid == schedule_uuid)
    if assignee_uuid:
        query = query.filter(ScheduleItem.assignee_uuid == assignee_uuid)
    if status:
        query = query.filter(ScheduleItem.status == status)
    
    items = (
        query.order_by(ScheduleItem.start_at.asc().nullslast())
        .offset(offset)
        .limit(limit)
        .all()
    )
    return [_serialize_item(i) for i in items]


@router.get("/{id}", response_model=dict)
def get_schedule_item(
    id: str,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    base_query = db.query(ScheduleItem).filter(ScheduleItem.deleted_at.is_(None))
    item = base_query.filter(ScheduleItem.uuid == id).first()
    if not item:
        item = base_query.filter(ScheduleItem.public_id == id).first()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Schedule item not found")
    return _serialize_item(item)


@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED)
def create_schedule_item(
    payload: ScheduleItemCreate,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    item = ScheduleItem()
    item.uuid = str(uuid.uuid4())
    item.schedule_uuid = payload.schedule_uuid
    item.assignee_uuid = payload.assignee_uuid
    item.assignee_type = payload.assignee_type
    item.resource_uuid = payload.resource_uuid
    item.resource_type = payload.resource_type
    item.start_at = payload.start_at
    item.end_at = payload.end_at
    item.duration = payload.duration
    item.break_start_at = payload.break_start_at
    item.break_end_at = payload.break_end_at
    item.status = payload.status
    item.meta = payload.meta or {}

    # Calculate duration if not provided
    if not item.duration and item.start_at and item.end_at:
        item.duration = int((item.end_at - item.start_at).total_seconds() / 60)

    item.created_at = datetime.now(timezone.utc)
    item.updated_at = datetime.now(timezone.utc)

    db.add(item)
    db.commit()
    db.refresh(item)
    return _serialize_item(item)


@router.put("/{id}", response_model=dict)
@router.patch("/{id}", response_model=dict)
def update_schedule_item(
    id: str,
    payload: dict,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    base_query = db.query(ScheduleItem).filter(ScheduleItem.deleted_at.is_(None))
    item = base_query.filter(ScheduleItem.uuid == id).first()
    if not item:
        item = base_query.filter(ScheduleItem.public_id == id).first()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Schedule item not found")
    
    for field, value in payload.items():
        if hasattr(item, field):
            setattr(item, field, value)
    
    # Recalculate duration if start/end changed
    if (item.start_at and item.end_at) and (not item.duration or 'start_at' in payload or 'end_at' in payload):
        item.duration = int((item.end_at - item.start_at).total_seconds() / 60)
    
    item.updated_at = datetime.now(timezone.utc)
    db.add(item)
    db.commit()
    db.refresh(item)
    return _serialize_item(item)


@router.delete("/{id}", status_code=status.HTTP_200_OK)
def delete_schedule_item(
    id: str,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    base_query = db.query(ScheduleItem).filter(ScheduleItem.deleted_at.is_(None))
    item = base_query.filter(ScheduleItem.uuid == id).first()
    if not item:
        item = base_query.filter(ScheduleItem.public_id == id).first()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Schedule item not found")
    
    item.deleted_at = datetime.now(timezone.utc)
    db.add(item)
    db.commit()
    return {"status": "ok", "message": "Schedule item deleted"}

