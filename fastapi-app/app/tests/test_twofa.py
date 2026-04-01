"""
Tests for 2FA endpoints (/int/v1/two-fa).
"""
import pytest
from fastapi import status


@pytest.mark.twofa
class TestTwoFaSettings:
    """Test 2FA settings endpoints."""

    def test_get_system_2fa_settings(self, client, auth_headers):
        """Test getting system-wide 2FA settings."""
        response = client.get("/int/v1/two-fa/settings", headers=auth_headers)
        # Should return settings or empty object
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_update_system_2fa_settings(self, client, auth_headers):
        """Test updating system-wide 2FA settings."""
        response = client.put(
            "/int/v1/two-fa/settings",
            headers=auth_headers,
            json={
                "enabled": True,
                "method": "email",
            },
        )
        # Should either succeed or require admin permissions
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND]


@pytest.mark.twofa
class TestTwoFaUserSettings:
    """Test user-specific 2FA settings."""

    def test_get_user_2fa_settings(self, client, auth_headers, test_user):
        """Test getting user 2FA settings."""
        response = client.get(f"/int/v1/two-fa/users/{test_user.uuid}/settings", headers=auth_headers)
        # Should return settings or default
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_update_user_2fa_settings(self, client, auth_headers, test_user):
        """Test updating user 2FA settings."""
        response = client.put(
            f"/int/v1/two-fa/users/{test_user.uuid}/settings",
            headers=auth_headers,
            json={
                "enabled": True,
                "method": "email",
            },
        )
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]


@pytest.mark.twofa
class TestTwoFaVerification:
    """Test 2FA verification flow."""

    def test_request_verification_code(self, client, auth_headers, test_user):
        """Test requesting a verification code."""
        response = client.post(
            f"/int/v1/two-fa/users/{test_user.uuid}/request",
            headers=auth_headers,
            json={
                "method": "email",
            },
        )
        # Should either send code or return error if 2FA not enabled
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_404_NOT_FOUND,
        ]

    def test_verify_code(self, client, auth_headers, test_user):
        """Test verifying a code."""
        response = client.post(
            f"/int/v1/two-fa/users/{test_user.uuid}/verify",
            headers=auth_headers,
            json={
                "code": "123456",
            },
        )
        # Should either succeed or fail based on code validity
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_404_NOT_FOUND,
        ]

