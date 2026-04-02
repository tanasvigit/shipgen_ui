import { apiClient } from './apiClient';
import { normalizeList, normalizeSingle } from './baseService';
import type { ListResponse } from '../types/api';

type UnknownRecord = Record<string, unknown>;

export interface UiGroup {
  id: string;
  name: string;
  description: string;
  created_at: string;
}

const mapGroup = (row: UnknownRecord): UiGroup => ({
  id: String(row.uuid ?? row.public_id ?? row.id ?? ''),
  name: String(row.name ?? ''),
  description: String(row.description ?? ''),
  created_at: String(row.created_at ?? ''),
});

class GroupsService {
  async list(params: { limit?: number; offset?: number } = {}): Promise<UiGroup[]> {
    const payload = await apiClient.get<ListResponse<UnknownRecord>>('/int/v1/groups/', {
      limit: params.limit ?? 100,
      offset: params.offset ?? 0,
    });
    return normalizeList<UnknownRecord>(payload, ['groups']).map((x) => mapGroup((x ?? {}) as UnknownRecord));
  }

  async getById(id: string): Promise<UiGroup> {
    const payload = await apiClient.get<unknown>(`/int/v1/groups/${id}`);
    return mapGroup((normalizeSingle<UnknownRecord>(payload, ['group']) ?? {}) as UnknownRecord);
  }

  async create(input: { name: string; description?: string }): Promise<UiGroup> {
    const payload = await apiClient.post<unknown>('/int/v1/groups/', {
      name: input.name,
      description: input.description || null,
    });
    return mapGroup((normalizeSingle<UnknownRecord>(payload, ['group']) ?? {}) as UnknownRecord);
  }

  async update(id: string, input: { name?: string; description?: string }): Promise<UiGroup> {
    const payload = await apiClient.patch<unknown>(`/int/v1/groups/${id}`, {
      name: input.name,
      description: input.description ?? null,
    });
    return mapGroup((normalizeSingle<UnknownRecord>(payload, ['group']) ?? {}) as UnknownRecord);
  }

  async remove(id: string): Promise<void> {
    await apiClient.delete(`/int/v1/groups/${id}`);
  }
}

export const groupsService = new GroupsService();
