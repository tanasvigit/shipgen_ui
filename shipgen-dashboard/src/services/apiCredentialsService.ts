import { apiClient } from './apiClient';

type UnknownRecord = Record<string, unknown>;

export interface UiApiCredential {
  id: string;
  name: string;
  keyMasked: string;
  created_at: string;
}

export interface ApiCredentialSecretResult {
  id: string;
  name: string;
  fullKey: string;
  created_at: string;
}

const maskKey = (key: string): string => {
  if (!key) return '****';
  const tail = key.slice(-4);
  return `****${tail}`;
};

const toUi = (row: UnknownRecord): UiApiCredential => {
  const key = String(row.key ?? '');
  return {
    id: String(row.uuid ?? row.id ?? ''),
    name: String(row.name ?? ''),
    keyMasked: maskKey(key),
    created_at: String(row.created_at ?? ''),
  };
};

const toSecretResult = (row: UnknownRecord): ApiCredentialSecretResult => ({
  id: String(row.uuid ?? row.id ?? ''),
  name: String(row.name ?? ''),
  fullKey: String(row.key ?? ''),
  created_at: String(row.created_at ?? ''),
});

class ApiCredentialsService {
  async list(params: { limit?: number; offset?: number } = {}): Promise<UiApiCredential[]> {
    const payload = await apiClient.get<UnknownRecord[]>('/int/v1/api-credentials/', {
      limit: params.limit ?? 100,
      offset: params.offset ?? 0,
    });
    return Array.isArray(payload) ? payload.map((x) => toUi((x ?? {}) as UnknownRecord)) : [];
  }

  async create(name: string): Promise<ApiCredentialSecretResult> {
    const payload = await apiClient.post<UnknownRecord>('/int/v1/api-credentials/', { name });
    return toSecretResult(payload);
  }

  async rotate(id: string, password: string): Promise<ApiCredentialSecretResult> {
    const payload = await apiClient.patch<UnknownRecord>(`/int/v1/api-credentials/roll/${id}`, { password });
    return toSecretResult(payload);
  }

  async remove(id: string): Promise<void> {
    await apiClient.delete(`/int/v1/api-credentials/${id}`);
  }
}

export const apiCredentialsService = new ApiCredentialsService();
