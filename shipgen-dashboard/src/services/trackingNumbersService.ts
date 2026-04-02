import { apiClient } from './apiClient';
import { normalizeList, normalizeSingle } from './baseService';
import type { ListResponse } from '../types/api';

type UnknownRecord = Record<string, unknown>;

export interface UiTrackingNumber {
  id: string;
  tracking_number: string;
  type: string;
  status: string;
  created_at: string;
  related_order_id: string;
}

export interface TrackingNumberInput {
  tracking_number: string;
  type?: string;
  status?: string;
}

const mapTrackingNumber = (row: UnknownRecord): UiTrackingNumber => ({
  id: String(row.uuid ?? row.public_id ?? row.id ?? ''),
  tracking_number: String(row.tracking_number ?? ''),
  type: String(row.type ?? ''),
  status: String(row.status ?? ''),
  created_at: String(row.created_at ?? ''),
  related_order_id: String(
    row.order_uuid ??
      row.order_id ??
      row.entity_id ??
      ((row.meta as UnknownRecord | undefined)?.order_id ?? ''),
  ),
});

class TrackingNumbersService {
  async list(params: { limit?: number; offset?: number } = {}): Promise<UiTrackingNumber[]> {
    const payload = await apiClient.get<ListResponse<UnknownRecord>>('/fleetops/v1/tracking-numbers/', {
      limit: params.limit ?? 100,
      offset: params.offset ?? 0,
    });
    const rows = normalizeList<UnknownRecord>(payload, ['tracking_numbers']);
    return rows.map((x) => mapTrackingNumber((x ?? {}) as UnknownRecord));
  }

  async getById(id: string): Promise<UiTrackingNumber> {
    const payload = await apiClient.get<unknown>(`/fleetops/v1/tracking-numbers/${id}`);
    return mapTrackingNumber((normalizeSingle<UnknownRecord>(payload, ['tracking_number']) ?? {}) as UnknownRecord);
  }

  async create(input: TrackingNumberInput): Promise<UiTrackingNumber> {
    // Backend create schema currently supports region/type/owner, not tracking_number/status directly.
    const payload = await apiClient.post<unknown>('/fleetops/v1/tracking-numbers/', {
      type: input.type || undefined,
      region: input.tracking_number,
    });
    return mapTrackingNumber((normalizeSingle<UnknownRecord>(payload, ['tracking_number']) ?? {}) as UnknownRecord);
  }

  async update(id: string, input: Partial<TrackingNumberInput>): Promise<UiTrackingNumber> {
    const body = {
      ...(input.type !== undefined ? { type: input.type } : {}),
      ...(input.status !== undefined ? { status: input.status } : {}),
      ...(input.tracking_number !== undefined ? { tracking_number: input.tracking_number } : {}),
    };
    const payload = await apiClient.patch<unknown>(`/fleetops/v1/tracking-numbers/${id}`, body);
    return mapTrackingNumber((normalizeSingle<UnknownRecord>(payload, ['tracking_number']) ?? {}) as UnknownRecord);
  }

  async remove(id: string): Promise<void> {
    await apiClient.delete(`/fleetops/v1/tracking-numbers/${id}`);
  }
}

export const trackingNumbersService = new TrackingNumbersService();
