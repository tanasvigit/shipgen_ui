from typing import List
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.v1.routers.auth import _get_current_user
from app.core.database import get_db
from app.models.place import Place
from app.models.user import User
from app.schemas.place import PlaceCreate, PlaceOut, PlaceUpdate, PlaceResponse, PlacesResponse

router = APIRouter(prefix="/fleetops/v1/places", tags=["fleetops-places"])


@router.get("/", response_model=PlacesResponse)
def list_places(
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    q = db.query(Place).filter(Place.company_uuid == current.company_uuid, Place.deleted_at.is_(None))
    places = q.offset(offset).limit(limit).all()
    return {"places": places}


@router.get("/{id}", response_model=PlaceResponse)
def get_place(
    id: str,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    place = (
        db.query(Place)
        .filter(Place.company_uuid == current.company_uuid, (Place.uuid == id) | (Place.public_id == id))
        .first()
    )
    if not place:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Place not found.")
    return {"place": place}


@router.post("/", response_model=PlaceResponse, status_code=status.HTTP_201_CREATED)
def create_place(
    payload: PlaceCreate,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    place = Place()
    place.uuid = str(uuid.uuid4())
    place.public_id = f"place_{uuid.uuid4().hex[:12]}"
    place.company_uuid = current.company_uuid
    place.name = payload.name
    place.street1 = payload.street1
    place.street2 = payload.street2
    place.city = payload.city
    place.province = payload.province
    place.postal_code = payload.postal_code
    place.country = payload.country
    place.latitude = payload.latitude
    place.longitude = payload.longitude
    place.phone = payload.phone
    place.type = payload.type
    place.meta = payload.meta

    db.add(place)
    db.commit()
    db.refresh(place)
    return {"place": place}


@router.put("/{id}", response_model=PlaceResponse)
@router.patch("/{id}", response_model=PlaceResponse)
def update_place(
    id: str,
    payload: PlaceUpdate,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    place = (
        db.query(Place)
        .filter(Place.company_uuid == current.company_uuid, (Place.uuid == id) | (Place.public_id == id))
        .first()
    )
    if not place:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Place not found.")

    for field, value in payload.dict(exclude_unset=True).items():
        setattr(place, field, value)

    db.add(place)
    db.commit()
    db.refresh(place)
    return {"place": place}


@router.delete("/{id}", response_model=PlaceResponse)
def delete_place(
    id: str,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    place = (
        db.query(Place)
        .filter(Place.company_uuid == current.company_uuid, (Place.uuid == id) | (Place.public_id == id))
        .first()
    )
    if not place:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Place not found.")

    place.deleted_at = datetime.utcnow()
    db.add(place)
    db.commit()
    return {"place": place}



