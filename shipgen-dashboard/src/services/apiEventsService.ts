import { apiClient } from './apiClient';

type UnknownRecord = Record<string, unknown>;

export interface UiApiEvent {
  id: string;
  event: string;
  request_method: string;
  endpoint: string;
  status_code: number | null;
  created_at: string;
  raw: UnknownRecord;
}

const parseStatusCode = (value: unknown): number | null => {
  if (typeof value === 'number' && Number.isFinite(value)) return value;
  if (typeof value === 'string' && value.trim()) {
    const parsed = Number(value);
    return Number.isFinite(parsed) ? parsed : null;
  }
  return null;
};

const mapRow = (row: UnknownRecord): UiApiEvent => {
  const data = (row.data ?? {}) as UnknownRecord;
  return {
    id: String(row.uuid ?? row.public_id ?? row.id ?? ''),
    event: String(row.event ?? row.type ?? ''),
    request_method: String(row.method ?? row.request_method ?? data.method ?? ''),
    endpoint: String(row.endpoint ?? row.path ?? row.source ?? data.endpoint ?? data.path ?? ''),
    status_code: parseStatusCode(row.status_code ?? data.status_code),
    created_at: String(row.created_at ?? ''),
    raw: row,
  };
};

class ApiEventsService {
  async list(params: { limit?: number; offset?: number } = {}): Promise<UiApiEvent[]> {
    const payload = await apiClient.get<UnknownRecord[]>('/int/v1/api-events/', {
      limit: params.limit ?? 100,
      offset: params.offset ?? 0,
    });
    return Array.isArray(payload) ? payload.map((x) => mapRow((x ?? {}) as UnknownRecord)) : [];
  }

  async getById(id: string): Promise<UiApiEvent> {
    const payload = await apiClient.get<UnknownRecord>(`/int/v1/api-events/${id}`);
    return mapRow((payload ?? {}) as UnknownRecord);
  }

  async remove(id: string): Promise<void> {
    await apiClient.delete(`/int/v1/api-events/${id}`);
  }
}

export const apiEventsService = new ApiEventsService();
