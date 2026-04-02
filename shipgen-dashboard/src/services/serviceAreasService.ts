import { apiClient } from './apiClient';
import { normalizeList, normalizeSingle } from './baseService';
import type { ListResponse } from '../types/api';

type UnknownRecord = Record<string, unknown>;

export interface UiServiceArea {
  id: string;
  name: string;
  description: string;
  status: string;
  created_at: string;
}

export interface ServiceAreaInput {
  name: string;
  description?: string;
  status?: string;
}

const mapServiceArea = (row: UnknownRecord): UiServiceArea => ({
  id: String(row.uuid ?? row.public_id ?? row.id ?? ''),
  name: String(row.name ?? ''),
  // Backend has no explicit description field; using type as a lightweight proxy.
  description: String(row.description ?? row.type ?? ''),
  status: String(row.status ?? ''),
  created_at: String(row.created_at ?? ''),
});

class ServiceAreasService {
  async list(params: { limit?: number; offset?: number } = {}): Promise<UiServiceArea[]> {
    const payload = await apiClient.get<ListResponse<UnknownRecord>>('/fleetops/v1/service-areas/', {
      limit: params.limit ?? 100,
      offset: params.offset ?? 0,
    });
    const rows = normalizeList<UnknownRecord>(payload, ['service_areas']);
    return rows.map((x) => mapServiceArea((x ?? {}) as UnknownRecord));
  }

  async getById(id: string): Promise<UiServiceArea> {
    const payload = await apiClient.get<unknown>(`/fleetops/v1/service-areas/${id}`);
    return mapServiceArea((normalizeSingle<UnknownRecord>(payload, ['service_area']) ?? {}) as UnknownRecord);
  }

  async create(input: ServiceAreaInput): Promise<UiServiceArea> {
    const payload = await apiClient.post<unknown>('/fleetops/v1/service-areas/', {
      name: input.name,
      ...(input.description ? { type: input.description } : {}),
      ...(input.status ? { status: input.status } : {}),
    });
    return mapServiceArea((normalizeSingle<UnknownRecord>(payload, ['service_area']) ?? {}) as UnknownRecord);
  }

  async update(id: string, input: Partial<ServiceAreaInput>): Promise<UiServiceArea> {
    const body = {
      ...(input.name !== undefined ? { name: input.name } : {}),
      ...(input.description !== undefined ? { type: input.description } : {}),
      ...(input.status !== undefined ? { status: input.status } : {}),
    };
    const payload = await apiClient.put<unknown>(`/fleetops/v1/service-areas/${id}`, body);
    return mapServiceArea((normalizeSingle<UnknownRecord>(payload, ['service_area']) ?? {}) as UnknownRecord);
  }

  async remove(id: string): Promise<void> {
    await apiClient.delete(`/fleetops/v1/service-areas/${id}`);
  }
}

export const serviceAreasService = new ServiceAreasService();
