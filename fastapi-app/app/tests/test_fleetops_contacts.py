"""
Tests for FleetOps contact endpoints (/fleetops/v1/contacts).
"""
import pytest
from fastapi import status


@pytest.mark.fleetops
class TestContactList:
    """Test contact listing endpoint."""

    def test_list_contacts_success(self, client, auth_headers, test_contact):
        """Test listing contacts with authentication."""
        response = client.get("/fleetops/v1/contacts", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)

    def test_list_contacts_no_auth(self, client):
        """Test listing contacts without authentication."""
        response = client.get("/fleetops/v1/contacts")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.fleetops
class TestContactGet:
    """Test get contact endpoint."""

    def test_get_contact_success(self, client, auth_headers, test_contact):
        """Test getting a contact by public_id."""
        response = client.get(f"/fleetops/v1/contacts/{test_contact.public_id}", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["public_id"] == test_contact.public_id
        assert data["name"] == test_contact.name

    def test_get_contact_not_found(self, client, auth_headers):
        """Test getting non-existent contact."""
        response = client.get("/fleetops/v1/contacts/nonexistent", headers=auth_headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.fleetops
class TestContactCreate:
    """Test contact creation endpoint."""

    def test_create_contact_success(self, client, auth_headers):
        """Test creating a new contact."""
        response = client.post(
            "/fleetops/v1/contacts",
            headers=auth_headers,
            json={
                "name": "New Contact",
                "phone": "+1987654321",
                "email": "newcontact@example.com",
            },
        )
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["name"] == "New Contact"
        assert "public_id" in data
        assert "uuid" in data


@pytest.mark.fleetops
class TestContactUpdate:
    """Test contact update endpoint."""

    def test_update_contact_success(self, client, auth_headers, test_contact):
        """Test updating a contact."""
        response = client.put(
            f"/fleetops/v1/contacts/{test_contact.public_id}",
            headers=auth_headers,
            json={
                "name": "Updated Contact Name",
                "phone": "+1999999999",
            },
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] == "Updated Contact Name"


@pytest.mark.fleetops
class TestContactDelete:
    """Test contact deletion endpoint."""

    def test_delete_contact_success(self, client, auth_headers, db_session):
        """Test deleting a contact."""
        # Create a contact to delete
        create_response = client.post(
            "/fleetops/v1/contacts",
            headers=auth_headers,
            json={
                "name": "Contact To Delete",
                "phone": "+1111111111",
                "email": "todelete@example.com",
            },
        )
        assert create_response.status_code == status.HTTP_201_CREATED
        contact_public_id = create_response.json()["public_id"]

        # Delete the contact
        response = client.delete(f"/fleetops/v1/contacts/{contact_public_id}", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK

