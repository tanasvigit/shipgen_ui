# FastAPI Test Suite

This directory contains comprehensive tests for the FastAPI application migrated from Laravel.

## Test Structure

- **`conftest.py`**: Pytest configuration, fixtures, and test database setup
- **`test_auth.py`**: Authentication, session, and bootstrap endpoint tests
- **`test_users.py`**: User management endpoint tests
- **`test_companies.py`**: Company management endpoint tests
- **`test_roles.py`**: Role management endpoint tests
- **`test_permissions.py`**: Permission management endpoint tests
- **`test_policies.py`**: Policy management endpoint tests
- **`test_twofa.py`**: 2FA flow and settings tests
- **`test_notifications.py`**: Notification management tests
- **`test_fleetops_orders.py`**: FleetOps order endpoint tests
- **`test_fleetops_drivers.py`**: FleetOps driver endpoint tests
- **`test_fleetops_vehicles.py`**: FleetOps vehicle endpoint tests
- **`test_fleetops_contacts.py`**: FleetOps contact endpoint tests
- **`test_fleetops_vendors.py`**: FleetOps vendor endpoint tests
- **`test_fleetops_places.py`**: FleetOps place endpoint tests
- **`test_validation.py`**: Pydantic schema validation tests

## Running Tests

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Run All Tests

```bash
pytest
```

### Run Specific Test File

```bash
pytest app/tests/test_auth.py
```

### Run Tests by Marker

```bash
# Run only authentication tests
pytest -m auth

# Run only IAM tests
pytest -m iam

# Run only FleetOps tests
pytest -m fleetops

# Run only 2FA tests
pytest -m twofa

# Run only notification tests
pytest -m notifications

# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration
```

### Run with Coverage

```bash
pytest --cov=app --cov-report=html
```

This will generate an HTML coverage report in `htmlcov/index.html`.

### Run with Verbose Output

```bash
pytest -v
```

## Test Database

Tests use an in-memory SQLite database (`sqlite:///:memory:`) for fast execution. Each test gets a fresh database session that is automatically cleaned up after the test completes.

## Fixtures

Common fixtures available in `conftest.py`:

- `db_session`: Fresh database session for each test
- `client`: FastAPI test client with database override
- `test_user`: Test user with UUID and credentials
- `test_company`: Test company with UUID
- `test_company_user`: Company-user relationship
- `auth_token`: JWT token for test user
- `auth_headers`: Authorization headers for authenticated requests
- `test_role`: Test role
- `test_permission`: Test permission
- `test_policy`: Test policy
- `test_driver`: Test driver
- `test_vehicle`: Test vehicle
- `test_order`: Test order
- `test_contact`: Test contact
- `test_vendor`: Test vendor
- `test_place`: Test place

## Test Markers

Tests are organized with markers for easy filtering:

- `@pytest.mark.auth`: Authentication tests
- `@pytest.mark.iam`: IAM (users, companies, roles, permissions, policies) tests
- `@pytest.mark.fleetops`: FleetOps tests
- `@pytest.mark.twofa`: 2FA tests
- `@pytest.mark.notifications`: Notification tests
- `@pytest.mark.unit`: Unit tests (schema validation, etc.)
- `@pytest.mark.integration`: Integration tests (API endpoints)

## Writing New Tests

When adding new tests:

1. Use appropriate fixtures from `conftest.py`
2. Add appropriate markers (`@pytest.mark.*`)
3. Follow the existing test structure and naming conventions
4. Test both success and failure cases
5. Test authentication/authorization requirements
6. Test validation errors

## Example Test

```python
@pytest.mark.fleetops
class TestOrderCreate:
    """Test order creation endpoint."""

    def test_create_order_success(self, client, auth_headers, test_company):
        """Test creating a new order."""
        response = client.post(
            "/fleetops/v1/orders",
            headers=auth_headers,
            json={
                "internal_id": "ORD-TEST-001",
                "status": "pending",
            },
        )
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["internal_id"] == "ORD-TEST-001"
        assert "public_id" in data
```

## Notes

- Tests use SQLite in-memory database for speed
- Each test is isolated with its own database session
- Authentication is handled via JWT tokens in fixtures
- Tests verify both success and error cases
- Schema validation is tested separately in `test_validation.py`

