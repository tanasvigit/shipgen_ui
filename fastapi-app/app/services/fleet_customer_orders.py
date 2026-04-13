from __future__ import annotations

from datetime import datetime
import uuid

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.company_scope import require_company_uuid
from app.core.roles import ADMIN, DRIVER, FLEET_CUSTOMER, effective_user_role
from app.models.contact import Contact
from app.models.driver import Driver
from app.models.order import Order
from app.models.trip import Trip
from app.models.user import User
from app.models.vehicle import Vehicle
from app.services.fleet_customer_contacts import ensure_fleet_customer_contact
from app.schemas.fleet_customer import ASSIGNED, IN_PROGRESS, ORDER_CREATED


def _resolve_order(db: Session, company_uuid: str, order_id: str) -> Order:
    order = (
        db.query(Order)
        .filter(
            Order.company_uuid == company_uuid,
            Order.deleted_at.is_(None),
            (Order.uuid == order_id) | (Order.public_id == order_id),
        )
        .first()
    )
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found.")
    return order


def _resolve_driver(db: Session, company_uuid: str, driver_id: str) -> Driver:
    driver = (
        db.query(Driver)
        .filter(
            Driver.company_uuid == company_uuid,
            Driver.deleted_at.is_(None),
            (Driver.uuid == driver_id) | (Driver.public_id == driver_id),
        )
        .first()
    )
    if not driver:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Driver not found.")
    return driver


def _resolve_vehicle(db: Session, company_uuid: str, vehicle_id: str) -> Vehicle:
    vehicle = (
        db.query(Vehicle)
        .filter(
            Vehicle.company_uuid == company_uuid,
            Vehicle.deleted_at.is_(None),
            (Vehicle.uuid == vehicle_id) | (Vehicle.public_id == vehicle_id),
        )
        .first()
    )
    if not vehicle:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vehicle not found.")
    return vehicle


def _driver_record_for_user(db: Session, user: User, company_uuid: str) -> Driver:
    driver = (
        db.query(Driver)
        .filter(
            Driver.company_uuid == company_uuid,
            Driver.deleted_at.is_(None),
            Driver.user_uuid == user.uuid,
        )
        .first()
    )
    if not driver:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Driver profile not found for current user.",
        )
    return driver


def _trip_for_order(db: Session, order_id: int) -> Trip | None:
    return (
        db.query(Trip)
        .filter(Trip.order_id == order_id)
        .order_by(Trip.id.desc())
        .first()
    )


def _serialize_order(db: Session, order: Order) -> dict:
    driver = None
    vehicle = None
    if order.driver_assigned_uuid:
        driver = db.query(Driver).filter(Driver.uuid == order.driver_assigned_uuid).first()
    if order.vehicle_assigned_uuid:
        vehicle = db.query(Vehicle).filter(Vehicle.uuid == order.vehicle_assigned_uuid).first()
    trip = _trip_for_order(db, order.id)

    customer_display_name = None
    if order.customer_uuid:
        c = db.query(Contact).filter(Contact.uuid == order.customer_uuid, Contact.deleted_at.is_(None)).first()
        if c and c.name:
            customer_display_name = c.name

    created_by_display_name = None
    if order.created_by:
        u = db.query(User).filter(User.uuid == order.created_by).first()
        if u:
            created_by_display_name = (u.name or u.email or "").strip() or None

    return {
        "id": order.id,
        "uuid": order.uuid,
        "public_id": order.public_id,
        "status": order.status,
        "type": order.type,
        "internal_id": order.internal_id,
        "customer_uuid": order.customer_uuid,
        "customer_type": order.customer_type,
        "customer_display_name": customer_display_name,
        "created_by": order.created_by,
        "created_by_display_name": created_by_display_name,
        "notes": order.notes,
        "scheduled_at": order.scheduled_at,
        "driver_assigned_uuid": order.driver_assigned_uuid,
        "vehicle_assigned_uuid": order.vehicle_assigned_uuid,
        "meta": order.meta,
        "options": order.options or {},
        "created_at": order.created_at,
        "updated_at": order.updated_at,
        "driver": {
            "uuid": driver.uuid,
            "public_id": driver.public_id,
            "user_uuid": driver.user_uuid,
            "status": driver.status,
        }
        if driver
        else None,
        "vehicle": {
            "uuid": vehicle.uuid,
            "public_id": vehicle.public_id,
            "make": vehicle.make,
            "model": vehicle.model,
            "plate_number": vehicle.plate_number,
            "status": vehicle.status,
        }
        if vehicle
        else None,
        "trip": {
            "id": trip.id,
            "status": trip.status,
            "start_time": trip.start_time,
            "end_time": trip.end_time,
            "current_location": trip.current_location,
        }
        if trip
        else None,
    }


