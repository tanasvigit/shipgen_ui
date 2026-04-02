import { apiClient } from './apiClient';
import { normalizeList, normalizeSingle } from './baseService';
import type { ListResponse, PaginatedResponse } from '../types/api';
import type { MockFuelReport } from '../mocks/data/fuel_reports';

interface BackendFuelReport {
  uuid?: string | null;
  public_id?: string | null;
  company_uuid?: string | null;
  driver_uuid?: string | null;
  vehicle_uuid?: string | null;
  reported_by_uuid?: string | null;
  odometer?: string | null;
  location?: Record<string, unknown> | null;
  latitude?: string | null;
  longitude?: string | null;
  amount?: string | null;
  currency?: string | null;
  volume?: string | null;
  metric_unit?: string | null;
  report?: string | null;
  meta?: Record<string, unknown> | null;
  status?: string | null;
  created_at?: string | null;
  updated_at?: string | null;
  id?: number | null;
  vehicle_name?: string | null;
  driver_name?: string | null;
  reporter_name?: string | null;
}

export type FuelReportListResult = PaginatedResponse<MockFuelReport>;

const FUEL_REPORTS_BASE_PATH = '/fleetops/v1/fuel-reports';

const mapBackendFuelReportToUi = (r: BackendFuelReport): MockFuelReport => ({
  uuid: r.uuid ?? null,
  public_id: r.public_id ?? null,
  company_uuid: r.company_uuid ?? null,
  driver_uuid: r.driver_uuid ?? null,
  vehicle_uuid: r.vehicle_uuid ?? null,
  reported_by_uuid: r.reported_by_uuid ?? null,
  odometer: r.odometer ?? null,
  location: r.location ?? null,
  latitude: r.latitude ?? null,
  longitude: r.longitude ?? null,
  amount: r.amount ?? null,
  currency: r.currency ?? null,
  volume: r.volume ?? null,
  metric_unit: r.metric_unit ?? null,
  report: r.report ?? null,
  meta: r.meta ?? null,
  status: r.status ?? null,
  created_at: r.created_at ?? null,
  updated_at: r.updated_at ?? null,
  id: r.id ?? null,
  vehicle_name: r.vehicle_name ?? null,
  driver_name: r.driver_name ?? null,
  reporter_name: r.reporter_name ?? null,
});

class FuelReportsService {
  async list(params: { page: number; pageSize: number }): Promise<FuelReportListResult> {
    const query = new URLSearchParams({
      limit: String(params.pageSize),
      offset: String((params.page - 1) * params.pageSize),
    });
    const payload = await apiClient.get<ListResponse<BackendFuelReport>>(
      `${FUEL_REPORTS_BASE_PATH}/?${query.toString()}`
    );
    const rows = normalizeList<BackendFuelReport>(payload, ['fuel_reports']);
    const mapped = rows.map(mapBackendFuelReportToUi);
    return { data: mapped, pagination: { total: mapped.length, page: params.page, pageSize: params.pageSize } };
  }

  async getById(id: string): Promise<MockFuelReport> {
    const payload = await apiClient.get<unknown>(`${FUEL_REPORTS_BASE_PATH}/${id}`);
    return mapBackendFuelReportToUi((normalizeSingle<BackendFuelReport>(payload, ['fuel_report']) ?? {}) as BackendFuelReport);
  }

  async create(input: Record<string, unknown>): Promise<MockFuelReport> {
    const payload = await apiClient.post<unknown>(`${FUEL_REPORTS_BASE_PATH}/`, input);
    return mapBackendFuelReportToUi((normalizeSingle<BackendFuelReport>(payload, ['fuel_report']) ?? {}) as BackendFuelReport);
  }

  async updatePut(id: string, input: Record<string, unknown>): Promise<MockFuelReport> {
    const payload = await apiClient.put<unknown>(`${FUEL_REPORTS_BASE_PATH}/${id}`, input);
    return mapBackendFuelReportToUi((normalizeSingle<BackendFuelReport>(payload, ['fuel_report']) ?? {}) as BackendFuelReport);
  }

  async remove(id: string): Promise<void> {
    await apiClient.delete(`${FUEL_REPORTS_BASE_PATH}/${id}`);
  }
}

export const fuelReportsService = new FuelReportsService();
