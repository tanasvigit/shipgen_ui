import { apiClient } from './apiClient';
import { normalizeSingle, parseFleetPaginatedResponse } from './baseService';
import type { PaginatedResponse } from '../types/api';

export interface UiDriver {
  id: string;
  company_uuid: string | null;
  user_uuid: string | null;
  vehicle_uuid?: string | null;
  vendor_uuid?: string | null;
  drivers_license_number: string;
  status: string;
  online: number;
  latitude?: number | null;
  longitude?: number | null;
  heading?: string | null;
  speed?: string | null;
  altitude?: string | null;
  created_at?: string | null;
  updated_at?: string | null;
}

interface BackendDriver {
  id?: number | null;
  uuid?: string | null;
  public_id?: string | null;
  company_uuid?: string | null;
  user_uuid?: string | null;
  vehicle_uuid?: string | null;
  vendor_uuid?: string | null;
  drivers_license_number?: string | null;
  status?: string | null;
  online?: number | null;
  latitude?: number | null;
  longitude?: number | null;
  heading?: string | null;
  speed?: string | null;
  altitude?: string | null;
  created_at?: string | null;
  updated_at?: string | null;
}

export type DriverListResult = PaginatedResponse<UiDriver>;

const DRIVERS_BASE_PATH = '/fleetops/v1/drivers';

const toStr = (v?: string | null): string | null => (v == null ? null : String(v));

const mapBackendDriverToUi = (driver: BackendDriver): UiDriver => ({
  id: String(driver.uuid ?? driver.id ?? ''),
  company_uuid: toStr(driver.company_uuid),
  user_uuid: toStr(driver.user_uuid),
  vehicle_uuid: toStr(driver.vehicle_uuid),
  vendor_uuid: toStr(driver.vendor_uuid),
  drivers_license_number: String(driver.drivers_license_number ?? ''),
  status: String(driver.status ?? 'active'),
  online: Number(driver.online ?? 0),
  latitude: driver.latitude != null && !Number.isNaN(Number(driver.latitude)) ? Number(driver.latitude) : null,
  longitude: driver.longitude != null && !Number.isNaN(Number(driver.longitude)) ? Number(driver.longitude) : null,
  heading: toStr(driver.heading),
  speed: toStr(driver.speed),
  altitude: toStr(driver.altitude),
  created_at: toStr(driver.created_at),
  updated_at: toStr(driver.updated_at),
});

class DriversService {
  async list(params: {
    page: number;
    pageSize: number;
    status?: string;
    online?: number;
    unassigned?: boolean;
  }): Promise<DriverListResult> {
    const query = new URLSearchParams({
      limit: String(params.pageSize),
      offset: String((params.page - 1) * params.pageSize),
    });
    if (params.status) query.set('status', params.status);
    if (params.online != null) query.set('online', String(params.online));
    if (params.unassigned) query.set('unassigned', 'true');
    const payload = await apiClient.get<unknown>(`${DRIVERS_BASE_PATH}/?${query.toString()}`);
    const { rows, total } = parseFleetPaginatedResponse<BackendDriver>(payload, ['drivers']);
    const mapped = rows.map(mapBackendDriverToUi);
    return {
      data: mapped,
      pagination: { total, page: params.page, pageSize: params.pageSize },
    };
  }

  /** Drivers with driver.vehicle_uuid === this vehicle (company-scoped on the server). */
  async listForVehicle(vehicleUuid: string, pageSize = 20): Promise<UiDriver[]> {
    const query = new URLSearchParams({
      vehicle_uuid: vehicleUuid,
      limit: String(pageSize),
      offset: '0',
    });
    const payload = await apiClient.get<unknown>(`${DRIVERS_BASE_PATH}/?${query.toString()}`);
    const { rows } = parseFleetPaginatedResponse<BackendDriver>(payload, ['drivers']);
    return rows.map(mapBackendDriverToUi);
  }

  async getById(id: string): Promise<UiDriver> {
    const payload = await apiClient.get<unknown>(`${DRIVERS_BASE_PATH}/${id}`);
    return mapBackendDriverToUi((normalizeSingle<BackendDriver>(payload, ['driver']) ?? {}) as BackendDriver);
  }

  async create(input: {
    company_uuid?: string | null;
    user_uuid?: string | null;
    drivers_license_number: string;
    status: string;
  }): Promise<UiDriver> {
    const payload = await apiClient.post<unknown>(`${DRIVERS_BASE_PATH}/`, {
      company_uuid: input.company_uuid ?? null,
      user_uuid: input.user_uuid ?? null,
      drivers_license_number: input.drivers_license_number,
      status: input.status,
    });
    return mapBackendDriverToUi((normalizeSingle<BackendDriver>(payload, ['driver']) ?? {}) as BackendDriver);
  }

  async update(
    id: string,
    input: { user_uuid?: string | null; drivers_license_number?: string; status?: string; online?: number },
  ): Promise<UiDriver> {
    const payload = await apiClient.patch<unknown>(`${DRIVERS_BASE_PATH}/${id}`, input);
    return mapBackendDriverToUi((normalizeSingle<BackendDriver>(payload, ['driver']) ?? {}) as BackendDriver);
  }

  async remove(id: string): Promise<void> {
    await apiClient.delete(`${DRIVERS_BASE_PATH}/${id}`);
  }
}

export const driversService = new DriversService();
