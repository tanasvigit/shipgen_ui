from typing import List, Optional, Any
import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.api.v1.routers.auth import _get_current_user
from app.core.database import get_db
from app.models.storefront_notification_channel import StorefrontNotificationChannel
from app.models.user import User

router = APIRouter(prefix="/int/v1/notification-channels", tags=["int-storefront-notification-channels"])


class NotificationChannelCreate(BaseModel):
    company_uuid: Optional[str] = None
    owner_uuid: Optional[str] = None
    owner_type: Optional[str] = None
    certificate_uuid: Optional[str] = None
    config: Optional[dict[str, Any]] = None
    options: Optional[dict[str, Any]] = None
    name: str
    scheme: Optional[str] = None


class NotificationChannelUpdate(BaseModel):
    owner_uuid: Optional[str] = None
    owner_type: Optional[str] = None
    certificate_uuid: Optional[str] = None
    config: Optional[dict[str, Any]] = None
    options: Optional[dict[str, Any]] = None
    name: Optional[str] = None
    scheme: Optional[str] = None


@router.get("/", response_model=List[dict])
def list_notification_channels(
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    channels = db.query(StorefrontNotificationChannel).filter(
        StorefrontNotificationChannel.company_uuid == current.company_uuid,
        StorefrontNotificationChannel.deleted_at.is_(None)
    ).offset(offset).limit(limit).all()
    return [ch.__dict__ for ch in channels]


@router.get("/{id}", response_model=dict)
def get_notification_channel(
    id: str,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    channel = db.query(StorefrontNotificationChannel).filter(
        StorefrontNotificationChannel.company_uuid == current.company_uuid,
        (StorefrontNotificationChannel.uuid == id) | (StorefrontNotificationChannel.id == int(id) if id.isdigit() else False),
        StorefrontNotificationChannel.deleted_at.is_(None)
    ).first()
    if not channel:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification channel not found")
    return channel.__dict__


@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED)
def create_notification_channel(
    payload: NotificationChannelCreate,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    import hashlib
    import secrets
    
    channel = StorefrontNotificationChannel()
    channel.uuid = str(uuid.uuid4())
    channel.company_uuid = payload.company_uuid or current.company_uuid
    channel.created_by_uuid = current.uuid
    channel.owner_uuid = payload.owner_uuid
    channel.owner_type = payload.owner_type
    channel.certificate_uuid = payload.certificate_uuid
    channel.config = payload.config
    channel.options = payload.options
    channel.name = payload.name
    channel.scheme = payload.scheme
    # Generate app_key similar to Laravel
    channel.app_key = 'noty_channel_' + hashlib.md5((secrets.token_urlsafe(14) + str(datetime.utcnow().timestamp())).encode()).hexdigest()
    
    db.add(channel)
    db.commit()
    db.refresh(channel)
    return channel.__dict__


@router.put("/{id}", response_model=dict)
@router.patch("/{id}", response_model=dict)
def update_notification_channel(
    id: str,
    payload: NotificationChannelUpdate,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    channel = db.query(StorefrontNotificationChannel).filter(
        StorefrontNotificationChannel.company_uuid == current.company_uuid,
        (StorefrontNotificationChannel.uuid == id) | (StorefrontNotificationChannel.id == int(id) if id.isdigit() else False),
        StorefrontNotificationChannel.deleted_at.is_(None)
    ).first()
    if not channel:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification channel not found")
    
    for field, value in payload.dict(exclude_unset=True).items():
        if hasattr(channel, field):
            setattr(channel, field, value)
    
    db.add(channel)
    db.commit()
    db.refresh(channel)
    return channel.__dict__


@router.delete("/{id}", status_code=status.HTTP_200_OK)
def delete_notification_channel(
    id: str,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    channel = db.query(StorefrontNotificationChannel).filter(
        StorefrontNotificationChannel.company_uuid == current.company_uuid,
        (StorefrontNotificationChannel.uuid == id) | (StorefrontNotificationChannel.id == int(id) if id.isdigit() else False),
        StorefrontNotificationChannel.deleted_at.is_(None)
    ).first()
    if not channel:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification channel not found")
    
    channel.deleted_at = datetime.utcnow()
    db.add(channel)
    db.commit()
    return channel.__dict__

