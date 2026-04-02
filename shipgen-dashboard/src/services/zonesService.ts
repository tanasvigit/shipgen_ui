import { apiClient } from './apiClient';
import { normalizeList, normalizeSingle } from './baseService';
import type { ListResponse } from '../types/api';

type UnknownRecord = Record<string, unknown>;

export interface UiZone {
  id: string;
  name: string;
  description: string;
  status: string;
  created_at: string;
}

export interface ZoneInput {
  name: string;
  description?: string;
  status?: string;
}

const mapZone = (row: UnknownRecord): UiZone => ({
  id: String(row.uuid ?? row.public_id ?? row.id ?? ''),
  name: String(row.name ?? ''),
  description: String(row.description ?? ''),
  status: String(row.status ?? ''),
  created_at: String(row.created_at ?? ''),
});

class ZonesService {
  async list(params: { limit?: number; offset?: number } = {}): Promise<UiZone[]> {
    const payload = await apiClient.get<ListResponse<UnknownRecord>>('/fleetops/v1/zones/', {
      limit: params.limit ?? 100,
      offset: params.offset ?? 0,
    });
    const rows = normalizeList<UnknownRecord>(payload, ['zones']);
    return rows.map((x) => mapZone((x ?? {}) as UnknownRecord));
  }

  async getById(id: string): Promise<UiZone> {
    const payload = await apiClient.get<unknown>(`/fleetops/v1/zones/${id}`);
    return mapZone((normalizeSingle<UnknownRecord>(payload, ['zone']) ?? {}) as UnknownRecord);
  }

  async create(input: ZoneInput): Promise<UiZone> {
    const payload = await apiClient.post<unknown>('/fleetops/v1/zones/', {
      name: input.name,
      ...(input.description ? { description: input.description } : {}),
      ...(input.status ? { status: input.status } : {}),
    });
    return mapZone((normalizeSingle<UnknownRecord>(payload, ['zone']) ?? {}) as UnknownRecord);
  }

  async update(id: string, input: Partial<ZoneInput>): Promise<UiZone> {
    const body = {
      ...(input.name !== undefined ? { name: input.name } : {}),
      ...(input.description !== undefined ? { description: input.description } : {}),
      ...(input.status !== undefined ? { status: input.status } : {}),
    };
    const payload = await apiClient.put<unknown>(`/fleetops/v1/zones/${id}`, body);
    return mapZone((normalizeSingle<UnknownRecord>(payload, ['zone']) ?? {}) as UnknownRecord);
  }

  async remove(id: string): Promise<void> {
    await apiClient.delete(`/fleetops/v1/zones/${id}`);
  }
}

export const zonesService = new ZonesService();
