"""Aggregated fleet dashboard for drivers, vehicles, and assignments (company-scoped)."""

from __future__ import annotations

from typing import Any, Optional

from fastapi import APIRouter, Depends
from sqlalchemy import and_, exists, func, not_, or_
from sqlalchemy.orm import Session, aliased

from app.api.v1.routers.auth import _get_current_user
from app.core.company_scope import require_company_uuid
from app.core.database import get_db
from app.models.driver import Driver
from app.models.order import Order
from app.models.user import User
from app.models.vehicle import Vehicle
from app.schemas.fleet_dashboard import (
    FleetDashboardDriverRow,
    FleetDashboardKpis,
    FleetDashboardResponse,
    FleetDashboardVehicleRow,
)

router = APIRouter(prefix="/fleetops/v1/fleet", tags=["fleetops-fleet-dashboard"])

TERMINAL_ORDER_STATUSES = ("completed", "cancelled", "failed")


def _coerce_float(v: Any) -> Optional[float]:
    if v is None:
        return None
    if isinstance(v, (int, float)) and not isinstance(v, bool):
        return float(v)
    s = str(v).strip()
    if not s:
        return None
    try:
        return float(s)
    except ValueError:
        return None


def _vehicle_meta_coords(meta: Any) -> tuple[Optional[float], Optional[float]]:
    if not meta or not isinstance(meta, dict):
        return None, None
    return _coerce_float(meta.get("latitude")), _coerce_float(meta.get("longitude"))


def _driver_name(d: Driver) -> str:
    lic = (d.drivers_license_number or "").strip()
    if lic:
        return lic
    if d.public_id:
        return str(d.public_id)
    return str(d.uuid or "")


