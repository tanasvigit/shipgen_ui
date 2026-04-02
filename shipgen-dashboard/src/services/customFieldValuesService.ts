import { apiClient } from './apiClient';

type UnknownRecord = Record<string, unknown>;

export interface UiCustomFieldValue {
  id: string;
  custom_field_id: string;
  entity_id: string;
  value: string;
  created_at: string;
}

export interface CustomFieldValueInput {
  custom_field_id: string;
  entity_id: string;
  value: string;
  entity_type?: string;
  value_type?: string;
}

const mapValue = (row: UnknownRecord): UiCustomFieldValue => ({
  id: String(row.uuid ?? row.public_id ?? row.id ?? ''),
  custom_field_id: String(row.custom_field_uuid ?? row.custom_field_id ?? ''),
  entity_id: String(row.subject_uuid ?? row.entity_id ?? ''),
  value: String(row.value ?? ''),
  created_at: String(row.created_at ?? ''),
});

class CustomFieldValuesService {
  async list(params: { limit?: number; offset?: number } = {}): Promise<UiCustomFieldValue[]> {
    const payload = await apiClient.get<UnknownRecord[]>('/int/v1/custom-field-values/', {
      limit: params.limit ?? 100,
      offset: params.offset ?? 0,
    });
    return Array.isArray(payload) ? payload.map((x) => mapValue((x ?? {}) as UnknownRecord)) : [];
  }

  async getById(id: string): Promise<UiCustomFieldValue> {
    const payload = await apiClient.get<UnknownRecord>(`/int/v1/custom-field-values/${id}`);
    return mapValue((payload ?? {}) as UnknownRecord);
  }

  async create(input: CustomFieldValueInput): Promise<UiCustomFieldValue> {
    const payload = await apiClient.post<UnknownRecord>('/int/v1/custom-field-values/', {
      custom_field_uuid: input.custom_field_id,
      subject_uuid: input.entity_id,
      subject_type: input.entity_type || 'order',
      value: input.value,
      value_type: input.value_type || 'text',
    });
    return mapValue((payload ?? {}) as UnknownRecord);
  }

  async update(id: string, input: Partial<CustomFieldValueInput>): Promise<UiCustomFieldValue> {
    const payload = await apiClient.patch<UnknownRecord>(`/int/v1/custom-field-values/${id}`, {
      ...(input.custom_field_id !== undefined ? { custom_field_uuid: input.custom_field_id } : {}),
      ...(input.entity_id !== undefined ? { subject_uuid: input.entity_id } : {}),
      ...(input.entity_type !== undefined ? { subject_type: input.entity_type } : {}),
      ...(input.value !== undefined ? { value: input.value } : {}),
      ...(input.value_type !== undefined ? { value_type: input.value_type } : {}),
    });
    return mapValue((payload ?? {}) as UnknownRecord);
  }

  async remove(id: string): Promise<void> {
    await apiClient.delete(`/int/v1/custom-field-values/${id}`);
  }
}

export const customFieldValuesService = new CustomFieldValuesService();
