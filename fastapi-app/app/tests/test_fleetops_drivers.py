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
        assert "data" in data
        assert "total" in data
        assert "limit" in data
        assert "offset" in data
        assert isinstance(data["data"], list)
        assert data["total"] >= 1

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
        assert "driver" in data
        assert data["driver"]["public_id"] == test_driver.public_id
        assert data["driver"]["drivers_license_number"] == test_driver.drivers_license_number

    def test_get_driver_not_found(self, client, auth_headers):
        """Test getting non-existent driver."""
        response = client.get("/fleetops/v1/drivers/nonexistent", headers=auth_headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.fleetops
class TestDriverCreate:
    """Test driver creation endpoint."""

    def test_create_driver_success(self, client, auth_headers):
        """Test creating a new driver."""
        response = client.post(
            "/fleetops/v1/drivers",
            headers=auth_headers,
            json={
                "drivers_license_number": "DL-NEW-001",
                "status": "active",
            },
        )
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert "driver" in data
        assert data["driver"]["drivers_license_number"] == "DL-NEW-001"
        assert "public_id" in data["driver"]
        assert "uuid" in data["driver"]


@pytest.mark.fleetops
class TestDriverUpdate:
    """Test driver update endpoint."""

    def test_update_driver_success(self, client, auth_headers, test_driver):
        """Test updating a driver."""
        response = client.put(
            f"/fleetops/v1/drivers/{test_driver.public_id}",
            headers=auth_headers,
            json={
                "drivers_license_number": "DL-UPDATED-001",
                "status": "inactive",
            },
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["driver"]["drivers_license_number"] == "DL-UPDATED-001"
        assert data["driver"]["status"] == "inactive"


@pytest.mark.fleetops
class TestDriverStatus:
    """Test driver online toggle."""

    def test_toggle_driver_online(self, client, auth_headers, test_driver):
        """Test toggle-online endpoint."""
        response = client.post(
            f"/fleetops/v1/drivers/{test_driver.public_id}/toggle-online",
            headers=auth_headers,
        )
        assert response.status_code == status.HTTP_200_OK
        assert "driver" in response.json()
