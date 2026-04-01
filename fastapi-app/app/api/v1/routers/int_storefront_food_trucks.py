from typing import List, Optional, Any
import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.api.v1.routers.auth import _get_current_user
from app.core.database import get_db
from app.models.storefront_food_truck import StorefrontFoodTruck
from app.models.user import User

router = APIRouter(prefix="/int/v1/food-trucks", tags=["int-storefront-food-trucks"])


class FoodTruckCreate(BaseModel):
    store_uuid: str
    name: str
    description: Optional[str] = None
    meta: Optional[dict[str, Any]] = None


class FoodTruckUpdate(BaseModel):
    store_uuid: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    meta: Optional[dict[str, Any]] = None


@router.get("/", response_model=List[dict])
def list_food_trucks(
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    food_trucks = db.query(StorefrontFoodTruck).filter(
        StorefrontFoodTruck.company_uuid == current.company_uuid,
        StorefrontFoodTruck.deleted_at.is_(None)
    ).offset(offset).limit(limit).all()
    return [ft.__dict__ for ft in food_trucks]


@router.get("/{id}", response_model=dict)
def get_food_truck(
    id: str,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    food_truck = db.query(StorefrontFoodTruck).filter(
        StorefrontFoodTruck.company_uuid == current.company_uuid,
        (StorefrontFoodTruck.uuid == id) | (StorefrontFoodTruck.public_id == id),
        StorefrontFoodTruck.deleted_at.is_(None)
    ).first()
    if not food_truck:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Food truck not found")
    return food_truck.__dict__


@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED)
def create_food_truck(
    payload: FoodTruckCreate,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    food_truck = StorefrontFoodTruck()
    food_truck.uuid = str(uuid.uuid4())
    food_truck.company_uuid = current.company_uuid
    food_truck.created_by_uuid = current.uuid
    food_truck.store_uuid = payload.store_uuid
    food_truck.name = payload.name
    food_truck.description = payload.description
    food_truck.meta = payload.meta
    
    db.add(food_truck)
    db.commit()
    db.refresh(food_truck)
    return food_truck.__dict__


@router.put("/{id}", response_model=dict)
@router.patch("/{id}", response_model=dict)
def update_food_truck(
    id: str,
    payload: FoodTruckUpdate,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    food_truck = db.query(StorefrontFoodTruck).filter(
        StorefrontFoodTruck.company_uuid == current.company_uuid,
        (StorefrontFoodTruck.uuid == id) | (StorefrontFoodTruck.public_id == id),
        StorefrontFoodTruck.deleted_at.is_(None)
    ).first()
    if not food_truck:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Food truck not found")
    
    for field, value in payload.dict(exclude_unset=True).items():
        if hasattr(food_truck, field):
            setattr(food_truck, field, value)
    
    db.add(food_truck)
    db.commit()
    db.refresh(food_truck)
    return food_truck.__dict__


@router.delete("/{id}", status_code=status.HTTP_200_OK)
def delete_food_truck(
    id: str,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    food_truck = db.query(StorefrontFoodTruck).filter(
        StorefrontFoodTruck.company_uuid == current.company_uuid,
        (StorefrontFoodTruck.uuid == id) | (StorefrontFoodTruck.public_id == id),
        StorefrontFoodTruck.deleted_at.is_(None)
    ).first()
    if not food_truck:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Food truck not found")
    
    food_truck.deleted_at = datetime.utcnow()
    db.add(food_truck)
    db.commit()
    return food_truck.__dict__