def create_customer_order(
    db: Session,
    current: User,
    *,
    internal_id: str | None = None,
    pickup_location: str,
    drop_location: str,
    goods_description: str,
) -> dict:
    if effective_user_role(current) != FLEET_CUSTOMER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")

    company_uuid = require_company_uuid(current)
    contact = ensure_fleet_customer_contact(db, current)
    pick = pickup_location.strip()
    dr = drop_location.strip()
    goods = goods_description.strip()
    display_internal_id = (internal_id or "").strip()
    cust_label = (contact.name or current.name or current.email or "").strip()
    meta = {
        "customer_name": cust_label,
        "priority": "normal",
        "pickup": {"address": pick, "lat": None, "lng": None},
        "delivery": {"address": dr, "lat": None, "lng": None},
        "pickup_location": pick,
        "drop_location": dr,
        "goods_description": goods,
        "source": "fleet_customer",
    }
    order = Order(
        uuid=str(uuid.uuid4()),
        public_id=f"order_{uuid.uuid4().hex[:12]}",
        company_uuid=company_uuid,
        customer_uuid=contact.uuid,
        customer_type="customer",
        created_by=current.uuid,
        status=ORDER_CREATED,
        type="delivery",
        internal_id=display_internal_id or None,
        notes=goods,
        meta=meta,
        options={},
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db.add(order)
    db.commit()
    db.refresh(order)
    return _serialize_order(db, order)


def list_orders_for_role(db: Session, current: User) -> list[dict]:
    if effective_user_role(current) != FLEET_CUSTOMER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
    company_uuid = require_company_uuid(current)
    query = db.query(Order).filter(Order.company_uuid == company_uuid, Order.deleted_at.is_(None))
    query = query.filter(Order.created_by == current.uuid)
    rows = query.order_by(Order.created_at.desc().nullslast(), Order.id.desc()).all()
    return [_serialize_order(db, row) for row in rows]


def get_order_for_role(db: Session, current: User, order_id: str) -> dict:
    if effective_user_role(current) != FLEET_CUSTOMER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
    company_uuid = require_company_uuid(current)
    order = _resolve_order(db, company_uuid, order_id)
    if order.created_by != current.uuid:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found.")
    return _serialize_order(db, order)


def assign_order(db: Session, current: User, order_id: str, *, driver_id: str, vehicle_id: str) -> dict:
    if effective_user_role(current) != ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")

    company_uuid = require_company_uuid(current)
    order = _resolve_order(db, company_uuid, order_id)
    driver = _resolve_driver(db, company_uuid, driver_id)
    vehicle = _resolve_vehicle(db, company_uuid, vehicle_id)

    order.driver_assigned_uuid = driver.uuid
    order.vehicle_assigned_uuid = vehicle.uuid
    order.status = ASSIGNED
    order.updated_at = datetime.utcnow()
    db.add(order)
    db.commit()
    db.refresh(order)
    return _serialize_order(db, order)


def start_trip(
    db: Session,
    current: User,
    *,
    order_id: str,
    current_location: dict | None = None,
) -> dict:
    if effective_user_role(current) != DRIVER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")

    company_uuid = require_company_uuid(current)
    driver = _driver_record_for_user(db, current, company_uuid)
    order = _resolve_order(db, company_uuid, order_id)

    if order.driver_assigned_uuid != driver.uuid:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Order not assigned to current driver")
    if (order.status or "").lower() != "assigned":
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Trip can start only when order is assigned")

    now = datetime.utcnow()
    order.status = IN_PROGRESS
    order.started = True
    order.started_at = order.started_at or now
    order.updated_at = now

    trip = _trip_for_order(db, order.id)
    if trip is None:
        trip = Trip(
            order_id=order.id,
            driver_id=driver.id,
            start_time=now,
            status=IN_PROGRESS,
            current_location=current_location or {},
            created_at=now,
            updated_at=now,
        )
    else:
        trip.start_time = trip.start_time or now
        trip.status = IN_PROGRESS
        if current_location is not None:
            trip.current_location = current_location
        trip.updated_at = now

    db.add(order)
    db.add(trip)
    db.commit()
    db.refresh(order)
    return _serialize_order(db, order)
