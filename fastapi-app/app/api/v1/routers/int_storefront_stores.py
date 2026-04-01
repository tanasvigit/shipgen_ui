from typing import Any, Dict, List, Optional
import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.api.v1.routers.auth import _get_current_user
from app.core.database import get_db
from app.models.storefront_store import StorefrontStore
from app.models.user import User

router = APIRouter(prefix="/int/v1/stores", tags=["int-storefront-stores"])


class StoreCreate(BaseModel):
    name: str
    description: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None
    facebook: Optional[str] = None
    instagram: Optional[str] = None
    twitter: Optional[str] = None
    tags: Optional[list[str]] = None
    currency: Optional[str] = None
    timezone: Optional[str] = None
    options: Optional[dict[str, Any]] = None
    meta: Optional[dict[str, Any]] = None
    online: Optional[bool] = True


class StoreUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None
    facebook: Optional[str] = None
    instagram: Optional[str] = None
    twitter: Optional[str] = None
    tags: Optional[list[str]] = None
    currency: Optional[str] = None
    timezone: Optional[str] = None
    options: Optional[dict[str, Any]] = None
    meta: Optional[dict[str, Any]] = None
    online: Optional[bool] = None


@router.get("/", response_model=List[dict])
def list_stores(
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    q = db.query(StorefrontStore).filter(StorefrontStore.company_uuid == current.company_uuid, StorefrontStore.deleted_at.is_(None))
    stores = q.offset(offset).limit(limit).all()
    return [store.__dict__ for store in stores]


@router.get("/{id}", response_model=dict)
def get_store(
    id: str,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    store = (
        db.query(StorefrontStore)
        .filter(StorefrontStore.company_uuid == current.company_uuid, (StorefrontStore.uuid == id) | (StorefrontStore.public_id == id))
        .first()
    )
    if not store:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Store not found.")
    return store.__dict__


@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED)
def create_store(
    payload: StoreCreate,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    store = StorefrontStore()
    store.uuid = str(uuid.uuid4())
    store.company_uuid = current.company_uuid
    store.created_by_uuid = current.uuid
    store.name = payload.name
    store.description = payload.description
    store.phone = payload.phone
    store.email = payload.email
    store.website = payload.website
    store.facebook = payload.facebook
    store.instagram = payload.instagram
    store.twitter = payload.twitter
    store.tags = payload.tags
    store.currency = payload.currency
    store.timezone = payload.timezone
    store.options = payload.options
    store.meta = payload.meta
    store.online = payload.online
    
    db.add(store)
    db.commit()
    db.refresh(store)
    return store.__dict__


@router.put("/{id}", response_model=dict)
@router.patch("/{id}", response_model=dict)
def update_store(
    id: str,
    payload: StoreUpdate,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    store = (
        db.query(StorefrontStore)
        .filter(StorefrontStore.company_uuid == current.company_uuid, (StorefrontStore.uuid == id) | (StorefrontStore.public_id == id))
        .first()
    )
    if not store:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Store not found.")
    
    for field, value in payload.dict(exclude_unset=True).items():
        if hasattr(store, field):
            setattr(store, field, value)
    
    db.add(store)
    db.commit()
    db.refresh(store)
    return store.__dict__


@router.delete("/{id}", status_code=status.HTTP_200_OK)
def delete_store(
    id: str,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    store = (
        db.query(StorefrontStore)
        .filter(StorefrontStore.company_uuid == current.company_uuid, (StorefrontStore.uuid == id) | (StorefrontStore.public_id == id))
        .first()
    )
    if not store:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Store not found.")
    
    store.deleted_at = datetime.utcnow()
    db.add(store)
    db.commit()
    return store.__dict__

