from typing import List, Optional

from pydantic import BaseModel


class FleetDashboardKpis(BaseModel):
    drivers_total: int
    drivers_active: int
    drivers_online: int
    drivers_on_active_orders: int
    drivers_unassigned: int
    vehicles_total: int
    vehicles_active: int
    vehicles_unassigned: int
    vehicles_in_use: int


class FleetDashboardDriverRow(BaseModel):
    driver_uuid: str
    public_id: Optional[str] = None
    driver_name: Optional[str] = None
    status: Optional[str] = None
    online: int = 0
    vehicle_uuid: Optional[str] = None
    vehicle_name: Optional[str] = None
    vehicle_plate: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class FleetDashboardVehicleRow(BaseModel):
    vehicle_uuid: str
    vehicle_name: Optional[str] = None
    plate_number: Optional[str] = None
    status: Optional[str] = None
    assigned_driver_uuid: Optional[str] = None
    assigned_driver_name: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class FleetDashboardResponse(BaseModel):
    kpis: FleetDashboardKpis
    drivers: List[FleetDashboardDriverRow]
    vehicles: List[FleetDashboardVehicleRow]