@router.get("/dashboard", response_model=FleetDashboardResponse)
def get_fleet_dashboard(
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
) -> FleetDashboardResponse:
    cid = require_company_uuid(current)

    def drivers_base():
        return db.query(Driver).filter(Driver.company_uuid == cid, Driver.deleted_at.is_(None))

    def vehicles_base():
        return db.query(Vehicle).filter(Vehicle.company_uuid == cid, Vehicle.deleted_at.is_(None))

    drivers_total = drivers_base().count()
    drivers_active = drivers_base().filter(Driver.status == "active").count()
    drivers_online = drivers_base().filter(Driver.online == 1).count()
    # Unassigned driver = no linked vehicle AND not assigned on any active order.
    active_order_for_driver = exists().where(
        and_(
            Order.company_uuid == cid,
            Order.deleted_at.is_(None),
            Order.driver_assigned_uuid.isnot(None),
            Order.driver_assigned_uuid != "",
            Order.driver_assigned_uuid == Driver.uuid,
            Order.status.notin_(list(TERMINAL_ORDER_STATUSES)),
        )
    )
    drivers_unassigned = drivers_base().filter(
        or_(Driver.vehicle_uuid.is_(None), Driver.vehicle_uuid == ""),
        not_(active_order_for_driver),
    ).count()

    vehicles_total = vehicles_base().count()
    vehicles_active = vehicles_base().filter(Vehicle.status == "active").count()

    DriverAssign = aliased(Driver)
    has_assigned_driver = exists().where(
        and_(
            DriverAssign.vehicle_uuid == Vehicle.uuid,
            DriverAssign.company_uuid == cid,
            DriverAssign.deleted_at.is_(None),
        )
    )
    # Unassigned vehicle = no linked driver AND not used on any active order.
    active_order_for_vehicle = exists().where(
        and_(
            Order.company_uuid == cid,
            Order.deleted_at.is_(None),
            Order.vehicle_assigned_uuid.isnot(None),
            Order.vehicle_assigned_uuid != "",
            Order.vehicle_assigned_uuid == Vehicle.uuid,
            Order.status.notin_(list(TERMINAL_ORDER_STATUSES)),
        )
    )
    vehicles_unassigned = vehicles_base().filter(
        not_(has_assigned_driver),
        not_(active_order_for_vehicle),
    ).count()

    in_use_q = db.query(func.count(func.distinct(Order.vehicle_assigned_uuid))).filter(
        Order.company_uuid == cid,
        Order.deleted_at.is_(None),
        Order.vehicle_assigned_uuid.isnot(None),
        Order.vehicle_assigned_uuid != "",
        Order.status.notin_(list(TERMINAL_ORDER_STATUSES)),
    )
    vehicles_in_use = int(in_use_q.scalar() or 0)

    drivers_on_orders_q = db.query(func.count(func.distinct(Order.driver_assigned_uuid))).filter(
        Order.company_uuid == cid,
        Order.deleted_at.is_(None),
        Order.driver_assigned_uuid.isnot(None),
        Order.driver_assigned_uuid != "",
        Order.status.notin_(list(TERMINAL_ORDER_STATUSES)),
    )
    drivers_on_active_orders = int(drivers_on_orders_q.scalar() or 0)

    # Pull active order assignments once and use them as fallback mapping for table display.
    active_order_pairs = (
        db.query(Order.driver_assigned_uuid, Order.vehicle_assigned_uuid)
        .filter(
            Order.company_uuid == cid,
            Order.deleted_at.is_(None),
            Order.status.notin_(list(TERMINAL_ORDER_STATUSES)),
            Order.driver_assigned_uuid.isnot(None),
            Order.driver_assigned_uuid != "",
            Order.vehicle_assigned_uuid.isnot(None),
            Order.vehicle_assigned_uuid != "",
        )
        .all()
    )
    order_driver_to_vehicle: dict[str, str] = {}
    order_vehicle_to_driver: dict[str, str] = {}
    for driver_uuid_raw, vehicle_uuid_raw in active_order_pairs:
        driver_uuid = str(driver_uuid_raw)
        vehicle_uuid = str(vehicle_uuid_raw)
        if driver_uuid and vehicle_uuid and driver_uuid not in order_driver_to_vehicle:
            order_driver_to_vehicle[driver_uuid] = vehicle_uuid
        if driver_uuid and vehicle_uuid and vehicle_uuid not in order_vehicle_to_driver:
            order_vehicle_to_driver[vehicle_uuid] = driver_uuid

    drivers_all = drivers_base().order_by(Driver.id.asc()).all()
    vehicles_all = vehicles_base().order_by(Vehicle.id.asc()).all()
    vehicle_by_uuid: dict[str, Vehicle] = {
        str(v.uuid): v for v in vehicles_all if v.uuid
    }
    driver_by_uuid: dict[str, Driver] = {
        str(d.uuid): d for d in drivers_all if d.uuid
    }

    drivers_out: list[FleetDashboardDriverRow] = []
    for dr in drivers_all:
        dr_uuid = str(dr.uuid or "")
        linked_vehicle_uuid = str(dr.vehicle_uuid) if dr.vehicle_uuid else None
        fallback_vehicle_uuid = order_driver_to_vehicle.get(dr_uuid)
        # Prefer active order assignment so dispatch matches order detail; fall back to driver↔vehicle link.
        assigned_vehicle_uuid = fallback_vehicle_uuid or linked_vehicle_uuid
        assigned_vehicle = (
            vehicle_by_uuid.get(assigned_vehicle_uuid) if assigned_vehicle_uuid else None
        )
        drivers_out.append(
            FleetDashboardDriverRow(
                driver_uuid=dr_uuid,
                public_id=dr.public_id,
                status=dr.status,
                online=int(dr.online or 0),
                vehicle_uuid=assigned_vehicle_uuid,
                vehicle_plate=assigned_vehicle.plate_number if assigned_vehicle else None,
                latitude=_coerce_float(dr.latitude),
                longitude=_coerce_float(dr.longitude),
            )
        )

    # One driver per vehicle (first by id) for reverse link
    assigned: dict[str, Driver] = {}
    for dr in drivers_all:
        if not dr.vehicle_uuid:
            continue
        vu = str(dr.vehicle_uuid)
        if vu not in assigned:
            assigned[vu] = dr

    vehicles_out: list[FleetDashboardVehicleRow] = []
    for veh in vehicles_all:
        v_uuid = str(veh.uuid or "")
        dr_linked = assigned.get(v_uuid)
        fallback_driver_uuid = order_vehicle_to_driver.get(v_uuid)
        dr_order = (
            driver_by_uuid.get(fallback_driver_uuid) if fallback_driver_uuid else None
        )
        # Prefer active order assignment over driver.vehicle_uuid link (same as driver rows).
        effective_dr = dr_order or dr_linked
        lat_v, lng_v = _vehicle_meta_coords(veh.meta)
        if effective_dr and effective_dr.uuid:
            ad_uuid: Optional[str] = str(effective_dr.uuid)
            ad_name: Optional[str] = _driver_name(effective_dr)
        elif fallback_driver_uuid:
            ad_uuid = fallback_driver_uuid
            ad_name = None
        else:
            ad_uuid = None
            ad_name = None
        vehicles_out.append(
            FleetDashboardVehicleRow(
                vehicle_uuid=v_uuid,
                plate_number=veh.plate_number,
                status=veh.status,
                assigned_driver_uuid=ad_uuid,
                assigned_driver_name=ad_name,
                latitude=lat_v,
                longitude=lng_v,
            )
        )

    return FleetDashboardResponse(
        kpis=FleetDashboardKpis(
            drivers_total=drivers_total,
            drivers_active=drivers_active,
            drivers_online=drivers_online,
            drivers_on_active_orders=drivers_on_active_orders,
            drivers_unassigned=drivers_unassigned,
            vehicles_total=vehicles_total,
            vehicles_active=vehicles_active,
            vehicles_unassigned=vehicles_unassigned,
            vehicles_in_use=vehicles_in_use,
        ),
        drivers=drivers_out,
        vehicles=vehicles_out,
    )
