import { apiClient } from './apiClient';
import { normalizeList, normalizeSingle, withEndpointFallback } from './baseService';
import type { ListResponse } from '../types/api';

type UnknownRecord = Record<string, unknown>;

const ENDPOINTS = ['/int/v1/schedules-templates'];

export interface UiScheduleTemplate {
  id: string;
  name: string;
  type: string;
  status: string;
  created_at: string;
}

export interface ScheduleTemplateInput {
  name: string;
  type?: string;
  status?: string;
}

const mapTemplate = (row: UnknownRecord): UiScheduleTemplate => ({
  id: String(row.uuid ?? row.public_id ?? row.id ?? ''),
  name: String(row.name ?? ''),
  type: String(row.type ?? row.subject_type ?? ''),
  status: String(row.status ?? ''),
  created_at: String(row.created_at ?? ''),
});

class ScheduleTemplatesService {
  async list(params: { limit?: number; offset?: number } = {}): Promise<UiScheduleTemplate[]> {
    const payload = await withEndpointFallback<ListResponse<UnknownRecord>>(ENDPOINTS, (endpoint) =>
      apiClient.get(`${endpoint}/`, {
        limit: params.limit ?? 100,
        offset: params.offset ?? 0,
      })
    );
    return normalizeList<UnknownRecord>(payload).map((x) => mapTemplate((x ?? {}) as UnknownRecord));
  }

  async getById(id: string): Promise<UiScheduleTemplate> {
    const payload = await withEndpointFallback<unknown>(ENDPOINTS, (endpoint) => apiClient.get(`${endpoint}/${id}`));
    return mapTemplate((normalizeSingle<UnknownRecord>(payload) ?? {}) as UnknownRecord);
  }

  async create(input: ScheduleTemplateInput): Promise<UiScheduleTemplate> {
    const payload = await withEndpointFallback<unknown>(ENDPOINTS, (endpoint) =>
      apiClient.post(`${endpoint}/`, {
        name: input.name,
        ...(input.type ? { subject_type: input.type } : {}),
        ...(input.status ? { status: input.status } : {}),
      })
    );
    return mapTemplate((normalizeSingle<UnknownRecord>(payload) ?? {}) as UnknownRecord);
  }

  async update(id: string, input: Partial<ScheduleTemplateInput>): Promise<UiScheduleTemplate> {
    const payload = await withEndpointFallback<unknown>(ENDPOINTS, (endpoint) =>
      apiClient.patch(`${endpoint}/${id}`, {
        ...(input.name !== undefined ? { name: input.name } : {}),
        ...(input.type !== undefined ? { subject_type: input.type } : {}),
        ...(input.status !== undefined ? { status: input.status } : {}),
      })
    );
    return mapTemplate((normalizeSingle<UnknownRecord>(payload) ?? {}) as UnknownRecord);
  }

  async remove(id: string): Promise<void> {
    await withEndpointFallback<void>(ENDPOINTS, (endpoint) => apiClient.delete(`${endpoint}/${id}`));
  }
}

export const scheduleTemplatesService = new ScheduleTemplatesService();
