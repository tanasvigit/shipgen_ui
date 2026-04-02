import { apiClient } from './apiClient';
import { normalizeList, normalizeSingle, withEndpointFallback } from './baseService';
import type { ListResponse } from '../types/api';

type UnknownRecord = Record<string, unknown>;

const ENDPOINTS = ['/int/v1/schedules-availability'];

export interface UiScheduleAvailability {
  id: string;
  schedule_id: string;
  type: string;
  status: string;
  created_at: string;
  start_time: string;
  end_time: string;
  day_of_week: string;
}

export interface ScheduleAvailabilityInput {
  schedule_id: string;
  type?: string;
  status?: string;
  start_time?: string;
  end_time?: string;
  day_of_week?: string;
}

const mapAvailability = (row: UnknownRecord): UiScheduleAvailability => {
  const meta = (row.meta as UnknownRecord | undefined) ?? {};
  return {
    id: String(row.uuid ?? row.public_id ?? row.id ?? ''),
    schedule_id: String(row.schedule_uuid ?? row.subject_uuid ?? ''),
    type: String(row.type ?? row.subject_type ?? ''),
    status: String(row.status ?? (row.is_available === true ? 'available' : row.is_available === false ? 'unavailable' : '')),
    created_at: String(row.created_at ?? ''),
    start_time: String(row.start_time ?? row.start_at ?? ''),
    end_time: String(row.end_time ?? row.end_at ?? ''),
    day_of_week: String(row.day_of_week ?? meta.day_of_week ?? ''),
  };
};

class ScheduleAvailabilityService {
  async list(params: { limit?: number; offset?: number } = {}): Promise<UiScheduleAvailability[]> {
    const payload = await withEndpointFallback<ListResponse<UnknownRecord>>(ENDPOINTS, (endpoint) =>
      apiClient.get(`${endpoint}/`, {
        limit: params.limit ?? 100,
        offset: params.offset ?? 0,
      })
    );
    return normalizeList<UnknownRecord>(payload).map((x) => mapAvailability((x ?? {}) as UnknownRecord));
  }

  async getById(id: string): Promise<UiScheduleAvailability> {
    const payload = await withEndpointFallback<unknown>(ENDPOINTS, (endpoint) => apiClient.get(`${endpoint}/${id}`));
    return mapAvailability((normalizeSingle<UnknownRecord>(payload) ?? {}) as UnknownRecord);
  }

  async create(input: ScheduleAvailabilityInput): Promise<UiScheduleAvailability> {
    const payload = await withEndpointFallback<unknown>(ENDPOINTS, (endpoint) =>
      apiClient.post(`${endpoint}/`, {
        subject_uuid: input.schedule_id,
        subject_type: input.type || 'schedule',
        ...(input.status ? { status: input.status, is_available: input.status.toLowerCase() !== 'unavailable' } : {}),
        ...(input.start_time ? { start_at: input.start_time } : {}),
        ...(input.end_time ? { end_at: input.end_time } : {}),
        ...(input.day_of_week ? { meta: { day_of_week: input.day_of_week } } : {}),
      })
    );
    return mapAvailability((normalizeSingle<UnknownRecord>(payload) ?? {}) as UnknownRecord);
  }

  async update(id: string, input: Partial<ScheduleAvailabilityInput>): Promise<UiScheduleAvailability> {
    const payload = await withEndpointFallback<unknown>(ENDPOINTS, (endpoint) =>
      apiClient.patch(`${endpoint}/${id}`, {
        ...(input.schedule_id !== undefined ? { subject_uuid: input.schedule_id } : {}),
        ...(input.type !== undefined ? { subject_type: input.type } : {}),
        ...(input.status !== undefined
          ? { status: input.status, is_available: input.status.toLowerCase() !== 'unavailable' }
          : {}),
        ...(input.start_time !== undefined ? { start_at: input.start_time } : {}),
        ...(input.end_time !== undefined ? { end_at: input.end_time } : {}),
        ...(input.day_of_week !== undefined ? { meta: { day_of_week: input.day_of_week } } : {}),
      })
    );
    return mapAvailability((normalizeSingle<UnknownRecord>(payload) ?? {}) as UnknownRecord);
  }

  async remove(id: string): Promise<void> {
    await withEndpointFallback<void>(ENDPOINTS, (endpoint) => apiClient.delete(`${endpoint}/${id}`));
  }
}

export const scheduleAvailabilityService = new ScheduleAvailabilityService();
