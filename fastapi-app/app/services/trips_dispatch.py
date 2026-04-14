from __future__ import annotations

from datetime import datetime
import uuid

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.company_scope import require_company_uuid
from app.models.driver import Driver
from app.models.order import Order
from app.models.trips_dispatch import (
    DispatchTrip,
    DispatchTripEvent,
    DispatchTripOrder,
    DispatchTripStop,
)
from app.models.user import User
from app.models.vehicle import Vehicle
from app.schemas.trips_dispatch import (
    AssignTripOrderRequest,
    CompleteStopRequest,
    CreateTripRequest,
    StopPickupIn,
    TripOut,
    UpdateTripLocationRequest,
)

PLANNED = "PLANNED"
IN_PROGRESS = "IN_PROGRESS"
COMPLETED = "COMPLETED"
LOADED = "LOADED"
IN_TRANSIT = "IN_TRANSIT"
DELIVERED = "DELIVERED"


def _resolve_trip(db: Session, company_uuid: str, trip_id: str) -> DispatchTrip:
    q = db.query(DispatchTrip).filter(DispatchTrip.company_uuid == company_uuid)
    if trip_id.isdigit():
        row = q.filter(DispatchTrip.id == int(trip_id)).first()
        if row:
            return row
    row = q.filter((DispatchTrip.uuid == trip_id) | (DispatchTrip.public_id == trip_id)).first()
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trip not found.")
    return row


def _resolve_driver(db: Session, company_uuid: str, driver_id: str) -> Driver:
    key = driver_id.strip()
    q = db.query(Driver).filter(Driver.company_uuid == company_uuid, Driver.deleted_at.is_(None))
    row = q.filter((Driver.uuid == key) | (Driver.public_id == key)).first()
    if not row and key.isdigit():
        row = q.filter(Driver.id == int(key)).first()
    if not row:
        # Allow driver lookup by user name/email for UI friendliness.
        user_row = (
            db.query(User.uuid)
            .filter(
                User.company_uuid == company_uuid,
                User.deleted_at.is_(None),
                ((User.name == key) | (User.email == key)),
            )
            .first()
        )
        if user_row and user_row[0]:
            row = q.filter(Driver.user_uuid == str(user_row[0])).first()
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Driver not found.")
    return row


def _resolve_vehicle(db: Session, company_uuid: str, vehicle_id: str) -> Vehicle:
    key = vehicle_id.strip()
    q = db.query(Vehicle).filter(Vehicle.company_uuid == company_uuid, Vehicle.deleted_at.is_(None))
    row = q.filter((Vehicle.uuid == key) | (Vehicle.public_id == key) | (Vehicle.plate_number == key)).first()
    if not row and key.isdigit():
        row = q.filter(Vehicle.id == int(key)).first()
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vehicle not found.")
    return row


def _resolve_order(db: Session, company_uuid: str, order_id: str) -> Order:
    q = db.query(Order).filter(Order.company_uuid == company_uuid, Order.deleted_at.is_(None))
    row = q.filter((Order.uuid == order_id) | (Order.public_id == order_id)).first()
    if not row and order_id.isdigit():
        row = q.filter(Order.id == int(order_id)).first()
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found.")
    return row


def _recompute_capacity(trip: DispatchTrip, orders: list[DispatchTripOrder]) -> None:
    current_load = sum(o.load_units for o in orders if o.status != DELIVERED)
    if current_load > trip.total_capacity:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Capacity exceeded: current_load cannot be greater than total_capacity.",
        )
    trip.current_load = current_load
    trip.available_capacity = trip.total_capacity - current_load


def _event(db: Session, trip_id: int, event_type: str, metadata: dict | None = None) -> None:
    db.add(
        DispatchTripEvent(
            trip_id=trip_id,
            event_type=event_type,
            event_metadata=metadata or {},
            created_at=datetime.utcnow(),
        )
    )


def _dashboard(trip: DispatchTrip, orders: list[DispatchTripOrder]) -> dict:
    delivered = sum(1 for o in orders if o.status == DELIVERED)
    pending = sum(1 for o in orders if o.status != DELIVERED)
    return {
        "total_capacity": trip.total_capacity,
        "current_load": trip.current_load,
        "available_capacity": trip.available_capacity,
        "delivered_orders_count": delivered,
        "pending_orders_count": pending,
    }


def _driver_name_for_trip(db: Session, trip: DispatchTrip) -> str | None:
    if not trip.driver_uuid:
        return None
    d = db.query(Driver).filter(Driver.uuid == trip.driver_uuid, Driver.deleted_at.is_(None)).first()
    if not d:
        return None
    if d.user_uuid:
        u = db.query(User).filter(User.uuid == d.user_uuid, User.deleted_at.is_(None)).first()
        if u:
            return (u.name or u.email or "").strip() or None
    return (d.public_id or d.uuid or "").strip() or None


