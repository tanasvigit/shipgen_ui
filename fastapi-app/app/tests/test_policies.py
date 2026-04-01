"""
Tests for policy management endpoints (/int/v1/policies).
"""
import pytest
from fastapi import status


@pytest.mark.iam
class TestPolicyList:
    """Test policy listing endpoint."""

    def test_list_policies_success(self, client, auth_headers, test_policy):
        """Test listing policies with authentication."""
        response = client.get("/int/v1/policies", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)

    def test_list_policies_no_auth(self, client):
        """Test listing policies without authentication."""
        response = client.get("/int/v1/policies")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.iam
class TestPolicyGet:
    """Test get policy endpoint."""

    def test_get_policy_success(self, client, auth_headers, test_policy):
        """Test getting a policy by ID."""
        response = client.get(f"/int/v1/policies/{test_policy.id}", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == test_policy.id
        assert data["name"] == test_policy.name


@pytest.mark.iam
class TestPolicyCreate:
    """Test policy creation endpoint."""

    def test_create_policy_success(self, client, auth_headers, test_company):
        """Test creating a new policy."""
        response = client.post(
            "/int/v1/policies",
            headers=auth_headers,
            json={
                "name": "new_policy",
                "company_uuid": test_company.uuid,
                "guard_name": "web",
            },
        )
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["name"] == "new_policy"
        assert "id" in data

