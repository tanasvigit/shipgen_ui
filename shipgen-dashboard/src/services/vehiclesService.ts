import { apiClient } from './apiClient';
import { normalizeSingle, parseFleetPaginatedResponse } from './baseService';
import type { PaginatedResponse } from '../types/api';

export interface UiVehicle {
  id: string;
  company_uuid: string | null;
  vendor_uuid: string | null;
  make: string;
  model: string;
  year: string;
  trim: string;
  type: string;
  plate_number: string;
  vin: string;
  status: string;
  meta?: Record<string, unknown> | null;
  latitude?: number | null;
  longitude?: number | null;
  created_at?: string | null;
  updated_at?: string | null;
}

interface BackendVehicle {
  id?: number | null;
  uuid?: string | null;
  company_uuid?: string | null;
  vendor_uuid?: string | null;
  make?: string | null;
  model?: string | null;
  year?: string | null;
  trim?: string | null;
  type?: string | null;
  plate_number?: string | null;
  vin?: string | null;
  status?: string | null;
  meta?: Record<string, unknown> | null;
  latitude?: number | null;
  longitude?: number | null;
  created_at?: string | null;
  updated_at?: string | null;
}

export type VehicleListResult = PaginatedResponse<UiVehicle>;

const VEHICLES_BASE_PATH = '/fleetops/v1/vehicles';

const mapBackendVehicleToUi = (vehicle: BackendVehicle): UiVehicle => ({
  id: String(vehicle.uuid ?? vehicle.id ?? ''),
  company_uuid: vehicle.company_uuid ?? null,
  vendor_uuid: vehicle.vendor_uuid ?? null,
  make: String(vehicle.make ?? ''),
  model: String(vehicle.model ?? ''),
  year: String(vehicle.year ?? ''),
  trim: String(vehicle.trim ?? ''),
  type: String(vehicle.type ?? ''),
  plate_number: String(vehicle.plate_number ?? ''),
  vin: String(vehicle.vin ?? ''),
  status: String(vehicle.status ?? 'active'),
  meta: vehicle.meta ?? null,
  latitude: vehicle.latitude != null && !Number.isNaN(Number(vehicle.latitude)) ? Number(vehicle.latitude) : null,
  longitude: vehicle.longitude != null && !Number.isNaN(Number(vehicle.longitude)) ? Number(vehicle.longitude) : null,
  created_at: vehicle.created_at ?? null,
  updated_at: vehicle.updated_at ?? null,
});

class VehiclesService {
  async list(params: { page: number; pageSize: number; status?: string; unassigned?: boolean; in_use?: boolean }): Promise<VehicleListResult> {
    const query = new URLSearchParams({
      limit: String(params.pageSize),
      offset: String((params.page - 1) * params.pageSize),
    });
    if (params.status && params.status !== 'all') query.set('status', params.status);
    if (params.unassigned) query.set('unassigned', 'true');
    if (params.in_use) query.set('in_use', 'true');
    const payload = await apiClient.get<unknown>(`${VEHICLES_BASE_PATH}/?${query.toString()}`);
    const { rows, total } = parseFleetPaginatedResponse<BackendVehicle>(payload, ['vehicles']);
    const mapped = rows.map(mapBackendVehicleToUi);
    return { data: mapped, pagination: { total, page: params.page, pageSize: params.pageSize } };
  }

  async getById(id: string): Promise<UiVehicle> {
    const payload = await apiClient.get<unknown>(`${VEHICLES_BASE_PATH}/${id}`);
    return mapBackendVehicleToUi((normalizeSingle<BackendVehicle>(payload, ['vehicle']) ?? {}) as BackendVehicle);
  }

  async create(input: {
    company_uuid: string | null;
    vendor_uuid: string | null;
    make: string;
    model: string;
    year: string;
    trim: string;
    type: string;
    plate_number: string;
    vin: string;
    status: string;
  }): Promise<UiVehicle> {
    const payload = await apiClient.post<unknown>(`${VEHICLES_BASE_PATH}/`, input);
    return mapBackendVehicleToUi((normalizeSingle<BackendVehicle>(payload, ['vehicle']) ?? {}) as BackendVehicle);
  }

  /** Partial update; matches OpenAPI / Postman PATCH & PUT body fields (VehicleUpdate). */
  async update(
    id: string,
    input: {
      vendor_uuid?: string | null;
      make?: string;
      model?: string;
      year?: string | null;
      trim?: string | null;
      type?: string;
      plate_number?: string;
      vin?: string;
      status?: string;
      meta?: Record<string, unknown> | null;
    },
  ): Promise<UiVehicle> {
    const payload = await apiClient.patch<unknown>(`${VEHICLES_BASE_PATH}/${id}`, input);
    return mapBackendVehicleToUi((normalizeSingle<BackendVehicle>(payload, ['vehicle']) ?? {}) as BackendVehicle);
  }

  async remove(id: string): Promise<void> {
    await apiClient.delete(`${VEHICLES_BASE_PATH}/${id}`);
  }
}

export const vehiclesService = new VehiclesService();
