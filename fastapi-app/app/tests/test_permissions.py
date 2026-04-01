"""
Tests for permission management endpoints (/int/v1/permissions).
"""
import pytest
from fastapi import status


@pytest.mark.iam
class TestPermissionList:
    """Test permission listing endpoint."""

    def test_list_permissions_success(self, client, auth_headers, test_permission):
        """Test listing permissions with authentication."""
        response = client.get("/int/v1/permissions", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)

    def test_list_permissions_no_auth(self, client):
        """Test listing permissions without authentication."""
        response = client.get("/int/v1/permissions")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.iam
class TestPermissionGet:
    """Test get permission endpoint."""

    def test_get_permission_success(self, client, auth_headers, test_permission):
        """Test getting a permission by ID."""
        response = client.get(f"/int/v1/permissions/{test_permission.id}", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == test_permission.id
        assert data["name"] == test_permission.name


@pytest.mark.iam
class TestPermissionCreate:
    """Test permission creation endpoint."""

    def test_create_permission_success(self, client, auth_headers):
        """Test creating a new permission."""
        response = client.post(
            "/int/v1/permissions",
            headers=auth_headers,
            json={
                "name": "new.permission",
                "guard_name": "web",
            },
        )
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["name"] == "new.permission"
        assert "id" in data

