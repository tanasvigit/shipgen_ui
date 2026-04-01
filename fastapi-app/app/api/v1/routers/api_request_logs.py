import uuid
from datetime import datetime, timezone
from typing import List, Optional, Any
from pydantic import BaseModel

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.v1.routers.auth import _get_current_user
from app.core.database import get_db
from app.models.api_request_log import ApiRequestLog
from app.models.user import User

router = APIRouter(prefix="/int/v1/api-request-logs", tags=["api-request-logs"])


def _serialize_log(log: ApiRequestLog) -> dict:
    """Convert ApiRequestLog model to plain dict without SQLAlchemy state."""
    data = log.__dict__.copy()
    data.pop("_sa_instance_state", None)
    return data


@router.get("/", response_model=List[dict])
def list_api_request_logs(
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    method: Optional[str] = None,
):
    query = db.query(ApiRequestLog).filter(
        ApiRequestLog.company_uuid == current.company_uuid
    )
    if method:
        query = query.filter(ApiRequestLog.method == method.upper())
    
    logs = (
        query.order_by(ApiRequestLog.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )
    return [_serialize_log(l) for l in logs]


@router.get("/{id}", response_model=dict)
def get_api_request_log(
    id: str,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    base_query = db.query(ApiRequestLog).filter(
        ApiRequestLog.company_uuid == current.company_uuid
    )
    # Try uuid/public_id first
    log = base_query.filter(
        (ApiRequestLog.uuid == id) | (ApiRequestLog.public_id == id)
    ).first()
    if not log:
        # if looks like integer, try numeric id
        try:
            numeric_id = int(id)
        except ValueError:
            numeric_id = None
        if numeric_id is not None:
            log = base_query.filter(ApiRequestLog.id == numeric_id).first()
    if not log:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="API request log not found")
    return _serialize_log(log)


@router.delete("/{id}", status_code=status.HTTP_200_OK)
def delete_api_request_log(
    id: str,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    base_query = db.query(ApiRequestLog).filter(
        ApiRequestLog.company_uuid == current.company_uuid
    )
    log = base_query.filter(
        (ApiRequestLog.uuid == id) | (ApiRequestLog.public_id == id)
    ).first()
    if not log:
        try:
            numeric_id = int(id)
        except ValueError:
            numeric_id = None
        if numeric_id is not None:
            log = base_query.filter(ApiRequestLog.id == numeric_id).first()
    if not log:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="API request log not found")
    
    db.delete(log)
    db.commit()
    return {"status": "ok", "message": "API request log deleted"}

