"""
Tests for company management endpoints (/int/v1/companies).
"""
import pytest
from fastapi import status


@pytest.mark.iam
class TestCompanyList:
    """Test company listing endpoint."""

    def test_list_companies_success(self, client, auth_headers, test_company):
        """Test listing companies with authentication."""
        response = client.get("/int/v1/companies", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)

    def test_list_companies_no_auth(self, client):
        """Test listing companies without authentication."""
        response = client.get("/int/v1/companies")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.iam
class TestCompanyGet:
    """Test get company endpoint."""

    def test_get_company_success(self, client, auth_headers, test_company):
        """Test getting a company by UUID."""
        response = client.get(f"/int/v1/companies/{test_company.uuid}", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["uuid"] == test_company.uuid
        assert data["name"] == test_company.name

    def test_get_company_not_found(self, client, auth_headers):
        """Test getting non-existent company."""
        response = client.get("/int/v1/companies/nonexistent-uuid", headers=auth_headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.iam
class TestCompanyCreate:
    """Test company creation endpoint."""

    def test_create_company_success(self, client, auth_headers):
        """Test creating a new company."""
        response = client.post(
            "/int/v1/companies",
            headers=auth_headers,
            json={
                "name": "New Company",
                "phone": "+1987654321",
                "email": "newcompany@example.com",
            },
        )
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["name"] == "New Company"
        assert "uuid" in data


@pytest.mark.iam
class TestCompanyUpdate:
    """Test company update endpoint."""

    def test_update_company_success(self, client, auth_headers, test_company):
        """Test updating a company."""
        response = client.put(
            f"/int/v1/companies/{test_company.uuid}",
            headers=auth_headers,
            json={
                "name": "Updated Company Name",
                "phone": "+1999999999",
            },
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] == "Updated Company Name"


@pytest.mark.iam
class TestCompanyUsers:
    """Test company users endpoint."""

    def test_list_company_users_success(self, client, auth_headers, test_company, test_company_user):
        """Test listing users for a company."""
        response = client.get(f"/int/v1/companies/{test_company.uuid}/users", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)

