"""
Telematics endpoints for provider integration management.
"""
import uuid
from datetime import datetime, timezone, timedelta
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.roles import ADMIN, OPERATIONS_MANAGER, DISPATCHER, require_roles
from app.models.telematic import Telematic
from app.schemas.telematic import TelematicCreate, TelematicOut, TelematicUpdate, TelematicHeartbeat
from app.api.v1.routers.auth import _get_current_user
from app.models.user import User

router = APIRouter(prefix="/int/v1/telematics", tags=["telematics"])
bearer_scheme = HTTPBearer(auto_error=False)


@router.get("/", response_model=List[TelematicOut])
def list_telematics(
    db: Session = Depends(get_db),
    _current: User = Depends(_get_current_user),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    provider: Optional[str] = Query(None),
    status_filter: Optional[str] = Query(None, alias="status"),
    online: Optional[bool] = Query(None),
):
    """List telematics providers."""
    query = db.query(Telematic).filter(Telematic.deleted_at.is_(None))
    
    if provider:
        query = query.filter(Telematic.provider == provider)
    if status_filter:
        query = query.filter(Telematic.status == status_filter)
    if online is not None:
        if online:
            query = query.filter(Telematic.last_seen_at.isnot(None))
            query = query.filter(Telematic.last_seen_at >= datetime.now(timezone.utc) - timedelta(minutes=5))
        else:
            query = query.filter(
                (Telematic.last_seen_at.is_(None)) |
                (Telematic.last_seen_at < datetime.now(timezone.utc) - timedelta(minutes=5))
            )
    
    telematics = query.offset(offset).limit(limit).all()
    
    # Add computed fields
    for telematic in telematics:
        telematic.is_online = telematic.is_online()
        telematic.connection_status = telematic.get_connection_status()
        telematic.signal_strength = telematic.get_signal_strength()
        telematic.last_location = telematic.get_last_location()
    
    return telematics


@router.get("/{telematic_id}", response_model=TelematicOut)
def get_telematic(
    telematic_id: str,
    db: Session = Depends(get_db),
    _current: User = Depends(_get_current_user),
):
    """Get a telematic by public_id or uuid."""
    telematic = db.query(Telematic).filter(
        (Telematic.public_id == telematic_id) | (Telematic.uuid == telematic_id),
        Telematic.deleted_at.is_(None)
    ).first()
    
    if not telematic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Telematic not found."
        )
    
    telematic.is_online = telematic.is_online()
    telematic.connection_status = telematic.get_connection_status()
    telematic.signal_strength = telematic.get_signal_strength()
    telematic.last_location = telematic.get_last_location()
    
    return telematic


@router.post("/", response_model=TelematicOut, status_code=status.HTTP_201_CREATED)
def create_telematic(
    payload: TelematicCreate,
    db: Session = Depends(get_db),
    _current: User = Depends(require_roles(ADMIN, OPERATIONS_MANAGER, DISPATCHER)),
):
    """Create a new telematic provider integration."""
    telematic_uuid = str(uuid.uuid4())
    public_id = f"telematic_{uuid.uuid4().hex[:12]}"
    
    telematic = Telematic(
        uuid=telematic_uuid,
        public_id=public_id,
        company_uuid=_current.company_uuid if hasattr(_current, 'company_uuid') else None,
        name=payload.name,
        provider=payload.provider,
        model=payload.model,
        serial_number=payload.serial_number,
        firmware_version=payload.firmware_version,
        status=payload.status or "initialized",
        type=payload.type,
        imei=payload.imei,
        iccid=payload.iccid,
        imsi=payload.imsi,
        msisdn=payload.msisdn,
        config=payload.config,
        credentials=payload.credentials,
        meta=payload.meta,
        warranty_uuid=payload.warranty_uuid,
        created_by_uuid=_current.uuid if hasattr(_current, 'uuid') else None,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    
    db.add(telematic)
    db.commit()
    db.refresh(telematic)
    
    telematic.is_online = telematic.is_online()
    telematic.connection_status = telematic.get_connection_status()
    telematic.signal_strength = telematic.get_signal_strength()
    telematic.last_location = telematic.get_last_location()
    
    return telematic


@router.put("/{telematic_id}", response_model=TelematicOut)
def update_telematic(
    telematic_id: str,
    payload: TelematicUpdate,
    db: Session = Depends(get_db),
    _current: User = Depends(require_roles(ADMIN, OPERATIONS_MANAGER, DISPATCHER)),
):
    """Update a telematic provider."""
    telematic = db.query(Telematic).filter(
        (Telematic.public_id == telematic_id) | (Telematic.uuid == telematic_id),
        Telematic.deleted_at.is_(None)
    ).first()
    
    if not telematic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Telematic not found."
        )
    
    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(telematic, field, value)
    
    telematic.updated_by_uuid = _current.uuid if hasattr(_current, 'uuid') else None
    telematic.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(telematic)
    
    telematic.is_online = telematic.is_online()
    telematic.connection_status = telematic.get_connection_status()
    telematic.signal_strength = telematic.get_signal_strength()
    telematic.last_location = telematic.get_last_location()
    
    return telematic


@router.post("/{telematic_id}/heartbeat", response_model=TelematicOut)
def telematic_heartbeat(
    telematic_id: str,
    payload: TelematicHeartbeat,
    db: Session = Depends(get_db),
    _current: User = Depends(require_roles(ADMIN, OPERATIONS_MANAGER, DISPATCHER)),
):
    """Update telematic heartbeat/metrics."""
    telematic = db.query(Telematic).filter(
        (Telematic.public_id == telematic_id) | (Telematic.uuid == telematic_id),
        Telematic.deleted_at.is_(None)
    ).first()
    
    if not telematic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Telematic not found."
        )
    
    # Merge metrics
    current_metrics = telematic.last_metrics or {}
    if payload.metrics:
        current_metrics.update(payload.metrics)
    
    telematic.last_seen_at = payload.timestamp or datetime.now(timezone.utc)
    telematic.last_metrics = current_metrics
    telematic.updated_at = datetime.now(timezone.utc)
    
    db.commit()
    db.refresh(telematic)
    
    telematic.is_online = telematic.is_online()
    telematic.connection_status = telematic.get_connection_status()
    telematic.signal_strength = telematic.get_signal_strength()
    telematic.last_location = telematic.get_last_location()
    
    return telematic


@router.delete("/{telematic_id}", status_code=status.HTTP_200_OK)
def delete_telematic(
    telematic_id: str,
    db: Session = Depends(get_db),
    _current: User = Depends(require_roles(ADMIN, OPERATIONS_MANAGER, DISPATCHER)),
):
    """Soft delete a telematic provider."""
    telematic = db.query(Telematic).filter(
        (Telematic.public_id == telematic_id) | (Telematic.uuid == telematic_id),
        Telematic.deleted_at.is_(None)
    ).first()
    
    if not telematic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Telematic not found."
        )
    
    telematic.deleted_at = datetime.now(timezone.utc)
    db.commit()
    
    return {"message": "Telematic deleted successfully."}

