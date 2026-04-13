from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.roles import ADMIN, DRIVER, FLEET_CUSTOMER, require_roles
from app.models.user import User
from app.schemas.fleet_customer import (
    FleetCustomerOrderCreate,
    FleetCustomerOrderResponse,
    FleetCustomerOrdersResponse,
    OrderAssignmentRequest,
    TripStartRequest,
)
from app.services.fleet_customer_orders import (
    assign_order,
    create_customer_order,
    get_order_for_role,
    list_orders_for_role,
    start_trip,
)

router = APIRouter(tags=["fleet-customer-orders"])


@router.post("/orders", response_model=FleetCustomerOrderResponse, status_code=status.HTTP_201_CREATED)
@router.post("/orders/", response_model=FleetCustomerOrderResponse, status_code=status.HTTP_201_CREATED, include_in_schema=False)
def post_order(
    payload: FleetCustomerOrderCreate,
    db: Session = Depends(get_db),
    current: User = Depends(require_roles(FLEET_CUSTOMER)),
):
    order = create_customer_order(
        db,
        current,
        internal_id=payload.internal_id,
        pickup_location=payload.pickup_location,
        drop_location=payload.drop_location,
        goods_description=payload.goods_description,
    )
    return {"order": order}


@router.get("/orders", response_model=FleetCustomerOrdersResponse)
@router.get("/orders/", response_model=FleetCustomerOrdersResponse, include_in_schema=False)
def get_orders(
    db: Session = Depends(get_db),
    current: User = Depends(require_roles(FLEET_CUSTOMER)),
):
    return {"orders": list_orders_for_role(db, current)}


@router.get("/orders/{order_id}", response_model=FleetCustomerOrderResponse)
def get_order(
    order_id: str,
    db: Session = Depends(get_db),
    current: User = Depends(require_roles(FLEET_CUSTOMER)),
):
    return {"order": get_order_for_role(db, current, order_id)}


@router.patch("/orders/{order_id}/assign", response_model=FleetCustomerOrderResponse)
def patch_assign_order(
    order_id: str,
    payload: OrderAssignmentRequest,
    db: Session = Depends(get_db),
    current: User = Depends(require_roles(ADMIN)),
):
    order = assign_order(
        db,
        current,
        order_id,
        driver_id=payload.driver_id,
        vehicle_id=payload.vehicle_id,
    )
    return {"order": order}


@router.post("/trips/start", response_model=FleetCustomerOrderResponse)
def post_start_trip(
    payload: TripStartRequest,
    db: Session = Depends(get_db),
    current: User = Depends(require_roles(DRIVER)),
):
    return {"order": start_trip(db, current, order_id=payload.order_id, current_location=payload.current_location)}
