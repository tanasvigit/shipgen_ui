import { apiClient } from './apiClient';
import { normalizeList, normalizeSingle } from './baseService';
import type { ListResponse } from '../types/api';

type UnknownRecord = Record<string, unknown>;

export interface UiEntity {
  id: string;
  name: string;
  type: string;
  status: string;
  created_at: string;
}

export interface EntityInput {
  name: string;
  type?: string;
  status?: string;
}

const mapEntity = (row: UnknownRecord): UiEntity => ({
  id: String(row.uuid ?? row.public_id ?? row.id ?? ''),
  name: String(row.name ?? ''),
  type: String(row.type ?? ''),
  status: String(row.status ?? ''),
  created_at: String(row.created_at ?? ''),
});

class EntitiesService {
  async list(params: { limit?: number; offset?: number } = {}): Promise<UiEntity[]> {
    const payload = await apiClient.get<ListResponse<UnknownRecord>>('/fleetops/v1/entities/', {
      limit: params.limit ?? 100,
      offset: params.offset ?? 0,
    });
    const rows = normalizeList<UnknownRecord>(payload, ['entities']);
    return rows.map((x) => mapEntity((x ?? {}) as UnknownRecord));
  }

  async getById(id: string): Promise<UiEntity> {
    const payload = await apiClient.get<unknown>(`/fleetops/v1/entities/${id}`);
    return mapEntity((normalizeSingle<UnknownRecord>(payload, ['entity']) ?? {}) as UnknownRecord);
  }

  async create(input: EntityInput): Promise<UiEntity> {
    const payload = await apiClient.post<unknown>('/fleetops/v1/entities/', {
      name: input.name,
      ...(input.type ? { type: input.type } : {}),
      ...(input.status ? { status: input.status } : {}),
    });
    return mapEntity((normalizeSingle<UnknownRecord>(payload, ['entity']) ?? {}) as UnknownRecord);
  }

  async update(id: string, input: Partial<EntityInput>): Promise<UiEntity> {
    const payload = await apiClient.put<unknown>(`/fleetops/v1/entities/${id}`, {
      ...(input.name !== undefined ? { name: input.name } : {}),
      ...(input.type !== undefined ? { type: input.type } : {}),
      ...(input.status !== undefined ? { status: input.status } : {}),
    });
    return mapEntity((normalizeSingle<UnknownRecord>(payload, ['entity']) ?? {}) as UnknownRecord);
  }

  async remove(id: string): Promise<void> {
    await apiClient.delete(`/fleetops/v1/entities/${id}`);
  }
}

export const entitiesService = new EntitiesService();
