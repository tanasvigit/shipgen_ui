import { apiClient } from './apiClient';
import { normalizeList, normalizeSingle } from './baseService';

export type TripStatus = 'PLANNED' | 'IN_PROGRESS' | 'COMPLETED';
export type TripOrderStatus = 'LOADED' | 'IN_TRANSIT' | 'DELIVERED';
export type StopType = 'PICKUP' | 'DROPOFF';

export interface UiTripStop {
  location_name: string;
  type: StopType;
  sequence: number;
  is_completed?: boolean;
  completed_at?: string | null;
}

export interface UiTripOrder {
  order_id: number;
  pickup_location: string;
  drop_location: string;
  status: TripOrderStatus;
  load_units: number;
}

export interface UiTripEvent {
  event_type: string;
  metadata?: Record<string, unknown> | null;
  created_at?: string | null;
}

export interface UiTrip {
  id: number;
  uuid?: string | null;
  public_id?: string | null;
  vehicle_id: string;
  driver_id: string;
  vehicle_plate_number?: string | null;
  driver_name?: string | null;
  start_location: string;
  end_location: string;
  status: TripStatus;
  total_capacity: number;
  current_load: number;
  available_capacity: number;
  current_lat?: number | null;
  current_lng?: number | null;
  last_location_update?: string | null;
  started_at?: string | null;
  completed_at?: string | null;
  orders: UiTripOrder[];
  stops: UiTripStop[];
  events: UiTripEvent[];
  dashboard: {
    total_capacity: number;
    current_load: number;
    available_capacity: number;
    delivered_orders_count: number;
    pending_orders_count: number;
  };
}

const BASE = '/trips';

class TripsDispatchService {
  async list(): Promise<UiTrip[]> {
    const payload = await apiClient.get<unknown>(BASE);
    return normalizeList<UiTrip>(payload, ['trips']);
  }

  async getById(id: string | number): Promise<UiTrip> {
    const payload = await apiClient.get<unknown>(`${BASE}/${id}`);
    return (normalizeSingle<UiTrip>(payload, ['trip']) ?? {}) as UiTrip;
  }

  async create(input: {
    vehicle_id: string;
    driver_id: string;
    start_location: string;
    end_location: string;
    total_capacity: number;
    stops: { location_name: string; type: StopType; sequence: number }[];
  }): Promise<UiTrip> {
    const payload = await apiClient.post<unknown>(BASE, input);
    return (normalizeSingle<UiTrip>(payload, ['trip']) ?? {}) as UiTrip;
  }

  async assignOrder(
    tripId: string | number,
    input: { order_id: string; pickup_location: string; drop_location: string; load_units: number }
  ): Promise<UiTrip> {
    const payload = await apiClient.post<unknown>(`${BASE}/${tripId}/assign-order`, input);
    return (normalizeSingle<UiTrip>(payload, ['trip']) ?? {}) as UiTrip;
  }

  async start(tripId: string | number): Promise<UiTrip> {
    const payload = await apiClient.post<unknown>(`${BASE}/${tripId}/start`, {});
    return (normalizeSingle<UiTrip>(payload, ['trip']) ?? {}) as UiTrip;
  }

  async completeStop(
    tripId: string | number,
    input: {
      stop_sequence: number;
      new_pickups: { order_id: string; pickup_location: string; drop_location: string; load_units: number }[];
    }
  ): Promise<UiTrip> {
    const payload = await apiClient.post<unknown>(`${BASE}/${tripId}/complete-stop`, input);
    return (normalizeSingle<UiTrip>(payload, ['trip']) ?? {}) as UiTrip;
  }

  async updateLocation(tripId: string | number, input: { current_lat: number; current_lng: number }): Promise<UiTrip> {
    const payload = await apiClient.post<unknown>(`${BASE}/${tripId}/location`, input);
    return (normalizeSingle<UiTrip>(payload, ['trip']) ?? {}) as UiTrip;
  }

  async events(tripId: string | number): Promise<UiTripEvent[]> {
    const payload = await apiClient.get<unknown>(`${BASE}/${tripId}/events`);
    return normalizeList<UiTripEvent>(payload, ['events']);
  }
}

export const tripsDispatchService = new TripsDispatchService();
