import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import and_, exists, not_
from sqlalchemy.orm import Session

from app.api.v1.routers.auth import _get_current_user
from app.core.company_scope import require_company_uuid
from app.core.database import get_db
from app.models.driver import Driver
from app.models.order import Order
from app.models.user import User
from app.models.vehicle import Vehicle
from app.schemas.vehicle import (
    VehicleCreate,
    VehicleOut,
    VehicleUpdate,
    VehicleResponse,
    VehiclesListResponse,
)

router = APIRouter(prefix="/fleetops/v1/vehicles", tags=["fleetops-vehicles"])
TERMINAL_ORDER_STATUSES = ("completed", "cancelled", "failed")


def _get_vehicle_for_company(
    db: Session, *, company_uuid: str, vehicle_id: str, include_deleted: bool = False
) -> Vehicle | None:
    q = db.query(Vehicle).filter(
        Vehicle.company_uuid == company_uuid,
        (Vehicle.uuid == vehicle_id) | (Vehicle.public_id == vehicle_id),
    )
    if not include_deleted:
        q = q.filter(Vehicle.deleted_at.is_(None))
    return q.first()


def _get_driver_for_company(db: Session, *, company_uuid: str, driver_id: str) -> Driver | None:
    return (
        db.query(Driver)
        .filter(
            Driver.company_uuid == company_uuid,
            Driver.deleted_at.is_(None),
            (Driver.uuid == driver_id) | (Driver.public_id == driver_id),
        )
        .first()
    )


@router.get("/", response_model=VehiclesListResponse)
def list_vehicles(
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    status_filter: str | None = Query(None, alias="status"),
    unassigned: bool = Query(False),
):
    company_uuid = require_company_uuid(current)
    query = db.query(Vehicle).filter(
        Vehicle.company_uuid == company_uuid,
        Vehicle.deleted_at.is_(None),
    )
    if status_filter:
        query = query.filter(Vehicle.status == status_filter)
    if unassigned:
        has_assigned_driver = exists().where(
            and_(
                Driver.company_uuid == company_uuid,
                Driver.deleted_at.is_(None),
                Driver.vehicle_uuid == Vehicle.uuid,
            )
        )
        active_order_for_vehicle = exists().where(
            and_(
                Order.company_uuid == company_uuid,
                Order.deleted_at.is_(None),
                Order.vehicle_assigned_uuid.isnot(None),
                Order.vehicle_assigned_uuid != "",
                Order.vehicle_assigned_uuid == Vehicle.uuid,
                Order.status.notin_(list(TERMINAL_ORDER_STATUSES)),
            )
        )
        query = query.filter(not_(has_assigned_driver), not_(active_order_for_vehicle))
    total = query.count()
    vehicles = query.offset(offset).limit(limit).all()
    return VehiclesListResponse(
        data=[VehicleOut.model_validate(v) for v in vehicles],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get("/{vehicle_id}", response_model=VehicleResponse)
def get_vehicle(
    vehicle_id: str,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    company_uuid = require_company_uuid(current)
    vehicle = _get_vehicle_for_company(db, company_uuid=company_uuid, vehicle_id=vehicle_id)
    if not vehicle:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vehicle not found.")
    return VehicleResponse(vehicle=VehicleOut.model_validate(vehicle))


@router.post("/", response_model=VehicleResponse, status_code=status.HTTP_201_CREATED)
def create_vehicle(
    payload: VehicleCreate,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    company_uuid = require_company_uuid(current)
    vehicle = Vehicle()
    vehicle.uuid = str(uuid.uuid4())
    vehicle.public_id = f"vehicle_{uuid.uuid4().hex[:12]}"
    vehicle.company_uuid = company_uuid
    vehicle.vendor_uuid = payload.vendor_uuid
    vehicle.make = payload.make
    vehicle.model = payload.model
    vehicle.year = payload.year
    vehicle.trim = payload.trim
    vehicle.type = payload.type
    vehicle.plate_number = payload.plate_number
    vehicle.vin = payload.vin
    vehicle.status = payload.status

    db.add(vehicle)
    db.commit()
    db.refresh(vehicle)

    return VehicleResponse(vehicle=VehicleOut.model_validate(vehicle))


@router.put("/{vehicle_id}", response_model=VehicleResponse)
@router.patch("/{vehicle_id}", response_model=VehicleResponse)
def update_vehicle(
    vehicle_id: str,
    payload: VehicleUpdate,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    company_uuid = require_company_uuid(current)
    vehicle = _get_vehicle_for_company(db, company_uuid=company_uuid, vehicle_id=vehicle_id)
    if not vehicle:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vehicle not found.")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(vehicle, field, value)

    db.add(vehicle)
    db.commit()
    db.refresh(vehicle)

    return VehicleResponse(vehicle=VehicleOut.model_validate(vehicle))


@router.delete("/{vehicle_id}", response_model=VehicleResponse)
def delete_vehicle(
    vehicle_id: str,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    company_uuid = require_company_uuid(current)
    vehicle = _get_vehicle_for_company(db, company_uuid=company_uuid, vehicle_id=vehicle_id)
    if not vehicle:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vehicle not found.")

    vehicle.deleted_at = datetime.utcnow()
    db.add(vehicle)
    db.commit()
    db.refresh(vehicle)

    return VehicleResponse(vehicle=VehicleOut.model_validate(vehicle))


@router.post("/{vehicle_id}/track", response_model=VehicleResponse)
def track_vehicle(
    vehicle_id: str,
    latitude: float | None = None,
    longitude: float | None = None,
    altitude: float | None = None,
    heading: float | None = None,
    speed: float | None = None,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    company_uuid = require_company_uuid(current)
    vehicle = _get_vehicle_for_company(db, company_uuid=company_uuid, vehicle_id=vehicle_id)
    if not vehicle:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vehicle not found.")

    if latitude is not None:
        vehicle.meta = (vehicle.meta or {}) | {"latitude": latitude}
    if longitude is not None:
        vehicle.meta = (vehicle.meta or {}) | {"longitude": longitude}
    if altitude is not None:
        vehicle.meta = (vehicle.meta or {}) | {"altitude": altitude}
    if heading is not None:
        vehicle.meta = (vehicle.meta or {}) | {"heading": heading}
    if speed is not None:
        vehicle.meta = (vehicle.meta or {}) | {"speed": speed}

    db.add(vehicle)
    db.commit()
    db.refresh(vehicle)

    return VehicleResponse(vehicle=VehicleOut.model_validate(vehicle))


@router.post("/{vehicle_id}/assign-driver", response_model=VehicleResponse)
def assign_driver(
    vehicle_id: str,
    driver_uuid: str,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    """Assign a driver to this vehicle by setting driver.vehicle_uuid only."""
    company_uuid = require_company_uuid(current)
    vehicle = _get_vehicle_for_company(db, company_uuid=company_uuid, vehicle_id=vehicle_id)
    if not vehicle:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vehicle not found.")

    driver = _get_driver_for_company(db, company_uuid=company_uuid, driver_id=driver_uuid)
    if not driver:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Driver not found.")

    driver.vehicle_uuid = vehicle.uuid
    db.add(driver)
    db.commit()
    db.refresh(vehicle)

    return VehicleResponse(vehicle=VehicleOut.model_validate(vehicle))


@router.post("/{vehicle_id}/assgn-driver", response_model=VehicleResponse)
def assign_driver_spec_alias(
    vehicle_id: str,
    driver_uuid: str,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    """POST /vehicles/{vehicle_id}/assgn-driver – spec path (typo); same as assign-driver."""
    return assign_driver(vehicle_id, driver_uuid, db, current)
