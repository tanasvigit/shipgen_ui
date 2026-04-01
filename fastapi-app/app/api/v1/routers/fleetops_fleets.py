from typing import List
import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.v1.routers.auth import _get_current_user
from app.core.database import get_db
from app.models.fleet import Fleet
from app.models.service_area import ServiceArea
from app.models.user import User
from app.schemas.fleet import FleetCreate, FleetOut, FleetUpdate, FleetResponse, FleetsResponse

router = APIRouter(prefix="/fleetops/v1/fleets", tags=["fleetops-fleets"])


@router.get("/", response_model=FleetsResponse)
def list_fleets(
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    q = db.query(Fleet).filter(Fleet.company_uuid == current.company_uuid, Fleet.deleted_at.is_(None))
    fleets = q.offset(offset).limit(limit).all()
    return {"fleets": fleets}


@router.get("/{id}", response_model=FleetResponse)
def get_fleet(
    id: str,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    fleet = (
        db.query(Fleet)
        .filter(Fleet.company_uuid == current.company_uuid, (Fleet.uuid == id) | (Fleet.public_id == id))
        .first()
    )
    if not fleet:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Fleet not found.")
    return {"fleet": fleet}


@router.post("/", response_model=FleetResponse, status_code=status.HTTP_201_CREATED)
def create_fleet(
    payload: FleetCreate,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    fleet = Fleet()
    fleet.uuid = str(uuid.uuid4())
    fleet.public_id = f"fleet_{uuid.uuid4().hex[:12]}"
    fleet.company_uuid = current.company_uuid
    fleet.name = payload.name
    fleet.color = payload.color
    fleet.task = payload.task
    fleet.status = payload.status

    # Handle service area assignment
    if payload.service_area:
        service_area = (
            db.query(ServiceArea)
            .filter(ServiceArea.company_uuid == current.company_uuid, (ServiceArea.uuid == payload.service_area) | (ServiceArea.public_id == payload.service_area))
            .first()
        )
        if service_area:
            fleet.service_area_uuid = service_area.uuid

    db.add(fleet)
    db.commit()
    db.refresh(fleet)
    return {"fleet": fleet}


@router.put("/{id}", response_model=FleetResponse)
def update_fleet(
    id: str,
    payload: FleetUpdate,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    fleet = (
        db.query(Fleet)
        .filter(Fleet.company_uuid == current.company_uuid, (Fleet.uuid == id) | (Fleet.public_id == id))
        .first()
    )
    if not fleet:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Fleet not found.")

    for field, value in payload.dict(exclude_unset=True, exclude={"service_area"}).items():
        setattr(fleet, field, value)

    # Handle service area assignment
    if payload.service_area:
        service_area = (
            db.query(ServiceArea)
            .filter(ServiceArea.company_uuid == current.company_uuid, (ServiceArea.uuid == payload.service_area) | (ServiceArea.public_id == payload.service_area))
            .first()
        )
        if service_area:
            fleet.service_area_uuid = service_area.uuid

    db.add(fleet)
    db.commit()
    db.refresh(fleet)
    return {"fleet": fleet}


@router.delete("/{id}", response_model=FleetResponse)
def delete_fleet(
    id: str,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    fleet = (
        db.query(Fleet)
        .filter(Fleet.company_uuid == current.company_uuid, (Fleet.uuid == id) | (Fleet.public_id == id))
        .first()
    )
    if not fleet:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Fleet not found.")

    fleet.deleted_at = datetime.utcnow()
    db.add(fleet)
    db.commit()
    return {"fleet": fleet}

