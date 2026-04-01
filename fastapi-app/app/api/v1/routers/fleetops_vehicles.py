import uuid
from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.v1.routers.auth import _get_current_user
from app.core.database import get_db
from app.models.driver import Driver
from app.models.user import User
from app.models.vehicle import Vehicle
from app.schemas.vehicle import VehicleCreate, VehicleOut, VehicleUpdate, VehicleResponse, VehiclesResponse

router = APIRouter(prefix="/fleetops/v1/vehicles", tags=["fleetops-vehicles"])


@router.get("/", response_model=VehiclesResponse)
def list_vehicles(
    db: Session = Depends(get_db),
    _current: User = Depends(_get_current_user),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    status_filter: str | None = Query(None, alias="status"),
):
    query = db.query(Vehicle).filter(Vehicle.deleted_at.is_(None))
    if status_filter:
        query = query.filter(Vehicle.status == status_filter)
    vehicles = query.offset(offset).limit(limit).all()
    return {"vehicles": vehicles}


@router.get("/{vehicle_id}", response_model=VehicleResponse)
def get_vehicle(
    vehicle_id: str,
    db: Session = Depends(get_db),
    _current: User = Depends(_get_current_user),
):
    vehicle = db.query(Vehicle).filter(Vehicle.uuid == vehicle_id).first()
    if not vehicle:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vehicle not found.")
    return {"vehicle": vehicle}


@router.post("/", response_model=VehicleResponse, status_code=status.HTTP_201_CREATED)
def create_vehicle(
    payload: VehicleCreate,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    vehicle = Vehicle()
    vehicle.uuid = str(uuid.uuid4())
    vehicle.public_id = f"vehicle_{uuid.uuid4().hex[:12]}"
    vehicle.company_uuid = payload.company_uuid or current.company_uuid
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

    return {"vehicle": vehicle}


@router.put("/{vehicle_id}", response_model=VehicleResponse)
@router.patch("/{vehicle_id}", response_model=VehicleResponse)
def update_vehicle(
    vehicle_id: str,
    payload: VehicleUpdate,
    db: Session = Depends(get_db),
    _current: User = Depends(_get_current_user),
):
    vehicle = db.query(Vehicle).filter(Vehicle.uuid == vehicle_id).first()
    if not vehicle:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vehicle not found.")

    for field, value in payload.dict(exclude_unset=True).items():
        setattr(vehicle, field, value)

    db.add(vehicle)
    db.commit()
    db.refresh(vehicle)

    return {"vehicle": vehicle}


@router.delete("/{vehicle_id}", response_model=VehicleResponse)
def delete_vehicle(
    vehicle_id: str,
    db: Session = Depends(get_db),
    _current: User = Depends(_get_current_user),
):
    vehicle = db.query(Vehicle).filter(Vehicle.uuid == vehicle_id).first()
    if not vehicle:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vehicle not found.")

    vehicle.deleted_at = datetime.utcnow()
    db.add(vehicle)
    db.commit()
    return {"vehicle": vehicle}


@router.post("/{vehicle_id}/track", response_model=VehicleResponse)
def track_vehicle(
    vehicle_id: str,
    latitude: float | None = None,
    longitude: float | None = None,
    altitude: float | None = None,
    heading: float | None = None,
    speed: float | None = None,
    db: Session = Depends(get_db),
    _current: User = Depends(_get_current_user),
):
    vehicle = db.query(Vehicle).filter(Vehicle.uuid == vehicle_id).first()
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
    return {"vehicle": vehicle}


@router.post("/{vehicle_id}/assign-driver", response_model=VehicleResponse)
def assign_driver(
    vehicle_id: str,
    driver_uuid: str,
    db: Session = Depends(get_db),
    _current: User = Depends(_get_current_user),
):
    """Assign a driver to this vehicle by linking driver.vehicle_uuid."""
    vehicle = db.query(Vehicle).filter(Vehicle.uuid == vehicle_id).first()
    if not vehicle:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vehicle not found.")

    driver = db.query(Driver).filter(Driver.uuid == driver_uuid).first()
    if not driver:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Driver not found.")

    driver.vehicle_uuid = vehicle.uuid
    db.add(driver)
    db.commit()
    db.refresh(vehicle)

    return {"vehicle": vehicle}


@router.post("/{vehicle_id}/assgn-driver", response_model=VehicleResponse)
def assign_driver_spec_alias(
    vehicle_id: str,
    driver_uuid: str,
    db: Session = Depends(get_db),
    _current: User = Depends(_get_current_user),
):
    """POST /vehicles/{vehicle_id}/assgn-driver – spec path (typo); same as assign-driver."""
    return assign_driver(vehicle_id, driver_uuid, db, _current)





