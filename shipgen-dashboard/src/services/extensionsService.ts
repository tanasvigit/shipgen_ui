import { apiClient } from './apiClient';
import { normalizeList, normalizeSingle } from './baseService';
import type { ListResponse } from '../types/api';

type UnknownRecord = Record<string, unknown>;

export interface UiExtension {
  id: string;
  name: string;
  type: string;
  status: string;
  created_at: string;
}

const mapExtension = (row: UnknownRecord): UiExtension => ({
  id: String(row.uuid ?? row.public_id ?? row.id ?? ''),
  name: String(row.display_name ?? row.name ?? ''),
  type: String(row.type_uuid ?? row.type ?? ''),
  status: String(row.status ?? ''),
  created_at: String(row.created_at ?? ''),
});

class ExtensionsService {
  async list(params: { limit?: number; offset?: number } = {}): Promise<UiExtension[]> {
    const payload = await apiClient.get<ListResponse<UnknownRecord>>('/int/v1/extensions/', {
      limit: params.limit ?? 100,
      offset: params.offset ?? 0,
    });
    return normalizeList<UnknownRecord>(payload, ['extensions']).map((x) => mapExtension((x ?? {}) as UnknownRecord));
  }

  async getById(id: string): Promise<UiExtension> {
    const payload = await apiClient.get<unknown>(`/int/v1/extensions/${id}`);
    return mapExtension((normalizeSingle<UnknownRecord>(payload, ['extension']) ?? {}) as UnknownRecord);
  }

  async create(input: { name: string; type?: string; status?: string }): Promise<UiExtension> {
    const payload = await apiClient.post<unknown>('/int/v1/extensions/', {
      name: input.name,
      type_uuid: input.type || null,
      status: input.status || undefined,
    });
    return mapExtension((normalizeSingle<UnknownRecord>(payload, ['extension']) ?? {}) as UnknownRecord);
  }

  async update(id: string, input: { name?: string; type?: string; status?: string }): Promise<UiExtension> {
    const payload = await apiClient.patch<unknown>(`/int/v1/extensions/${id}`, {
      ...(input.name !== undefined ? { name: input.name } : {}),
      ...(input.type !== undefined ? { type_uuid: input.type } : {}),
      ...(input.status !== undefined ? { status: input.status } : {}),
    });
    return mapExtension((normalizeSingle<UnknownRecord>(payload, ['extension']) ?? {}) as UnknownRecord);
  }

  async remove(id: string): Promise<void> {
    await apiClient.delete(`/int/v1/extensions/${id}`);
  }
}

export const extensionsService = new ExtensionsService();
