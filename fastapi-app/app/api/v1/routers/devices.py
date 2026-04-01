"""
Device endpoints for IoT device management.
"""
import uuid
from datetime import datetime, timezone, timedelta
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.device import Device
from app.schemas.device import DeviceCreate, DeviceOut, DeviceUpdate, DeviceLocationUpdate, DeviceHeartbeat
from app.api.v1.routers.auth import _get_current_user
from app.models.user import User

router = APIRouter(prefix="/int/v1/devices", tags=["devices"])
bearer_scheme = HTTPBearer(auto_error=False)


@router.get("/", response_model=List[DeviceOut])
def list_devices(
    db: Session = Depends(get_db),
    _current: User = Depends(_get_current_user),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    status_filter: Optional[str] = Query(None, alias="status"),
    online: Optional[bool] = Query(None),
    attachable_type: Optional[str] = Query(None),
):
    """List devices."""
    query = db.query(Device).filter(Device.deleted_at.is_(None))
    
    if status_filter:
        query = query.filter(Device.status == status_filter)
    if online is not None:
        if online:
            query = query.filter(Device.last_online_at.isnot(None))
            query = query.filter(Device.last_online_at >= datetime.now(timezone.utc) - timedelta(minutes=10))
        else:
            query = query.filter(
                (Device.last_online_at.is_(None)) |
                (Device.last_online_at < datetime.now(timezone.utc) - timedelta(minutes=10))
            )
    if attachable_type:
        query = query.filter(Device.attachable_type == attachable_type)
    
    devices = query.offset(offset).limit(limit).all()
    
    # Add computed fields
    for device in devices:
        device.is_online = device.is_online()
        device.connection_status = device.get_connection_status()
    
    return devices


@router.get("/{device_id}", response_model=DeviceOut)
def get_device(
    device_id: str,
    db: Session = Depends(get_db),
    _current: User = Depends(_get_current_user),
):
    """Get a device by public_id, uuid, or device_id."""
    device = db.query(Device).filter(
        (Device.public_id == device_id) |
        (Device.uuid == device_id) |
        (Device.device_id == device_id) |
        (Device.imei == device_id),
        Device.deleted_at.is_(None)
    ).first()
    
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found."
        )
    
    device.is_online = device.is_online()
    device.connection_status = device.get_connection_status()
    
    return device


@router.post("/", response_model=DeviceOut, status_code=status.HTTP_201_CREATED)
def create_device(
    payload: DeviceCreate,
    db: Session = Depends(get_db),
    _current: User = Depends(_get_current_user),
):
    """Create a new device."""
    device_uuid = str(uuid.uuid4())
    public_id = f"device_{uuid.uuid4().hex[:12]}"
    
    device = Device(
        uuid=device_uuid,
        public_id=public_id,
        company_uuid=_current.company_uuid if hasattr(_current, 'company_uuid') else None,
        name=payload.name,
        model=payload.model,
        manufacturer=payload.manufacturer,
        serial_number=payload.serial_number,
        device_id=payload.device_id,
        imei=payload.imei,
        imsi=payload.imsi,
        provider=payload.provider,
        type=payload.type,
        firmware_version=payload.firmware_version,
        telematic_uuid=payload.telematic_uuid,
        attachable_type=payload.attachable_type,
        attachable_uuid=payload.attachable_uuid,
        status=payload.status or "active",
        online=payload.online,
        data_frequency=payload.data_frequency,
        installation_date=payload.installation_date,
        last_maintenance_date=payload.last_maintenance_date,
        meta=payload.meta,
        data=payload.data,
        options=payload.options,
        notes=payload.notes,
        photo_uuid=payload.photo_uuid,
        warranty_uuid=payload.warranty_uuid,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    
    db.add(device)
    db.commit()
    db.refresh(device)
    
    device.is_online = device.is_online()
    device.connection_status = device.get_connection_status()
    
    return device


@router.put("/{device_id}", response_model=DeviceOut)
def update_device(
    device_id: str,
    payload: DeviceUpdate,
    db: Session = Depends(get_db),
    _current: User = Depends(_get_current_user),
):
    """Update a device."""
    device = db.query(Device).filter(
        (Device.public_id == device_id) |
        (Device.uuid == device_id) |
        (Device.device_id == device_id),
        Device.deleted_at.is_(None)
    ).first()
    
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found."
        )
    
    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(device, field, value)
    
    device.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(device)
    
    device.is_online = device.is_online()
    device.connection_status = device.get_connection_status()
    
    return device


@router.post("/{device_id}/location", response_model=DeviceOut)
def update_device_location(
    device_id: str,
    payload: DeviceLocationUpdate,
    db: Session = Depends(get_db),
    _current: User = Depends(_get_current_user),
):
    """Update device location from telemetry."""
    device = db.query(Device).filter(
        (Device.public_id == device_id) |
        (Device.uuid == device_id) |
        (Device.device_id == device_id) |
        (Device.imei == device_id),
        Device.deleted_at.is_(None)
    ).first()
    
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found."
        )
    
    device.latitude = str(payload.latitude)
    device.longitude = str(payload.longitude)
    if payload.heading is not None:
        device.heading = str(payload.heading)
    if payload.speed is not None:
        device.speed = str(payload.speed)
    if payload.altitude is not None:
        device.altitude = str(payload.altitude)
    
    device.last_online_at = payload.timestamp or datetime.now(timezone.utc)
    device.online = True
    device.updated_at = datetime.now(timezone.utc)
    
    db.commit()
    db.refresh(device)
    
    device.is_online = device.is_online()
    device.connection_status = device.get_connection_status()
    
    return device


@router.post("/{device_id}/heartbeat", response_model=DeviceOut)
def device_heartbeat(
    device_id: str,
    payload: DeviceHeartbeat,
    db: Session = Depends(get_db),
    _current: User = Depends(_get_current_user),
):
    """Update device heartbeat/online status."""
    device = db.query(Device).filter(
        (Device.public_id == device_id) |
        (Device.uuid == device_id) |
        (Device.device_id == device_id) |
        (Device.imei == device_id),
        Device.deleted_at.is_(None)
    ).first()
    
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found."
        )
    
    device.online = payload.online
    device.last_online_at = payload.timestamp or datetime.now(timezone.utc)
    if payload.metrics:
        if device.data is None:
            device.data = {}
        device.data.update(payload.metrics)
    
    device.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(device)
    
    device.is_online = device.is_online()
    device.connection_status = device.get_connection_status()
    
    return device


@router.delete("/{device_id}", status_code=status.HTTP_200_OK)
def delete_device(
    device_id: str,
    db: Session = Depends(get_db),
    _current: User = Depends(_get_current_user),
):
    """Soft delete a device."""
    device = db.query(Device).filter(
        (Device.public_id == device_id) |
        (Device.uuid == device_id) |
        (Device.device_id == device_id),
        Device.deleted_at.is_(None)
    ).first()
    
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found."
        )
    
    device.deleted_at = datetime.now(timezone.utc)
    db.commit()
    
    return {"message": "Device deleted successfully."}

