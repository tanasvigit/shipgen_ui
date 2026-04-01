from typing import List, Optional, Any
import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.api.v1.routers.auth import _get_current_user
from app.core.database import get_db
from app.models.storefront_catalog import StorefrontCatalog
from app.models.user import User

router = APIRouter(prefix="/int/v1/catalogs", tags=["int-storefront-catalogs"])


class CatalogCreate(BaseModel):
    store_uuid: Optional[str] = None
    name: str
    description: Optional[str] = None
    status: str = "draft"
    meta: Optional[dict[str, Any]] = None


class CatalogUpdate(BaseModel):
    store_uuid: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    meta: Optional[dict[str, Any]] = None


@router.get("/", response_model=List[dict])
def list_catalogs(
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    catalogs = db.query(StorefrontCatalog).filter(
        StorefrontCatalog.company_uuid == current.company_uuid,
        StorefrontCatalog.deleted_at.is_(None)
    ).offset(offset).limit(limit).all()
    return [cat.__dict__ for cat in catalogs]


@router.get("/{id}", response_model=dict)
def get_catalog(
    id: str,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    catalog = db.query(StorefrontCatalog).filter(
        StorefrontCatalog.company_uuid == current.company_uuid,
        (StorefrontCatalog.uuid == id) | (StorefrontCatalog.public_id == id),
        StorefrontCatalog.deleted_at.is_(None)
    ).first()
    if not catalog:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Catalog not found")
    return catalog.__dict__


@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED)
def create_catalog(
    payload: CatalogCreate,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    catalog = StorefrontCatalog()
    catalog.uuid = str(uuid.uuid4())
    catalog.company_uuid = current.company_uuid
    catalog.created_by_uuid = current.uuid
    catalog.store_uuid = payload.store_uuid
    catalog.name = payload.name
    catalog.description = payload.description
    catalog.status = payload.status
    catalog.meta = payload.meta
    
    db.add(catalog)
    db.commit()
    db.refresh(catalog)
    return catalog.__dict__


@router.put("/{id}", response_model=dict)
@router.patch("/{id}", response_model=dict)
def update_catalog(
    id: str,
    payload: CatalogUpdate,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    catalog = db.query(StorefrontCatalog).filter(
        StorefrontCatalog.company_uuid == current.company_uuid,
        (StorefrontCatalog.uuid == id) | (StorefrontCatalog.public_id == id),
        StorefrontCatalog.deleted_at.is_(None)
    ).first()
    if not catalog:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Catalog not found")
    
    for field, value in payload.dict(exclude_unset=True).items():
        if hasattr(catalog, field):
            setattr(catalog, field, value)
    
    db.add(catalog)
    db.commit()
    db.refresh(catalog)
    return catalog.__dict__


@router.delete("/{id}", status_code=status.HTTP_200_OK)
def delete_catalog(
    id: str,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    catalog = db.query(StorefrontCatalog).filter(
        StorefrontCatalog.company_uuid == current.company_uuid,
        (StorefrontCatalog.uuid == id) | (StorefrontCatalog.public_id == id),
        StorefrontCatalog.deleted_at.is_(None)
    ).first()
    if not catalog:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Catalog not found")
    
    catalog.deleted_at = datetime.utcnow()
    db.add(catalog)
    db.commit()
    return catalog.__dict__

