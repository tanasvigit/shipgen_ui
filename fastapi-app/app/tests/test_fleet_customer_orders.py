import uuid

from fastapi import status

from app.core.security import create_access_token, get_password_hash
from app.models.driver import Driver
from app.models.order import Order
from app.models.user import User
from app.models.vehicle import Vehicle


def _make_user(db_session, *, company_uuid: str, role: str, email: str) -> User:
    user = User(
        uuid=str(uuid.uuid4()),
        public_id=f"user_{uuid.uuid4().hex[:8]}",
        company_uuid=company_uuid,
        name=role.title(),
        email=email,
        password=get_password_hash("password123"),
        type="user",
        role=role,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


def _headers_for(user: User) -> dict[str, str]:
    token = create_access_token(subject=user.uuid, token_type=user.type)
    return {"Authorization": f"Bearer {token}"}


def test_fleet_customer_creates_order_and_sees_only_own(db_session, client, test_company):
    fleet_customer = _make_user(
        db_session, company_uuid=test_company.uuid, role="FLEET_CUSTOMER", email="fc@test.example"
    )
    other_customer = _make_user(
        db_session, company_uuid=test_company.uuid, role="FLEET_CUSTOMER", email="fc2@test.example"
    )
    admin = _make_user(db_session, company_uuid=test_company.uuid, role="ADMIN", email="admin@test.example")

    own_create = client.post(
        "/orders",
        headers=_headers_for(fleet_customer),
        json={
            "pickup_location": "A Warehouse",
            "drop_location": "B Store",
            "goods_description": "Food packages",
        },
    )
    assert own_create.status_code == status.HTTP_201_CREATED
    own_id = own_create.json()["order"]["public_id"]

    other_create = client.post(
        "/orders",
        headers=_headers_for(other_customer),
        json={
            "pickup_location": "X Warehouse",
            "drop_location": "Y Store",
            "goods_description": "Medical items",
        },
    )
    assert other_create.status_code == status.HTTP_201_CREATED
    other_id = other_create.json()["order"]["public_id"]

    own_list = client.get("/orders", headers=_headers_for(fleet_customer))
    assert own_list.status_code == status.HTTP_200_OK
    own_public_ids = {row["public_id"] for row in own_list.json()["orders"]}
    assert own_id in own_public_ids
    assert other_id not in own_public_ids

    forbidden_get = client.get(f"/orders/{other_id}", headers=_headers_for(fleet_customer))
    assert forbidden_get.status_code == status.HTTP_404_NOT_FOUND

    # Admin can still view company-scoped orders.
    admin_list = client.get("/orders", headers=_headers_for(admin))
    assert admin_list.status_code == status.HTTP_200_OK
    admin_ids = {row["public_id"] for row in admin_list.json()["orders"]}
    assert own_id in admin_ids and other_id in admin_ids


def test_admin_assigns_driver_and_vehicle(db_session, client, test_company):
    admin = _make_user(db_session, company_uuid=test_company.uuid, role="ADMIN", email="admin2@test.example")
    fleet_customer = _make_user(
        db_session, company_uuid=test_company.uuid, role="FLEET_CUSTOMER", email="fc3@test.example"
    )
    driver_user = _make_user(db_session, company_uuid=test_company.uuid, role="DRIVER", email="driver@test.example")

    driver = Driver(
        uuid=str(uuid.uuid4()),
        public_id=f"drv_{uuid.uuid4().hex[:8]}",
        company_uuid=test_company.uuid,
        user_uuid=driver_user.uuid,
        status="active",
        online=1,
    )
    vehicle = Vehicle(
        uuid=str(uuid.uuid4()),
        public_id=f"veh_{uuid.uuid4().hex[:8]}",
        company_uuid=test_company.uuid,
        status="active",
        make="Toyota",
        model="Hiace",
        plate_number="TST-100",
    )
    db_session.add(driver)
    db_session.add(vehicle)
    db_session.commit()

    created = client.post(
        "/orders",
        headers=_headers_for(fleet_customer),
        json={
            "pickup_location": "Pickup Point",
            "drop_location": "Drop Point",
            "goods_description": "Electronics",
        },
    )
    assert created.status_code == status.HTTP_201_CREATED
    order_id = created.json()["order"]["public_id"]

    assign = client.patch(
        f"/orders/{order_id}/assign",
        headers=_headers_for(admin),
        json={"driver_id": driver.public_id, "vehicle_id": vehicle.public_id},
    )
    assert assign.status_code == status.HTTP_200_OK
    data = assign.json()["order"]
    assert data["status"] == "ASSIGNED"
    assert data["driver_assigned_uuid"] == driver.uuid
    assert data["vehicle_assigned_uuid"] == vehicle.uuid


def test_driver_starts_trip_only_when_assigned(db_session, client, test_company):
    admin = _make_user(db_session, company_uuid=test_company.uuid, role="ADMIN", email="admin3@test.example")
    fleet_customer = _make_user(
        db_session, company_uuid=test_company.uuid, role="FLEET_CUSTOMER", email="fc4@test.example"
    )
    driver_user = _make_user(db_session, company_uuid=test_company.uuid, role="DRIVER", email="driver2@test.example")
    other_driver_user = _make_user(
        db_session, company_uuid=test_company.uuid, role="DRIVER", email="driver3@test.example"
    )

    driver = Driver(
        uuid=str(uuid.uuid4()),
        public_id=f"drv_{uuid.uuid4().hex[:8]}",
        company_uuid=test_company.uuid,
        user_uuid=driver_user.uuid,
        status="active",
        online=1,
    )
    other_driver = Driver(
        uuid=str(uuid.uuid4()),
        public_id=f"drv_{uuid.uuid4().hex[:8]}",
        company_uuid=test_company.uuid,
        user_uuid=other_driver_user.uuid,
        status="active",
        online=1,
    )
    vehicle = Vehicle(
        uuid=str(uuid.uuid4()),
        public_id=f"veh_{uuid.uuid4().hex[:8]}",
        company_uuid=test_company.uuid,
        status="active",
    )
    db_session.add_all([driver, other_driver, vehicle])
    db_session.commit()

    created = client.post(
        "/orders",
        headers=_headers_for(fleet_customer),
        json={
            "pickup_location": "P1",
            "drop_location": "P2",
            "goods_description": "Bulk goods",
        },
    )
    assert created.status_code == status.HTTP_201_CREATED
    order_public_id = created.json()["order"]["public_id"]

    # Starting before assignment should fail.
    early_start = client.post(
        "/trips/start",
        headers=_headers_for(driver_user),
        json={"order_id": order_public_id, "current_location": {"lat": 1.0, "lng": 2.0}},
    )
    assert early_start.status_code == status.HTTP_409_CONFLICT

    assign = client.patch(
        f"/orders/{order_public_id}/assign",
        headers=_headers_for(admin),
        json={"driver_id": driver.public_id, "vehicle_id": vehicle.public_id},
    )
    assert assign.status_code == status.HTTP_200_OK

    # Wrong driver cannot start.
    wrong_driver_start = client.post(
        "/trips/start",
        headers=_headers_for(other_driver_user),
        json={"order_id": order_public_id, "current_location": {"lat": 1.0, "lng": 2.0}},
    )
    assert wrong_driver_start.status_code == status.HTTP_403_FORBIDDEN

    # Assigned driver can start.
    started = client.post(
        "/trips/start",
        headers=_headers_for(driver_user),
        json={"order_id": order_public_id, "current_location": {"lat": 25.2, "lng": 55.2}},
    )
    assert started.status_code == status.HTTP_200_OK
    out = started.json()["order"]
    assert out["status"] == "IN_PROGRESS"
    assert out["trip"] is not None
    assert out["trip"]["status"] == "IN_PROGRESS"
    assert out["trip"]["current_location"] == {"lat": 25.2, "lng": 55.2}

    db_order = db_session.query(Order).filter(Order.public_id == order_public_id).first()
    assert db_order is not None
    assert db_order.status == "IN_PROGRESS"
