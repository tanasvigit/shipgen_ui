from datetime import datetime
import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import false, or_
from sqlalchemy.orm import Session

from app.api.v1.routers.auth import _get_current_user
from app.core.database import get_db
from app.core.roles import (
    ADMIN,
    DRIVER,
    DISPATCHER,
    FLEET_CUSTOMER,
    OPERATIONS_MANAGER,
    effective_user_role,
    require_roles,
)
from app.models.contact import Contact
from app.models.driver import Driver
from app.models.order import Order
from app.models.user import User
from app.schemas.order import OrderCreate, OrderOut, OrderUpdate, OrderResponse, OrdersResponse

router = APIRouter(prefix="/fleetops/v1/orders", tags=["fleetops-orders"])


def _require_company_uuid(current: User) -> str:
    if not current.company_uuid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current user is not associated with a company.",
        )
    return current.company_uuid


def _deny_fleet_customer_access(current: User) -> None:
    if effective_user_role(current) == FLEET_CUSTOMER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Fleet customers can only use /orders endpoints.",
        )


def _driver_uuid_for_user(db: Session, current: User) -> str | None:
    if not current.uuid or not current.company_uuid:
        return None
    row = (
        db.query(Driver.uuid)
        .filter(
            Driver.user_uuid == current.uuid,
            Driver.company_uuid == current.company_uuid,
            Driver.deleted_at.is_(None),
        )
        .first()
    )
    return str(row[0]) if row and row[0] else None


def _apply_driver_order_filters(query, db: Session, current: User):
    role = effective_user_role(current)
    if role == DRIVER:
        du = _driver_uuid_for_user(db, current)
        if not du:
            return query.filter(false())
        return query.filter(Order.driver_assigned_uuid == du)
    return query


def _get_scoped_order(db: Session, current: User, order_id: str) -> Order:
    company_uuid = _require_company_uuid(current)
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
    if effective_user_role(current) == DRIVER:
        du = _driver_uuid_for_user(db, current)
        if not du or order.driver_assigned_uuid != du:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found.")
    return order


def _require_customer_for_company(db: Session, *, customer_uuid: str, company_uuid: str) -> Contact:
    cust = (
        db.query(Contact)
        .filter(
            Contact.uuid == customer_uuid,
            Contact.company_uuid == company_uuid,
            Contact.type == "customer",
            Contact.deleted_at.is_(None),
        )
        .first()
    )
    if not cust:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid customer for this company",
        )
    return cust


def _customer_name_map(db: Session, company_uuid: str, uuids: List[str]) -> dict[str, str]:
    if not uuids:
        return {}
    rows = (
        db.query(Contact.uuid, Contact.name)
        .filter(
            Contact.uuid.in_(uuids),
            Contact.company_uuid == company_uuid,
            Contact.type == "customer",
            Contact.deleted_at.is_(None),
        )
        .all()
    )
    return {str(r[0]): (r[1] or "") for r in rows if r[0]}


def _display_name_for_order(db: Session, company_uuid: str, order: Order) -> str | None:
    """Prefer linked customer; meta.customer_name; then placing user (fleet customer) name."""
    if order.customer_uuid:
        names = _customer_name_map(db, company_uuid, [order.customer_uuid])
        n = names.get(order.customer_uuid)
        if n:
            return n
    meta = order.meta if isinstance(order.meta, dict) else None
    if meta:
        legacy = meta.get("customer_name")
        if legacy:
            return str(legacy)
    if order.created_by:
        u = (
            db.query(User)
            .filter(User.uuid == order.created_by, User.company_uuid == company_uuid, User.deleted_at.is_(None))
            .first()
        )
        if u:
            label = (u.name or u.email or "").strip()
            if label:
                return label
    return None


def _creator_display_name(db: Session, company_uuid: str, order: Order) -> str | None:
    if not order.created_by:
        return None
    u = (
        db.query(User)
        .filter(User.uuid == order.created_by, User.company_uuid == company_uuid, User.deleted_at.is_(None))
        .first()
    )
    if not u:
        return None
    return (u.name or u.email or "").strip() or None


def _enrich_order_out(db: Session, current: User, order: Order) -> OrderOut:
    base = OrderOut.model_validate(order)
    company_uuid = _require_company_uuid(current)
    display = _display_name_for_order(db, company_uuid, order)
    creator = _creator_display_name(db, company_uuid, order)
    return base.model_copy(update={"customer_display_name": display, "created_by_display_name": creator})


def _order_response(db: Session, current: User, order: Order) -> OrderResponse:
    return OrderResponse(order=_enrich_order_out(db, current, order))


