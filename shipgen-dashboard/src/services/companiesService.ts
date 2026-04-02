import { apiClient } from './apiClient';
import { normalizeList, normalizeSingle } from './baseService';
import type { ListResponse } from '../types/api';

type UnknownRecord = Record<string, unknown>;

export interface UiCompany {
  id: string;
  name: string;
  slug: string;
  status: string;
  created_at: string;
}

export interface CompanyInput {
  name: string;
  slug?: string;
  status?: string;
}

const mapCompany = (row: UnknownRecord): UiCompany => ({
  id: String(row.uuid ?? row.public_id ?? row.id ?? ''),
  name: String(row.name ?? ''),
  slug: String(row.slug ?? ''),
  status: String(row.status ?? ''),
  created_at: String(row.created_at ?? ''),
});

class CompaniesService {
  async list(params: { limit?: number; offset?: number } = {}): Promise<UiCompany[]> {
    const payload = await apiClient.get<ListResponse<UnknownRecord>>('/int/v1/companies/', {
      limit: params.limit ?? 100,
      offset: params.offset ?? 0,
    });
    return normalizeList<UnknownRecord>(payload, ['companies']).map((x) =>
      mapCompany((x ?? {}) as UnknownRecord)
    );
  }

  async getById(id: string): Promise<UiCompany> {
    const payload = await apiClient.get<unknown>(`/int/v1/companies/${id}`);
    return mapCompany((normalizeSingle<UnknownRecord>(payload, ['company']) ?? {}) as UnknownRecord);
  }

  async create(input: CompanyInput): Promise<UiCompany> {
    const payload = await apiClient.post<unknown>('/int/v1/companies/', {
      name: input.name,
      ...(input.slug ? { slug: input.slug } : {}),
      ...(input.status ? { status: input.status } : {}),
    });
    return mapCompany((normalizeSingle<UnknownRecord>(payload, ['company']) ?? {}) as UnknownRecord);
  }

  async update(id: string, input: Partial<CompanyInput>): Promise<UiCompany> {
    const payload = await apiClient.patch<unknown>(`/int/v1/companies/${id}`, {
      ...(input.name !== undefined ? { name: input.name } : {}),
      ...(input.slug !== undefined ? { slug: input.slug } : {}),
      ...(input.status !== undefined ? { status: input.status } : {}),
    });
    return mapCompany((normalizeSingle<UnknownRecord>(payload, ['company']) ?? {}) as UnknownRecord);
  }

  async remove(id: string): Promise<void> {
    await apiClient.delete(`/int/v1/companies/${id}`);
  }
}

export const companiesService = new CompaniesService();
