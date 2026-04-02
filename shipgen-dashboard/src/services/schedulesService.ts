import { apiClient } from './apiClient';
import { normalizeList, normalizeSingle } from './baseService';
import type { ListResponse } from '../types/api';

type UnknownRecord = Record<string, unknown>;

export interface UiSchedule {
  id: string;
  name: string;
  type: string;
  status: string;
  created_at: string;
}

export interface ScheduleInput {
  name: string;
  type?: string;
  status?: string;
}

const mapSchedule = (row: UnknownRecord): UiSchedule => ({
  id: String(row.uuid ?? row.public_id ?? row.id ?? ''),
  name: String(row.name ?? ''),
  type: String(row.type ?? row.subject_type ?? ''),
  status: String(row.status ?? ''),
  created_at: String(row.created_at ?? ''),
});

class SchedulesService {
  async list(params: { limit?: number; offset?: number } = {}): Promise<UiSchedule[]> {
    const payload = await apiClient.get<ListResponse<UnknownRecord>>('/int/v1/schedules/', {
      limit: params.limit ?? 100,
      offset: params.offset ?? 0,
    });
    return normalizeList<UnknownRecord>(payload, ['schedules']).map((x) =>
      mapSchedule((x ?? {}) as UnknownRecord)
    );
  }

  async getById(id: string): Promise<UiSchedule> {
    const payload = await apiClient.get<unknown>(`/int/v1/schedules/${id}`);
    return mapSchedule((normalizeSingle<UnknownRecord>(payload, ['schedule']) ?? {}) as UnknownRecord);
  }

  async create(input: ScheduleInput): Promise<UiSchedule> {
    const payload = await apiClient.post<unknown>('/int/v1/schedules/', {
      name: input.name,
      ...(input.type ? { subject_type: input.type } : {}),
      ...(input.status ? { status: input.status } : {}),
    });
    return mapSchedule((normalizeSingle<UnknownRecord>(payload, ['schedule']) ?? {}) as UnknownRecord);
  }

  async update(id: string, input: Partial<ScheduleInput>): Promise<UiSchedule> {
    const payload = await apiClient.patch<unknown>(`/int/v1/schedules/${id}`, {
      ...(input.name !== undefined ? { name: input.name } : {}),
      ...(input.type !== undefined ? { subject_type: input.type } : {}),
      ...(input.status !== undefined ? { status: input.status } : {}),
    });
    return mapSchedule((normalizeSingle<UnknownRecord>(payload, ['schedule']) ?? {}) as UnknownRecord);
  }

  async remove(id: string): Promise<void> {
    await apiClient.delete(`/int/v1/schedules/${id}`);
  }
}

export const schedulesService = new SchedulesService();
