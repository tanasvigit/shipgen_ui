from typing import List, Optional
import uuid
from datetime import datetime, time

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.api.v1.routers.auth import _get_current_user
from app.core.database import get_db
from app.models.storefront_catalog_hour import StorefrontCatalogHour
from app.models.user import User

router = APIRouter(prefix="/int/v1/catalog-hours", tags=["int-storefront-catalog-hours"])


class CatalogHourCreate(BaseModel):
    catalog_uuid: str
    day_of_week: str
    start: Optional[time] = None
    end: Optional[time] = None


class CatalogHourUpdate(BaseModel):
    catalog_uuid: Optional[str] = None
    day_of_week: Optional[str] = None
    start: Optional[time] = None
    end: Optional[time] = None


@router.get("/", response_model=List[dict])
def list_catalog_hours(
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    catalog_hours = db.query(StorefrontCatalogHour).filter(
        StorefrontCatalogHour.deleted_at.is_(None)
    ).offset(offset).limit(limit).all()
    return [ch.__dict__ for ch in catalog_hours]


@router.get("/{id}", response_model=dict)
def get_catalog_hour(
    id: str,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    catalog_hour = db.query(StorefrontCatalogHour).filter(
        (StorefrontCatalogHour.uuid == id) | (StorefrontCatalogHour.id == int(id) if id.isdigit() else False),
        StorefrontCatalogHour.deleted_at.is_(None)
    ).first()
    if not catalog_hour:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Catalog hour not found")
    return catalog_hour.__dict__


@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED)
def create_catalog_hour(
    payload: CatalogHourCreate,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    catalog_hour = StorefrontCatalogHour()
    catalog_hour.uuid = str(uuid.uuid4())
    catalog_hour.catalog_uuid = payload.catalog_uuid
    catalog_hour.day_of_week = payload.day_of_week
    catalog_hour.start = payload.start
    catalog_hour.end = payload.end
    
    db.add(catalog_hour)
    db.commit()
    db.refresh(catalog_hour)
    return catalog_hour.__dict__


@router.put("/{id}", response_model=dict)
@router.patch("/{id}", response_model=dict)
def update_catalog_hour(
    id: str,
    payload: CatalogHourUpdate,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    catalog_hour = db.query(StorefrontCatalogHour).filter(
        (StorefrontCatalogHour.uuid == id) | (StorefrontCatalogHour.id == int(id) if id.isdigit() else False),
        StorefrontCatalogHour.deleted_at.is_(None)
    ).first()
    if not catalog_hour:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Catalog hour not found")
    
    for field, value in payload.dict(exclude_unset=True).items():
        if hasattr(catalog_hour, field):
            setattr(catalog_hour, field, value)
    
    db.add(catalog_hour)
    db.commit()
    db.refresh(catalog_hour)
    return catalog_hour.__dict__


@router.delete("/{id}", status_code=status.HTTP_200_OK)
def delete_catalog_hour(
    id: str,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    catalog_hour = db.query(StorefrontCatalogHour).filter(
        (StorefrontCatalogHour.uuid == id) | (StorefrontCatalogHour.id == int(id) if id.isdigit() else False),
        StorefrontCatalogHour.deleted_at.is_(None)
    ).first()
    if not catalog_hour:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Catalog hour not found")
    
    catalog_hour.deleted_at = datetime.utcnow()
    db.add(catalog_hour)
    db.commit()
    return catalog_hour.__dict__

