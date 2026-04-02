import { apiClient } from './apiClient';

type UnknownRecord = Record<string, unknown>;

export interface UiTransaction {
  id: string;
  amount: number;
  currency: string;
  status: string;
  type: string;
  reference: string;
  created_at: string;
  raw: UnknownRecord;
}

const toNumber = (value: unknown): number => {
  if (typeof value === 'number' && Number.isFinite(value)) return value;
  if (typeof value === 'string') {
    const parsed = Number(value);
    return Number.isFinite(parsed) ? parsed : 0;
  }
  return 0;
};

const mapTransaction = (row: UnknownRecord): UiTransaction => ({
  id: String(row.uuid ?? row.public_id ?? row.id ?? ''),
  amount: toNumber(row.amount),
  currency: String(row.currency ?? 'USD'),
  status: String(row.status ?? ''),
  type: String(row.type ?? ''),
  reference: String(
    row.gateway_transaction_id ??
    row.owner_uuid ??
    row.customer_uuid ??
    row.internal_id ??
    '',
  ),
  created_at: String(row.created_at ?? ''),
  raw: row,
});

class TransactionsService {
  async list(params: { limit?: number; offset?: number } = {}): Promise<UiTransaction[]> {
    const payload = await apiClient.get<UnknownRecord[]>('/int/v1/transactions/', {
      limit: params.limit ?? 100,
      offset: params.offset ?? 0,
    });
    return Array.isArray(payload) ? payload.map((x) => mapTransaction((x ?? {}) as UnknownRecord)) : [];
  }

  async getById(id: string): Promise<UiTransaction> {
    const payload = await apiClient.get<UnknownRecord>(`/int/v1/transactions/${id}`);
    return mapTransaction((payload ?? {}) as UnknownRecord);
  }
}

export const transactionsService = new TransactionsService();
