import uuid
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy import and_, exists, not_, or_
from sqlalchemy.orm import Session

from app.api.v1.routers.auth import _get_current_user
from app.core.company_scope import require_company_uuid
from app.core.database import get_db
from app.core.roles import ADMIN, DRIVER, DISPATCHER, OPERATIONS_MANAGER, effective_user_role, require_roles
from app.models.driver import Driver
from app.models.order import Order
from app.models.user import User
from app.schemas.driver import (
    DriverCreate,
    DriverOut,
    DriverUpdate,
    DriverResponse,
    DriversListResponse,
)

router = APIRouter(prefix="/fleetops/v1/drivers", tags=["fleetops-drivers"])
TERMINAL_ORDER_STATUSES = ("completed", "cancelled", "failed")


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


def _get_driver_for_company(
    db: Session, *, company_uuid: str, driver_id: str, include_deleted: bool = False
) -> Driver | None:
    q = db.query(Driver).filter(
        Driver.company_uuid == company_uuid,
        (Driver.uuid == driver_id) | (Driver.public_id == driver_id),
    )
    if not include_deleted:
        q = q.filter(Driver.deleted_at.is_(None))
    return q.first()


def _validate_driver_user_link(
    db: Session, *, company_uuid: str, user_uuid: str
) -> None:
    user = (
        db.query(User)
        .filter(
            User.uuid == user_uuid,
            User.company_uuid == company_uuid,
            User.deleted_at.is_(None),
        )
        .first()
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Linked user not found in current company.",
        )
    if effective_user_role(user) != DRIVER:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Linked user must have DRIVER role.",
        )


def _driver_name_by_user_uuid(db: Session, *, user_uuid: str | None, company_uuid: str) -> str | None:
    if not user_uuid:
        return None
    user = (
        db.query(User.name)
        .filter(
            User.uuid == user_uuid,
            User.company_uuid == company_uuid,
            User.deleted_at.is_(None),
        )
        .first()
    )
    if not user:
        return None
    return str(user[0]) if user[0] else None


def _driver_out(db: Session, *, driver: Driver, company_uuid: str) -> DriverOut:
    out = DriverOut.model_validate(driver)
    return out.model_copy(
        update={"name": _driver_name_by_user_uuid(db, user_uuid=driver.user_uuid, company_uuid=company_uuid)}
    )


@router.get("/", response_model=DriversListResponse)
def list_drivers(
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    status_filter: str | None = Query(None, alias="status"),
    online: int | None = Query(None, ge=0, le=1),
    unassigned: bool = Query(False),
    vehicle_uuid: str | None = Query(None, description="Filter drivers assigned to this vehicle uuid"),
):
    company_uuid = require_company_uuid(current)
    query = db.query(Driver).filter(
        Driver.company_uuid == company_uuid,
        Driver.deleted_at.is_(None),
    )
    if status_filter:
        query = query.filter(Driver.status == status_filter)
    if online is not None:
        query = query.filter(Driver.online == online)
    if unassigned:
        active_order_for_driver = exists().where(
            and_(
                Order.company_uuid == company_uuid,
                Order.deleted_at.is_(None),
                Order.driver_assigned_uuid.isnot(None),
                Order.driver_assigned_uuid != "",
                Order.driver_assigned_uuid == Driver.uuid,
                Order.status.notin_(list(TERMINAL_ORDER_STATUSES)),
            )
        )
        query = query.filter(
            or_(Driver.vehicle_uuid.is_(None), Driver.vehicle_uuid == ""),
            not_(active_order_for_driver),
        )
    if vehicle_uuid:
        query = query.filter(Driver.vehicle_uuid == vehicle_uuid)
    total = query.count()
    drivers = query.offset(offset).limit(limit).all()
    return DriversListResponse(
        data=[_driver_out(db, driver=d, company_uuid=company_uuid) for d in drivers],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get("/{driver_id}", response_model=DriverResponse)
def get_driver(
    driver_id: str,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    company_uuid = require_company_uuid(current)
    driver = _get_driver_for_company(db, company_uuid=company_uuid, driver_id=driver_id)
    if not driver:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Driver not found.")
    return DriverResponse(driver=_driver_out(db, driver=driver, company_uuid=company_uuid))


@router.post("/", response_model=DriverResponse, status_code=status.HTTP_201_CREATED)
def create_driver(
    payload: DriverCreate,
    db: Session = Depends(get_db),
    current: User = Depends(require_roles(ADMIN, OPERATIONS_MANAGER)),
):
    company_uuid = require_company_uuid(current)
    if not payload.user_uuid:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="user_uuid is required. Create the DRIVER user first, then link profile.",
        )
    _validate_driver_user_link(db, company_uuid=company_uuid, user_uuid=payload.user_uuid)
    existing_link = (
        db.query(Driver)
        .filter(
            Driver.company_uuid == company_uuid,
            Driver.user_uuid == payload.user_uuid,
            Driver.deleted_at.is_(None),
        )
        .first()
    )
    if existing_link:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A driver is already linked to this user_uuid.",
        )
    driver = Driver()
    driver.uuid = str(uuid.uuid4())
    driver.public_id = f"driver_{uuid.uuid4().hex[:12]}"
    driver.company_uuid = company_uuid
    driver.user_uuid = payload.user_uuid
    driver.drivers_license_number = payload.drivers_license_number
    driver.status = payload.status
    driver.online = 0

    db.add(driver)
    db.commit()
    db.refresh(driver)

    return DriverResponse(driver=_driver_out(db, driver=driver, company_uuid=company_uuid))