@router.get("/", response_model=OrdersResponse)
def list_orders(
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    status_filter: str | None = Query(None, alias="status"),
    search: str | None = Query(None),
    start_date: str | None = Query(None),
    end_date: str | None = Query(None),
):
    _deny_fleet_customer_access(current)
    company_uuid = _require_company_uuid(current)
    query = db.query(Order).filter(
        Order.deleted_at.is_(None),
        Order.company_uuid == company_uuid,
    )
    if status_filter:
        query = query.filter(Order.status == status_filter)
    if search:
        q = f"%{search.strip()}%"
        customer_uuids: list[str] = [
            str(r[0])
            for r in db.query(Contact.uuid)
            .filter(
                Contact.company_uuid == company_uuid,
                Contact.type == "customer",
                Contact.deleted_at.is_(None),
                or_(Contact.name.ilike(q), Contact.phone.ilike(q), Contact.email.ilike(q)),
            )
            .all()
            if r[0]
        ]
        creator_uuids: list[str] = [
            str(r[0])
            for r in db.query(User.uuid)
            .filter(
                User.company_uuid == company_uuid,
                User.deleted_at.is_(None),
                or_(User.name.ilike(q), User.email.ilike(q)),
            )
            .all()
            if r[0]
        ]
        search_conds = [
            Order.internal_id.ilike(q),
            Order.public_id.ilike(q),
            Order.uuid.ilike(q),
            Order.notes.ilike(q),
            Order.type.ilike(q),
        ]
        if customer_uuids:
            search_conds.append(Order.customer_uuid.in_(customer_uuids))
        if creator_uuids:
            search_conds.append(Order.created_by.in_(creator_uuids))
        query = query.filter(or_(*search_conds))

    def _parse_iso(value: str | None) -> datetime | None:
        if not value:
            return None
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00"))
        except Exception:
            return None

    start_dt = _parse_iso(start_date)
    end_dt = _parse_iso(end_date)
    if start_dt:
        query = query.filter(Order.created_at.is_not(None), Order.created_at >= start_dt)
    if end_dt:
        query = query.filter(Order.created_at.is_not(None), Order.created_at <= end_dt)

    query = _apply_driver_order_filters(query, db, current)
    orders = query.offset(offset).limit(limit).all()
    out: list[OrderOut] = []
    for o in orders:
        base = OrderOut.model_validate(o)
        disp = _display_name_for_order(db, company_uuid, o)
        creator = _creator_display_name(db, company_uuid, o)
        out.append(base.model_copy(update={"customer_display_name": disp, "created_by_display_name": creator}))
    return {"orders": out}