def _vehicle_plate_for_trip(db: Session, trip: DispatchTrip) -> str | None:
    if not trip.vehicle_uuid:
        return None
    v = db.query(Vehicle).filter(Vehicle.uuid == trip.vehicle_uuid, Vehicle.deleted_at.is_(None)).first()
    if not v:
        return None
    return (v.plate_number or v.public_id or v.uuid or "").strip() or None


def _serialize_trip(
    db: Session,
    trip: DispatchTrip,
    orders: list[DispatchTripOrder],
    stops: list[DispatchTripStop],
    events: list[DispatchTripEvent],
) -> TripOut:
    return TripOut(
        id=trip.id,
        uuid=trip.uuid,
        public_id=trip.public_id,
        vehicle_id=trip.vehicle_uuid,
        driver_id=trip.driver_uuid,
        vehicle_plate_number=_vehicle_plate_for_trip(db, trip),
        driver_name=_driver_name_for_trip(db, trip),
        start_location=trip.start_location,
        end_location=trip.end_location,
        status=trip.status,  # type: ignore[arg-type]
        total_capacity=trip.total_capacity,
        current_load=trip.current_load,
        available_capacity=trip.available_capacity,
        current_lat=trip.current_lat,
        current_lng=trip.current_lng,
        last_location_update=trip.last_location_update,
        started_at=trip.started_at,
        completed_at=trip.completed_at,
        orders=[
            {
                "order_id": o.order_id,
                "pickup_location": o.pickup_location,
                "drop_location": o.drop_location,
                "status": o.status,
                "load_units": o.load_units,
            }
            for o in orders
        ],
        stops=[
            {
                "location_name": s.location_name,
                "type": s.type,
                "sequence": s.sequence,
                "is_completed": bool(s.is_completed),
                "completed_at": s.completed_at,
            }
            for s in stops
        ],
        events=[{"event_type": e.event_type, "metadata": e.event_metadata, "created_at": e.created_at} for e in events],
        dashboard=_dashboard(trip, orders),
    )


def create_trip(db: Session, current: User, payload: CreateTripRequest) -> TripOut:
    company_uuid = require_company_uuid(current)
    driver = _resolve_driver(db, company_uuid, payload.driver_id)
    vehicle = _resolve_vehicle(db, company_uuid, payload.vehicle_id)

    now = datetime.utcnow()
    trip = DispatchTrip(
        uuid=str(uuid.uuid4()),
        public_id=f"trip_{uuid.uuid4().hex[:12]}",
        company_uuid=company_uuid,
        vehicle_uuid=vehicle.uuid or "",
        driver_uuid=driver.uuid or "",
        start_location=payload.start_location.strip(),
        end_location=payload.end_location.strip(),
        total_capacity=payload.total_capacity,
        current_load=0,
        available_capacity=payload.total_capacity,
        status=PLANNED,
        created_at=now,
        updated_at=now,
    )
    db.add(trip)
    db.flush()

    stops: list[DispatchTripStop] = []
    for stop in payload.stops:
        s = DispatchTripStop(
            trip_id=trip.id,
            location_name=stop.location_name.strip(),
            type=stop.type,
            sequence=stop.sequence,
            is_completed=False,
            created_at=now,
            updated_at=now,
        )
        db.add(s)
        stops.append(s)
    db.commit()
    db.refresh(trip)
    stops = db.query(DispatchTripStop).filter(DispatchTripStop.trip_id == trip.id).order_by(DispatchTripStop.sequence.asc()).all()
    events = db.query(DispatchTripEvent).filter(DispatchTripEvent.trip_id == trip.id).order_by(DispatchTripEvent.created_at.asc()).all()
    return _serialize_trip(db, trip, [], stops, events)


