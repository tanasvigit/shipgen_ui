import uuid
from datetime import datetime, timezone
from typing import List, Optional, Any
from pydantic import BaseModel

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.v1.routers.auth import _get_current_user
from app.core.database import get_db
from app.models.api_event import ApiEvent
from app.models.user import User

router = APIRouter(prefix="/int/v1/api-events", tags=["api-events"])


def _serialize_event(event: ApiEvent) -> dict:
    """Convert ApiEvent model to plain dict without SQLAlchemy state."""
    data = event.__dict__.copy()
    data.pop("_sa_instance_state", None)
    return data


class ApiEventCreate(BaseModel):
    event: str
    source: Optional[str] = None
    data: Optional[dict] = None
    description: Optional[str] = None
    method: Optional[str] = None
    api_credential_uuid: Optional[str] = None
    access_token_id: Optional[str] = None


@router.get("/", response_model=List[dict])
def list_api_events(
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    query = (
        db.query(ApiEvent)
        .filter(ApiEvent.company_uuid == current.company_uuid)
        .order_by(ApiEvent.created_at.desc())
        .offset(offset)
        .limit(limit)
    )
    events = query.all()
    return [_serialize_event(e) for e in events]


@router.get("/{id}", response_model=dict)
def get_api_event(
    id: str,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    base_query = (
        db.query(ApiEvent)
        .filter(ApiEvent.company_uuid == current.company_uuid)
    )
    # Try UUID / public_id first
    event = (
        base_query.filter(
            (ApiEvent.uuid == id) | (ApiEvent.public_id == id)
        ).first()
    )
    if not event:
        # If looks like an integer, try numeric id
        try:
            numeric_id = int(id)
        except ValueError:
            numeric_id = None
        if numeric_id is not None:
            event = base_query.filter(ApiEvent.id == numeric_id).first()
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="API event not found")
    return _serialize_event(event)


@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED)
def create_api_event(
    payload: ApiEventCreate,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    event = ApiEvent()
    event.uuid = str(uuid.uuid4())
    event.company_uuid = current.company_uuid
    event.api_credential_uuid = payload.api_credential_uuid
    event.access_token_id = payload.access_token_id
    event.event = payload.event
    event.source = payload.source
    event.data = payload.data or {}
    event.description = payload.description
    event.method = payload.method
    event.created_at = datetime.now(timezone.utc)
    event.updated_at = datetime.now(timezone.utc)

    db.add(event)
    db.commit()
    db.refresh(event)
    return _serialize_event(event)


@router.delete("/{id}", status_code=status.HTTP_200_OK)
def delete_api_event(
    id: str,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    base_query = (
        db.query(ApiEvent)
        .filter(ApiEvent.company_uuid == current.company_uuid)
    )
    event = (
        base_query.filter(
            (ApiEvent.uuid == id) | (ApiEvent.public_id == id)
        ).first()
    )
    if not event:
        try:
            numeric_id = int(id)
        except ValueError:
            numeric_id = None
        if numeric_id is not None:
            event = base_query.filter(ApiEvent.id == numeric_id).first()
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="API event not found")
    
    db.delete(event)
    db.commit()
    return {"status": "ok", "message": "API event deleted"}

