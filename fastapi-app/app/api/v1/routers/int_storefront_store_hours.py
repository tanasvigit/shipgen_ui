from typing import List, Optional
import uuid
from datetime import datetime, time

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.api.v1.routers.auth import _get_current_user
from app.core.database import get_db
from app.models.storefront_store_hour import StorefrontStoreHour
from app.models.user import User

router = APIRouter(prefix="/int/v1/store-hours", tags=["int-storefront-store-hours"])


class StoreHourCreate(BaseModel):
    store_location_uuid: str
    day_of_week: Optional[str] = None
    start: time
    end: time


class StoreHourUpdate(BaseModel):
    store_location_uuid: Optional[str] = None
    day_of_week: Optional[str] = None
    start: Optional[time] = None
    end: Optional[time] = None


@router.get("/", response_model=List[dict])
def list_store_hours(
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    store_hours = db.query(StorefrontStoreHour).filter(
        StorefrontStoreHour.deleted_at.is_(None)
    ).offset(offset).limit(limit).all()
    return [sh.__dict__ for sh in store_hours]


@router.get("/{id}", response_model=dict)
def get_store_hour(
    id: str,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    store_hour = db.query(StorefrontStoreHour).filter(
        (StorefrontStoreHour.uuid == id) | (StorefrontStoreHour.id == int(id) if id.isdigit() else False),
        StorefrontStoreHour.deleted_at.is_(None)
    ).first()
    if not store_hour:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Store hour not found")
    return store_hour.__dict__


@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED)
def create_store_hour(
    payload: StoreHourCreate,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    store_hour = StorefrontStoreHour()
    store_hour.uuid = str(uuid.uuid4())
    store_hour.store_location_uuid = payload.store_location_uuid
    store_hour.day_of_week = payload.day_of_week
    store_hour.start = payload.start
    store_hour.end = payload.end
    
    db.add(store_hour)
    db.commit()
    db.refresh(store_hour)
    return store_hour.__dict__


@router.put("/{id}", response_model=dict)
@router.patch("/{id}", response_model=dict)
def update_store_hour(
    id: str,
    payload: StoreHourUpdate,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    store_hour = db.query(StorefrontStoreHour).filter(
        (StorefrontStoreHour.uuid == id) | (StorefrontStoreHour.id == int(id) if id.isdigit() else False),
        StorefrontStoreHour.deleted_at.is_(None)
    ).first()
    if not store_hour:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Store hour not found")
    
    for field, value in payload.dict(exclude_unset=True).items():
        if hasattr(store_hour, field):
            setattr(store_hour, field, value)
    
    db.add(store_hour)
    db.commit()
    db.refresh(store_hour)
    return store_hour.__dict__


@router.delete("/{id}", status_code=status.HTTP_200_OK)
def delete_store_hour(
    id: str,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    store_hour = db.query(StorefrontStoreHour).filter(
        (StorefrontStoreHour.uuid == id) | (StorefrontStoreHour.id == int(id) if id.isdigit() else False),
        StorefrontStoreHour.deleted_at.is_(None)
    ).first()
    if not store_hour:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Store hour not found")
    
    store_hour.deleted_at = datetime.utcnow()
    db.add(store_hour)
    db.commit()
    return store_hour.__dict__

