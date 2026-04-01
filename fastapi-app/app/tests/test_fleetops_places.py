"""
Tests for FleetOps place endpoints (/fleetops/v1/places).
"""
import pytest
from fastapi import status


@pytest.mark.fleetops
class TestPlaceList:
    """Test place listing endpoint."""

    def test_list_places_success(self, client, auth_headers, test_place):
        """Test listing places with authentication."""
        response = client.get("/fleetops/v1/places", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)

    def test_list_places_no_auth(self, client):
        """Test listing places without authentication."""
        response = client.get("/fleetops/v1/places")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.fleetops
class TestPlaceGet:
    """Test get place endpoint."""

    def test_get_place_success(self, client, auth_headers, test_place):
        """Test getting a place by public_id."""
        response = client.get(f"/fleetops/v1/places/{test_place.public_id}", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["public_id"] == test_place.public_id
        assert data["name"] == test_place.name

    def test_get_place_not_found(self, client, auth_headers):
        """Test getting non-existent place."""
        response = client.get("/fleetops/v1/places/nonexistent", headers=auth_headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.fleetops
class TestPlaceCreate:
    """Test place creation endpoint."""

    def test_create_place_success(self, client, auth_headers):
        """Test creating a new place."""
        response = client.post(
            "/fleetops/v1/places",
            headers=auth_headers,
            json={
                "name": "New Place",
                "address": "456 New St",
                "city": "New City",
                "country": "US",
                "latitude": 40.7589,
                "longitude": -73.9851,
            },
        )
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["name"] == "New Place"
        assert "public_id" in data
        assert "uuid" in data


@pytest.mark.fleetops
class TestPlaceUpdate:
    """Test place update endpoint."""

    def test_update_place_success(self, client, auth_headers, test_place):
        """Test updating a place."""
        response = client.put(
            f"/fleetops/v1/places/{test_place.public_id}",
            headers=auth_headers,
            json={
                "name": "Updated Place Name",
                "address": "789 Updated St",
            },
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] == "Updated Place Name"


@pytest.mark.fleetops
class TestPlaceGeocode:
    """Test place geocoding endpoint."""

    def test_geocode_place(self, client, auth_headers):
        """Test geocoding an address."""
        response = client.post(
            "/fleetops/v1/places/geocode",
            headers=auth_headers,
            json={
                "address": "1600 Amphitheatre Parkway, Mountain View, CA",
            },
        )
        # Should either return coordinates or error if geocoding service not configured
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_503_SERVICE_UNAVAILABLE,
        ]

