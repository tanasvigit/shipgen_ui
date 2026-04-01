from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.v1.routers.auth import _get_current_user
from app.core.database import get_db
from app.models.webhook_request_log import WebhookRequestLog
from app.models.user import User

router = APIRouter(prefix="/int/v1/webhook-request-logs", tags=["webhook-request-logs"])


@router.get("/", response_model=List[dict])
def list_webhook_request_logs(
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    webhook_uuid: Optional[str] = Query(None),
):
    query = db.query(WebhookRequestLog).filter(
        WebhookRequestLog.company_uuid == current.company_uuid
    )
    
    if webhook_uuid:
        query = query.filter(WebhookRequestLog.webhook_uuid == webhook_uuid)
    
    logs = query.order_by(WebhookRequestLog.created_at.desc()).offset(offset).limit(limit).all()
    return [log.__dict__ for log in logs]


@router.get("/{id}", response_model=dict)
def get_webhook_request_log(
    id: str,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    log = db.query(WebhookRequestLog).filter(
        WebhookRequestLog.company_uuid == current.company_uuid,
        (WebhookRequestLog.uuid == id) | (WebhookRequestLog.public_id == id)
    ).first()
    if not log:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Webhook request log not found")
    return log.__dict__

