from typing import List, Optional
import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.api.v1.routers.auth import _get_current_user
from app.core.database import get_db
from app.models.webhook_endpoint import WebhookEndpoint
from app.models.user import User

router = APIRouter(prefix="/int/v1/webhook-endpoints", tags=["webhook-endpoints"])


class WebhookEndpointCreate(BaseModel):
    url: str
    api_credential_uuid: Optional[str] = None
    mode: Optional[str] = None
    version: Optional[str] = None
    description: Optional[str] = None
    events: Optional[list[str]] = None
    status: str = "enabled"


class WebhookEndpointUpdate(BaseModel):
    url: Optional[str] = None
    api_credential_uuid: Optional[str] = None
    mode: Optional[str] = None
    version: Optional[str] = None
    description: Optional[str] = None
    events: Optional[list[str]] = None
    status: Optional[str] = None


@router.get("/", response_model=List[dict])
def list_webhook_endpoints(
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    endpoints = db.query(WebhookEndpoint).filter(
        WebhookEndpoint.company_uuid == current.company_uuid,
        WebhookEndpoint.deleted_at.is_(None)
    ).offset(offset).limit(limit).all()
    return [ep.__dict__ for ep in endpoints]


@router.get("/{id}", response_model=dict)
def get_webhook_endpoint(
    id: str,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    endpoint = db.query(WebhookEndpoint).filter(
        WebhookEndpoint.company_uuid == current.company_uuid,
        (WebhookEndpoint.uuid == id) | (WebhookEndpoint.id == int(id) if id.isdigit() else False),
        WebhookEndpoint.deleted_at.is_(None)
    ).first()
    if not endpoint:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Webhook endpoint not found")
    return endpoint.__dict__


@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED)
def create_webhook_endpoint(
    payload: WebhookEndpointCreate,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    endpoint = WebhookEndpoint()
    endpoint.uuid = str(uuid.uuid4())
    endpoint.company_uuid = current.company_uuid
    endpoint.created_by_uuid = current.uuid
    endpoint.url = payload.url
    endpoint.api_credential_uuid = payload.api_credential_uuid
    endpoint.mode = payload.mode
    endpoint.version = payload.version
    endpoint.description = payload.description
    endpoint.events = payload.events
    endpoint.status = payload.status
    
    db.add(endpoint)
    db.commit()
    db.refresh(endpoint)
    return endpoint.__dict__


@router.put("/{id}", response_model=dict)
@router.patch("/{id}", response_model=dict)
def update_webhook_endpoint(
    id: str,
    payload: WebhookEndpointUpdate,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    endpoint = db.query(WebhookEndpoint).filter(
        WebhookEndpoint.company_uuid == current.company_uuid,
        (WebhookEndpoint.uuid == id) | (WebhookEndpoint.id == int(id) if id.isdigit() else False),
        WebhookEndpoint.deleted_at.is_(None)
    ).first()
    if not endpoint:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Webhook endpoint not found")
    
    for field, value in payload.dict(exclude_unset=True).items():
        if hasattr(endpoint, field):
            setattr(endpoint, field, value)
    
    endpoint.updated_by_uuid = current.uuid
    db.add(endpoint)
    db.commit()
    db.refresh(endpoint)
    return endpoint.__dict__


@router.delete("/{id}", status_code=status.HTTP_200_OK)
def delete_webhook_endpoint(
    id: str,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    endpoint = db.query(WebhookEndpoint).filter(
        WebhookEndpoint.company_uuid == current.company_uuid,
        (WebhookEndpoint.uuid == id) | (WebhookEndpoint.id == int(id) if id.isdigit() else False),
        WebhookEndpoint.deleted_at.is_(None)
    ).first()
    if not endpoint:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Webhook endpoint not found")
    
    endpoint.deleted_at = datetime.utcnow()
    db.add(endpoint)
    db.commit()
    return endpoint.__dict__


@router.patch("/{id}/enable", response_model=dict)
def enable_webhook_endpoint(
    id: str,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    endpoint = db.query(WebhookEndpoint).filter(
        WebhookEndpoint.company_uuid == current.company_uuid,
        (WebhookEndpoint.uuid == id) | (WebhookEndpoint.id == int(id) if id.isdigit() else False),
        WebhookEndpoint.deleted_at.is_(None)
    ).first()
    if not endpoint:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Webhook endpoint not found")
    
    endpoint.status = "enabled"
    db.add(endpoint)
    db.commit()
    db.refresh(endpoint)
    return endpoint.__dict__


@router.patch("/{id}/disable", response_model=dict)
def disable_webhook_endpoint(
    id: str,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    endpoint = db.query(WebhookEndpoint).filter(
        WebhookEndpoint.company_uuid == current.company_uuid,
        (WebhookEndpoint.uuid == id) | (WebhookEndpoint.id == int(id) if id.isdigit() else False),
        WebhookEndpoint.deleted_at.is_(None)
    ).first()
    if not endpoint:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Webhook endpoint not found")
    
    endpoint.status = "disabled"
    db.add(endpoint)
    db.commit()
    db.refresh(endpoint)
    return endpoint.__dict__


@router.get("/events", response_model=List[str])
def get_webhook_events(
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    """Return available webhook events."""
    # Define standard webhook events
    events = [
        "order.created",
        "order.updated",
        "order.completed",
        "order.cancelled",
        "order.dispatched",
        "driver.created",
        "driver.updated",
        "driver.online",
        "driver.offline",
        "vehicle.created",
        "vehicle.updated",
        "customer.created",
        "customer.updated",
        "storefront.order.created",
        "storefront.order.accepted",
        "storefront.order.ready",
        "storefront.order.completed",
        "storefront.order.cancelled",
        "payment.processed",
        "payment.failed",
        "notification.sent",
    ]
    return events


@router.get("/versions", response_model=List[str])
def get_webhook_versions(
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    """Return available webhook API versions."""
    return ["v1", "v2"]

