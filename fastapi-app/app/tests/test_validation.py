"""
Tests for request/response schema validation.
"""
import pytest
from pydantic import ValidationError

from app.schemas.auth import LoginRequest, LoginResponse
from app.schemas.user import UserCreate, UserUpdate, UserOut
from app.schemas.company import CompanyCreate, CompanyUpdate
from app.schemas.order import OrderCreate, OrderUpdate
from app.schemas.driver import DriverCreate, DriverUpdate
from app.schemas.vehicle import VehicleCreate, VehicleUpdate
from app.schemas.contact import ContactCreate, ContactUpdate
from app.schemas.vendor import VendorCreate, VendorUpdate
from app.schemas.place import PlaceCreate, PlaceUpdate


@pytest.mark.unit
class TestAuthSchemas:
    """Test authentication schemas."""

    def test_login_request_valid(self):
        """Test valid login request."""
        request = LoginRequest(identity="test@example.com", password="password123")
        assert request.identity == "test@example.com"
        assert request.password == "password123"

    def test_login_request_missing_fields(self):
        """Test login request with missing fields."""
        with pytest.raises(ValidationError):
            LoginRequest(identity="test@example.com")

    def test_login_response_valid(self):
        """Test valid login response."""
        response = LoginResponse(token="test_token", type="user")
        assert response.token == "test_token"
        assert response.type == "user"


@pytest.mark.unit
class TestUserSchemas:
    """Test user schemas."""

    def test_user_create_valid(self):
        """Test valid user creation."""
        user = UserCreate(
            name="Test User",
            email="test@example.com",
            phone="+1234567890",
            password="password123",
        )
        assert user.name == "Test User"
        assert user.email == "test@example.com"

    def test_user_create_invalid_email(self):
        """Test user creation with invalid email."""
        with pytest.raises(ValidationError):
            UserCreate(
                name="Test User",
                email="invalid-email",
                phone="+1234567890",
                password="password123",
            )

    def test_user_update_partial(self):
        """Test user update with partial fields."""
        user = UserUpdate(name="Updated Name")
        assert user.name == "Updated Name"
        assert user.email is None


@pytest.mark.unit
class TestCompanySchemas:
    """Test company schemas."""

    def test_company_create_valid(self):
        """Test valid company creation."""
        company = CompanyCreate(
            name="Test Company",
            email="company@example.com",
            phone="+1234567890",
        )
        assert company.name == "Test Company"
        assert company.email == "company@example.com"


@pytest.mark.unit
class TestOrderSchemas:
    """Test order schemas."""

    def test_order_create_valid(self):
        """Test valid order creation."""
        order = OrderCreate(
            internal_id="ORD-001",
            status="pending",
        )
        assert order.internal_id == "ORD-001"
        assert order.status == "pending"

    def test_order_update_valid(self):
        """Test valid order update."""
        order = OrderUpdate(status="dispatched")
        assert order.status == "dispatched"


@pytest.mark.unit
class TestDriverSchemas:
    """Test driver schemas."""

    def test_driver_create_valid(self):
        """Test valid driver creation."""
        driver = DriverCreate(
            name="Test Driver",
            phone="+1234567890",
            email="driver@example.com",
            status="active",
        )
        assert driver.name == "Test Driver"
        assert driver.status == "active"

    def test_driver_update_valid(self):
        """Test valid driver update."""
        driver = DriverUpdate(name="Updated Driver")
        assert driver.name == "Updated Driver"


@pytest.mark.unit
class TestVehicleSchemas:
    """Test vehicle schemas."""

    def test_vehicle_create_valid(self):
        """Test valid vehicle creation."""
        vehicle = VehicleCreate(
            make="Toyota",
            model="Camry",
            year="2020",
            vin="TESTVIN123",
            plate_number="TEST123",
        )
        assert vehicle.make == "Toyota"
        assert vehicle.model == "Camry"

    def test_vehicle_update_valid(self):
        """Test valid vehicle update."""
        vehicle = VehicleUpdate(plate_number="UPDATED123")
        assert vehicle.plate_number == "UPDATED123"


@pytest.mark.unit
class TestContactSchemas:
    """Test contact schemas."""

    def test_contact_create_valid(self):
        """Test valid contact creation."""
        contact = ContactCreate(
            name="Test Contact",
            phone="+1234567890",
            email="contact@example.com",
        )
        assert contact.name == "Test Contact"
        assert contact.email == "contact@example.com"


@pytest.mark.unit
class TestVendorSchemas:
    """Test vendor schemas."""

    def test_vendor_create_valid(self):
        """Test valid vendor creation."""
        vendor = VendorCreate(
            name="Test Vendor",
            phone="+1234567890",
            email="vendor@example.com",
        )
        assert vendor.name == "Test Vendor"
        assert vendor.email == "vendor@example.com"


@pytest.mark.unit
class TestPlaceSchemas:
    """Test place schemas."""

    def test_place_create_valid(self):
        """Test valid place creation."""
        place = PlaceCreate(
            name="Test Place",
            address="123 Test St",
            city="Test City",
            country="US",
            latitude=40.7128,
            longitude=-74.0060,
        )
        assert place.name == "Test Place"
        assert place.latitude == 40.7128
        assert place.longitude == -74.0060

    def test_place_create_invalid_coordinates(self):
        """Test place creation with invalid coordinates."""
        with pytest.raises(ValidationError):
            PlaceCreate(
                name="Test Place",
                address="123 Test St",
                city="Test City",
                country="US",
                latitude=200.0,  # Invalid latitude
                longitude=-74.0060,
            )