def assign_order(db: Session, current: User, trip_id: str, payload: AssignTripOrderRequest) -> TripOut:
    company_uuid = require_company_uuid(current)
    trip = _resolve_trip(db, company_uuid, trip_id)
    if trip.status not in {PLANNED, IN_PROGRESS}:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Orders can be assigned only to planned/in-progress trips.")

    order = _resolve_order(db, company_uuid, payload.order_id)
    exists = (
        db.query(DispatchTripOrder)
        .filter(DispatchTripOrder.trip_id == trip.id, DispatchTripOrder.order_id == order.id)
        .first()
    )
    if exists:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Order already assigned to this trip.")

    trip_order = DispatchTripOrder(
        trip_id=trip.id,
        order_id=order.id,
        pickup_location=payload.pickup_location.strip(),
        drop_location=payload.drop_location.strip(),
        status=IN_TRANSIT if trip.status == IN_PROGRESS else LOADED,
        load_units=payload.load_units,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db.add(trip_order)
    db.flush()

    orders = db.query(DispatchTripOrder).filter(DispatchTripOrder.trip_id == trip.id).all()
    _recompute_capacity(trip, orders)
    trip.updated_at = datetime.utcnow()
    db.add(trip)
    _event(
        db,
        trip.id,
        "pickup_added" if trip.status == IN_PROGRESS else "order_assigned",
        {"order_id": order.id, "pickup_location": trip_order.pickup_location, "drop_location": trip_order.drop_location, "load_units": trip_order.load_units},
    )
    db.commit()
    db.refresh(trip)
    orders = db.query(DispatchTripOrder).filter(DispatchTripOrder.trip_id == trip.id).all()
    stops = db.query(DispatchTripStop).filter(DispatchTripStop.trip_id == trip.id).order_by(DispatchTripStop.sequence.asc()).all()
    events = db.query(DispatchTripEvent).filter(DispatchTripEvent.trip_id == trip.id).order_by(DispatchTripEvent.created_at.asc()).all()
    return _serialize_trip(db, trip, orders, stops, events)


def start_trip(db: Session, current: User, trip_id: str) -> TripOut:
    company_uuid = require_company_uuid(current)
    trip = _resolve_trip(db, company_uuid, trip_id)
    if trip.status != PLANNED:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Only planned trips can be started.")

    orders = db.query(DispatchTripOrder).filter(DispatchTripOrder.trip_id == trip.id).all()
    for row in orders:
        row.status = IN_TRANSIT
        row.updated_at = datetime.utcnow()
        db.add(row)

    trip.status = IN_PROGRESS
    trip.started_at = datetime.utcnow()
    _recompute_capacity(trip, orders)
    trip.updated_at = datetime.utcnow()
    db.add(trip)
    _event(db, trip.id, "trip_start", {"trip_id": trip.id})
    db.commit()
    db.refresh(trip)
    stops = db.query(DispatchTripStop).filter(DispatchTripStop.trip_id == trip.id).order_by(DispatchTripStop.sequence.asc()).all()
    events = db.query(DispatchTripEvent).filter(DispatchTripEvent.trip_id == trip.id).order_by(DispatchTripEvent.created_at.asc()).all()
    return _serialize_trip(db, trip, orders, stops, events)


def _add_new_pickup(db: Session, company_uuid: str, trip: DispatchTrip, pickup: StopPickupIn) -> None:
    if trip.status != IN_PROGRESS:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Dynamic order assignment is allowed only when trip is IN_PROGRESS.",
        )
    order = _resolve_order(db, company_uuid, pickup.order_id)
    exists = (
        db.query(DispatchTripOrder)
        .filter(DispatchTripOrder.trip_id == trip.id, DispatchTripOrder.order_id == order.id)
        .first()
    )
    if exists:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Pickup order already assigned to this trip.")
    row = DispatchTripOrder(
        trip_id=trip.id,
        order_id=order.id,
        pickup_location=pickup.pickup_location.strip(),
        drop_location=pickup.drop_location.strip(),
        status=IN_TRANSIT,
        load_units=pickup.load_units,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db.add(row)
    _event(
        db,
        trip.id,
        "pickup_added",
        {
            "order_id": order.id,
            "pickup_location": row.pickup_location,
            "drop_location": row.drop_location,
            "load_units": row.load_units,
        },
    )


def complete_stop(db: Session, current: User, trip_id: str, payload: CompleteStopRequest) -> TripOut:
    company_uuid = require_company_uuid(current)
    trip = _resolve_trip(db, company_uuid, trip_id)
    if trip.status != IN_PROGRESS:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Only in-progress trips can complete stops.")

    stop = (
        db.query(DispatchTripStop)
        .filter(DispatchTripStop.trip_id == trip.id, DispatchTripStop.sequence == payload.stop_sequence)
        .first()
    )
    if not stop:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Stop not found for trip.")
    if stop.is_completed:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Stop already completed.")
    prev_pending = (
        db.query(DispatchTripStop)
        .filter(
            DispatchTripStop.trip_id == trip.id,
            DispatchTripStop.sequence < payload.stop_sequence,
            DispatchTripStop.is_completed.is_(False),
        )
        .count()
    )
    if prev_pending > 0:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Stop sequence violation: complete earlier stops first.")

    # Delivered orders at the current stop (drop location match).
    orders = db.query(DispatchTripOrder).filter(DispatchTripOrder.trip_id == trip.id).all()
    for row in orders:
        if row.status != DELIVERED and row.drop_location.strip().lower() == stop.location_name.strip().lower():
            row.status = DELIVERED
            row.updated_at = datetime.utcnow()
            db.add(row)
            _event(db, trip.id, "order_delivered", {"order_id": row.order_id, "stop_sequence": payload.stop_sequence})

    # New pickups at stop can be dynamically assigned while trip is in progress.
    for pickup in payload.new_pickups:
        _add_new_pickup(db, company_uuid, trip, pickup)

    orders = db.query(DispatchTripOrder).filter(DispatchTripOrder.trip_id == trip.id).all()
    _recompute_capacity(trip, orders)
    stop.is_completed = True
    stop.completed_at = datetime.utcnow()
    stop.updated_at = datetime.utcnow()
    db.add(stop)
    _event(
        db,
        trip.id,
        "stop_completed",
        {"stop_sequence": stop.sequence, "location_name": stop.location_name, "type": stop.type},
    )
    max_sequence = max((s.sequence for s in db.query(DispatchTripStop).filter(DispatchTripStop.trip_id == trip.id).all()), default=0)
    if payload.stop_sequence >= max_sequence and all(o.status == DELIVERED for o in orders):
        trip.status = COMPLETED
        trip.completed_at = datetime.utcnow()
    trip.updated_at = datetime.utcnow()
    db.add(trip)
    db.commit()
    db.refresh(trip)
    stops = db.query(DispatchTripStop).filter(DispatchTripStop.trip_id == trip.id).order_by(DispatchTripStop.sequence.asc()).all()
    events = db.query(DispatchTripEvent).filter(DispatchTripEvent.trip_id == trip.id).order_by(DispatchTripEvent.created_at.asc()).all()
    return _serialize_trip(db, trip, orders, stops, events)


def get_trip(db: Session, current: User, trip_id: str) -> TripOut:
    company_uuid = require_company_uuid(current)
    trip = _resolve_trip(db, company_uuid, trip_id)
    orders = db.query(DispatchTripOrder).filter(DispatchTripOrder.trip_id == trip.id).all()
    stops = db.query(DispatchTripStop).filter(DispatchTripStop.trip_id == trip.id).order_by(DispatchTripStop.sequence.asc()).all()
    _recompute_capacity(trip, orders)
    db.add(trip)
    db.commit()
    db.refresh(trip)
    events = db.query(DispatchTripEvent).filter(DispatchTripEvent.trip_id == trip.id).order_by(DispatchTripEvent.created_at.asc()).all()
    return _serialize_trip(db, trip, orders, stops, events)


def update_trip_location(db: Session, current: User, trip_id: str, payload: UpdateTripLocationRequest) -> TripOut:
    company_uuid = require_company_uuid(current)
    trip = _resolve_trip(db, company_uuid, trip_id)
    if trip.status != IN_PROGRESS:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Location updates allowed only for in-progress trips.")
    now = datetime.utcnow()
    trip.current_lat = payload.current_lat
    trip.current_lng = payload.current_lng
    trip.last_location_update = now
    trip.updated_at = now
    db.add(trip)
    _event(db, trip.id, "location_updated", {"current_lat": payload.current_lat, "current_lng": payload.current_lng})
    db.commit()
    db.refresh(trip)
    orders = db.query(DispatchTripOrder).filter(DispatchTripOrder.trip_id == trip.id).all()
    stops = db.query(DispatchTripStop).filter(DispatchTripStop.trip_id == trip.id).order_by(DispatchTripStop.sequence.asc()).all()
    events = db.query(DispatchTripEvent).filter(DispatchTripEvent.trip_id == trip.id).order_by(DispatchTripEvent.created_at.asc()).all()
    return _serialize_trip(db, trip, orders, stops, events)


def list_trip_events(db: Session, current: User, trip_id: str) -> list[dict]:
    company_uuid = require_company_uuid(current)
    trip = _resolve_trip(db, company_uuid, trip_id)
    rows = db.query(DispatchTripEvent).filter(DispatchTripEvent.trip_id == trip.id).order_by(DispatchTripEvent.created_at.asc()).all()
    return [{"event_type": r.event_type, "metadata": r.event_metadata, "created_at": r.created_at} for r in rows]


def list_trips(db: Session, current: User) -> list[TripOut]:
    company_uuid = require_company_uuid(current)
    trips = (
        db.query(DispatchTrip)
        .filter(DispatchTrip.company_uuid == company_uuid)
        .order_by(DispatchTrip.created_at.desc().nullslast(), DispatchTrip.id.desc())
        .all()
    )
    out: list[TripOut] = []
    for trip in trips:
        orders = db.query(DispatchTripOrder).filter(DispatchTripOrder.trip_id == trip.id).all()
        stops = db.query(DispatchTripStop).filter(DispatchTripStop.trip_id == trip.id).order_by(DispatchTripStop.sequence.asc()).all()
        events = db.query(DispatchTripEvent).filter(DispatchTripEvent.trip_id == trip.id).order_by(DispatchTripEvent.created_at.asc()).all()
        _recompute_capacity(trip, orders)
        out.append(_serialize_trip(db, trip, orders, stops, events))
    db.commit()
    return out
