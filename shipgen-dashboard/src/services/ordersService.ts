import { apiClient } from './apiClient';
import { normalizeList, normalizeSingle } from './baseService';
import type { ListResponse, PaginatedResponse } from '../types/api';

export interface UiOrder {
  id: string;
  public_id?: string;
  type: string;
  internal_id: string;
  notes: string;
  scheduled_at: string;
  status: string;
  driver_assigned_uuid?: string;
  vehicle_assigned_uuid?: string;
  meta: {
    customer_name: string;
    priority: string;
    pickup?: {
      address: string;
      lat: number | null;
      lng: number | null;
    };
    delivery?: {
      address: string;
      lat: number | null;
      lng: number | null;
    };
    [key: string]: unknown;
  };
  options: {
    pod_required: boolean;
  };
  created_at: string;
  updated_at: string;
}

interface BackendOrder {
  id?: number | string | null;
  uuid?: string | null;
  public_id?: string | null;
  type?: string | null;
  internal_id?: string | null;
  notes?: string | null;
  scheduled_at?: string | null;
  status?: string | null;
  driver_assigned_uuid?: string | null;
  vehicle_assigned_uuid?: string | null;
  pod_required?: boolean | null;
  meta?: Record<string, unknown> | null;
  options?: Record<string, unknown> | null;
  created_at?: string | null;
  updated_at?: string | null;
}

export type OrderListResult = PaginatedResponse<UiOrder>;
export interface UiOrderLifecycleEvent {
  uuid: string;
  event_type: string;
  from_status: string;
  to_status: string;
  actor_uuid: string;
  payload: Record<string, unknown>;
  created_at: string;
}

const ORDERS_BASE_PATH = '/fleetops/v1/orders';
const MAX_ORDERS_LIMIT = 100;

const toIsoOrEmpty = (value?: string | null): string => {
  if (!value) return '';
  const d = new Date(value);
  return Number.isNaN(d.getTime()) ? '' : d.toISOString();
};

const normalizeStatus = (status?: string | null): string => {
  if (!status) return 'created';
  return status.toLowerCase();
};

const mapBackendOrderToUi = (order: BackendOrder): UiOrder => {
  const meta = (order.meta ?? {}) as Record<string, unknown>;
  const options = (order.options ?? {}) as Record<string, unknown>;

  return {
    id: String(order.uuid ?? order.public_id ?? order.id ?? ''),
    public_id: String(order.public_id ?? ''),
    type: String(order.type ?? 'pickup'),
    internal_id: String(order.internal_id ?? ''),
    notes: String(order.notes ?? ''),
    scheduled_at: toIsoOrEmpty(order.scheduled_at),
    status: normalizeStatus(order.status),
    driver_assigned_uuid: String(order.driver_assigned_uuid ?? ''),
    vehicle_assigned_uuid: String(order.vehicle_assigned_uuid ?? ''),
    meta: {
      customer_name: String(meta.customer_name ?? ''),
      priority: String(meta.priority ?? 'normal'),
      pickup:
        meta.pickup && typeof meta.pickup === 'object'
          ? {
              address: String((meta.pickup as Record<string, unknown>).address ?? ''),
              lat:
                (meta.pickup as Record<string, unknown>).lat == null
                  ? null
                  : Number((meta.pickup as Record<string, unknown>).lat),
              lng:
                (meta.pickup as Record<string, unknown>).lng == null
                  ? null
                  : Number((meta.pickup as Record<string, unknown>).lng),
            }
          : undefined,
      delivery:
        meta.delivery && typeof meta.delivery === 'object'
          ? {
              address: String((meta.delivery as Record<string, unknown>).address ?? ''),
              lat:
                (meta.delivery as Record<string, unknown>).lat == null
                  ? null
                  : Number((meta.delivery as Record<string, unknown>).lat),
              lng:
                (meta.delivery as Record<string, unknown>).lng == null
                  ? null
                  : Number((meta.delivery as Record<string, unknown>).lng),
            }
          : undefined,
    },
    options: {
      pod_required: Boolean(options.pod_required ?? order.pod_required ?? false),
    },
    created_at: toIsoOrEmpty(order.created_at),
    updated_at: toIsoOrEmpty(order.updated_at),
  };
};

class OrdersService {
  async list(params: {
    page: number;
    pageSize: number;
    status?: string;
    search?: string;
    start_date?: string;
    end_date?: string;
  }): Promise<OrderListResult> {
    const requestedPageSize = Number.isFinite(params.pageSize) ? params.pageSize : 50;
    const safePageSize = Math.min(Math.max(1, requestedPageSize), MAX_ORDERS_LIMIT);
    const query = new URLSearchParams({
      limit: String(safePageSize),
      offset: String((params.page - 1) * safePageSize),
    });
    if (params.status && params.status !== 'all') {
      query.set('status', params.status);
    }
    if (params.search) {
      query.set('search', params.search);
    }
    if (params.start_date) {
      query.set('start_date', params.start_date);
    }
    if (params.end_date) {
      query.set('end_date', params.end_date);
    }

    const payload = await apiClient.get<ListResponse<BackendOrder>>(`${ORDERS_BASE_PATH}/?${query.toString()}`);
    const rows = normalizeList<BackendOrder>(payload, ['orders']);
    const mapped = rows.map(mapBackendOrderToUi);
    if (import.meta.env.DEV) {
      // eslint-disable-next-line no-console -- dev-only API debugging
      console.debug('[ordersService.list] payload', payload);
      // eslint-disable-next-line no-console -- dev-only API debugging
      console.debug('[ordersService.list] extracted', rows.length, rows.map((r) => ({ uuid: r.uuid, public_id: r.public_id, id: r.id })));
      // eslint-disable-next-line no-console -- dev-only API debugging
      console.debug('[ordersService.list] mapped ids', mapped.map((m) => m.id));
    }
    return {
      data: mapped,
      pagination: {
        total: mapped.length,
        page: params.page,
        pageSize: safePageSize,
      },
    };
  }

