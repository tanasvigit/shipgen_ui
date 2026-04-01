from typing import List
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.v1.routers.auth import _get_current_user
from app.core.database import get_db
from app.models.storefront_food_truck import StorefrontFoodTruck
from app.models.user import User
from app.schemas.storefront_food_truck import FoodTruckOut

router = APIRouter(prefix="/storefront/v1/food-trucks", tags=["storefront-food-trucks"])


@router.get("/", response_model=List[FoodTruckOut])
def list_food_trucks(
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
    limit: int = Query(None, ge=1, le=100),
    offset: int = Query(None, ge=0),
):
    # Get storefront_store from session (simplified)
    query = db.query(StorefrontFoodTruck).filter(StorefrontFoodTruck.company_uuid == current.company_uuid)
    
    if limit:
        query = query.limit(limit)
    if offset:
        query = query.offset(offset)
    
    trucks = query.all()
    return trucks


@router.get("/{id}", response_model=FoodTruckOut)
def get_food_truck(
    id: str,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    truck = (
        db.query(StorefrontFoodTruck)
        .filter(StorefrontFoodTruck.company_uuid == current.company_uuid, (StorefrontFoodTruck.uuid == id) | (StorefrontFoodTruck.public_id == id))
        .first()
    )
    if not truck:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Food truck not found.")
    return truck

