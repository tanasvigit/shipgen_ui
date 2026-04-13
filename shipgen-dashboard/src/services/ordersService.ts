import { apiClient } from './apiClient';
import { normalizeList, normalizeSingle } from './baseService';
import type { ListResponse, PaginatedResponse } from '../types/api';
import { UserRole } from '../types';

export interface UiOrder {
  id: string;
  public_id?: string;
  type: string;
  internal_id: string;
  notes: string;
  scheduled_at: string;
  status: string;
  /** Resolved customer link; required for new orders from the API. */
  customer_uuid?: string;
  /** API-enriched display name (preferred over meta.customer_name). */
  customer_display_name?: string;
  /** User uuid when order was placed by a fleet customer (or other user). */
  created_by?: string;
  created_by_display_name?: string;
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
    goods_description?: string;
    pickup_location?: string;
    drop_location?: string;
    source?: string;
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
  customer_uuid?: string | null;
  customer_display_name?: string | null;
  created_by?: string | null;
  created_by_display_name?: string | null;
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
const CUSTOMER_ORDERS_BASE_PATH = '/orders';
const MAX_ORDERS_LIMIT = 100;

const toIsoOrEmpty = (value?: string | null): string => {
  if (!value) return '';
  const d = new Date(value);
  return Number.isNaN(d.getTime()) ? '' : d.toISOString();
};

const normalizeStatus = (status?: string | null): string => {
  if (!status) return 'created';
  const s = status.toLowerCase();
  if (s === 'order_created') return 'created';
  return s;
};

const getStoredRole = (): UserRole | null => {
  if (typeof localStorage === 'undefined') return null;
  try {
    const raw = localStorage.getItem('user');
    if (!raw) return null;
    const parsed = JSON.parse(raw) as { role?: string };
    return (parsed.role?.toUpperCase() as UserRole) || null;
  } catch {
    return null;
  }
};

const isFleetCustomer = (): boolean => getStoredRole() === UserRole.FLEET_CUSTOMER;
const shouldFallbackToCustomerOrders = (err: unknown): boolean => {
  const msg = err instanceof Error ? err.message : String(err ?? '');
  return msg.includes('Fleet customers can only use /orders endpoints');
};
const listUrlForBasePath = (basePath: string, query: string): string =>
  basePath === CUSTOMER_ORDERS_BASE_PATH ? `${basePath}?${query}` : `${basePath}/?${query}`;

const mapPickupFromMeta = (meta: Record<string, unknown>) => {
  if (meta.pickup && typeof meta.pickup === 'object') {
    const p = meta.pickup as Record<string, unknown>;
    return {
      address: String(p.address ?? ''),
      lat: p.lat == null ? null : Number(p.lat),
      lng: p.lng == null ? null : Number(p.lng),
    };
  }
  if (meta.pickup_location != null && String(meta.pickup_location).trim()) {
    return { address: String(meta.pickup_location), lat: null as number | null, lng: null as number | null };
  }
  return undefined;
};

const mapDeliveryFromMeta = (meta: Record<string, unknown>) => {
  if (meta.delivery && typeof meta.delivery === 'object') {
    const p = meta.delivery as Record<string, unknown>;
    return {
      address: String(p.address ?? ''),
      lat: p.lat == null ? null : Number(p.lat),
      lng: p.lng == null ? null : Number(p.lng),
    };
  }
  if (meta.drop_location != null && String(meta.drop_location).trim()) {
    return { address: String(meta.drop_location), lat: null as number | null, lng: null as number | null };
  }
  return undefined;
};

const mapBackendOrderToUi = (order: BackendOrder): UiOrder => {
  const meta = (order.meta ?? {}) as Record<string, unknown>;
  const options = (order.options ?? {}) as Record<string, unknown>;
  const pickup = mapPickupFromMeta(meta);
  const delivery = mapDeliveryFromMeta(meta);
  const goods =
    meta.goods_description != null && String(meta.goods_description).trim()
      ? String(meta.goods_description)
      : undefined;

  return {
    id: String(order.uuid ?? order.public_id ?? order.id ?? ''),
    public_id: String(order.public_id ?? ''),
    type: String(order.type ?? 'pickup'),
    internal_id: String(order.internal_id ?? ''),
    notes: String(order.notes ?? ''),
    scheduled_at: toIsoOrEmpty(order.scheduled_at),
    status: normalizeStatus(order.status),
    customer_uuid: order.customer_uuid ? String(order.customer_uuid) : undefined,
    customer_display_name: order.customer_display_name ? String(order.customer_display_name) : undefined,
    created_by: order.created_by ? String(order.created_by) : undefined,
    created_by_display_name: order.created_by_display_name ? String(order.created_by_display_name) : undefined,
    driver_assigned_uuid: String(order.driver_assigned_uuid ?? ''),
    vehicle_assigned_uuid: String(order.vehicle_assigned_uuid ?? ''),
    meta: {
      ...meta,
      customer_name: String(meta.customer_name ?? ''),
      priority: String(meta.priority ?? 'normal'),
      pickup,
      delivery,
      goods_description: goods,
    },
    options: {
      pod_required: Boolean(options.pod_required ?? order.pod_required ?? false),
    },
    created_at: toIsoOrEmpty(order.created_at),
    updated_at: toIsoOrEmpty(order.updated_at),
  };
};

/** Prefer API-resolved name; fall back to legacy meta.customer_name. */
export function orderCustomerLabel(order: UiOrder): string {
  const fromMeta = String(order.meta?.customer_name ?? '').trim();
  const resolved = String(order.customer_display_name ?? '').trim();
  const creator = String(order.created_by_display_name ?? '').trim();
  return resolved || fromMeta || creator || '—';
}

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

