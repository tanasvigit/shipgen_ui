"""Fleet dashboard aggregate endpoint."""
import pytest
from fastapi import status


@pytest.mark.fleetops
def test_fleet_dashboard_success(client, auth_headers, test_driver, test_vehicle):
    response = client.get("/fleetops/v1/fleet/dashboard", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "kpis" in data
    assert "drivers" in data
    assert "vehicles" in data
    k = data["kpis"]
    assert k["drivers_total"] >= 1
    assert k["vehicles_total"] >= 1
    assert isinstance(data["drivers"], list)
    assert isinstance(data["vehicles"], list)


@pytest.mark.fleetops
def test_fleet_dashboard_no_auth(client):
    response = client.get("/fleetops/v1/fleet/dashboard")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
