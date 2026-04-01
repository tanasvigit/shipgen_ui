from typing import List
import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.v1.routers.auth import _get_current_user
from app.core.database import get_db
from app.models.zone import Zone
from app.models.service_area import ServiceArea
from app.models.user import User
from app.schemas.zone import ZoneCreate, ZoneOut, ZoneUpdate, ZoneResponse, ZonesResponse

router = APIRouter(prefix="/fleetops/v1/zones", tags=["fleetops-zones"])


@router.get("/", response_model=ZonesResponse)
def list_zones(
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    q = db.query(Zone).filter(Zone.company_uuid == current.company_uuid, Zone.deleted_at.is_(None))
    zones = q.offset(offset).limit(limit).all()
    return {"zones": zones}


@router.get("/{id}", response_model=ZoneResponse)
def get_zone(
    id: str,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    zone = (
        db.query(Zone)
        .filter(Zone.company_uuid == current.company_uuid, (Zone.uuid == id) | (Zone.public_id == id))
        .first()
    )
    if not zone:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Zone not found.")
    return {"zone": zone}


@router.post("/", response_model=ZoneResponse, status_code=status.HTTP_201_CREATED)
def create_zone(
    payload: ZoneCreate,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    zone = Zone()
    zone.uuid = str(uuid.uuid4())
    zone.public_id = f"zone_{uuid.uuid4().hex[:12]}"
    zone.company_uuid = current.company_uuid
    zone.name = payload.name
    zone.description = payload.description
    zone.border = payload.border
    zone.status = payload.status
    zone.color = payload.color
    zone.stroke_color = payload.stroke_color

    # Handle service area assignment
    if payload.service_area:
        service_area = (
            db.query(ServiceArea)
            .filter(ServiceArea.company_uuid == current.company_uuid, (ServiceArea.uuid == payload.service_area) | (ServiceArea.public_id == payload.service_area))
            .first()
        )
        if service_area:
            zone.service_area_uuid = service_area.uuid

    # Handle border creation from point and radius
    # Note: In a full implementation, you'd create a polygon from the point and radius
    # For now, we'll store the border if provided, or create a simple representation
    if not zone.border and (payload.latitude and payload.longitude):
        # Create a simple polygon representation (simplified)
        radius = payload.radius or 500
        # In production, you'd use a proper geospatial library to create the polygon
        zone.border = {
            "type": "Polygon",
            "coordinates": [[
                [payload.longitude - radius/111000, payload.latitude - radius/111000],
                [payload.longitude + radius/111000, payload.latitude - radius/111000],
                [payload.longitude + radius/111000, payload.latitude + radius/111000],
                [payload.longitude - radius/111000, payload.latitude + radius/111000],
                [payload.longitude - radius/111000, payload.latitude - radius/111000],
            ]]
        }

    db.add(zone)
    db.commit()
    db.refresh(zone)
    return {"zone": zone}


@router.put("/{id}", response_model=ZoneResponse)
def update_zone(
    id: str,
    payload: ZoneUpdate,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    zone = (
        db.query(Zone)
        .filter(Zone.company_uuid == current.company_uuid, (Zone.uuid == id) | (Zone.public_id == id))
        .first()
    )
    if not zone:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Zone not found.")

    for field, value in payload.dict(exclude_unset=True, exclude={"service_area", "latitude", "longitude", "location", "radius"}).items():
        setattr(zone, field, value)

    # Handle service area assignment
    if payload.service_area:
        service_area = (
            db.query(ServiceArea)
            .filter(ServiceArea.company_uuid == current.company_uuid, (ServiceArea.uuid == payload.service_area) | (ServiceArea.public_id == payload.service_area))
            .first()
        )
        if service_area:
            zone.service_area_uuid = service_area.uuid

    # Handle border update from point and radius
    if (payload.latitude and payload.longitude) or payload.location:
        lat = payload.latitude
        lng = payload.longitude
        if payload.location and isinstance(payload.location, dict):
            lat = payload.location.get("latitude") or payload.location.get("lat")
            lng = payload.location.get("longitude") or payload.location.get("lng")
        
        if lat and lng:
            radius = payload.radius or 500
            zone.border = {
                "type": "Polygon",
                "coordinates": [[
                    [lng - radius/111000, lat - radius/111000],
                    [lng + radius/111000, lat - radius/111000],
                    [lng + radius/111000, lat + radius/111000],
                    [lng - radius/111000, lat + radius/111000],
                    [lng - radius/111000, lat - radius/111000],
                ]]
            }

    db.add(zone)
    db.commit()
    db.refresh(zone)
    return {"zone": zone}


@router.delete("/{id}", response_model=ZoneResponse)
def delete_zone(
    id: str,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    zone = (
        db.query(Zone)
        .filter(Zone.company_uuid == current.company_uuid, (Zone.uuid == id) | (Zone.public_id == id))
        .first()
    )
    if not zone:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Zone not found.")

    zone.deleted_at = datetime.utcnow()
    db.add(zone)
    db.commit()
    return {"zone": zone}

