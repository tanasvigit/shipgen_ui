from typing import List, Optional, Any
import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.api.v1.routers.auth import _get_current_user
from app.core.database import get_db
from app.models.storefront_product_variant import StorefrontProductVariant
from app.models.user import User

router = APIRouter(prefix="/int/v1/product-variants", tags=["int-storefront-product-variants"])


class ProductVariantCreate(BaseModel):
    product_uuid: str
    name: str
    description: Optional[str] = None
    translations: Optional[dict[str, Any]] = None
    meta: Optional[dict[str, Any]] = None
    is_multiselect: bool = False
    is_required: bool = False
    min: int = 0
    max: int = 1


class ProductVariantUpdate(BaseModel):
    product_uuid: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    translations: Optional[dict[str, Any]] = None
    meta: Optional[dict[str, Any]] = None
    is_multiselect: Optional[bool] = None
    is_required: Optional[bool] = None
    min: Optional[int] = None
    max: Optional[int] = None


@router.get("/", response_model=List[dict])
def list_product_variants(
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    variants = db.query(StorefrontProductVariant).filter(
        StorefrontProductVariant.deleted_at.is_(None)
    ).offset(offset).limit(limit).all()
    return [v.__dict__ for v in variants]


@router.get("/{id}", response_model=dict)
def get_product_variant(
    id: str,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    variant = db.query(StorefrontProductVariant).filter(
        (StorefrontProductVariant.uuid == id) | (StorefrontProductVariant.public_id == id),
        StorefrontProductVariant.deleted_at.is_(None)
    ).first()
    if not variant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product variant not found")
    return variant.__dict__


@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED)
def create_product_variant(
    payload: ProductVariantCreate,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    variant = StorefrontProductVariant()
    variant.uuid = str(uuid.uuid4())
    variant.product_uuid = payload.product_uuid
    variant.name = payload.name
    variant.description = payload.description
    variant.translations = payload.translations
    variant.meta = payload.meta
    variant.is_multiselect = payload.is_multiselect
    variant.is_required = payload.is_required
    variant.min = payload.min
    variant.max = payload.max
    
    db.add(variant)
    db.commit()
    db.refresh(variant)
    return variant.__dict__


@router.put("/{id}", response_model=dict)
@router.patch("/{id}", response_model=dict)
def update_product_variant(
    id: str,
    payload: ProductVariantUpdate,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    variant = db.query(StorefrontProductVariant).filter(
        (StorefrontProductVariant.uuid == id) | (StorefrontProductVariant.public_id == id),
        StorefrontProductVariant.deleted_at.is_(None)
    ).first()
    if not variant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product variant not found")
    
    for field, value in payload.dict(exclude_unset=True).items():
        if hasattr(variant, field):
            setattr(variant, field, value)
    
    db.add(variant)
    db.commit()
    db.refresh(variant)
    return variant.__dict__


@router.delete("/{id}", status_code=status.HTTP_200_OK)
def delete_product_variant(
    id: str,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    variant = db.query(StorefrontProductVariant).filter(
        (StorefrontProductVariant.uuid == id) | (StorefrontProductVariant.public_id == id),
        StorefrontProductVariant.deleted_at.is_(None)
    ).first()
    if not variant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product variant not found")
    
    variant.deleted_at = datetime.utcnow()
    db.add(variant)
    db.commit()
    return variant.__dict__

