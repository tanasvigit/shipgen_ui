/**
 * Mock contacts — field names match backend OpenAPI / Postman (ContactOut).
 * Do not rename keys (snake_case as in API).
 */
export type MockContact = {
  uuid: string | null;
  public_id: string | null;
  company_uuid: string | null;
  user_uuid: string | null;
  name: string | null;
  title: string | null;
  email: string | null;
  phone: string | null;
  type: string | null;
  slug: string | null;
  meta: Record<string, unknown> | null;
  created_at: string | null;
  updated_at: string | null;
  id: number | null;
};

const t0 = Date.now();

export const mockContacts: MockContact[] = [
  {
    uuid: 'f1a2b3c4-5d6e-7f80-9a0b-1c2d3e4f5060',
    public_id: 'CNT-PUB-001',
    company_uuid: null,
    user_uuid: null,
    name: 'Ravi Kumar',
    title: 'Dispatch coordinator',
    email: 'ravi.kumar@example.com',
    phone: '+91-9876500011',
    type: 'contact',
    slug: 'ravi-kumar',
    meta: { notes: 'Primary billing contact' },
    created_at: new Date(t0 - 86400000 * 5).toISOString(),
    updated_at: new Date(t0 - 86400000).toISOString(),
    id: 1,
  },
  {
    uuid: 'a9b8c7d6-e5f4-3210-fedc-ba9876543210',
    public_id: 'CNT-PUB-002',
    company_uuid: null,
    user_uuid: null,
    name: 'Priya Sharma',
    title: 'Warehouse lead',
    email: 'priya.sharma@example.com',
    phone: '+91-9876500022',
    type: 'contact',
    slug: 'priya-sharma',
    meta: null,
    created_at: new Date(t0 - 86400000 * 12).toISOString(),
    updated_at: new Date(t0 - 86400000 * 3).toISOString(),
    id: 2,
  },
  {
    uuid: '12345678-1234-1234-1234-123456789abc',
    public_id: null,
    company_uuid: null,
    user_uuid: null,
    name: 'External vendor line',
    title: null,
    email: null,
    phone: '+1-555-0100',
    type: 'vendor',
    slug: null,
    meta: { source: 'manual' },
    created_at: new Date(t0 - 86400000 * 30).toISOString(),
    updated_at: new Date(t0 - 86400000 * 30).toISOString(),
    id: 3,
  },
];
