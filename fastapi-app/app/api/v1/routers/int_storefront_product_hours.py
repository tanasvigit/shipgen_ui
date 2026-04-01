from typing import List, Optional
import uuid
from datetime import datetime, time

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.api.v1.routers.auth import _get_current_user
from app.core.database import get_db
from app.models.storefront_product_hour import StorefrontProductHour
from app.models.user import User

router = APIRouter(prefix="/int/v1/product-hours", tags=["int-storefront-product-hours"])


class ProductHourCreate(BaseModel):
    product_uuid: str
    day_of_week: Optional[str] = None
    start: time
    end: time


class ProductHourUpdate(BaseModel):
    product_uuid: Optional[str] = None
    day_of_week: Optional[str] = None
    start: Optional[time] = None
    end: Optional[time] = None


@router.get("/", response_model=List[dict])
def list_product_hours(
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    product_hours = db.query(StorefrontProductHour).filter(
        StorefrontProductHour.deleted_at.is_(None)
    ).offset(offset).limit(limit).all()
    return [ph.__dict__ for ph in product_hours]


@router.get("/{id}", response_model=dict)
def get_product_hour(
    id: str,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    product_hour = db.query(StorefrontProductHour).filter(
        (StorefrontProductHour.uuid == id) | (StorefrontProductHour.id == int(id) if id.isdigit() else False),
        StorefrontProductHour.deleted_at.is_(None)
    ).first()
    if not product_hour:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product hour not found")
    return product_hour.__dict__


@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED)
def create_product_hour(
    payload: ProductHourCreate,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    product_hour = StorefrontProductHour()
    product_hour.uuid = str(uuid.uuid4())
    product_hour.product_uuid = payload.product_uuid
    product_hour.day_of_week = payload.day_of_week
    product_hour.start = payload.start
    product_hour.end = payload.end
    
    db.add(product_hour)
    db.commit()
    db.refresh(product_hour)
    return product_hour.__dict__


@router.put("/{id}", response_model=dict)
@router.patch("/{id}", response_model=dict)
def update_product_hour(
    id: str,
    payload: ProductHourUpdate,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    product_hour = db.query(StorefrontProductHour).filter(
        (StorefrontProductHour.uuid == id) | (StorefrontProductHour.id == int(id) if id.isdigit() else False),
        StorefrontProductHour.deleted_at.is_(None)
    ).first()
    if not product_hour:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product hour not found")
    
    for field, value in payload.dict(exclude_unset=True).items():
        if hasattr(product_hour, field):
            setattr(product_hour, field, value)
    
    db.add(product_hour)
    db.commit()
    db.refresh(product_hour)
    return product_hour.__dict__


@router.delete("/{id}", status_code=status.HTTP_200_OK)
def delete_product_hour(
    id: str,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    product_hour = db.query(StorefrontProductHour).filter(
        (StorefrontProductHour.uuid == id) | (StorefrontProductHour.id == int(id) if id.isdigit() else False),
        StorefrontProductHour.deleted_at.is_(None)
    ).first()
    if not product_hour:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product hour not found")
    
    product_hour.deleted_at = datetime.utcnow()
    db.add(product_hour)
    db.commit()
    return product_hour.__dict__

