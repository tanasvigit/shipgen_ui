from typing import List, Optional
import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.api.v1.routers.auth import _get_current_user
from app.core.database import get_db
from app.models.storefront_store_location import StorefrontStoreLocation
from app.models.user import User

router = APIRouter(prefix="/int/v1/store-locations", tags=["int-storefront-store-locations"])


class StoreLocationCreate(BaseModel):
    store_uuid: str
    place_uuid: Optional[str] = None
    name: Optional[str] = None


class StoreLocationUpdate(BaseModel):
    store_uuid: Optional[str] = None
    place_uuid: Optional[str] = None
    name: Optional[str] = None


@router.get("/", response_model=List[dict])
def list_store_locations(
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    locations = db.query(StorefrontStoreLocation).filter(
        StorefrontStoreLocation.deleted_at.is_(None)
    ).offset(offset).limit(limit).all()
    return [loc.__dict__ for loc in locations]


@router.get("/{id}", response_model=dict)
def get_store_location(
    id: str,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    location = db.query(StorefrontStoreLocation).filter(
        (StorefrontStoreLocation.uuid == id) | (StorefrontStoreLocation.public_id == id),
        StorefrontStoreLocation.deleted_at.is_(None)
    ).first()
    if not location:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Store location not found")
    return location.__dict__


@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED)
def create_store_location(
    payload: StoreLocationCreate,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    location = StorefrontStoreLocation()
    location.uuid = str(uuid.uuid4())
    location.created_by_uuid = current.uuid
    location.store_uuid = payload.store_uuid
    location.place_uuid = payload.place_uuid
    location.name = payload.name
    
    db.add(location)
    db.commit()
    db.refresh(location)
    return location.__dict__


@router.put("/{id}", response_model=dict)
@router.patch("/{id}", response_model=dict)
def update_store_location(
    id: str,
    payload: StoreLocationUpdate,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    location = db.query(StorefrontStoreLocation).filter(
        (StorefrontStoreLocation.uuid == id) | (StorefrontStoreLocation.public_id == id),
        StorefrontStoreLocation.deleted_at.is_(None)
    ).first()
    if not location:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Store location not found")
    
    for field, value in payload.dict(exclude_unset=True).items():
        if hasattr(location, field):
            setattr(location, field, value)
    
    db.add(location)
    db.commit()
    db.refresh(location)
    return location.__dict__


@router.delete("/{id}", status_code=status.HTTP_200_OK)
def delete_store_location(
    id: str,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    location = db.query(StorefrontStoreLocation).filter(
        (StorefrontStoreLocation.uuid == id) | (StorefrontStoreLocation.public_id == id),
        StorefrontStoreLocation.deleted_at.is_(None)
    ).first()
    if not location:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Store location not found")
    
    location.deleted_at = datetime.utcnow()
    db.add(location)
    db.commit()
    return location.__dict__

