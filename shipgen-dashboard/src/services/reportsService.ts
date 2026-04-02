import { apiClient } from './apiClient';

type UnknownRecord = Record<string, unknown>;

export interface UiReport {
  id: string;
  name: string;
  description: string;
  created_at: string;
}

interface ExecuteResult {
  resultType: 'array' | 'object';
  rows: UnknownRecord[];
  objectData: UnknownRecord | null;
}

const asArray = (value: unknown): UnknownRecord[] => (Array.isArray(value) ? (value as UnknownRecord[]) : []);

const mapBackendReport = (row: UnknownRecord): UiReport => ({
  id: String(row.uuid ?? row.public_id ?? row.id ?? ''),
  name: String(row.title ?? row.name ?? ''),
  description: String(row.description ?? ''),
  created_at: String(row.created_at ?? ''),
});

class ReportsService {
  async list(params: { limit?: number; offset?: number } = {}): Promise<UiReport[]> {
    const payload = await apiClient.get<UnknownRecord[]>('/int/v1/reports/', {
      limit: params.limit ?? 50,
      offset: params.offset ?? 0,
    });
    return asArray(payload).map(mapBackendReport);
  }

  async getById(id: string): Promise<UiReport> {
    const payload = await apiClient.get<UnknownRecord>(`/int/v1/reports/${id}`);
    return mapBackendReport(payload);
  }

  async execute(id: string): Promise<ExecuteResult> {
    const payload = await apiClient.post<unknown>(`/int/v1/reports/${id}/execute`, {});

    if (Array.isArray(payload)) {
      return { resultType: 'array', rows: payload as UnknownRecord[], objectData: null };
    }

    if (payload && typeof payload === 'object') {
      const p = payload as UnknownRecord;
      const rows = asArray(p.data);
      if (rows.length > 0) return { resultType: 'array', rows, objectData: null };
      return { resultType: 'object', rows: [], objectData: p };
    }

    return { resultType: 'object', rows: [], objectData: { value: payload } };
  }

  async export(id: string): Promise<unknown> {
    // Backend expects payload dict; empty is valid (defaults to csv).
    return apiClient.post(`/int/v1/reports/${id}/export`, {});
  }
}

export const reportsService = new ReportsService();