  async getById(id: string): Promise<UiOrder> {
    const payload = await apiClient.get<unknown>(`${ORDERS_BASE_PATH}/${id}`);
    const row = normalizeSingle<BackendOrder>(payload, ['order']);
    return mapBackendOrderToUi((row ?? {}) as BackendOrder);
  }

  async create(input: Omit<UiOrder, 'id' | 'created_at' | 'updated_at'>): Promise<UiOrder> {
    const payload = await apiClient.post<unknown>(`${ORDERS_BASE_PATH}/`, {
      type: input.type,
      internal_id: input.internal_id || null,
      notes: input.notes || null,
      scheduled_at: input.scheduled_at || null,
      meta: input.meta ?? {},
      options: input.options ?? {},
    });
    const row = normalizeSingle<BackendOrder>(payload, ['order']);
    return mapBackendOrderToUi((row ?? {}) as BackendOrder);
  }

  async update(id: string, input: Partial<Omit<UiOrder, 'id' | 'created_at' | 'updated_at'>>): Promise<UiOrder> {
    const payload = await apiClient.patch<unknown>(`${ORDERS_BASE_PATH}/${id}`, {
      type: input.type,
      internal_id: input.internal_id ?? null,
      notes: input.notes ?? null,
      scheduled_at: input.scheduled_at ?? null,
      status: input.status ?? null,
      meta: input.meta ?? {},
      options: input.options ?? {},
    });
    const row = normalizeSingle<BackendOrder>(payload, ['order']);
    return mapBackendOrderToUi((row ?? {}) as BackendOrder);
  }

  async assign(
    id: string,
    input: { driver_uuid?: string; vehicle_uuid?: string; mode?: 'auto' | 'manual'; note?: string }
  ): Promise<UiOrder> {
    const payload = await apiClient.post<unknown>(`${ORDERS_BASE_PATH}/${id}/assign`, {
      driver_id: input.driver_uuid || null,
      driver_uuid: input.driver_uuid || null,
      vehicle_id: input.vehicle_uuid || null,
      vehicle_uuid: input.vehicle_uuid || null,
      mode: input.mode || (input.driver_uuid || input.vehicle_uuid ? 'manual' : 'auto'),
      note: input.note || null,
    });
    const row = normalizeSingle<BackendOrder>(payload, ['order']);
    return mapBackendOrderToUi((row ?? {}) as BackendOrder);
  }

  async transition(id: string, input: { to_status: string; note?: string; meta?: Record<string, unknown> }): Promise<UiOrder> {
    const payload = await apiClient.post<unknown>(`${ORDERS_BASE_PATH}/${id}/transition`, {
      to_status: input.to_status,
      note: input.note || null,
      meta: input.meta ?? {},
    });
    const row = normalizeSingle<BackendOrder>(payload, ['order']);
    return mapBackendOrderToUi((row ?? {}) as BackendOrder);
  }

  async createException(
    id: string,
    input: {
      title: string;
      report: string;
      category?: string;
      type?: string;
      priority?: string;
      status?: string;
      reassign_driver_uuid?: string;
      meta?: Record<string, unknown>;
    }
  ): Promise<UiOrder> {
    const payload = await apiClient.post<unknown>(`${ORDERS_BASE_PATH}/${id}/exceptions`, {
      title: input.title,
      report: input.report,
      category: input.category || 'operations',
      type: input.type || 'delivery_exception',
      priority: input.priority || 'medium',
      status: input.status || 'open',
      reassign_driver_uuid: input.reassign_driver_uuid || null,
      meta: input.meta ?? {},
    });
    const row = normalizeSingle<BackendOrder>(payload, ['order']);
    return mapBackendOrderToUi((row ?? {}) as BackendOrder);
  }

  async lifecycle(id: string): Promise<UiOrderLifecycleEvent[]> {
    const payload = await apiClient.get<unknown>(`${ORDERS_BASE_PATH}/${id}/lifecycle`);
    const rows = normalizeList<Record<string, unknown>>(payload);
    return rows.map((row) => ({
      uuid: String(row.uuid ?? ''),
      event_type: String(row.event_type ?? ''),
      from_status: String(row.from_status ?? ''),
      to_status: String(row.to_status ?? ''),
      actor_uuid: String(row.actor_uuid ?? ''),
      payload: ((row.payload ?? {}) as Record<string, unknown>),
      created_at: toIsoOrEmpty(String(row.created_at ?? '')),
    }));
  }
}

export const ordersService = new OrdersService();
