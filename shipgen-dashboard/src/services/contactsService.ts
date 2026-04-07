import { apiClient } from './apiClient';
import { normalizeList, normalizeSingle } from './baseService';
import type { ListResponse, PaginatedResponse } from '../types/api';
import type { MockContact } from '../mocks/data/contacts';

interface BackendContact {
  id?: number | null;
  uuid?: string | null;
  public_id?: string | null;
  company_uuid?: string | null;
  user_uuid?: string | null;
  name?: string | null;
  title?: string | null;
  email?: string | null;
  phone?: string | null;
  type?: string | null;
  slug?: string | null;
  meta?: Record<string, unknown> | null;
  created_at?: string | null;
  updated_at?: string | null;
}

export type ContactListResult = PaginatedResponse<MockContact>;

const CONTACTS_BASE_PATH = '/fleetops/v1/contacts';

const mapBackendContactToUi = (c: BackendContact): MockContact => ({
  uuid: c.uuid ?? null,
  public_id: c.public_id ?? null,
  company_uuid: c.company_uuid ?? null,
  user_uuid: c.user_uuid ?? null,
  name: c.name ?? null,
  title: c.title ?? null,
  email: c.email ?? null,
  phone: c.phone ?? null,
  type: c.type ?? null,
  slug: c.slug ?? null,
  meta: c.meta ?? null,
  created_at: c.created_at ?? null,
  updated_at: c.updated_at ?? null,
  id: c.id ?? null,
});

class ContactsService {
  async list(params: { page: number; pageSize: number; kind?: string; search?: string }): Promise<ContactListResult> {
    const query = new URLSearchParams({
      limit: String(params.pageSize),
      offset: String((params.page - 1) * params.pageSize),
    });
    if (params.kind) query.set('kind', params.kind);
    if (params.search?.trim()) query.set('search', params.search.trim());
    const payload = await apiClient.get<ListResponse<BackendContact>>(
      `${CONTACTS_BASE_PATH}/`,
      Object.fromEntries(query.entries()) as Record<string, string>,
    );
    const rows = normalizeList<BackendContact>(payload, ['contacts']);
    const mapped = rows.map(mapBackendContactToUi);
    return { data: mapped, pagination: { total: mapped.length, page: params.page, pageSize: params.pageSize } };
  }

  async getById(id: string): Promise<MockContact> {
    const payload = await apiClient.get<unknown>(`${CONTACTS_BASE_PATH}/${id}`);
    return mapBackendContactToUi((normalizeSingle<BackendContact>(payload, ['contact']) ?? {}) as BackendContact);
  }

  async create(input: Record<string, unknown>): Promise<MockContact> {
    const payload = await apiClient.post<unknown>(`${CONTACTS_BASE_PATH}/`, input);
    return mapBackendContactToUi((normalizeSingle<BackendContact>(payload, ['contact']) ?? {}) as BackendContact);
  }

  async update(id: string, input: Record<string, unknown>): Promise<MockContact> {
    const payload = await apiClient.patch<unknown>(`${CONTACTS_BASE_PATH}/${id}`, input);
    return mapBackendContactToUi((normalizeSingle<BackendContact>(payload, ['contact']) ?? {}) as BackendContact);
  }

  async remove(id: string): Promise<void> {
    await apiClient.delete(`${CONTACTS_BASE_PATH}/${id}`);
  }
}

export const contactsService = new ContactsService();
