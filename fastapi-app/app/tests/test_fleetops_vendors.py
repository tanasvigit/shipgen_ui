"""
Tests for FleetOps vendor endpoints (/fleetops/v1/vendors).
"""
import pytest
from fastapi import status


@pytest.mark.fleetops
class TestVendorList:
    """Test vendor listing endpoint."""

    def test_list_vendors_success(self, client, auth_headers, test_vendor):
        """Test listing vendors with authentication."""
        response = client.get("/fleetops/v1/vendors", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)

    def test_list_vendors_no_auth(self, client):
        """Test listing vendors without authentication."""
        response = client.get("/fleetops/v1/vendors")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.fleetops
class TestVendorGet:
    """Test get vendor endpoint."""

    def test_get_vendor_success(self, client, auth_headers, test_vendor):
        """Test getting a vendor by public_id."""
        response = client.get(f"/fleetops/v1/vendors/{test_vendor.public_id}", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["public_id"] == test_vendor.public_id
        assert data["name"] == test_vendor.name

    def test_get_vendor_not_found(self, client, auth_headers):
        """Test getting non-existent vendor."""
        response = client.get("/fleetops/v1/vendors/nonexistent", headers=auth_headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.fleetops
class TestVendorCreate:
    """Test vendor creation endpoint."""

    def test_create_vendor_success(self, client, auth_headers):
        """Test creating a new vendor."""
        response = client.post(
            "/fleetops/v1/vendors",
            headers=auth_headers,
            json={
                "name": "New Vendor",
                "phone": "+1987654321",
                "email": "newvendor@example.com",
            },
        )
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["name"] == "New Vendor"
        assert "public_id" in data
        assert "uuid" in data


@pytest.mark.fleetops
class TestVendorUpdate:
    """Test vendor update endpoint."""

    def test_update_vendor_success(self, client, auth_headers, test_vendor):
        """Test updating a vendor."""
        response = client.put(
            f"/fleetops/v1/vendors/{test_vendor.public_id}",
            headers=auth_headers,
            json={
                "name": "Updated Vendor Name",
                "phone": "+1999999999",
            },
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] == "Updated Vendor Name"

