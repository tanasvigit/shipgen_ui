"""
Pytest configuration and fixtures for FastAPI tests.
"""
import pytest
import uuid
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base, get_db
from app.main import create_app
from app.models import (
    User,
    Company,
    CompanyUser,
    Role,
    Permission,
    Policy,
    Order,
    Driver,
    Vehicle,
    Contact,
    Vendor,
    Place,
    Notification,
    TwoFaSession,
    Trip,
)
from app.core.security import get_password_hash, create_access_token


# Test database URL (SQLite in-memory for speed)
TEST_DATABASE_URL = "sqlite:///:memory:"


@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database session for each test."""
    engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    # Create all tables
    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """Create a test client with database override."""
    app = create_app()

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def test_user(db_session, test_company):
    """Create a test user scoped to test_company (fleetops tenancy)."""
    user_uuid = str(uuid.uuid4())
    user = User(
        uuid=user_uuid,
        public_id="test_user_123",
        company_uuid=test_company.uuid,
        name="Test User",
        email="test@example.com",
        password=get_password_hash("password123"),
        phone="+1234567890",
        type="user",
        role="ADMIN",
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def test_company(db_session):
    """Create a test company."""
    company_uuid = str(uuid.uuid4())
    company = Company(
        uuid=company_uuid,
        public_id="test_company_123",
        name="Test Company",
        phone="+1234567890",
    )
    db_session.add(company)
    db_session.commit()
    db_session.refresh(company)
    return company


@pytest.fixture
def test_company_user(db_session, test_user, test_company):
    """Create a company-user relationship."""
    existing = (
        db_session.query(CompanyUser)
        .filter(
            CompanyUser.user_uuid == test_user.uuid,
            CompanyUser.company_uuid == test_company.uuid,
            CompanyUser.deleted_at.is_(None),
        )
        .first()
    )
    if existing:
        return existing
    company_user = CompanyUser(
        uuid=str(uuid.uuid4()),
        user_uuid=test_user.uuid,
        company_uuid=test_company.uuid,
        status="active",
    )
    db_session.add(company_user)
    db_session.commit()
    db_session.refresh(company_user)
    return company_user


@pytest.fixture
def auth_token(test_user):
    """Create a JWT token for the test user."""
    return create_access_token(subject=test_user.uuid, token_type=test_user.type)


@pytest.fixture
def auth_headers(auth_token):
    """Create authorization headers."""
    return {"Authorization": f"Bearer {auth_token}"}


@pytest.fixture
def test_role(db_session, test_company):
    """Create a test role."""
    role = Role(
        name="test_role",
        company_uuid=test_company.uuid,
        guard_name="web",
    )
    db_session.add(role)
    db_session.commit()
    db_session.refresh(role)
    return role


@pytest.fixture
def test_permission(db_session):
    """Create a test permission."""
    permission = Permission(
        name="test.permission",
        guard_name="web",
    )
    db_session.add(permission)
    db_session.commit()
    db_session.refresh(permission)
    return permission


@pytest.fixture
def test_policy(db_session, test_company):
    """Create a test policy."""
    policy = Policy(
        name="test_policy",
        company_uuid=test_company.uuid,
        guard_name="web",
    )
    db_session.add(policy)
    db_session.commit()
    db_session.refresh(policy)
    return policy


@pytest.fixture
def test_driver(db_session, test_company, test_user):
    """Create a test driver."""
    driver_uuid = str(uuid.uuid4())
    driver = Driver(
        uuid=driver_uuid,
        public_id="test_driver_123",
        company_uuid=test_company.uuid,
        user_uuid=test_user.uuid,
        drivers_license_number="DL-TEST-001",
        status="active",
        online=0,
    )
    db_session.add(driver)
    db_session.commit()
    db_session.refresh(driver)
    return driver


@pytest.fixture
def test_vehicle(db_session, test_company, test_driver):
    """Create a test vehicle."""
    vehicle_uuid = str(uuid.uuid4())
    vehicle = Vehicle(
        uuid=vehicle_uuid,
        public_id="test_vehicle_123",
        company_uuid=test_company.uuid,
        make="Toyota",
        model="Camry",
        year="2020",
        vin="TESTVIN123456",
        plate_number="TEST123",
        status="active",
    )
    db_session.add(vehicle)
    db_session.commit()
    db_session.refresh(vehicle)
    return vehicle


@pytest.fixture
def test_customer_contact(db_session, test_company):
    """Customer contact (type=customer) for order FK tests."""
    contact_uuid = str(uuid.uuid4())
    contact = Contact(
        uuid=contact_uuid,
        public_id="test_customer_contact_123",
        company_uuid=test_company.uuid,
        name="Test Customer",
        type="customer",
        phone="+10987654321",
        email="customer@test.example",
    )
    db_session.add(contact)
    db_session.commit()
    db_session.refresh(contact)
    return contact


@pytest.fixture
def test_order(db_session, test_company, test_driver, test_customer_contact):
    """Create a test order."""
    order_uuid = str(uuid.uuid4())
    order = Order(
        uuid=order_uuid,
        public_id="test_order_123",
        company_uuid=test_company.uuid,
        driver_assigned_uuid=test_driver.uuid,
        customer_uuid=test_customer_contact.uuid,
        customer_type="customer",
        type="pickup",
        internal_id="ORD-001",
        status="pending",
    )
    db_session.add(order)
    db_session.commit()
    db_session.refresh(order)
    return order


@pytest.fixture
def test_contact(db_session, test_company):
    """Create a test contact."""
    contact_uuid = str(uuid.uuid4())
    contact = Contact(
        uuid=contact_uuid,
        public_id="test_contact_123",
        company_uuid=test_company.uuid,
        name="Test Contact",
        phone="+1234567890",
        email="contact@example.com",
    )
    db_session.add(contact)
    db_session.commit()
    db_session.refresh(contact)
    return contact


@pytest.fixture
def test_vendor(db_session, test_company):
    """Create a test vendor."""
    vendor_uuid = str(uuid.uuid4())
    vendor = Vendor(
        uuid=vendor_uuid,
        public_id="test_vendor_123",
        company_uuid=test_company.uuid,
        name="Test Vendor",
        phone="+1234567890",
        email="vendor@example.com",
    )
    db_session.add(vendor)
    db_session.commit()
    db_session.refresh(vendor)
    return vendor


@pytest.fixture
def test_place(db_session, test_company):
    """Create a test place."""
    place_uuid = str(uuid.uuid4())
    place = Place(
        uuid=place_uuid,
        public_id="test_place_123",
        company_uuid=test_company.uuid,
        name="Test Place",
        address="123 Test St",
        city="Test City",
        country="US",
        latitude=40.7128,
        longitude=-74.0060,
    )
    db_session.add(place)
    db_session.commit()
    db_session.refresh(place)
    return place

