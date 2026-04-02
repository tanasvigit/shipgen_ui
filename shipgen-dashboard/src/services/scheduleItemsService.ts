import { apiClient } from './apiClient';
import { normalizeList, normalizeSingle, withEndpointFallback } from './baseService';
import type { ListResponse } from '../types/api';

type UnknownRecord = Record<string, unknown>;

/** Matches FastAPI `APIRouter(prefix="/int/v1/schedules-items")` — list/create at `.../`. */
const ENDPOINTS = ['/int/v1/schedules-items'];

const getNestedTitle = (row: UnknownRecord): string => {
  const meta = row.meta as UnknownRecord | undefined;
  return String(meta?.title ?? '');
};

export interface UiScheduleItem {
  id: string;
  schedule_id: string;
  title: string;
  type: string;
  status: string;
  created_at: string;
}

export interface ScheduleItemInput {
  title: string;
  schedule_id: string;
  type?: string;
  status?: string;
}

const mapItem = (row: UnknownRecord): UiScheduleItem => {
  const id = String(row.uuid ?? row.public_id ?? row.id ?? '');
  return {
    id,
    schedule_id: String(row.schedule_uuid ?? row.schedule_id ?? ''),
    title: String(row.name ?? row.title ?? getNestedTitle(row) ?? '') || id,
    type: String(row.type ?? row.resource_type ?? row.assignee_type ?? ''),
    status: String(row.status ?? ''),
    created_at: String(row.created_at ?? ''),
  };
};

class ScheduleItemsService {
  async list(params: { limit?: number; offset?: number } = {}): Promise<UiScheduleItem[]> {
    const payload = await withEndpointFallback<ListResponse<UnknownRecord>>(ENDPOINTS, (endpoint) =>
      apiClient.get(`${endpoint}/`, {
        limit: params.limit ?? 100,
        offset: params.offset ?? 0,
      })
    );
    return normalizeList<UnknownRecord>(payload).map((x) => mapItem((x ?? {}) as UnknownRecord));
  }

  async getById(id: string): Promise<UiScheduleItem> {
    const payload = await withEndpointFallback<unknown>(ENDPOINTS, (endpoint) => apiClient.get(`${endpoint}/${id}`));
    return mapItem((normalizeSingle<UnknownRecord>(payload) ?? {}) as UnknownRecord);
  }

  async create(input: ScheduleItemInput): Promise<UiScheduleItem> {
    const payload = await withEndpointFallback<unknown>(ENDPOINTS, (endpoint) =>
      apiClient.post(`${endpoint}/`, {
        schedule_uuid: input.schedule_id,
        status: input.status || undefined,
        resource_type: input.type || undefined,
        meta: { title: input.title },
      })
    );
    return mapItem((normalizeSingle<UnknownRecord>(payload) ?? {}) as UnknownRecord);
  }

  async update(id: string, input: Partial<ScheduleItemInput>): Promise<UiScheduleItem> {
    const payload = await withEndpointFallback<unknown>(ENDPOINTS, (endpoint) =>
      apiClient.patch(`${endpoint}/${id}`, {
        ...(input.schedule_id !== undefined ? { schedule_uuid: input.schedule_id } : {}),
        ...(input.status !== undefined ? { status: input.status } : {}),
        ...(input.type !== undefined ? { resource_type: input.type } : {}),
        ...(input.title !== undefined ? { meta: { title: input.title } } : {}),
      })
    );
    return mapItem((normalizeSingle<UnknownRecord>(payload) ?? {}) as UnknownRecord);
  }

  async remove(id: string): Promise<void> {
    await withEndpointFallback<void>(ENDPOINTS, (endpoint) => apiClient.delete(`${endpoint}/${id}`));
  }
}

export const scheduleItemsService = new ScheduleItemsService();
