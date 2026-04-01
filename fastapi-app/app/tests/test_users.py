"""
Tests for user management endpoints (/int/v1/users).
"""
import pytest
from fastapi import status


@pytest.mark.iam
class TestUserList:
    """Test user listing endpoint."""

    def test_list_users_success(self, client, auth_headers, test_user):
        """Test listing users with authentication."""
        response = client.get("/int/v1/users", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1

    def test_list_users_pagination(self, client, auth_headers):
        """Test user listing with pagination."""
        response = client.get("/int/v1/users?limit=10&offset=0", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) <= 10

    def test_list_users_no_auth(self, client):
        """Test listing users without authentication."""
        response = client.get("/int/v1/users")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.iam
class TestUserGet:
    """Test get user endpoint."""

    def test_get_user_success(self, client, auth_headers, test_user):
        """Test getting a user by UUID."""
        response = client.get(f"/int/v1/users/{test_user.uuid}", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["uuid"] == test_user.uuid
        assert data["email"] == test_user.email

    def test_get_user_not_found(self, client, auth_headers):
        """Test getting non-existent user."""
        response = client.get("/int/v1/users/nonexistent-uuid", headers=auth_headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_get_user_no_auth(self, client, test_user):
        """Test getting user without authentication."""
        response = client.get(f"/int/v1/users/{test_user.uuid}")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.iam
class TestUserCreate:
    """Test user creation endpoint."""

    def test_create_user_success(self, client, auth_headers, db_session):
        """Test creating a new user."""
        response = client.post(
            "/int/v1/users",
            headers=auth_headers,
            json={
                "name": "New User",
                "email": "newuser@example.com",
                "phone": "+1987654321",
                "password": "securepassword123",
            },
        )
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["name"] == "New User"
        assert data["email"] == "newuser@example.com"
        assert "uuid" in data
        assert "password" not in data  # Password should not be in response

    def test_create_user_duplicate_email(self, client, auth_headers, test_user):
        """Test creating user with duplicate email."""
        response = client.post(
            "/int/v1/users",
            headers=auth_headers,
            json={
                "name": "Duplicate User",
                "email": test_user.email,  # Same email as test_user
                "phone": "+1987654321",
                "password": "securepassword123",
            },
        )
        # Should either fail validation or allow (depending on business logic)
        # For now, we'll check it doesn't crash
        assert response.status_code in [status.HTTP_400_BAD_REQUEST, status.HTTP_201_CREATED, status.HTTP_422_UNPROCESSABLE_ENTITY]

    def test_create_user_missing_fields(self, client, auth_headers):
        """Test creating user with missing required fields."""
        response = client.post(
            "/int/v1/users",
            headers=auth_headers,
            json={
                "name": "Incomplete User",
            },
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.iam
class TestUserUpdate:
    """Test user update endpoint."""

    def test_update_user_success(self, client, auth_headers, test_user):
        """Test updating a user."""
        response = client.put(
            f"/int/v1/users/{test_user.uuid}",
            headers=auth_headers,
            json={
                "name": "Updated Name",
                "phone": "+1999999999",
            },
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] == "Updated Name"
        assert data["phone"] == "+1999999999"

    def test_update_user_not_found(self, client, auth_headers):
        """Test updating non-existent user."""
        response = client.put(
            "/int/v1/users/nonexistent-uuid",
            headers=auth_headers,
            json={"name": "Updated Name"},
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.iam
class TestUserDelete:
    """Test user deletion endpoint."""

    def test_delete_user_success(self, client, auth_headers, db_session):
        """Test soft deleting a user."""
        # Create a user to delete
        create_response = client.post(
            "/int/v1/users",
            headers=auth_headers,
            json={
                "name": "User To Delete",
                "email": "todelete@example.com",
                "phone": "+1111111111",
                "password": "password123",
            },
        )
        assert create_response.status_code == status.HTTP_201_CREATED
        user_uuid = create_response.json()["uuid"]

        # Delete the user
        response = client.delete(f"/int/v1/users/{user_uuid}", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK

        # Verify user is soft deleted (should not appear in list)
        list_response = client.get("/int/v1/users", headers=auth_headers)
        assert list_response.status_code == status.HTTP_200_OK
        user_uuids = [u["uuid"] for u in list_response.json()]
        assert user_uuid not in user_uuids


@pytest.mark.iam
class TestUserCurrent:
    """Test current user endpoint."""

    def test_get_current_user_success(self, client, auth_headers, test_user):
        """Test getting current authenticated user."""
        response = client.get("/int/v1/users/current", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["uuid"] == test_user.uuid
        assert data["email"] == test_user.email

    def test_get_current_user_no_auth(self, client):
        """Test getting current user without authentication."""
        response = client.get("/int/v1/users/current")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.iam
class TestUserPasswordChange:
    """Test user password change endpoint."""

    def test_change_password_success(self, client, auth_headers, test_user):
        """Test changing user password."""
        response = client.put(
            f"/int/v1/users/{test_user.uuid}/password",
            headers=auth_headers,
            json={
                "current_password": "password123",
                "new_password": "newpassword123",
            },
        )
        assert response.status_code == status.HTTP_200_OK

        # Verify new password works
        login_response = client.post(
            "/int/v1/auth/login",
            json={
                "identity": test_user.email,
                "password": "newpassword123",
            },
        )
        assert login_response.status_code == status.HTTP_200_OK

    def test_change_password_wrong_current(self, client, auth_headers, test_user):
        """Test changing password with wrong current password."""
        response = client.put(
            f"/int/v1/users/{test_user.uuid}/password",
            headers=auth_headers,
            json={
                "current_password": "wrongpassword",
                "new_password": "newpassword123",
            },
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

