import { apiClient } from './apiClient';
import { normalizeList, normalizeSingle, withEndpointFallback } from './baseService';
import type { ListResponse } from '../types/api';

type UnknownRecord = Record<string, unknown>;

const ENDPOINTS = ['/int/v1/schedules-constraints'];

export interface UiScheduleConstraint {
  id: string;
  schedule_id: string;
  type: string;
  value: string;
  status: string;
  created_at: string;
  limit: string;
  rule_type: string;
  meta: string;
}

export interface ScheduleConstraintInput {
  schedule_id: string;
  type?: string;
  value?: string;
  status?: string;
  limit?: string;
  rule_type?: string;
  meta?: string;
}

const parseMeta = (meta: string): unknown => {
  const text = meta.trim();
  if (!text) return {};
  try {
    return JSON.parse(text);
  } catch {
    return { value: text };
  }
};

const safeJsonStringify = (value: unknown): string => {
  try {
    return value == null ? '' : JSON.stringify(value, null, 2);
  } catch {
    return '';
  }
};

const mapConstraint = (row: UnknownRecord): UiScheduleConstraint => {
  const value = row.constraint_value ?? row.value ?? '';
  const status =
    row.status ?? (row.is_active === true ? 'active' : row.is_active === false ? 'inactive' : '');

  return {
    id: String(row.uuid ?? row.public_id ?? row.id ?? ''),
    schedule_id: String(row.schedule_uuid ?? row.subject_uuid ?? ''),
    type: String(row.type ?? row.subject_type ?? ''),
    value: String(value ?? ''),
    status: String(status ?? ''),
    created_at: String(row.created_at ?? ''),
    limit: String(row.limit ?? row.priority ?? ''),
    rule_type: String(row.rule_type ?? row.category ?? ''),
    meta: typeof row.meta === 'string' ? String(row.meta) : safeJsonStringify(row.meta),
  };
};

class ScheduleConstraintsService {
  async list(params: { limit?: number; offset?: number } = {}): Promise<UiScheduleConstraint[]> {
    const payload = await withEndpointFallback<ListResponse<UnknownRecord>>(ENDPOINTS, (endpoint) =>
      apiClient.get(`${endpoint}/`, {
        limit: params.limit ?? 100,
        offset: params.offset ?? 0,
      })
    );
    return normalizeList<UnknownRecord>(payload).map((x) => mapConstraint((x ?? {}) as UnknownRecord));
  }

  async getById(id: string): Promise<UiScheduleConstraint> {
    const payload = await withEndpointFallback<unknown>(ENDPOINTS, (endpoint) => apiClient.get(`${endpoint}/${id}`));
    return mapConstraint((normalizeSingle<UnknownRecord>(payload) ?? {}) as UnknownRecord);
  }

  async create(input: ScheduleConstraintInput): Promise<UiScheduleConstraint> {
    const payload = await withEndpointFallback<unknown>(ENDPOINTS, (endpoint) =>
      apiClient.post(`${endpoint}/`, {
        name: input.type || 'constraint',
        subject_uuid: input.schedule_id,
        subject_type: input.type || 'schedule',
        type: input.type || undefined,
        constraint_value: input.value || undefined,
        ...(input.status !== undefined ? { is_active: input.status.toLowerCase() !== 'inactive' } : {}),
        ...(input.limit ? { priority: Number(input.limit) || undefined } : {}),
        ...(input.rule_type ? { category: input.rule_type } : {}),
        ...(input.meta ? { meta: parseMeta(input.meta) } : {}),
      })
    );
    return mapConstraint((normalizeSingle<UnknownRecord>(payload) ?? {}) as UnknownRecord);
  }

  async update(id: string, input: Partial<ScheduleConstraintInput>): Promise<UiScheduleConstraint> {
    const payload = await withEndpointFallback<unknown>(ENDPOINTS, (endpoint) =>
      apiClient.patch(`${endpoint}/${id}`, {
        ...(input.schedule_id !== undefined ? { subject_uuid: input.schedule_id } : {}),
        ...(input.type !== undefined
          ? { type: input.type, subject_type: input.type, name: input.type || 'constraint' }
          : {}),
        ...(input.value !== undefined ? { constraint_value: input.value } : {}),
        ...(input.status !== undefined ? { is_active: input.status.toLowerCase() !== 'inactive' } : {}),
        ...(input.limit !== undefined ? { priority: Number(input.limit) || null } : {}),
        ...(input.rule_type !== undefined ? { category: input.rule_type } : {}),
        ...(input.meta !== undefined ? { meta: parseMeta(input.meta) } : {}),
      })
    );
    return mapConstraint((normalizeSingle<UnknownRecord>(payload) ?? {}) as UnknownRecord);
  }

  async remove(id: string): Promise<void> {
    await withEndpointFallback<void>(ENDPOINTS, (endpoint) => apiClient.delete(`${endpoint}/${id}`));
  }
}

export const scheduleConstraintsService = new ScheduleConstraintsService();
