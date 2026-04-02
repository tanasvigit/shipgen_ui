import { apiClient } from './apiClient';

type UnknownRecord = Record<string, unknown>;

export interface UiCustomField {
  id: string;
  name: string;
  type: string;
  entity: string;
  required: boolean;
  created_at: string;
}

export interface CustomFieldInput {
  name: string;
  type?: string;
  entity?: string;
  required?: boolean;
}

const toBool = (value: unknown): boolean => {
  if (typeof value === 'boolean') return value;
  if (typeof value === 'number') return value === 1;
  if (typeof value === 'string') return ['1', 'true', 'yes'].includes(value.toLowerCase());
  return false;
};

const mapField = (row: UnknownRecord): UiCustomField => ({
  id: String(row.uuid ?? row.public_id ?? row.id ?? ''),
  name: String(row.name ?? row.label ?? ''),
  type: String(row.type ?? ''),
  entity: String(row.subject_type ?? row.for_field ?? ''),
  required: toBool(row.required),
  created_at: String(row.created_at ?? ''),
});

class CustomFieldsService {
  async list(params: { limit?: number; offset?: number } = {}): Promise<UiCustomField[]> {
    const payload = await apiClient.get<UnknownRecord[]>('/int/v1/custom-fields/', {
      limit: params.limit ?? 100,
      offset: params.offset ?? 0,
    });
    return Array.isArray(payload) ? payload.map((x) => mapField((x ?? {}) as UnknownRecord)) : [];
  }

  async getById(id: string): Promise<UiCustomField> {
    const payload = await apiClient.get<UnknownRecord>(`/int/v1/custom-fields/${id}`);
    return mapField((payload ?? {}) as UnknownRecord);
  }

  async create(input: CustomFieldInput): Promise<UiCustomField> {
    const payload = await apiClient.post<UnknownRecord>('/int/v1/custom-fields/', {
      name: input.name,
      label: input.name,
      type: input.type || null,
      subject_type: input.entity || null,
      required: !!input.required,
    });
    return mapField((payload ?? {}) as UnknownRecord);
  }

  async update(id: string, input: CustomFieldInput): Promise<UiCustomField> {
    const payload = await apiClient.patch<UnknownRecord>(`/int/v1/custom-fields/${id}`, {
      ...(input.name !== undefined ? { name: input.name, label: input.name } : {}),
      ...(input.type !== undefined ? { type: input.type } : {}),
      ...(input.entity !== undefined ? { subject_type: input.entity } : {}),
      ...(input.required !== undefined ? { required: !!input.required } : {}),
    });
    return mapField((payload ?? {}) as UnknownRecord);
  }

  async remove(id: string): Promise<void> {
    await apiClient.delete(`/int/v1/custom-fields/${id}`);
  }
}

export const customFieldsService = new CustomFieldsService();
