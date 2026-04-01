from typing import List
import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.v1.routers.auth import _get_current_user
from app.core.database import get_db
from app.models.service_area import ServiceArea
from app.models.user import User
from app.schemas.service_area import ServiceAreaCreate, ServiceAreaOut, ServiceAreaUpdate, ServiceAreaResponse, ServiceAreasResponse

router = APIRouter(prefix="/fleetops/v1/service-areas", tags=["fleetops-service-areas"])


@router.get("/", response_model=ServiceAreasResponse)
def list_service_areas(
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    q = db.query(ServiceArea).filter(ServiceArea.company_uuid == current.company_uuid, ServiceArea.deleted_at.is_(None))
    areas = q.offset(offset).limit(limit).all()
    return {"service_areas": areas}


@router.get("/{id}", response_model=ServiceAreaResponse)
def get_service_area(
    id: str,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    area = (
        db.query(ServiceArea)
        .filter(ServiceArea.company_uuid == current.company_uuid, (ServiceArea.uuid == id) | (ServiceArea.public_id == id))
        .first()
    )
    if not area:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Service area not found.")
    return {"service_area": area}


@router.post("/", response_model=ServiceAreaResponse, status_code=status.HTTP_201_CREATED)
def create_service_area(
    payload: ServiceAreaCreate,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    area = ServiceArea()
    area.uuid = str(uuid.uuid4())
    area.public_id = f"service_area_{uuid.uuid4().hex[:12]}"
    area.company_uuid = current.company_uuid
    area.name = payload.name
    area.type = payload.type
    area.status = payload.status
    area.country = payload.country

    # Handle parent assignment
    if payload.parent:
        parent = (
            db.query(ServiceArea)
            .filter(ServiceArea.company_uuid == current.company_uuid, (ServiceArea.uuid == payload.parent) | (ServiceArea.public_id == payload.parent))
            .first()
        )
        if parent:
            area.parent_uuid = parent.uuid

    # Handle border creation from point and radius
    if not area.border and (payload.latitude and payload.longitude):
        radius = payload.radius or 500
        # Create a multipolygon representation (simplified)
        area.border = {
            "type": "MultiPolygon",
            "coordinates": [[[
                [payload.longitude - radius/111000, payload.latitude - radius/111000],
                [payload.longitude + radius/111000, payload.latitude - radius/111000],
                [payload.longitude + radius/111000, payload.latitude + radius/111000],
                [payload.longitude - radius/111000, payload.latitude + radius/111000],
                [payload.longitude - radius/111000, payload.latitude - radius/111000],
            ]]]
        }

    db.add(area)
    db.commit()
    db.refresh(area)
    return {"service_area": area}


@router.put("/{id}", response_model=ServiceAreaResponse)
def update_service_area(
    id: str,
    payload: ServiceAreaUpdate,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    area = (
        db.query(ServiceArea)
        .filter(ServiceArea.company_uuid == current.company_uuid, (ServiceArea.uuid == id) | (ServiceArea.public_id == id))
        .first()
    )
    if not area:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Service area not found.")

    for field, value in payload.dict(exclude_unset=True, exclude={"parent", "latitude", "longitude", "location", "radius"}).items():
        setattr(area, field, value)

    # Handle parent assignment
    if payload.parent:
        parent = (
            db.query(ServiceArea)
            .filter(ServiceArea.company_uuid == current.company_uuid, (ServiceArea.uuid == payload.parent) | (ServiceArea.public_id == payload.parent))
            .first()
        )
        if parent:
            area.parent_uuid = parent.uuid

    # Handle border update
    if (payload.latitude and payload.longitude) or payload.location:
        lat = payload.latitude
        lng = payload.longitude
        if payload.location and isinstance(payload.location, dict):
            lat = payload.location.get("latitude") or payload.location.get("lat")
            lng = payload.location.get("longitude") or payload.location.get("lng")
        
        if lat and lng:
            radius = payload.radius or 500
            area.border = {
                "type": "MultiPolygon",
                "coordinates": [[[
                    [lng - radius/111000, lat - radius/111000],
                    [lng + radius/111000, lat - radius/111000],
                    [lng + radius/111000, lat + radius/111000],
                    [lng - radius/111000, lat + radius/111000],
                    [lng - radius/111000, lat - radius/111000],
                ]]]
            }

    db.add(area)
    db.commit()
    db.refresh(area)
    return {"service_area": area}


@router.delete("/{id}", response_model=ServiceAreaResponse)
def delete_service_area(
    id: str,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    area = (
        db.query(ServiceArea)
        .filter(ServiceArea.company_uuid == current.company_uuid, (ServiceArea.uuid == id) | (ServiceArea.public_id == id))
        .first()
    )
    if not area:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Service area not found.")

    area.deleted_at = datetime.utcnow()
    db.add(area)
    db.commit()
    return {"service_area": area}

