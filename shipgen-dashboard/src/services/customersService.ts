import { contactsService } from './contactsService';
import type { ContactListResult } from './contactsService';
import type { MockContact } from '../mocks/data/contacts';

/**
 * Logistics customers: `Contact` rows with `type === "customer"`, scoped by company via `/fleetops/v1/contacts`.
 */
export type UiCustomer = MockContact;

export interface CustomerInput {
  name: string;
  phone: string;
  email?: string | null;
  /** Stored in `meta.address` */
  address?: string | null;
}

const toPayload = (input: CustomerInput): Record<string, unknown> => ({
  name: input.name.trim(),
  phone: input.phone.trim(),
  email: input.email?.trim() || null,
  type: 'customer',
  meta: input.address?.trim() ? { address: input.address.trim() } : null,
});

class CustomersService {
  async list(params: { page: number; pageSize: number; search?: string }): Promise<ContactListResult> {
    return contactsService.list({
      page: params.page,
      pageSize: params.pageSize,
      kind: 'customer',
      search: params.search,
    });
  }

  async getById(id: string): Promise<UiCustomer> {
    const c = await contactsService.getById(id);
    if ((c.type || '').toLowerCase() !== 'customer') {
      throw new Error('Not a customer record');
    }
    return c;
  }

  async create(input: CustomerInput): Promise<UiCustomer> {
    return contactsService.create(toPayload(input));
  }

  async update(id: string, input: CustomerInput): Promise<UiCustomer> {
    const current = await contactsService.getById(id);
    const prevMeta = { ...((current.meta ?? {}) as Record<string, unknown>) };
    if (input.address?.trim()) prevMeta.address = input.address.trim();
    else delete prevMeta.address;
    return contactsService.update(id, {
      name: input.name.trim(),
      phone: input.phone.trim(),
      email: input.email?.trim() || null,
      meta: Object.keys(prevMeta).length ? prevMeta : null,
    });
  }

  async remove(id: string): Promise<void> {
    await contactsService.remove(id);
  }
}

export const customersService = new CustomersService();
