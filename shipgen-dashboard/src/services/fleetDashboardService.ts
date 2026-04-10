import { apiClient } from './apiClient';

export interface FleetDashboardKpis {
  drivers_total: number;
  drivers_active: number;
  drivers_online: number;
  /** Distinct drivers on at least one active order (pairs with vehicles_in_use). */
  drivers_on_active_orders: number;
  drivers_unassigned: number;
  vehicles_total: number;
  vehicles_active: number;
  vehicles_unassigned: number;
  vehicles_in_use: number;
}

export interface FleetDashboardDriverRow {
  driver_uuid: string;
  public_id: string | null;
  driver_name: string | null;
  status: string | null;
  online: number;
  vehicle_uuid: string | null;
  vehicle_name: string | null;
  vehicle_plate: string | null;
  latitude: number | null;
  longitude: number | null;
}

export interface FleetDashboardVehicleRow {
  vehicle_uuid: string;
  vehicle_name: string | null;
  plate_number: string | null;
  status: string | null;
  assigned_driver_uuid: string | null;
  assigned_driver_name: string | null;
  latitude: number | null;
  longitude: number | null;
}

export interface FleetDashboardPayload {
  kpis: FleetDashboardKpis;
  drivers: FleetDashboardDriverRow[];
  vehicles: FleetDashboardVehicleRow[];
}

const PATH = '/fleetops/v1/fleet/dashboard';

export function formatLatLng(lat: number | null | undefined, lng: number | null | undefined): string {
  if (lat == null || lng == null || Number.isNaN(lat) || Number.isNaN(lng)) return '—';
  return `${lat}, ${lng}`;
}

export const fleetDashboardService = {
  async get(): Promise<FleetDashboardPayload> {
    return apiClient.get<FleetDashboardPayload>(PATH);
  },
};
