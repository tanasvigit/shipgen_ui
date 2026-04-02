import { apiClient } from './apiClient';
import { normalizeList, normalizeSingle } from './baseService';
import type { ListResponse } from '../types/api';

type UnknownRecord = Record<string, unknown>;

export interface UiFleet {
  id: string;
  name: string;
  description: string;
  created_at: string;
}

export interface FleetInput {
  name: string;
  description?: string;
}

const mapFleet = (row: UnknownRecord): UiFleet => ({
  id: String(row.uuid ?? row.public_id ?? row.id ?? ''),
  name: String(row.name ?? ''),
  // Backend does not expose a dedicated description field; use task as fallback.
  description: String(row.description ?? row.task ?? ''),
  created_at: String(row.created_at ?? ''),
});

class FleetsService {
  async list(params: { limit?: number; offset?: number } = {}): Promise<UiFleet[]> {
    const payload = await apiClient.get<ListResponse<UnknownRecord>>('/fleetops/v1/fleets/', {
      limit: params.limit ?? 100,
      offset: params.offset ?? 0,
    });
    const rows = normalizeList<UnknownRecord>(payload, ['fleets']);
    return rows.map((x) => mapFleet((x ?? {}) as UnknownRecord));
  }

  async getById(id: string): Promise<UiFleet> {
    const payload = await apiClient.get<unknown>(`/fleetops/v1/fleets/${id}`);
    return mapFleet((normalizeSingle<UnknownRecord>(payload, ['fleet']) ?? {}) as UnknownRecord);
  }

  async create(input: FleetInput): Promise<UiFleet> {
    const payload = await apiClient.post<unknown>('/fleetops/v1/fleets/', {
      name: input.name,
      ...(input.description ? { task: input.description } : {}),
    });
    return mapFleet((normalizeSingle<UnknownRecord>(payload, ['fleet']) ?? {}) as UnknownRecord);
  }

  async update(id: string, input: Partial<FleetInput>): Promise<UiFleet> {
    const body = {
      ...(input.name !== undefined ? { name: input.name } : {}),
      ...(input.description !== undefined ? { task: input.description } : {}),
    };
    const payload = await apiClient.put<unknown>(`/fleetops/v1/fleets/${id}`, body);
    return mapFleet((normalizeSingle<UnknownRecord>(payload, ['fleet']) ?? {}) as UnknownRecord);
  }

  async remove(id: string): Promise<void> {
    await apiClient.delete(`/fleetops/v1/fleets/${id}`);
  }
}

export const fleetsService = new FleetsService();
