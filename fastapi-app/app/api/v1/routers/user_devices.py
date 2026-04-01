import uuid
from datetime import datetime, timezone
from typing import List, Optional, Any
from pydantic import BaseModel

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.v1.routers.auth import _get_current_user
from app.core.database import get_db
from app.models.user_device import UserDevice
from app.models.user import User

router = APIRouter(prefix="/int/v1/user-devices", tags=["user-devices"])


class UserDeviceCreate(BaseModel):
    platform: str
    token: str
    status: Optional[str] = "active"


@router.get("/", response_model=List[dict])
def list_user_devices(
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    user_uuid: Optional[str] = None,
    platform: Optional[str] = None,
):
    query = db.query(UserDevice).filter(UserDevice.deleted_at.is_(None))
    if user_uuid:
        query = query.filter(UserDevice.user_uuid == user_uuid)
    else:
        query = query.filter(UserDevice.user_uuid == current.uuid)
    if platform:
        query = query.filter(UserDevice.platform == platform)
    
    devices = query.order_by(UserDevice.created_at.desc()).offset(offset).limit(limit).all()
    return [d.__dict__ for d in devices]


@router.get("/{id}", response_model=dict)
def get_user_device(
    id: str,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    device = db.query(UserDevice).filter(
        (UserDevice.uuid == id) | (UserDevice.public_id == id),
        UserDevice.deleted_at.is_(None)
    ).first()
    if not device:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User device not found")
    return device.__dict__


@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED)
def create_user_device(
    payload: UserDeviceCreate,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    device = UserDevice()
    device.uuid = str(uuid.uuid4())
    device.user_uuid = current.uuid
    device.platform = payload.platform
    device.token = payload.token
    device.status = payload.status
    device.created_at = datetime.now(timezone.utc)
    device.updated_at = datetime.now(timezone.utc)
    
    db.add(device)
    db.commit()
    db.refresh(device)
    return device.__dict__


@router.put("/{id}", response_model=dict)
@router.patch("/{id}", response_model=dict)
def update_user_device(
    id: str,
    payload: dict,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    device = db.query(UserDevice).filter(
        (UserDevice.uuid == id) | (UserDevice.public_id == id),
        UserDevice.user_uuid == current.uuid,
        UserDevice.deleted_at.is_(None)
    ).first()
    if not device:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User device not found")
    
    for field, value in payload.items():
        if hasattr(device, field):
            setattr(device, field, value)
    
    device.updated_at = datetime.now(timezone.utc)
    db.add(device)
    db.commit()
    db.refresh(device)
    return device.__dict__


@router.delete("/{id}", status_code=status.HTTP_200_OK)
def delete_user_device(
    id: str,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    device = db.query(UserDevice).filter(
        (UserDevice.uuid == id) | (UserDevice.public_id == id),
        UserDevice.user_uuid == current.uuid,
        UserDevice.deleted_at.is_(None)
    ).first()
    if not device:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User device not found")
    
    device.deleted_at = datetime.now(timezone.utc)
    db.add(device)
    db.commit()
    return {"status": "ok", "message": "User device deleted"}

