import { apiClient } from './apiClient';

type UnknownRecord = Record<string, unknown>;

export interface UiActivity {
  id: string;
  action: string;
  description: string;
  user: string;
  created_at: string;
  raw: UnknownRecord;
}

const mapActivity = (row: UnknownRecord): UiActivity => ({
  id: String(row.uuid ?? row.id ?? ''),
  action: String(row.event ?? row.log_name ?? 'activity'),
  description: String(row.description ?? ''),
  user: String(row.causer_id ?? row.causer_type ?? ''),
  created_at: String(row.created_at ?? ''),
  raw: row,
});

class ActivitiesService {
  async list(params: { limit?: number; offset?: number } = {}): Promise<UiActivity[]> {
    const payload = await apiClient.get<UnknownRecord[]>('/int/v1/activities/', {
      limit: params.limit ?? 100,
      offset: params.offset ?? 0,
    });
    return Array.isArray(payload) ? payload.map(mapActivity) : [];
  }

  async getById(id: string): Promise<UiActivity> {
    const payload = await apiClient.get<UnknownRecord>(`/int/v1/activities/${id}`);
    return mapActivity(payload);
  }
}

export const activitiesService = new ActivitiesService();
