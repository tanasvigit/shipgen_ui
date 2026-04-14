from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.roles import ADMIN, DISPATCHER, DRIVER, OPERATIONS_MANAGER, require_roles
from app.models.user import User
from app.schemas.trips_dispatch import (
    AssignTripOrderRequest,
    CompleteStopRequest,
    CreateTripRequest,
    StartTripRequest,
    TripsResponse,
    UpdateTripLocationRequest,
    TripResponse,
)
from app.services.trips_dispatch import (
    assign_order,
    complete_stop,
    create_trip,
    get_trip,
    list_trips,
    list_trip_events,
    start_trip,
    update_trip_location,
)

router = APIRouter(tags=["trips-dispatch"])


@router.get("/trips", response_model=TripsResponse)
def get_trips(
    db: Session = Depends(get_db),
    current: User = Depends(require_roles(ADMIN, OPERATIONS_MANAGER, DISPATCHER, DRIVER)),
):
    return {"trips": list_trips(db, current)}


@router.post("/trips", response_model=TripResponse, status_code=status.HTTP_201_CREATED)
def post_trip(
    payload: CreateTripRequest,
    db: Session = Depends(get_db),
    current: User = Depends(require_roles(ADMIN, OPERATIONS_MANAGER, DISPATCHER)),
):
    return {"trip": create_trip(db, current, payload)}


@router.post("/trips/{trip_id}/assign-order", response_model=TripResponse)
def post_assign_order(
    trip_id: str,
    payload: AssignTripOrderRequest,
    db: Session = Depends(get_db),
    current: User = Depends(require_roles(ADMIN, OPERATIONS_MANAGER, DISPATCHER)),
):
    return {"trip": assign_order(db, current, trip_id, payload)}


@router.post("/trips/{trip_id}/start", response_model=TripResponse)
def post_start_trip(
    trip_id: str,
    payload: StartTripRequest,
    db: Session = Depends(get_db),
    current: User = Depends(require_roles(ADMIN, OPERATIONS_MANAGER, DISPATCHER, DRIVER)),
):
    _ = payload
    return {"trip": start_trip(db, current, trip_id)}


@router.post("/trips/{trip_id}/complete-stop", response_model=TripResponse)
def post_complete_stop(
    trip_id: str,
    payload: CompleteStopRequest,
    db: Session = Depends(get_db),
    current: User = Depends(require_roles(ADMIN, OPERATIONS_MANAGER, DISPATCHER, DRIVER)),
):
    return {"trip": complete_stop(db, current, trip_id, payload)}


@router.get("/trips/{trip_id}", response_model=TripResponse)
def get_trip_by_id(
    trip_id: str,
    db: Session = Depends(get_db),
    current: User = Depends(require_roles(ADMIN, OPERATIONS_MANAGER, DISPATCHER, DRIVER)),
):
    return {"trip": get_trip(db, current, trip_id)}


@router.post("/trips/{trip_id}/location", response_model=TripResponse)
def post_trip_location(
    trip_id: str,
    payload: UpdateTripLocationRequest,
    db: Session = Depends(get_db),
    current: User = Depends(require_roles(ADMIN, OPERATIONS_MANAGER, DISPATCHER, DRIVER)),
):
    return {"trip": update_trip_location(db, current, trip_id, payload)}


@router.get("/trips/{trip_id}/events")
def get_trip_events(
    trip_id: str,
    db: Session = Depends(get_db),
    current: User = Depends(require_roles(ADMIN, OPERATIONS_MANAGER, DISPATCHER, DRIVER)),
):
    return {"events": list_trip_events(db, current, trip_id)}
