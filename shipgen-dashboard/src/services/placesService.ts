import { apiClient } from './apiClient';
import { normalizeList, normalizeSingle } from './baseService';
import type { ListResponse, PaginatedResponse } from '../types/api';
import type { MockPlace } from '../mocks/data/places';

interface BackendPlace {
  uuid?: string | null;
  public_id?: string | null;
  company_uuid?: string | null;
  owner_uuid?: string | null;
  owner_type?: string | null;
  name?: string | null;
  street1?: string | null;
  street2?: string | null;
  city?: string | null;
  province?: string | null;
  postal_code?: string | null;
  neighborhood?: string | null;
  district?: string | null;
  building?: string | null;
  security_access_code?: string | null;
  country?: string | null;
  latitude?: string | null;
  longitude?: string | null;
  meta?: Record<string, unknown> | null;
  phone?: string | null;
  remarks?: string | null;
  type?: string | null;
  created_at?: string | null;
  updated_at?: string | null;
  id?: number | null;
}

export type PlaceListResult = PaginatedResponse<MockPlace>;

const PLACES_BASE_PATH = '/fleetops/v1/places';

const mapBackendPlaceToUi = (p: BackendPlace): MockPlace => ({
  uuid: p.uuid ?? null,
  public_id: p.public_id ?? null,
  company_uuid: p.company_uuid ?? null,
  owner_uuid: p.owner_uuid ?? null,
  owner_type: p.owner_type ?? null,
  name: p.name ?? null,
  street1: p.street1 ?? null,
  street2: p.street2 ?? null,
  city: p.city ?? null,
  province: p.province ?? null,
  postal_code: p.postal_code ?? null,
  neighborhood: p.neighborhood ?? null,
  district: p.district ?? null,
  building: p.building ?? null,
  security_access_code: p.security_access_code ?? null,
  country: p.country ?? null,
  latitude: p.latitude ?? null,
  longitude: p.longitude ?? null,
  meta: p.meta ?? null,
  phone: p.phone ?? null,
  remarks: p.remarks ?? null,
  type: p.type ?? null,
  created_at: p.created_at ?? null,
  updated_at: p.updated_at ?? null,
  id: p.id ?? null,
});

class PlacesService {
  async list(params: { page: number; pageSize: number }): Promise<PlaceListResult> {
    const query = new URLSearchParams({
      limit: String(params.pageSize),
      offset: String((params.page - 1) * params.pageSize),
    });
    const payload = await apiClient.get<ListResponse<BackendPlace>>(`${PLACES_BASE_PATH}/?${query.toString()}`);
    const rows = normalizeList<BackendPlace>(payload, ['places']);
    const mapped = rows.map(mapBackendPlaceToUi);
    return { data: mapped, pagination: { total: mapped.length, page: params.page, pageSize: params.pageSize } };
  }

  async getById(id: string): Promise<MockPlace> {
    const payload = await apiClient.get<unknown>(`${PLACES_BASE_PATH}/${id}`);
    return mapBackendPlaceToUi((normalizeSingle<BackendPlace>(payload, ['place']) ?? {}) as BackendPlace);
  }

  async create(input: Record<string, unknown>): Promise<MockPlace> {
    const payload = await apiClient.post<unknown>(`${PLACES_BASE_PATH}/`, input);
    return mapBackendPlaceToUi((normalizeSingle<BackendPlace>(payload, ['place']) ?? {}) as BackendPlace);
  }

  async update(id: string, input: Record<string, unknown>): Promise<MockPlace> {
    const payload = await apiClient.patch<unknown>(`${PLACES_BASE_PATH}/${id}`, input);
    return mapBackendPlaceToUi((normalizeSingle<BackendPlace>(payload, ['place']) ?? {}) as BackendPlace);
  }

  async remove(id: string): Promise<void> {
    await apiClient.delete(`${PLACES_BASE_PATH}/${id}`);
  }
}

export const placesService = new PlacesService();