    const basePath = isFleetCustomer() ? CUSTOMER_ORDERS_BASE_PATH : ORDERS_BASE_PATH;
    let payload: ListResponse<BackendOrder>;
    try {
      payload = await apiClient.get<ListResponse<BackendOrder>>(
        listUrlForBasePath(basePath, query.toString()),
      );
    } catch (err) {
      if (basePath === ORDERS_BASE_PATH && shouldFallbackToCustomerOrders(err)) {
        payload = await apiClient.get<ListResponse<BackendOrder>>(
          listUrlForBasePath(CUSTOMER_ORDERS_BASE_PATH, query.toString()),
        );
      } else {
        throw err;
      }
    }
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
    const basePath = isFleetCustomer() ? CUSTOMER_ORDERS_BASE_PATH : ORDERS_BASE_PATH;
    let payload: unknown;
    try {
      payload = await apiClient.get<unknown>(`${basePath}/${id}`);
    } catch (err) {
      if (basePath === ORDERS_BASE_PATH && shouldFallbackToCustomerOrders(err)) {
        payload = await apiClient.get<unknown>(`${CUSTOMER_ORDERS_BASE_PATH}/${id}`);
      } else {
        throw err;
      }
    }
    const row = normalizeSingle<BackendOrder>(payload, ['order']);
    return mapBackendOrderToUi((row ?? {}) as BackendOrder);
  }

  async create(input: Omit<UiOrder, 'id' | 'created_at' | 'updated_at'>): Promise<UiOrder> {
    const customerPayload = {
      internal_id: input.internal_id?.trim() || null,
      pickup_location: String(input.meta?.pickup?.address ?? '').trim() || 'Unknown pickup',
      drop_location: String(input.meta?.delivery?.address ?? '').trim() || 'Unknown drop',
      goods_description:
        String(input.notes || '').trim() || String(input.internal_id || '').trim() || 'Order request',
    };
    const staffPayload = {
      customer_uuid: input.customer_uuid ?? null,
      type: input.type,
      internal_id: input.internal_id || null,
      notes: input.notes || null,
      scheduled_at: input.scheduled_at || null,
      meta: input.meta ?? {},
      options: input.options ?? {},
    };
    let payload: unknown;
    if (isFleetCustomer()) {
      payload = await apiClient.post<unknown>(`${CUSTOMER_ORDERS_BASE_PATH}`, customerPayload);
    } else {
      try {
        payload = await apiClient.post<unknown>(`${ORDERS_BASE_PATH}/`, staffPayload);
      } catch (err) {
        if (shouldFallbackToCustomerOrders(err)) {
          payload = await apiClient.post<unknown>(`${CUSTOMER_ORDERS_BASE_PATH}`, customerPayload);
        } else {
          throw err;
        }
      }
    }
    const row = normalizeSingle<BackendOrder>(payload, ['order']);
    return mapBackendOrderToUi((row ?? {}) as BackendOrder);
  }

  async update(id: string, input: Partial<Omit<UiOrder, 'id' | 'created_at' | 'updated_at'>>): Promise<UiOrder> {
    const body: Record<string, unknown> = {
      type: input.type,
      internal_id: input.internal_id ?? null,
      notes: input.notes ?? null,
      scheduled_at: input.scheduled_at ?? null,
      status: input.status ?? null,
      meta: input.meta ?? {},
      options: input.options ?? {},
    };
    const cid = input.customer_uuid;
    if (cid !== undefined && cid !== null && String(cid).trim() !== '') {
      body.customer_uuid = String(cid).trim();
    }
    const payload = await apiClient.patch<unknown>(`${ORDERS_BASE_PATH}/${id}`, body);
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
