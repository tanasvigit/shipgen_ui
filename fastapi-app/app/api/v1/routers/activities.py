import uuid
from datetime import datetime, timezone
from typing import List, Optional, Any
from pydantic import BaseModel

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.v1.routers.auth import _get_current_user
from app.core.database import get_db
from app.models.activity import Activity
from app.models.user import User

router = APIRouter(prefix="/int/v1/activities", tags=["activities"])


def _serialize_activity(activity: Activity) -> dict:
    """Convert Activity model to plain dict without SQLAlchemy state."""
    data = activity.__dict__.copy()
    data.pop("_sa_instance_state", None)
    return data


class ActivityCreate(BaseModel):
    log_name: str
    description: str
    subject_type: Optional[str] = None
    subject_id: Optional[str] = None
    event: Optional[str] = None
    causer_type: Optional[str] = None
    causer_id: Optional[str] = None
    properties: Optional[dict] = None


@router.get("/", response_model=List[dict])
def list_activities(
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    subject_type: Optional[str] = None,
    log_name: Optional[str] = None,
):
    query = db.query(Activity)

    if subject_type:
        query = query.filter(Activity.subject_type == subject_type)
    if log_name:
        query = query.filter(Activity.log_name == log_name)

    activities = (
        query.order_by(Activity.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )
    return [_serialize_activity(a) for a in activities]


@router.get("/{id}", response_model=dict)
def get_activity(
    id: str,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    base_query = db.query(Activity)
    activity = base_query.filter(Activity.uuid == id).first()
    if not activity:
        try:
            numeric_id = int(id)
        except ValueError:
            numeric_id = None
        if numeric_id is not None:
            activity = base_query.filter(Activity.id == numeric_id).first()
    if not activity:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Activity not found")
    return _serialize_activity(activity)


@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED)
def create_activity(
    payload: ActivityCreate,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    activity = Activity()
    activity.uuid = str(uuid.uuid4())
    activity.log_name = payload.log_name
    activity.description = payload.description
    activity.subject_type = payload.subject_type
    activity.subject_id = payload.subject_id
    activity.event = payload.event
    activity.causer_type = payload.causer_type or "user"
    activity.causer_id = payload.causer_id or current.uuid
    activity.properties = payload.properties or {}
    activity.created_at = datetime.now(timezone.utc)
    activity.updated_at = datetime.now(timezone.utc)

    db.add(activity)
    db.commit()
    db.refresh(activity)
    return _serialize_activity(activity)


@router.delete("/{id}", status_code=status.HTTP_200_OK)
def delete_activity(
    id: str,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    base_query = db.query(Activity)
    activity = base_query.filter(Activity.uuid == id).first()
    if not activity:
        try:
            numeric_id = int(id)
        except ValueError:
            numeric_id = None
        if numeric_id is not None:
            activity = base_query.filter(Activity.id == numeric_id).first()
    if not activity:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Activity not found")

    db.delete(activity)
    db.commit()
    return {"status": "ok", "message": "Activity deleted"}

