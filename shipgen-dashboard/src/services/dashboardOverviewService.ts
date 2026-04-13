import { apiClient } from './apiClient';
import { normalizeList } from './baseService';
import { UserRole } from '../types';

type GenericRecord = Record<string, unknown>;

export interface DashboardModuleCount {
  key: string;
  label: string;
  endpoint: string;
  route: string;
  count: number;
}

export interface DashboardOverviewData {
  orders: GenericRecord[];
  drivers: GenericRecord[];
  vehicles: GenericRecord[];
  issues: GenericRecord[];
  fuelReports: GenericRecord[];
  moduleCounts: DashboardModuleCount[];
  backendLimitations: string[];
}

const asArray = (value: unknown): GenericRecord[] => (Array.isArray(value) ? (value as GenericRecord[]) : []);
const isFleetCustomerSession = (): boolean => {
  if (typeof localStorage === 'undefined') return false;
  try {
    const raw = localStorage.getItem('user');
    if (!raw) return false;
    const parsed = JSON.parse(raw) as { role?: string };
    return (parsed.role || '').toUpperCase() === UserRole.FLEET_CUSTOMER;
  } catch {
    return false;
  }
};

class DashboardOverviewService {
  private inferCollectionKey(payload: Record<string, unknown>): string | null {
    const keys = Object.keys(payload);
    for (const key of keys) {
      if (Array.isArray(payload[key])) {
        return key;
      }
    }
    return null;
  }

  private async fetchAll<T extends GenericRecord>(endpoint: string, collectionKey: string): Promise<T[]> {
    const limit = 100;
    let offset = 0;
    const all: T[] = [];

    while (true) {
      const payload = await apiClient.get<unknown>(`${endpoint}/`, { limit, offset });
      const page = normalizeList<T>(payload, [collectionKey]);
      if (page.length === 0) break;
      all.push(...page);
      if (page.length < limit) break;
      offset += limit;
    }

    return all;
  }

  private async fetchAllAuto<T extends GenericRecord>(endpoint: string): Promise<T[]> {
    const limit = 100;
    let offset = 0;
    const all: T[] = [];

    while (true) {
      const path = endpoint.endsWith('/tasks') ? endpoint : `${endpoint}/`;
      const payload = await apiClient.get<unknown>(path, { limit, offset });
      if (Array.isArray(payload)) {
        return payload as T[];
      }
      const recordPayload = payload as Record<string, unknown>;
      const collectionKey = this.inferCollectionKey(recordPayload);
      if (!collectionKey) break;
      const page = asArray(recordPayload[collectionKey]) as T[];
      if (page.length === 0) break;
      all.push(...page);
      if (page.length < limit) break;
      offset += limit;
    }

    return all;
  }

