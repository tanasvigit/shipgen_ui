"""
Device event endpoints for IoT telemetry ingestion and querying.
"""
import uuid
from datetime import datetime, timezone
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.core.database import get_db
from app.models.device import Device
from app.models.device_event import DeviceEvent
from app.schemas.device_event import DeviceEventCreate, DeviceEventOut, DeviceEventUpdate, DeviceEventIngest
from app.api.v1.routers.auth import _get_current_user
from app.models.user import User

router = APIRouter(prefix="/int/v1/device-events", tags=["device-events"])
bearer_scheme = HTTPBearer(auto_error=False)


@router.post("/ingest", response_model=List[DeviceEventOut], status_code=status.HTTP_201_CREATED)
def ingest_device_events(
    payload: DeviceEventIngest,
    db: Session = Depends(get_db),
    _current: User = Depends(_get_current_user),
):
    """
    Bulk ingest device events from IoT devices.
    Supports device identification by device_id, imei, or device_uuid.
    """
    # Resolve device UUID if device_id or imei provided
    device_uuid = payload.device_uuid
    if not device_uuid and payload.device_id:
        device = db.query(Device).filter(
            (Device.device_id == payload.device_id) |
            (Device.imei == payload.device_id) |
            (Device.public_id == payload.device_id),
            Device.deleted_at.is_(None)
        ).first()
        if device:
            device_uuid = device.uuid
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Device not found: {payload.device_id}"
            )
    
    if not device_uuid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="device_uuid or device_id must be provided"
        )
    
    # Create events
    created_events = []
    for event_data in payload.events:
        event_uuid = str(uuid.uuid4())
        public_id = f"device_event_{uuid.uuid4().hex[:12]}"
        
        event = DeviceEvent(
            uuid=event_uuid,
            public_id=public_id,
            company_uuid=_current.company_uuid if hasattr(_current, 'company_uuid') else None,
            device_uuid=device_uuid,
            event_type=event_data.event_type,
            severity=event_data.severity,
            ident=event_data.ident,
            protocol=event_data.protocol,
            provider=event_data.provider,
            payload=event_data.payload,
            meta=event_data.meta,
            latitude=event_data.latitude,
            longitude=event_data.longitude,
            code=event_data.code,
            reason=event_data.reason,
            comment=event_data.comment,
            state=event_data.state,
            mileage=event_data.mileage,
            occurred_at=event_data.occurred_at or datetime.now(timezone.utc),
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        
        db.add(event)
        created_events.append(event)
    
    db.commit()
    
    # Refresh and add computed fields
    for event in created_events:
        db.refresh(event)
        event.is_processed = event.is_processed()
        event.age_minutes = event.get_age_minutes()
        event.severity_level = event.get_severity_level()
    
    return created_events


@router.post("/", response_model=DeviceEventOut, status_code=status.HTTP_201_CREATED)
def create_device_event(
    payload: DeviceEventCreate,
    db: Session = Depends(get_db),
    _current: User = Depends(_get_current_user),
):
    """Create a single device event."""
    # Resolve device UUID if device_id provided
    device_uuid = payload.device_uuid
    if not device_uuid and payload.device_id:
        device = db.query(Device).filter(
            (Device.device_id == payload.device_id) |
            (Device.imei == payload.device_id) |
            (Device.public_id == payload.device_id),
            Device.deleted_at.is_(None)
        ).first()
        if device:
            device_uuid = device.uuid
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Device not found: {payload.device_id}"
            )
    
    event_uuid = str(uuid.uuid4())
    public_id = f"device_event_{uuid.uuid4().hex[:12]}"
    
    event = DeviceEvent(
        uuid=event_uuid,
        public_id=public_id,
        company_uuid=_current.company_uuid if hasattr(_current, 'company_uuid') else None,
        device_uuid=device_uuid,
        event_type=payload.event_type,
        severity=payload.severity,
        ident=payload.ident,
        protocol=payload.protocol,
        provider=payload.provider,
        payload=payload.payload,
        meta=payload.meta,
        latitude=payload.latitude,
        longitude=payload.longitude,
        code=payload.code,
        reason=payload.reason,
        comment=payload.comment,
        state=payload.state,
        mileage=payload.mileage,
        occurred_at=payload.occurred_at or datetime.now(timezone.utc),
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    
    db.add(event)
    db.commit()
    db.refresh(event)
    
    event.is_processed = event.is_processed()
    event.age_minutes = event.get_age_minutes()
    event.severity_level = event.get_severity_level()
    
    return event


@router.get("/", response_model=List[DeviceEventOut])
def list_device_events(
    db: Session = Depends(get_db),
    _current: User = Depends(_get_current_user),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    device_uuid: Optional[str] = Query(None),
    event_type: Optional[str] = Query(None),
    severity: Optional[str] = Query(None),
    processed: Optional[bool] = Query(None),
):
    """List device events with filtering."""
    query = db.query(DeviceEvent).filter(DeviceEvent.deleted_at.is_(None))
    
    if device_uuid:
        query = query.filter(DeviceEvent.device_uuid == device_uuid)
    if event_type:
        query = query.filter(DeviceEvent.event_type == event_type)
    if severity:
        query = query.filter(DeviceEvent.severity == severity)
    if processed is not None:
        if processed:
            query = query.filter(DeviceEvent.processed_at.isnot(None))
        else:
            query = query.filter(DeviceEvent.processed_at.is_(None))
    
    events = query.order_by(DeviceEvent.created_at.desc()).offset(offset).limit(limit).all()
    
    # Add computed fields
    for event in events:
        event.is_processed = event.is_processed()
        event.age_minutes = event.get_age_minutes()
        event.severity_level = event.get_severity_level()
    
    return events


@router.get("/{event_id}", response_model=DeviceEventOut)
def get_device_event(
    event_id: str,
    db: Session = Depends(get_db),
    _current: User = Depends(_get_current_user),
):
    """Get a device event by public_id or uuid."""
    event = db.query(DeviceEvent).filter(
        (DeviceEvent.public_id == event_id) | (DeviceEvent.uuid == event_id),
        DeviceEvent.deleted_at.is_(None)
    ).first()
    
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device event not found."
        )
    
    event.is_processed = event.is_processed()
    event.age_minutes = event.get_age_minutes()
    event.severity_level = event.get_severity_level()
    
    return event


@router.put("/{event_id}", response_model=DeviceEventOut)
def update_device_event(
    event_id: str,
    payload: DeviceEventUpdate,
    db: Session = Depends(get_db),
    _current: User = Depends(_get_current_user),
):
    """Update a device event (e.g., mark as processed/resolved)."""
    event = db.query(DeviceEvent).filter(
        (DeviceEvent.public_id == event_id) | (DeviceEvent.uuid == event_id),
        DeviceEvent.deleted_at.is_(None)
    ).first()
    
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device event not found."
        )
    
    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(event, field, value)
    
    event.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(event)
    
    event.is_processed = event.is_processed()
    event.age_minutes = event.get_age_minutes()
    event.severity_level = event.get_severity_level()
    
    return event

