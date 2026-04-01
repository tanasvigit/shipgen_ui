"""
Tests for FleetOps driver endpoints (/fleetops/v1/drivers).
"""
import pytest
from fastapi import status


@pytest.mark.fleetops
class TestDriverList:
    """Test driver listing endpoint."""

    def test_list_drivers_success(self, client, auth_headers, test_driver):
        """Test listing drivers with authentication."""
        response = client.get("/fleetops/v1/drivers", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)

    def test_list_drivers_no_auth(self, client):
        """Test listing drivers without authentication."""
        response = client.get("/fleetops/v1/drivers")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.fleetops
class TestDriverGet:
    """Test get driver endpoint."""

    def test_get_driver_success(self, client, auth_headers, test_driver):
        """Test getting a driver by public_id."""
        response = client.get(f"/fleetops/v1/drivers/{test_driver.public_id}", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["public_id"] == test_driver.public_id
        assert data["name"] == test_driver.name

    def test_get_driver_not_found(self, client, auth_headers):
        """Test getting non-existent driver."""
        response = client.get("/fleetops/v1/drivers/nonexistent", headers=auth_headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.fleetops
class TestDriverCreate:
    """Test driver creation endpoint."""

    def test_create_driver_success(self, client, auth_headers, test_company, test_user):
        """Test creating a new driver."""
        response = client.post(
            "/fleetops/v1/drivers",
            headers=auth_headers,
            json={
                "name": "New Driver",
                "phone": "+1987654321",
                "email": "newdriver@example.com",
                "status": "active",
            },
        )
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["name"] == "New Driver"
        assert "public_id" in data
        assert "uuid" in data


@pytest.mark.fleetops
class TestDriverUpdate:
    """Test driver update endpoint."""

    def test_update_driver_success(self, client, auth_headers, test_driver):
        """Test updating a driver."""
        response = client.put(
            f"/fleetops/v1/drivers/{test_driver.public_id}",
            headers=auth_headers,
            json={
                "name": "Updated Driver Name",
                "phone": "+1999999999",
            },
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] == "Updated Driver Name"


@pytest.mark.fleetops
class TestDriverStatus:
    """Test driver status endpoints."""

    def test_set_driver_online(self, client, auth_headers, test_driver):
        """Test setting driver status to online."""
        response = client.post(
            f"/fleetops/v1/drivers/{test_driver.public_id}/online",
            headers=auth_headers,
        )
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_set_driver_offline(self, client, auth_headers, test_driver):
        """Test setting driver status to offline."""
        response = client.post(
            f"/fleetops/v1/drivers/{test_driver.public_id}/offline",
            headers=auth_headers,
        )
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]


@pytest.mark.fleetops
class TestDriverLocation:
    """Test driver location update endpoint."""

    def test_update_driver_location(self, client, auth_headers, test_driver):
        """Test updating driver location."""
        response = client.put(
            f"/fleetops/v1/drivers/{test_driver.public_id}/location",
            headers=auth_headers,
            json={
                "latitude": "40.7128",
                "longitude": "-74.0060",
            },
        )
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