  async fetchOverview(): Promise<DashboardOverviewData> {
    if (isFleetCustomerSession()) {
      return {
        orders: [],
        drivers: [],
        vehicles: [],
        issues: [],
        fuelReports: [],
        moduleCounts: [],
        backendLimitations: ['Dashboard metrics are not available for fleet customer accounts.'],
      };
    }
    const [ordersRes, driversRes, vehiclesRes, issuesRes, fuelReportsRes] = await Promise.all([
      this.fetchAll<GenericRecord>('/fleetops/v1/orders', 'orders'),
      this.fetchAll<GenericRecord>('/fleetops/v1/drivers', 'drivers'),
      this.fetchAll<GenericRecord>('/fleetops/v1/vehicles', 'vehicles'),
      this.fetchAll<GenericRecord>('/fleetops/v1/issues', 'issues'),
      this.fetchAll<GenericRecord>('/fleetops/v1/fuel-reports', 'fuel_reports'),
    ]);

    const orders = ordersRes;
    const drivers = driversRes;
    const vehicles = vehiclesRes;
    const issues = issuesRes;
    const fuelReports = fuelReportsRes;

    const modules: Omit<DashboardModuleCount, 'count'>[] = [
      { key: 'orders', label: 'Orders', endpoint: '/fleetops/v1/orders', route: '/logistics/orders' },
      { key: 'drivers', label: 'Drivers', endpoint: '/fleetops/v1/drivers', route: '/fleet/drivers' },
      { key: 'vehicles', label: 'Vehicles', endpoint: '/fleetops/v1/vehicles', route: '/fleet/vehicles' },
      { key: 'vendors', label: 'Vendors', endpoint: '/fleetops/v1/vendors', route: '/fleet/vendors' },
      { key: 'places', label: 'Places', endpoint: '/fleetops/v1/places', route: '/fleet/places' },
      { key: 'contacts', label: 'Contacts', endpoint: '/fleetops/v1/contacts', route: '/fleet/contacts' },
      { key: 'issues', label: 'Issues', endpoint: '/fleetops/v1/issues', route: '/fleet/issues' },
      { key: 'fuel_reports', label: 'Fuel Reports', endpoint: '/fleetops/v1/fuel-reports', route: '/fleet/fuel-reports' },
      { key: 'fleets', label: 'Fleets', endpoint: '/fleetops/v1/fleets', route: '/fleet/fleets' },
      { key: 'service_areas', label: 'Service Areas', endpoint: '/fleetops/v1/service-areas', route: '/fleet/service-areas' },
      { key: 'zones', label: 'Zones', endpoint: '/fleetops/v1/zones', route: '/fleet/zones' },
      { key: 'tracking_numbers', label: 'Tracking Numbers', endpoint: '/fleetops/v1/tracking-numbers', route: '/fleet/tracking-numbers' },
      { key: 'tracking_statuses', label: 'Tracking Statuses', endpoint: '/fleetops/v1/tracking-statuses', route: '/fleet/tracking-statuses' },
      { key: 'payloads', label: 'Payloads', endpoint: '/fleetops/v1/payloads', route: '/fleet/payloads' },
      { key: 'entities', label: 'Entities', endpoint: '/fleetops/v1/entities', route: '/fleet/entities' },
      { key: 'transactions', label: 'Transactions', endpoint: '/int/v1/transactions', route: '/analytics/transactions' },
      { key: 'users', label: 'Users', endpoint: '/int/v1/users', route: '/analytics/users' },
      { key: 'companies', label: 'Companies', endpoint: '/int/v1/companies', route: '/analytics/companies' },
      { key: 'custom_fields', label: 'Custom Fields', endpoint: '/int/v1/custom-fields', route: '/analytics/custom-fields' },
      { key: 'custom_field_values', label: 'Custom Field Values', endpoint: '/int/v1/custom-field-values', route: '/analytics/custom-field-values' },
      { key: 'schedules', label: 'Schedules', endpoint: '/int/v1/schedules', route: '/analytics/schedules' },
      { key: 'schedule_items', label: 'Schedule Items', endpoint: '/int/v1/schedules-items', route: '/analytics/schedule-items' },
      { key: 'schedule_templates', label: 'Schedule Templates', endpoint: '/int/v1/schedules-templates', route: '/analytics/schedule-templates' },
      { key: 'schedule_availability', label: 'Schedule Availability', endpoint: '/int/v1/schedules-availability', route: '/analytics/schedule-availability' },
      { key: 'schedule_constraints', label: 'Schedule Constraints', endpoint: '/int/v1/schedules-constraints', route: '/analytics/schedule-constraints' },
      { key: 'schedule_monitor', label: 'Schedule Monitor', endpoint: '/int/v1/schedules-monitor/tasks', route: '/analytics/schedule-monitor' },
      { key: 'api_events', label: 'API Events', endpoint: '/int/v1/api-events', route: '/analytics/api-events' },
      { key: 'api_request_logs', label: 'API Request Logs', endpoint: '/int/v1/api-request-logs', route: '/analytics/api-request-logs' },
      { key: 'api_credentials', label: 'API Credentials', endpoint: '/int/v1/api-credentials', route: '/analytics/api-credentials' },
      { key: 'comments', label: 'Comments', endpoint: '/int/v1/comments', route: '/analytics/comments' },
    ];

    const backendLimitations: string[] = [];
    backendLimitations.push('`/int/v1/dashboards` stores dashboard configs/widgets, not aggregated KPI metrics.');
    const moduleCounts: DashboardModuleCount[] = [];

    await Promise.all(
      modules.map(async (moduleDef) => {
        try {
          const rows = await this.fetchAllAuto<GenericRecord>(moduleDef.endpoint);
          moduleCounts.push({
            ...moduleDef,
            count: rows.length,
          });
        } catch (err: unknown) {
          const message = err instanceof Error ? err.message : 'unknown error';
          backendLimitations.push(`Could not load \`${moduleDef.endpoint}\`: ${message}`);
        }
      }),
    );

    return {
      orders,
      drivers,
      vehicles,
      issues,
      fuelReports,
      moduleCounts: moduleCounts.sort((a, b) => a.label.localeCompare(b.label)),
      backendLimitations,
    };
  }
}

export const dashboardOverviewService = new DashboardOverviewService();
