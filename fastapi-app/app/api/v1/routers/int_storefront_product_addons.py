from typing import List, Optional, Any
import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.api.v1.routers.auth import _get_current_user
from app.core.database import get_db
from app.models.storefront_product_addon import StorefrontProductAddon
from app.models.user import User

router = APIRouter(prefix="/int/v1/product-addons", tags=["int-storefront-product-addons"])


class ProductAddonCreate(BaseModel):
    created_by_uuid: Optional[str] = None
    category_uuid: Optional[str] = None
    name: str
    description: Optional[str] = None
    translations: Optional[dict[str, Any]] = None
    price: int = 0
    sale_price: int = 0
    is_on_sale: bool = False


class ProductAddonUpdate(BaseModel):
    category_uuid: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    translations: Optional[dict[str, Any]] = None
    price: Optional[int] = None
    sale_price: Optional[int] = None
    is_on_sale: Optional[bool] = None


@router.get("/", response_model=List[dict])
def list_product_addons(
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    addons = db.query(StorefrontProductAddon).filter(
        StorefrontProductAddon.deleted_at.is_(None)
    ).offset(offset).limit(limit).all()
    return [addon.__dict__ for addon in addons]


@router.get("/{id}", response_model=dict)
def get_product_addon(
    id: str,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    addon = db.query(StorefrontProductAddon).filter(
        (StorefrontProductAddon.uuid == id) | (StorefrontProductAddon.public_id == id),
        StorefrontProductAddon.deleted_at.is_(None)
    ).first()
    if not addon:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product addon not found")
    return addon.__dict__


@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED)
def create_product_addon(
    payload: ProductAddonCreate,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    addon = StorefrontProductAddon()
    addon.uuid = str(uuid.uuid4())
    addon.created_by_uuid = payload.created_by_uuid or current.uuid
    addon.category_uuid = payload.category_uuid
    addon.name = payload.name
    addon.description = payload.description
    addon.translations = payload.translations
    addon.price = payload.price
    addon.sale_price = payload.sale_price
    addon.is_on_sale = payload.is_on_sale
    
    db.add(addon)
    db.commit()
    db.refresh(addon)
    return addon.__dict__


@router.put("/{id}", response_model=dict)
@router.patch("/{id}", response_model=dict)
def update_product_addon(
    id: str,
    payload: ProductAddonUpdate,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    addon = db.query(StorefrontProductAddon).filter(
        (StorefrontProductAddon.uuid == id) | (StorefrontProductAddon.public_id == id),
        StorefrontProductAddon.deleted_at.is_(None)
    ).first()
    if not addon:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product addon not found")
    
    for field, value in payload.dict(exclude_unset=True).items():
        if hasattr(addon, field):
            setattr(addon, field, value)
    
    db.add(addon)
    db.commit()
    db.refresh(addon)
    return addon.__dict__


@router.delete("/{id}", status_code=status.HTTP_200_OK)
def delete_product_addon(
    id: str,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    addon = db.query(StorefrontProductAddon).filter(
        (StorefrontProductAddon.uuid == id) | (StorefrontProductAddon.public_id == id),
        StorefrontProductAddon.deleted_at.is_(None)
    ).first()
    if not addon:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product addon not found")
    
    addon.deleted_at = datetime.utcnow()
    db.add(addon)
    db.commit()
    return addon.__dict__

