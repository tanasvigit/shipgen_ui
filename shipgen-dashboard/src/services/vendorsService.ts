import { apiClient } from './apiClient';
import type { MockVendor } from '../mocks/data/vendors';
import { normalizeList, normalizeSingle } from './baseService';
import type { ListResponse, PaginatedResponse } from '../types/api';

interface BackendVendor {
  uuid?: string | null;
  public_id?: string | null;
  company_uuid?: string | null;
  place_uuid?: string | null;
  name?: string | null;
  internal_id?: string | null;
  business_id?: string | null;
  connected?: number | null;
  email?: string | null;
  phone?: string | null;
  website_url?: string | null;
  country?: string | null;
  meta?: Record<string, unknown> | null;
  type?: string | null;
  status?: string | null;
  slug?: string | null;
  created_at?: string | null;
  updated_at?: string | null;
  id?: number | null;
}

const VENDORS_BASE_PATH = '/fleetops/v1/vendors';

const mapBackendVendorToUi = (v: BackendVendor): MockVendor => ({
  uuid: v.uuid ?? null,
  public_id: v.public_id ?? null,
  company_uuid: v.company_uuid ?? null,
  place_uuid: v.place_uuid ?? null,
  name: v.name ?? null,
  internal_id: v.internal_id ?? null,
  business_id: v.business_id ?? null,
  connected: v.connected ?? null,
  email: v.email ?? null,
  phone: v.phone ?? null,
  website_url: v.website_url ?? null,
  country: v.country ?? null,
  meta: v.meta ?? null,
  type: v.type ?? null,
  status: v.status ?? null,
  slug: v.slug ?? null,
  created_at: v.created_at ?? null,
  updated_at: v.updated_at ?? null,
  id: v.id ?? null,
});

class VendorsService {
  async list(params: { page: number; pageSize: number }): Promise<PaginatedResponse<MockVendor>> {
    const query = new URLSearchParams({
      limit: String(params.pageSize),
      offset: String((params.page - 1) * params.pageSize),
    });
    const payload = await apiClient.get<ListResponse<BackendVendor>>(
      `${VENDORS_BASE_PATH}?${query.toString()}`
    );
    const rows = normalizeList<BackendVendor>(payload, ['vendors']);
    const mapped = rows.map(mapBackendVendorToUi);
    return { data: mapped, pagination: { total: mapped.length, page: params.page, pageSize: params.pageSize } };
  }

  async getById(id: string): Promise<MockVendor> {
    const payload = await apiClient.get<unknown>(`${VENDORS_BASE_PATH}/${id}`);
    return mapBackendVendorToUi((normalizeSingle<BackendVendor>(payload, ['vendor']) ?? {}) as BackendVendor);
  }

  async create(input: Record<string, unknown>): Promise<MockVendor> {
    const payload = await apiClient.post<unknown>(VENDORS_BASE_PATH, input);
    return mapBackendVendorToUi((normalizeSingle<BackendVendor>(payload, ['vendor']) ?? {}) as BackendVendor);
  }

  async update(id: string, input: Record<string, unknown>): Promise<MockVendor> {
    const payload = await apiClient.patch<unknown>(`${VENDORS_BASE_PATH}/${id}`, input);
    return mapBackendVendorToUi((normalizeSingle<BackendVendor>(payload, ['vendor']) ?? {}) as BackendVendor);
  }

  async remove(id: string): Promise<void> {
    await apiClient.delete(`${VENDORS_BASE_PATH}/${id}`);
  }
}

export const vendorsService = new VendorsService();
