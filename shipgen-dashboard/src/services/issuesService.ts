import { apiClient } from './apiClient';
import { normalizeList, normalizeSingle } from './baseService';
import type { ListResponse, PaginatedResponse } from '../types/api';
import type { MockIssue } from '../mocks/data/issues';

interface BackendIssue {
  uuid?: string | null;
  public_id?: string | null;
  issue_id?: string | null;
  company_uuid?: string | null;
  driver_uuid?: string | null;
  vehicle_uuid?: string | null;
  assigned_to_uuid?: string | null;
  reported_by_uuid?: string | null;
  location?: Record<string, unknown> | null;
  latitude?: string | null;
  longitude?: string | null;
  category?: string | null;
  type?: string | null;
  report?: string | null;
  title?: string | null;
  tags?: string[] | null;
  priority?: string | null;
  meta?: Record<string, unknown> | null;
  resolved_at?: string | null;
  status?: string | null;
  created_at?: string | null;
  updated_at?: string | null;
  id?: number | null;
  driver_name?: string | null;
  vehicle_name?: string | null;
  assignee_name?: string | null;
  reporter_name?: string | null;
}

export type IssueListResult = PaginatedResponse<MockIssue>;

const ISSUES_BASE_PATH = '/fleetops/v1/issues';

const mapBackendIssueToUi = (i: BackendIssue): MockIssue => ({
  uuid: i.uuid ?? null,
  public_id: i.public_id ?? null,
  issue_id: i.issue_id ?? null,
  company_uuid: i.company_uuid ?? null,
  driver_uuid: i.driver_uuid ?? null,
  vehicle_uuid: i.vehicle_uuid ?? null,
  assigned_to_uuid: i.assigned_to_uuid ?? null,
  reported_by_uuid: i.reported_by_uuid ?? null,
  location: i.location ?? null,
  latitude: i.latitude ?? null,
  longitude: i.longitude ?? null,
  category: i.category ?? null,
  type: i.type ?? null,
  report: i.report ?? null,
  title: i.title ?? null,
  tags: i.tags ?? null,
  priority: i.priority ?? null,
  meta: i.meta ?? null,
  resolved_at: i.resolved_at ?? null,
  status: i.status ?? null,
  created_at: i.created_at ?? null,
  updated_at: i.updated_at ?? null,
  id: i.id ?? null,
  driver_name: i.driver_name ?? null,
  vehicle_name: i.vehicle_name ?? null,
  assignee_name: i.assignee_name ?? null,
  reporter_name: i.reporter_name ?? null,
});

class IssuesService {
  async list(params: { page: number; pageSize: number }): Promise<IssueListResult> {
    const query = new URLSearchParams({
      limit: String(params.pageSize),
      offset: String((params.page - 1) * params.pageSize),
    });
    const payload = await apiClient.get<ListResponse<BackendIssue>>(`${ISSUES_BASE_PATH}/?${query.toString()}`);
    const rows = normalizeList<BackendIssue>(payload, ['issues']);
    const mapped = rows.map(mapBackendIssueToUi);
    return { data: mapped, pagination: { total: mapped.length, page: params.page, pageSize: params.pageSize } };
  }

  async getById(id: string): Promise<MockIssue> {
    const payload = await apiClient.get<unknown>(`${ISSUES_BASE_PATH}/${id}`);
    return mapBackendIssueToUi((normalizeSingle<BackendIssue>(payload, ['issue']) ?? {}) as BackendIssue);
  }

  async create(input: Record<string, unknown>): Promise<MockIssue> {
    const payload = await apiClient.post<unknown>(`${ISSUES_BASE_PATH}/`, input);
    return mapBackendIssueToUi((normalizeSingle<BackendIssue>(payload, ['issue']) ?? {}) as BackendIssue);
  }

  async updatePut(id: string, input: Record<string, unknown>): Promise<MockIssue> {
    const payload = await apiClient.put<unknown>(`${ISSUES_BASE_PATH}/${id}`, input);
    return mapBackendIssueToUi((normalizeSingle<BackendIssue>(payload, ['issue']) ?? {}) as BackendIssue);
  }

  async remove(id: string): Promise<void> {
    await apiClient.delete(`${ISSUES_BASE_PATH}/${id}`);
  }
}

export const issuesService = new IssuesService();
