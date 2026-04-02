import axios from 'axios';
import { API_BASE_URL } from './api';

type UnknownRecord = Record<string, unknown>;

export interface UiNotification {
  id: string;
  title: string;
  message: string;
  read_at: string;
  created_at: string;
  raw: UnknownRecord;
}

const http = axios.create({ baseURL: API_BASE_URL });

http.interceptors.request.use((config) => {
  const token = localStorage.getItem('token') || localStorage.getItem('accessToken');
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

const toUi = (row: UnknownRecord): UiNotification => {
  const data = (row.data ?? {}) as UnknownRecord;
  return {
    id: String(row.id ?? ''),
    title: String(data.title ?? data.subject ?? row.type ?? 'Notification'),
    message: String(data.message ?? data.body ?? data.description ?? ''),
    read_at: String(row.read_at ?? ''),
    created_at: String(row.created_at ?? ''),
    raw: row,
  };
};

class NotificationsService {
  async list(params: { limit?: number; offset?: number } = {}): Promise<UiNotification[]> {
    const response = await http.get('/int/v1/notifications/', {
      params: { limit: params.limit ?? 100, offset: params.offset ?? 0 },
    });
    const payload = response.data;
    return Array.isArray(payload) ? payload.map((x) => toUi((x ?? {}) as UnknownRecord)) : [];
  }

  async markAsRead(ids: string[]): Promise<void> {
    await http.put('/int/v1/notifications/mark-as-read', {
      notifications: ids,
    });
  }

  async markAllRead(): Promise<void> {
    await http.put('/int/v1/notifications/mark-all-read');
  }

  async bulkDelete(ids?: string[]): Promise<void> {
    await http.delete('/int/v1/notifications/bulk-delete', {
      data: ids ? { notifications: ids } : {},
    });
  }
}

export const notificationsService = new NotificationsService();
