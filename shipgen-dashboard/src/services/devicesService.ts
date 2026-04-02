import { apiClient } from './apiClient';

type UnknownRecord = Record<string, unknown>;

export interface UiDevice {
  id: string;
  name: string;
  status: string;
  last_seen: string;
  latitude: string;
  longitude: string;
  device_id: string;
  connection_status: string;
}

const mapDevice = (row: UnknownRecord): UiDevice => ({
  id: String(row.public_id ?? row.uuid ?? row.device_id ?? ''),
  name: String(row.name ?? row.device_name ?? row.device_id ?? 'Unnamed Device'),
  status: String(row.status ?? 'unknown'),
  last_seen: String(row.last_online_at ?? row.updated_at ?? ''),
  latitude: String(row.latitude ?? ''),
  longitude: String(row.longitude ?? ''),
  device_id: String(row.device_id ?? ''),
  connection_status: String(row.connection_status ?? ''),
});

class DevicesService {
  async list(params: { limit?: number; offset?: number } = {}): Promise<UiDevice[]> {
    const payload = await apiClient.get<UnknownRecord[]>('/int/v1/devices/', {
      limit: params.limit ?? 100,
      offset: params.offset ?? 0,
    });
    return Array.isArray(payload) ? payload.map(mapDevice) : [];
  }

  async getById(id: string): Promise<UiDevice> {
    const payload = await apiClient.get<UnknownRecord>(`/int/v1/devices/${id}`);
    return mapDevice(payload);
  }

  async heartbeat(id: string): Promise<UiDevice> {
    const payload = await apiClient.post<UnknownRecord>(`/int/v1/devices/${id}/heartbeat`, {
      online: true,
    });
    return mapDevice(payload);
  }

  async updateLocation(id: string, latitude: number, longitude: number): Promise<UiDevice> {
    const payload = await apiClient.post<UnknownRecord>(`/int/v1/devices/${id}/location`, {
      latitude,
      longitude,
    });
    return mapDevice(payload);
  }

  async remove(id: string): Promise<void> {
    await apiClient.delete(`/int/v1/devices/${id}`);
  }
}

export const devicesService = new DevicesService();
