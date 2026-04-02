import axios from 'axios';
import { API_BASE_URL } from './api';

type UnknownRecord = Record<string, unknown>;

export interface UiFileItem {
  id: string;
  name: string;
  size: number;
  created_at: string;
}

const http = axios.create({
  baseURL: API_BASE_URL,
});

http.interceptors.request.use((config) => {
  const token = localStorage.getItem('token') || localStorage.getItem('accessToken');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

const asArray = (v: unknown): UnknownRecord[] => (Array.isArray(v) ? (v as UnknownRecord[]) : []);

const mapBackendFile = (row: UnknownRecord): UiFileItem => ({
  id: String(row.uuid ?? row.public_id ?? row.id ?? ''),
  name: String(row.original_filename ?? row.filename ?? row.name ?? 'untitled'),
  size: Number(row.file_size ?? row.size ?? 0),
  created_at: String(row.created_at ?? ''),
});

class FilesService {
  async list(params: { limit?: number; offset?: number } = {}): Promise<UiFileItem[]> {
    const response = await http.get('/int/v1/files/', {
      params: { limit: params.limit ?? 100, offset: params.offset ?? 0 },
    });
    return asArray(response.data).map(mapBackendFile);
  }

  async getById(id: string): Promise<UiFileItem> {
    const response = await http.get(`/int/v1/files/${id}`);
    return mapBackendFile((response.data ?? {}) as UnknownRecord);
  }

  async upload(file: File): Promise<UiFileItem> {
    const formData = new FormData();
    formData.append('file', file);
    const response = await http.post('/int/v1/files/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return mapBackendFile((response.data ?? {}) as UnknownRecord);
  }

  async download(id: string): Promise<void> {
    const response = await http.get(`/int/v1/files/download/${id}`, {
      responseType: 'blob',
    });
    const disposition = String(response.headers['content-disposition'] ?? '');
    const fileNameMatch = disposition.match(/filename="(.+?)"/);
    const fileName = fileNameMatch?.[1] ?? `file-${id}`;

    const blobUrl = window.URL.createObjectURL(new Blob([response.data]));
    const a = document.createElement('a');
    a.href = blobUrl;
    a.download = fileName;
    document.body.appendChild(a);
    a.click();
    a.remove();
    window.URL.revokeObjectURL(blobUrl);
  }

  async remove(id: string): Promise<void> {
    await http.delete(`/int/v1/files/${id}`);
  }
}

export const filesService = new FilesService();
