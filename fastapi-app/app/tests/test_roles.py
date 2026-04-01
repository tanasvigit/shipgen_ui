"""
Tests for role management endpoints (/int/v1/roles).
"""
import pytest
from fastapi import status


@pytest.mark.iam
class TestRoleList:
    """Test role listing endpoint."""

    def test_list_roles_success(self, client, auth_headers, test_role):
        """Test listing roles with authentication."""
        response = client.get("/int/v1/roles", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)

    def test_list_roles_no_auth(self, client):
        """Test listing roles without authentication."""
        response = client.get("/int/v1/roles")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.iam
class TestRoleGet:
    """Test get role endpoint."""

    def test_get_role_success(self, client, auth_headers, test_role):
        """Test getting a role by ID."""
        response = client.get(f"/int/v1/roles/{test_role.id}", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == test_role.id
        assert data["name"] == test_role.name

    def test_get_role_not_found(self, client, auth_headers):
        """Test getting non-existent role."""
        response = client.get("/int/v1/roles/99999", headers=auth_headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.iam
class TestRoleCreate:
    """Test role creation endpoint."""

    def test_create_role_success(self, client, auth_headers, test_company):
        """Test creating a new role."""
        response = client.post(
            "/int/v1/roles",
            headers=auth_headers,
            json={
                "name": "new_role",
                "company_uuid": test_company.uuid,
                "guard_name": "web",
            },
        )
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["name"] == "new_role"
        assert "id" in data


@pytest.mark.iam
class TestRoleUpdate:
    """Test role update endpoint."""

    def test_update_role_success(self, client, auth_headers, test_role):
        """Test updating a role."""
        response = client.put(
            f"/int/v1/roles/{test_role.id}",
            headers=auth_headers,
            json={
                "name": "updated_role_name",
            },
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] == "updated_role_name"


@pytest.mark.iam
class TestRoleDelete:
    """Test role deletion endpoint."""

    def test_delete_role_success(self, client, auth_headers, db_session, test_company):
        """Test deleting a role."""
        # Create a role to delete
        create_response = client.post(
            "/int/v1/roles",
            headers=auth_headers,
            json={
                "name": "role_to_delete",
                "company_uuid": test_company.uuid,
                "guard_name": "web",
            },
        )
        assert create_response.status_code == status.HTTP_201_CREATED
        role_id = create_response.json()["id"]

        # Delete the role
        response = client.delete(f"/int/v1/roles/{role_id}", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK

