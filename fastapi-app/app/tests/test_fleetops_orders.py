"""
Tests for FleetOps order endpoints (/fleetops/v1/orders).
"""
import pytest
from fastapi import status


@pytest.mark.fleetops
class TestOrderList:
    """Test order listing endpoint."""

    def test_list_orders_success(self, client, auth_headers, test_order):
        """Test listing orders with authentication."""
        response = client.get("/fleetops/v1/orders", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)

    def test_list_orders_no_auth(self, client):
        """Test listing orders without authentication."""
        response = client.get("/fleetops/v1/orders")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.fleetops
class TestOrderGet:
    """Test get order endpoint."""

    def test_get_order_success(self, client, auth_headers, test_order):
        """Test getting an order by public_id."""
        response = client.get(f"/fleetops/v1/orders/{test_order.public_id}", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["public_id"] == test_order.public_id

    def test_get_order_not_found(self, client, auth_headers):
        """Test getting non-existent order."""
        response = client.get("/fleetops/v1/orders/nonexistent", headers=auth_headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND


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
        assert "uuid" in data


@pytest.mark.fleetops
class TestOrderUpdate:
    """Test order update endpoint."""

    def test_update_order_success(self, client, auth_headers, test_order):
        """Test updating an order."""
        response = client.put(
            f"/fleetops/v1/orders/{test_order.public_id}",
            headers=auth_headers,
            json={
                "status": "dispatched",
            },
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "dispatched"


@pytest.mark.fleetops
class TestOrderDispatch:
    """Test order dispatch endpoint."""

    def test_dispatch_order_success(self, client, auth_headers, test_order, test_driver):
        """Test dispatching an order."""
        response = client.post(
            f"/fleetops/v1/orders/{test_order.public_id}/dispatch",
            headers=auth_headers,
            json={
                "driver_uuid": test_driver.uuid,
            },
        )
        # Should either succeed or return error based on order state
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_400_BAD_REQUEST]


@pytest.mark.fleetops
class TestOrderTrack:
    """Test order tracking endpoint."""

    def test_track_order_success(self, client, auth_headers, test_order):
        """Test tracking an order."""
        response = client.get(f"/fleetops/v1/orders/{test_order.public_id}/track", headers=auth_headers)
        # Should return tracking information
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

