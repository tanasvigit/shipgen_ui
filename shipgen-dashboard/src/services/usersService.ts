import { apiClient } from './apiClient';
import { normalizeList, normalizeSingle } from './baseService';
import type { ListResponse } from '../types/api';

type UnknownRecord = Record<string, unknown>;

export interface UiUser {
  id: string;
  name: string;
  email: string;
  role: string;
  status: string;
  created_at: string;
}

export interface UserInput {
  name: string;
  email: string;
  role: 'ADMIN' | 'OPERATIONS_MANAGER' | 'DISPATCHER' | 'DRIVER' | 'VIEWER';
  password?: string;
  status?: string;
}

const mapUser = (row: UnknownRecord): UiUser => ({
  id: String(row.uuid ?? ''),
  name: String(row.name ?? ''),
  email: String(row.email ?? ''),
  role: String(row.role ?? ''),
  status: String(row.status ?? ''),
  created_at: String(row.created_at ?? ''),
});

class UsersService {
  async list(params: { limit?: number; offset?: number } = {}): Promise<UiUser[]> {
    const payload = await apiClient.get<ListResponse<UnknownRecord>>('/int/v1/users/', {
      limit: params.limit ?? 100,
      offset: params.offset ?? 0,
    });
    return normalizeList<UnknownRecord>(payload, ['users']).map((x) => mapUser((x ?? {}) as UnknownRecord));
  }

  async getById(id: string): Promise<UiUser> {
    const payload = await apiClient.get<unknown>(`/int/v1/users/${id}`);
    return mapUser((normalizeSingle<UnknownRecord>(payload, ['user']) ?? {}) as UnknownRecord);
  }

  async create(input: UserInput): Promise<UiUser> {
    const payload = await apiClient.post<unknown>('/int/v1/users/', {
      name: input.name,
      email: input.email,
      role: input.role,
      ...(input.password ? { password: input.password } : {}),
    });
    return mapUser((normalizeSingle<UnknownRecord>(payload, ['user']) ?? {}) as UnknownRecord);
  }

  async update(id: string, input: Partial<UserInput>): Promise<UiUser> {
    const payload = await apiClient.patch<unknown>(`/int/v1/users/${id}`, {
      ...(input.name !== undefined ? { name: input.name } : {}),
      ...(input.email !== undefined ? { email: input.email } : {}),
      ...(input.status !== undefined ? { status: input.status } : {}),
      ...(input.role !== undefined ? { role: input.role } : {}),
    });
    return mapUser((normalizeSingle<UnknownRecord>(payload, ['user']) ?? {}) as UnknownRecord);
  }

  async remove(id: string): Promise<void> {
    await apiClient.delete(`/int/v1/users/${id}`);
  }

  async setCurrentUserPassword(password: string): Promise<void> {
    await apiClient.post(`/int/v1/users/set-password?password=${encodeURIComponent(password)}`);
  }

  async validatePassword(password: string): Promise<boolean> {
    try {
      await apiClient.post(`/int/v1/users/validate-password?password=${encodeURIComponent(password)}`);
      return true;
    } catch {
      return false;
    }
  }
}

export const usersService = new UsersService();
