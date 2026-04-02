/**
 * Mock vendors — keys match OpenAPI VendorOut (fleetops-vendors).
 */
export type MockVendor = {
  uuid: string | null;
  public_id: string | null;
  company_uuid: string | null;
  place_uuid: string | null;
  name: string | null;
  internal_id: string | null;
  business_id: string | null;
  connected: number | null;
  email: string | null;
  phone: string | null;
  website_url: string | null;
  country: string | null;
  meta: Record<string, unknown> | null;
  type: string | null;
  status: string | null;
  slug: string | null;
  created_at: string | null;
  updated_at: string | null;
  id: number | null;
};

const t0 = Date.now();

export const mockVendors: MockVendor[] = [
  {
    uuid: 'v1111111-1111-1111-1111-111111111111',
    public_id: 'VND-PUB-001',
    company_uuid: null,
    place_uuid: null,
    name: 'Acme Transport Partners',
    internal_id: 'INT-V-001',
    business_id: 'GST-29AAAAA0000A1Z5',
    connected: 1,
    email: 'ops@acmetransport.example.com',
    phone: '+91-80-4000-1000',
    website_url: 'https://acmetransport.example.com',
    country: 'IN',
    meta: { tier: 'gold' },
    type: 'carrier',
    status: 'active',
    slug: 'acme-transport-partners',
    created_at: new Date(t0 - 86400000 * 40).toISOString(),
    updated_at: new Date(t0 - 86400000 * 2).toISOString(),
    id: 1,
  },
  {
    uuid: 'v2222222-2222-2222-2222-222222222222',
    public_id: null,
    company_uuid: null,
    place_uuid: null,
    name: 'City Fuel & Tyres',
    internal_id: null,
    business_id: null,
    connected: 0,
    email: null,
    phone: '+91-9876500099',
    website_url: null,
    country: 'IN',
    meta: null,
    type: 'supplier',
    status: 'inactive',
    slug: null,
    created_at: new Date(t0 - 86400000 * 90).toISOString(),
    updated_at: new Date(t0 - 86400000 * 60).toISOString(),
    id: 2,
  },
  {
    uuid: 'v3333333-3333-3333-3333-333333333333',
    public_id: 'VND-PUB-003',
    company_uuid: null,
    place_uuid: null,
    name: 'Metro Cold Chain',
    internal_id: 'INT-V-003',
    business_id: null,
    connected: 1,
    email: 'contact@metrocc.example.com',
    phone: '+1-555-0199',
    website_url: 'https://metrocc.example.com',
    country: 'US',
    meta: { region: 'west' },
    type: 'carrier',
    status: 'active',
    slug: 'metro-cold-chain',
    created_at: new Date(t0 - 86400000 * 5).toISOString(),
    updated_at: new Date(t0 - 86400000).toISOString(),
    id: 3,
  },
];
