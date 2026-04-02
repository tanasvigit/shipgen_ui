import { apiClient } from './apiClient';

type UnknownRecord = Record<string, unknown>;

export interface UiApiRequestLog {
  id: string;
  method: string;
  endpoint: string;
  status_code: number | null;
  response_time: string;
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

const mapRow = (row: UnknownRecord): UiApiRequestLog => {
  const data = (row.data ?? {}) as UnknownRecord;
  return {
    id: String(row.uuid ?? row.public_id ?? row.id ?? ''),
    method: String(row.method ?? row.request_method ?? data.method ?? ''),
    endpoint: String(row.endpoint ?? row.url ?? row.path ?? data.endpoint ?? data.url ?? data.path ?? ''),
    status_code: parseStatusCode(row.status_code ?? data.status_code ?? row.response_status),
    response_time: String(row.response_time ?? row.duration_ms ?? data.response_time ?? data.duration_ms ?? ''),
    created_at: String(row.created_at ?? ''),
    raw: row,
  };
};

class ApiRequestLogsService {
  async list(params: { limit?: number; offset?: number; method?: string } = {}): Promise<UiApiRequestLog[]> {
    const payload = await apiClient.get<UnknownRecord[]>('/int/v1/api-request-logs/', {
      limit: params.limit ?? 100,
      offset: params.offset ?? 0,
      ...(params.method ? { method: params.method } : {}),
    });
    return Array.isArray(payload) ? payload.map((x) => mapRow((x ?? {}) as UnknownRecord)) : [];
  }

  async getById(id: string): Promise<UiApiRequestLog> {
    const payload = await apiClient.get<UnknownRecord>(`/int/v1/api-request-logs/${id}`);
    return mapRow((payload ?? {}) as UnknownRecord);
  }

  async remove(id: string): Promise<void> {
    await apiClient.delete(`/int/v1/api-request-logs/${id}`);
  }
}

export const apiRequestLogsService = new ApiRequestLogsService();
