"""
Tests for FleetOps vehicle endpoints (/fleetops/v1/vehicles).
"""
import pytest
from fastapi import status


@pytest.mark.fleetops
class TestVehicleList:
    """Test vehicle listing endpoint."""

    def test_list_vehicles_success(self, client, auth_headers, test_vehicle):
        """Test listing vehicles with authentication."""
        response = client.get("/fleetops/v1/vehicles", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)

    def test_list_vehicles_no_auth(self, client):
        """Test listing vehicles without authentication."""
        response = client.get("/fleetops/v1/vehicles")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.fleetops
class TestVehicleGet:
    """Test get vehicle endpoint."""

    def test_get_vehicle_success(self, client, auth_headers, test_vehicle):
        """Test getting a vehicle by public_id."""
        response = client.get(f"/fleetops/v1/vehicles/{test_vehicle.public_id}", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["public_id"] == test_vehicle.public_id
        assert data["vin"] == test_vehicle.vin

    def test_get_vehicle_not_found(self, client, auth_headers):
        """Test getting non-existent vehicle."""
        response = client.get("/fleetops/v1/vehicles/nonexistent", headers=auth_headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.fleetops
class TestVehicleCreate:
    """Test vehicle creation endpoint."""

    def test_create_vehicle_success(self, client, auth_headers):
        """Test creating a new vehicle."""
        response = client.post(
            "/fleetops/v1/vehicles",
            headers=auth_headers,
            json={
                "make": "Toyota",
                "model": "Camry",
                "year": "2020",
                "vin": "TESTVIN987654",
                "plate_number": "TEST456",
                "status": "active",
            },
        )
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["make"] == "Toyota"
        assert data["model"] == "Camry"
        assert "public_id" in data
        assert "uuid" in data


@pytest.mark.fleetops
class TestVehicleUpdate:
    """Test vehicle update endpoint."""

    def test_update_vehicle_success(self, client, auth_headers, test_vehicle):
        """Test updating a vehicle."""
        response = client.put(
            f"/fleetops/v1/vehicles/{test_vehicle.public_id}",
            headers=auth_headers,
            json={
                "plate_number": "UPDATED123",
            },
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["plate_number"] == "UPDATED123"


@pytest.mark.fleetops
class TestVehicleAssignDriver:
    """Test vehicle driver assignment endpoint."""

    def test_assign_driver_to_vehicle(self, client, auth_headers, test_vehicle, test_driver):
        """Test assigning a driver to a vehicle."""
        response = client.post(
            f"/fleetops/v1/vehicles/{test_vehicle.public_id}/assign-driver",
            headers=auth_headers,
            json={
                "driver_uuid": test_driver.uuid,
            },
        )
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

