import { apiClient } from './apiClient';
import { normalizeList, normalizeSingle } from './baseService';
import type { ListResponse } from '../types/api';

type UnknownRecord = Record<string, unknown>;

export interface UiPayload {
  id: string;
  type: string;
  status: string;
  created_at: string;
  raw: UnknownRecord;
}

const mapPayload = (row: UnknownRecord): UiPayload => ({
  id: String(row.uuid ?? row.public_id ?? row.id ?? ''),
  type: String(row.type ?? row.provider ?? ''),
  status: String(row.status ?? row.state ?? ''),
  created_at: String(row.created_at ?? ''),
  raw: row,
});

class PayloadsService {
  async list(params: { limit?: number; offset?: number } = {}): Promise<UiPayload[]> {
    const payload = await apiClient.get<ListResponse<UnknownRecord>>('/fleetops/v1/payloads/', {
      limit: params.limit ?? 100,
      offset: params.offset ?? 0,
    });
    const rows = normalizeList<UnknownRecord>(payload, ['payloads']);
    return rows.map((x) => mapPayload((x ?? {}) as UnknownRecord));
  }

  async getById(id: string): Promise<UiPayload> {
    const payload = await apiClient.get<unknown>(`/fleetops/v1/payloads/${id}`);
    return mapPayload((normalizeSingle<UnknownRecord>(payload, ['payload']) ?? {}) as UnknownRecord);
  }
}

export const payloadsService = new PayloadsService();
