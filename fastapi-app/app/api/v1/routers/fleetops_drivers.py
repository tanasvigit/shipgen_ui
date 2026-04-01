import uuid
from datetime import datetime, timezone
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.v1.routers.auth import _get_current_user
from app.core.database import get_db
from app.models.driver import Driver
from app.models.user import User
from app.schemas.driver import DriverCreate, DriverOut, DriverUpdate, DriverResponse, DriversResponse

router = APIRouter(prefix="/fleetops/v1/drivers", tags=["fleetops-drivers"])


class DriverTrackBody(BaseModel):
    """Body for POST /drivers/track (global)."""
    driver_id: str
    latitude: Optional[str] = None
    longitude: Optional[str] = None
    heading: Optional[str] = None
    speed: Optional[str] = None
    altitude: Optional[str] = None


class DriverSwitchOrgBody(BaseModel):
    """Body for POST /drivers/switch-organization (global)."""
    driver_id: str
    company_uuid: str


@router.get("/", response_model=DriversResponse)
def list_drivers(
    db: Session = Depends(get_db),
    _current: User = Depends(_get_current_user),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    status_filter: str | None = Query(None, alias="status"),
):
    query = db.query(Driver).filter(Driver.deleted_at.is_(None))
    if status_filter:
        query = query.filter(Driver.status == status_filter)
    drivers = query.offset(offset).limit(limit).all()
    return {"drivers": drivers}


@router.get("/{driver_id}", response_model=DriverResponse)
def get_driver(
    driver_id: str,
    db: Session = Depends(get_db),
    _current: User = Depends(_get_current_user),
):
    driver = db.query(Driver).filter(Driver.uuid == driver_id).first()
    if not driver:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Driver not found.")
    return {"driver": driver}


@router.post("/", response_model=DriverResponse, status_code=status.HTTP_201_CREATED)
def create_driver(
    payload: DriverCreate,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    driver = Driver()
    driver.uuid = str(uuid.uuid4())
    driver.public_id = f"driver_{uuid.uuid4().hex[:12]}"
    driver.company_uuid = payload.company_uuid or current.company_uuid
    driver.user_uuid = payload.user_uuid
    driver.drivers_license_number = payload.drivers_license_number
    driver.status = payload.status
    driver.online = 0

    db.add(driver)
    db.commit()
    db.refresh(driver)

    return {"driver": driver}


@router.post("/register-device")
def register_device_global():
    """Stub endpoint mirroring DriverController@registerDevice (global)."""
    return {"status": "ok"}


@router.post("/track", response_model=DriverResponse)
def track_driver_global(
    payload: DriverTrackBody,
    db: Session = Depends(get_db),
    _current: User = Depends(_get_current_user),
):
    """POST /drivers/track – update location for a driver by driver_id in body."""
    driver = db.query(Driver).filter(Driver.uuid == payload.driver_id).first()
    if not driver:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Driver not found.")
    if payload.latitude is not None:
        driver.latitude = payload.latitude
    if payload.longitude is not None:
        driver.longitude = payload.longitude
    if payload.heading is not None:
        driver.heading = payload.heading
    if payload.speed is not None:
        driver.speed = payload.speed
    if payload.altitude is not None:
        driver.altitude = payload.altitude
    db.add(driver)
    db.commit()
    db.refresh(driver)
    return {"driver": driver}


@router.post("/switch-organization", response_model=DriverResponse)
def switch_organization_global(
    payload: DriverSwitchOrgBody,
    db: Session = Depends(get_db),
    _current: User = Depends(_get_current_user),
):
    """POST /drivers/switch-organization – switch driver to another company by body."""
    driver = db.query(Driver).filter(Driver.uuid == payload.driver_id).first()
    if not driver:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Driver not found.")
    driver.company_uuid = payload.company_uuid
    db.add(driver)
    db.commit()
    db.refresh(driver)
    return {"driver": driver}


@router.put("/{driver_id}", response_model=DriverResponse)
@router.patch("/{driver_id}", response_model=DriverResponse)
def update_driver(
    driver_id: str,
    payload: DriverUpdate,
    db: Session = Depends(get_db),
    _current: User = Depends(_get_current_user),
):
    driver = db.query(Driver).filter(Driver.uuid == driver_id).first()
    if not driver:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Driver not found.")

    for field, value in payload.dict(exclude_unset=True).items():
        setattr(driver, field, value)

    db.add(driver)
    db.commit()
    db.refresh(driver)

    return {"driver": driver}


@router.delete("/{driver_id}", response_model=DriverResponse)
def delete_driver(
    driver_id: str,
    db: Session = Depends(get_db),
    _current: User = Depends(_get_current_user),
):
    driver = db.query(Driver).filter(Driver.uuid == driver_id).first()
    if not driver:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Driver not found.")

    driver.deleted_at = datetime.now(timezone.utc)
    db.add(driver)
    db.commit()
    db.refresh(driver)
    return {"driver": driver}


@router.post("/{driver_id}/toggle-online", response_model=DriverResponse)
def toggle_online(
    driver_id: str,
    db: Session = Depends(get_db),
    _current: User = Depends(_get_current_user),
):
    driver = db.query(Driver).filter(Driver.uuid == driver_id).first()
    if not driver:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Driver not found.")

    driver.online = 0 if driver.online else 1
    db.add(driver)
    db.commit()
    db.refresh(driver)
    return {"driver": driver}


@router.post("/{driver_id}/track", response_model=DriverResponse)
def track_driver_per_id(
    driver_id: str,
    payload: DriverUpdate,
    db: Session = Depends(get_db),
    _current: User = Depends(_get_current_user),
):
    driver = db.query(Driver).filter(Driver.uuid == driver_id).first()
    if not driver:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Driver not found.")

    for field, value in payload.dict(exclude_unset=True).items():
        if field in {"latitude", "longitude", "heading", "speed", "altitude"}:
            setattr(driver, field, value)

    db.add(driver)
    db.commit()
    db.refresh(driver)
    return {"driver": driver}


@router.post("/{driver_id}/register-device")
def register_device_for_driver(
    driver_id: str,
    db: Session = Depends(get_db),
    _current: User = Depends(_get_current_user),
):
    """Stub endpoint for per-driver device registration."""
    driver = db.query(Driver).filter(Driver.uuid == driver_id).first()
    if not driver:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Driver not found.")
    return {"status": "ok", "driver_uuid": driver.uuid}


@router.post("/{driver_id}/switch-organization", response_model=DriverResponse)
def switch_organization(
    driver_id: str,
    payload: dict,
    db: Session = Depends(get_db),
    _current: User = Depends(_get_current_user),
):
    """Simplified switch-organization: just updates driver.company_uuid."""
    driver = db.query(Driver).filter(Driver.uuid == driver_id).first()
    if not driver:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Driver not found.")

    company_uuid = payload.get("company_uuid")
    if not company_uuid:
         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="company_uuid required.")

    driver.company_uuid = company_uuid
    db.add(driver)
    db.commit()
    db.refresh(driver)
    return {"driver": driver}





