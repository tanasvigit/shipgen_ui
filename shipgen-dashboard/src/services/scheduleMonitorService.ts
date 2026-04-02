import { apiClient } from './apiClient';

type UnknownRecord = Record<string, unknown>;

/** List endpoint: GET `/int/v1/schedules-monitor/tasks` (see FastAPI schedule_monitor router). */
const MONITOR_TASKS_BASE = '/int/v1/schedules-monitor/tasks';

const mapMonitor = (row: UnknownRecord): UiScheduleMonitor => ({
  id: String(row.uuid ?? row.public_id ?? row.id ?? ''),
  schedule_id: String(row.schedule_id ?? row.subject_uuid ?? row.id ?? ''),
  type: String(row.type ?? row.subject_type ?? row.name ?? ''),
  status: String(row.status ?? ''),
  created_at: String(row.created_at ?? ''),
  logs: Array.isArray(row.logs) ? row.logs : [],
  result: row.result ?? row.properties ?? null,
  error_message: String(row.error_message ?? row.error ?? ''),
  raw: row,
});

const mapLogs = (rows: UnknownRecord[]): UnknownRecord[] =>
  rows.map((row) => ({
    id: String(row.uuid ?? row.public_id ?? row.id ?? ''),
    event: String(row.event ?? ''),
    description: String(row.description ?? ''),
    properties: (row.properties as UnknownRecord | undefined) ?? {},
    created_at: String(row.created_at ?? ''),
    causer_id: row.causer_id ?? null,
    causer_type: row.causer_type ?? null,
  }));

export interface UiScheduleMonitor {
  id: string;
  schedule_id: string;
  status: string;
  type: string;
  created_at: string;
  logs: unknown[];
  result: unknown;
  error_message: string;
  raw: UnknownRecord;
}

class ScheduleMonitorService {
  async list(params: { limit?: number; offset?: number } = {}): Promise<UiScheduleMonitor[]> {
    const query = {
      limit: params.limit ?? 100,
      offset: params.offset ?? 0,
    };
    const payload = await apiClient.get<unknown>(MONITOR_TASKS_BASE, query);
    const rows = Array.isArray(payload) ? payload : [];
    return rows.map((x) => mapMonitor((x ?? {}) as UnknownRecord));
  }

  async getById(id: string): Promise<UiScheduleMonitor> {
    const tasks = await this.list({ limit: 500, offset: 0 });
    const task = tasks.find((t) => t.id === id || t.schedule_id === id);
    if (!task) throw new Error('Schedule monitor record not found');

    try {
      const logsPayload = await apiClient.get<UnknownRecord[]>(
        `${MONITOR_TASKS_BASE}/${encodeURIComponent(id)}/logs`,
        { limit: 100, offset: 0 },
      );
      const logs = Array.isArray(logsPayload) ? mapLogs(logsPayload) : [];
      const latest = logs[0];
      return {
        ...task,
        logs,
        result: latest?.properties ?? task.result,
        error_message: task.error_message || '',
      };
    } catch {
      return task;
    }
  }
}

export const scheduleMonitorService = new ScheduleMonitorService();