@router.get("/{order_id}", response_model=OrderResponse)
def get_order(
    order_id: str,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    _deny_fleet_customer_access(current)
    order = _get_scoped_order(db, current, order_id)
    return _order_response(db, current, order)


@router.post("/", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
def create_order(
    payload: OrderCreate,
    db: Session = Depends(get_db),
    current: User = Depends(require_roles(ADMIN, OPERATIONS_MANAGER, DISPATCHER)),
):
    company_uuid = _require_company_uuid(current)
    customer = _require_customer_for_company(db, customer_uuid=payload.customer_uuid, company_uuid=company_uuid)
    meta = dict(payload.meta or {})
    meta.pop("customer_name", None)

    order = Order(
        uuid=str(uuid.uuid4()),
        public_id=f"order_{uuid.uuid4().hex[:12]}",
        type=payload.type,
        internal_id=payload.internal_id,
        notes=payload.notes,
        scheduled_at=payload.scheduled_at,
        meta=meta,
        options=payload.options,
        company_uuid=company_uuid,
        customer_uuid=customer.uuid,
        customer_type="customer",
        status="created",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db.add(order)
    db.commit()
    db.refresh(order)

    return _order_response(db, current, order)


@router.put("/{order_id}", response_model=OrderResponse)
@router.patch("/{order_id}", response_model=OrderResponse)
def update_order(
    order_id: str,
    payload: OrderUpdate,
    db: Session = Depends(get_db),
    current: User = Depends(require_roles(ADMIN, OPERATIONS_MANAGER, DISPATCHER)),
):
    company_uuid = _require_company_uuid(current)
    order = _get_scoped_order(db, current, order_id)

    data = payload.model_dump(exclude_unset=True)
    if "customer_uuid" in data:
        raw = data.pop("customer_uuid")
        if raw is None or (isinstance(raw, str) and not raw.strip()):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid customer for this company",
            )
        customer = _require_customer_for_company(
            db, customer_uuid=str(raw).strip(), company_uuid=company_uuid
        )
        order.customer_uuid = customer.uuid
        order.customer_type = "customer"
        meta = dict(order.meta or {})
        meta.pop("customer_name", None)
        order.meta = meta

    if "meta" in data and data["meta"] is not None:
        incoming = dict(data["meta"])
        incoming.pop("customer_name", None)
        data["meta"] = incoming

    for field, value in data.items():
        if field == "created_at":
            continue
        setattr(order, field, value)

    order.updated_at = datetime.utcnow()
    db.add(order)
    db.commit()
    db.refresh(order)

    return _order_response(db, current, order)


@router.delete("/{order_id}", response_model=OrderResponse)
def delete_order(
    order_id: str,
    db: Session = Depends(get_db),
    current: User = Depends(require_roles(ADMIN)),
):
    order = _get_scoped_order(db, current, order_id)
    order.deleted_at = datetime.utcnow()
    db.add(order)
    db.commit()
    return _order_response(db, current, order)


@router.delete("/{order_id}/delete", response_model=OrderResponse)
def delete_order_by_path(
    order_id: str,
    db: Session = Depends(get_db),
    current: User = Depends(require_roles(ADMIN)),
):
    return delete_order(order_id, db, current)


@router.post("/{order_id}/start", response_model=OrderResponse)
def start_order(
    order_id: str,
    db: Session = Depends(get_db),
    current: User = Depends(require_roles(ADMIN, OPERATIONS_MANAGER, DISPATCHER)),
):
    order = _get_scoped_order(db, current, order_id)
    order.started = True
    order.started_at = datetime.utcnow()
    order.status = "in_progress"
    db.add(order)
    db.commit()
    db.refresh(order)
    return _order_response(db, current, order)


@router.post("/{order_id}/complete", response_model=OrderResponse)
def complete_order(
    order_id: str,
    db: Session = Depends(get_db),
    current: User = Depends(require_roles(ADMIN, OPERATIONS_MANAGER, DISPATCHER)),
):
    order = _get_scoped_order(db, current, order_id)
    order.status = "completed"
    db.add(order)
    db.commit()
    db.refresh(order)
    return _order_response(db, current, order)


@router.delete("/{order_id}/cancel", response_model=OrderResponse)
def cancel_order(
    order_id: str,
    db: Session = Depends(get_db),
    current: User = Depends(require_roles(ADMIN, OPERATIONS_MANAGER, DISPATCHER)),
):
    order = _get_scoped_order(db, current, order_id)
    order.status = "cancelled"
    db.add(order)
    db.commit()
    db.refresh(order)
    return _order_response(db, current, order)


@router.post("/{order_id}/schedule", response_model=OrderResponse)
@router.patch("/{order_id}/schedule", response_model=OrderResponse)
def schedule_order(
    order_id: str,
    scheduled_at: datetime | None = None,
    db: Session = Depends(get_db),
    current: User = Depends(require_roles(ADMIN, OPERATIONS_MANAGER, DISPATCHER)),
):
    order = _get_scoped_order(db, current, order_id)
    if scheduled_at is None:
        scheduled_at = datetime.utcnow()
    order.scheduled_at = scheduled_at
    if not order.status or order.status in {"created", "scheduled"}:
        order.status = "scheduled"
    db.add(order)
    db.commit()
    db.refresh(order)
    return _order_response(db, current, order)


@router.post("/{order_id}/dispatch", response_model=OrderResponse)
@router.patch("/{order_id}/dispatch", response_model=OrderResponse)
def dispatch_order(
    order_id: str,
    db: Session = Depends(get_db),
    current: User = Depends(require_roles(ADMIN, OPERATIONS_MANAGER, DISPATCHER)),
):
    order = _get_scoped_order(db, current, order_id)
    order.dispatched = True
    order.dispatched_at = datetime.utcnow()
    if order.status not in {"in_progress", "completed", "cancelled"}:
        order.status = "dispatched"
    db.add(order)
    db.commit()
    db.refresh(order)
    return _order_response(db, current, order)


@router.get("/{order_id}/distance-and-time")
def get_distance_and_time(
    order_id: str,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    _deny_fleet_customer_access(current)
    order = _get_scoped_order(db, current, order_id)
    return {"distance": order.distance, "time": order.time}


@router.get("/{order_id}/eta")
def get_eta(
    order_id: str,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    _deny_fleet_customer_access(current)
    order = _get_scoped_order(db, current, order_id)
    return {
        "order_uuid": order.uuid,
        "status": order.status,
        "eta_seconds": order.time,
    }


@router.get("/{order_id}/tracker")
def tracker_data(
    order_id: str,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    _deny_fleet_customer_access(current)
    order = _get_scoped_order(db, current, order_id)
    return {
        "order_uuid": order.uuid,
        "status": order.status,
        "started": order.started,
        "started_at": order.started_at,
        "dispatched": order.dispatched,
        "dispatched_at": order.dispatched_at,
        "scheduled_at": order.scheduled_at,
        "driver_assigned_uuid": order.driver_assigned_uuid,
    }