@router.post("/register-device")
def register_device_global(
    current: User = Depends(require_roles(ADMIN, OPERATIONS_MANAGER, DISPATCHER)),
):
    """Stub endpoint mirroring DriverController@registerDevice (global)."""
    _ = current
    return {"status": "ok"}


@router.post("/track", response_model=DriverResponse)
def track_driver_global(
    payload: DriverTrackBody,
    db: Session = Depends(get_db),
    current: User = Depends(require_roles(ADMIN, OPERATIONS_MANAGER, DISPATCHER)),
):
    """POST /drivers/track – update location for a driver by driver_id in body."""
    company_uuid = require_company_uuid(current)
    driver = _get_driver_for_company(db, company_uuid=company_uuid, driver_id=payload.driver_id)
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
    return DriverResponse(driver=_driver_out(db, driver=driver, company_uuid=company_uuid))


@router.post("/switch-organization", response_model=DriverResponse)
def switch_organization_global(
    payload: DriverSwitchOrgBody,
    db: Session = Depends(get_db),
    current: User = Depends(require_roles(ADMIN, OPERATIONS_MANAGER, DISPATCHER)),
):
    """POST /drivers/switch-organization – restricted to current company (no cross-tenant moves)."""
    company_uuid = require_company_uuid(current)
    driver = _get_driver_for_company(db, company_uuid=company_uuid, driver_id=payload.driver_id)
    if not driver:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Driver not found.")
    target = str(payload.company_uuid).strip()
    if target != company_uuid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="company_uuid must match the authenticated user's company.",
        )
    driver.company_uuid = company_uuid
    db.add(driver)
    db.commit()
    db.refresh(driver)
    return DriverResponse(driver=DriverOut.model_validate(driver))


@router.put("/{driver_id}", response_model=DriverResponse)
@router.patch("/{driver_id}", response_model=DriverResponse)
def update_driver(
    driver_id: str,
    payload: DriverUpdate,
    db: Session = Depends(get_db),
    current: User = Depends(require_roles(ADMIN, OPERATIONS_MANAGER)),
):
    company_uuid = require_company_uuid(current)
    driver = _get_driver_for_company(db, company_uuid=company_uuid, driver_id=driver_id)
    if not driver:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Driver not found.")

    updates = payload.model_dump(exclude_unset=True)
    if "user_uuid" in updates and updates["user_uuid"]:
        _validate_driver_user_link(db, company_uuid=company_uuid, user_uuid=updates["user_uuid"])
        existing_link = (
            db.query(Driver)
            .filter(
                Driver.company_uuid == company_uuid,
                Driver.user_uuid == updates["user_uuid"],
                Driver.deleted_at.is_(None),
                Driver.id != driver.id,
            )
            .first()
        )
        if existing_link:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A driver is already linked to this user_uuid.",
            )
    for field, value in updates.items():
        setattr(driver, field, value)

    db.add(driver)
    db.commit()
    db.refresh(driver)

    return DriverResponse(driver=DriverOut.model_validate(driver))


