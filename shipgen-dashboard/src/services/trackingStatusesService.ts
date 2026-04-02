import { apiClient } from './apiClient';
import { normalizeList, normalizeSingle } from './baseService';
import type { ListResponse } from '../types/api';

type UnknownRecord = Record<string, unknown>;

export interface UiTrackingStatus {
  id: string;
  name: string;
  description: string;
  created_at: string;
}

export interface TrackingStatusInput {
  name: string;
  description?: string;
}

const mapTrackingStatus = (row: UnknownRecord): UiTrackingStatus => ({
  id: String(row.uuid ?? row.public_id ?? row.id ?? ''),
  name: String(row.status ?? row.name ?? ''),
  description: String(row.details ?? row.description ?? ''),
  created_at: String(row.created_at ?? ''),
});

class TrackingStatusesService {
  async list(params: { limit?: number; offset?: number } = {}): Promise<UiTrackingStatus[]> {
    const payload = await apiClient.get<ListResponse<UnknownRecord>>('/fleetops/v1/tracking-statuses/', {
      limit: params.limit ?? 100,
      offset: params.offset ?? 0,
    });
    const rows = normalizeList<UnknownRecord>(payload, ['tracking_statuses']);
    return rows.map((x) => mapTrackingStatus((x ?? {}) as UnknownRecord));
  }

  async getById(id: string): Promise<UiTrackingStatus> {
    const payload = await apiClient.get<unknown>(`/fleetops/v1/tracking-statuses/${id}`);
    return mapTrackingStatus((normalizeSingle<UnknownRecord>(payload, ['tracking_status']) ?? {}) as UnknownRecord);
  }

  async create(input: TrackingStatusInput): Promise<UiTrackingStatus> {
    const payload = await apiClient.post<unknown>('/fleetops/v1/tracking-statuses/', {
      status: input.name,
      ...(input.description ? { details: input.description } : {}),
    });
    return mapTrackingStatus((normalizeSingle<UnknownRecord>(payload, ['tracking_status']) ?? {}) as UnknownRecord);
  }

  async update(id: string, input: Partial<TrackingStatusInput>): Promise<UiTrackingStatus> {
    const body = {
      ...(input.name !== undefined ? { status: input.name } : {}),
      ...(input.description !== undefined ? { details: input.description } : {}),
    };
    const payload = await apiClient.put<unknown>(`/fleetops/v1/tracking-statuses/${id}`, body);
    return mapTrackingStatus((normalizeSingle<UnknownRecord>(payload, ['tracking_status']) ?? {}) as UnknownRecord);
  }

  async remove(id: string): Promise<void> {
    await apiClient.delete(`/fleetops/v1/tracking-statuses/${id}`);
  }
}

export const trackingStatusesService = new TrackingStatusesService();
