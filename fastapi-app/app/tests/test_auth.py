"""
Tests for authentication endpoints (/int/v1/auth).
"""
import pytest
from fastapi import status

from app.core.security import get_password_hash


@pytest.mark.auth
class TestAuthLogin:
    """Test authentication login endpoint."""

    def test_login_with_email_success(self, client, db_session, test_user):
        """Test successful login with email."""
        response = client.post(
            "/int/v1/auth/login",
            json={
                "identity": "test@example.com",
                "password": "password123",
            },
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "token" in data
        assert data["type"] == test_user.type
        assert len(data["token"]) > 0
        user_obj = data.get("user") or {}
        assert user_obj.get("id") == test_user.uuid
        assert user_obj.get("role") == "ADMIN"

    def test_login_with_phone_success(self, client, db_session, test_user):
        """Test successful login with phone number."""
        response = client.post(
            "/int/v1/auth/login",
            json={
                "identity": "+1234567890",
                "password": "password123",
            },
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "token" in data

    def test_login_invalid_identity(self, client):
        """Test login with non-existent user (400 = identity not found)."""
        response = client.post(
            "/int/v1/auth/login",
            json={
                "identity": "nonexistent@example.com",
                "password": "password123",
            },
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "No user found" in response.json()["detail"]

    def test_login_invalid_password(self, client, test_user):
        """Test login with wrong password."""
        response = client.post(
            "/int/v1/auth/login",
            json={
                "identity": "test@example.com",
                "password": "wrongpassword",
            },
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Authentication failed" in response.json()["detail"]

    def test_login_missing_fields(self, client):
        """Test login with missing required fields."""
        response = client.post(
            "/int/v1/auth/login",
            json={},
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.auth
class TestAuthSession:
    """Test session endpoint."""

    def test_get_session_success(self, client, auth_headers):
        """Test getting current session with valid token."""
        response = client.get("/int/v1/auth/session", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "token" in data
        assert "user" in data
        assert "verified" in data
        assert "type" in data

    def test_get_session_no_token(self, client):
        """Test getting session without token."""
        response = client.get("/int/v1/auth/session")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_session_invalid_token(self, client):
        """Test getting session with invalid token."""
        response = client.get(
            "/int/v1/auth/session",
            headers={"Authorization": "Bearer invalid_token"},
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.auth
class TestAuthBootstrap:
    """Test bootstrap endpoint."""

    def test_bootstrap_success(self, client, auth_headers, test_user, test_company, test_company_user):
        """Test bootstrap endpoint with valid token."""
        response = client.get("/int/v1/auth/bootstrap", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "user" in data
        assert "organizations" in data
        assert isinstance(data["organizations"], list)
        if len(data["organizations"]) > 0:
            org = data["organizations"][0]
            assert "uuid" in org
            assert "name" in org

    def test_bootstrap_no_token(self, client):
        """Test bootstrap without token."""
        response = client.get("/int/v1/auth/bootstrap")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_bootstrap_invalid_token(self, client):
        """Test bootstrap with invalid token."""
        response = client.get(
            "/int/v1/auth/bootstrap",
            headers={"Authorization": "Bearer invalid_token"},
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