@router.delete("/{driver_id}", response_model=DriverResponse)
def delete_driver(
    driver_id: str,
    db: Session = Depends(get_db),
    current: User = Depends(require_roles(ADMIN)),
):
    company_uuid = require_company_uuid(current)
    driver = _get_driver_for_company(db, company_uuid=company_uuid, driver_id=driver_id)
    if not driver:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Driver not found.")

    driver.deleted_at = datetime.now(timezone.utc)
    db.add(driver)
    db.commit()
    db.refresh(driver)

    return DriverResponse(driver=DriverOut.model_validate(driver))


@router.post("/{driver_id}/toggle-online", response_model=DriverResponse)
def toggle_online(
    driver_id: str,
    db: Session = Depends(get_db),
    current: User = Depends(require_roles(ADMIN, OPERATIONS_MANAGER, DISPATCHER)),
):
    company_uuid = require_company_uuid(current)
    driver = _get_driver_for_company(db, company_uuid=company_uuid, driver_id=driver_id)
    if not driver:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Driver not found.")

    driver.online = 0 if driver.online else 1
    db.add(driver)
    db.commit()
    db.refresh(driver)

    return DriverResponse(driver=DriverOut.model_validate(driver))


@router.post("/{driver_id}/track", response_model=DriverResponse)
def track_driver_per_id(
    driver_id: str,
    payload: DriverUpdate,
    db: Session = Depends(get_db),
    current: User = Depends(require_roles(ADMIN, OPERATIONS_MANAGER, DISPATCHER)),
):
    company_uuid = require_company_uuid(current)
    driver = _get_driver_for_company(db, company_uuid=company_uuid, driver_id=driver_id)
    if not driver:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Driver not found.")

    for field, value in payload.model_dump(exclude_unset=True).items():
        if field in {"latitude", "longitude", "heading", "speed", "altitude"}:
            setattr(driver, field, value)

    db.add(driver)
    db.commit()
    db.refresh(driver)

    return DriverResponse(driver=DriverOut.model_validate(driver))


@router.post("/{driver_id}/register-device")
def register_device_for_driver(
    driver_id: str,
    db: Session = Depends(get_db),
    current: User = Depends(require_roles(ADMIN, OPERATIONS_MANAGER, DISPATCHER)),
):
    """Stub endpoint for per-driver device registration."""
    company_uuid = require_company_uuid(current)
    driver = _get_driver_for_company(db, company_uuid=company_uuid, driver_id=driver_id)
    if not driver:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Driver not found.")
    return {"status": "ok", "driver_uuid": driver.uuid}


@router.post("/{driver_id}/switch-organization", response_model=DriverResponse)
def switch_organization(
    driver_id: str,
    payload: dict,
    db: Session = Depends(get_db),
    current: User = Depends(require_roles(ADMIN, OPERATIONS_MANAGER, DISPATCHER)),
):
    """Simplified switch-organization: company must stay the current user's company."""
    company_uuid = require_company_uuid(current)
    driver = _get_driver_for_company(db, company_uuid=company_uuid, driver_id=driver_id)
    if not driver:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Driver not found.")

    raw = payload.get("company_uuid")
    if not raw:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="company_uuid required.")
    target = str(raw).strip()
    if target != company_uuid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="company_uuid must match the authenticated user's company.",
        )
    driver.company_uuid = company_uuid
    db.add(driver)
    db.commit()
    db.refresh(driver)
    return DriverResponse(driver=DriverOut.model_validate(driver))
