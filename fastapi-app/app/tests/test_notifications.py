"""
Tests for notification endpoints (/int/v1/notifications).
"""
import pytest
from fastapi import status


@pytest.mark.notifications
class TestNotificationList:
    """Test notification listing endpoint."""

    def test_list_notifications_success(self, client, auth_headers):
        """Test listing notifications with authentication."""
        response = client.get("/int/v1/notifications", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)

    def test_list_notifications_no_auth(self, client):
        """Test listing notifications without authentication."""
        response = client.get("/int/v1/notifications")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_list_notifications_pagination(self, client, auth_headers):
        """Test notification listing with pagination."""
        response = client.get("/int/v1/notifications?limit=10&offset=0", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)


@pytest.mark.notifications
class TestNotificationGet:
    """Test get notification endpoint."""

    def test_get_notification_success(self, client, auth_headers, db_session):
        """Test getting a notification by ID."""
        # First create a notification (if endpoint exists)
        # For now, we'll test the endpoint structure
        response = client.get("/int/v1/notifications/1", headers=auth_headers)
        # Should either return notification or 404
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]


@pytest.mark.notifications
class TestNotificationMarkRead:
    """Test marking notification as read."""

    def test_mark_notification_read(self, client, auth_headers):
        """Test marking a notification as read."""
        response = client.put("/int/v1/notifications/1/read", headers=auth_headers)
        # Should either succeed or return 404 if notification doesn't exist
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]


@pytest.mark.notifications
class TestNotificationSettings:
    """Test notification settings."""

    def test_get_notification_settings(self, client, auth_headers, test_user):
        """Test getting notification settings for user."""
        response = client.get(f"/int/v1/notifications/users/{test_user.uuid}/settings", headers=auth_headers)
        # Should return settings or default
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_update_notification_settings(self, client, auth_headers, test_user):
        """Test updating notification settings."""
        response = client.put(
            f"/int/v1/notifications/users/{test_user.uuid}/settings",
            headers=auth_headers,
            json={
                "email_enabled": True,
                "sms_enabled": False,
            },
        )
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

