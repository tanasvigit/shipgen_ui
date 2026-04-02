/**
 * Mock places — keys match OpenAPI PlaceOut (fleetops-places).
 */
export type MockPlace = {
  uuid: string | null;
  public_id: string | null;
  company_uuid: string | null;
  owner_uuid: string | null;
  owner_type: string | null;
  name: string | null;
  street1: string | null;
  street2: string | null;
  city: string | null;
  province: string | null;
  postal_code: string | null;
  neighborhood: string | null;
  district: string | null;
  building: string | null;
  security_access_code: string | null;
  country: string | null;
  latitude: string | null;
  longitude: string | null;
  meta: Record<string, unknown> | null;
  phone: string | null;
  remarks: string | null;
  type: string | null;
  created_at: string | null;
  updated_at: string | null;
  id: number | null;
};

const t0 = Date.now();

export const mockPlaces: MockPlace[] = [
  {
    uuid: 'p1111111-1111-1111-1111-111111111111',
    public_id: 'PLC-001',
    company_uuid: null,
    owner_uuid: null,
    owner_type: null,
    name: 'Main warehouse gate',
    street1: '100 Industrial Road',
    street2: 'Block A',
    city: 'Bengaluru',
    province: 'KA',
    postal_code: '560001',
    neighborhood: 'Peenya',
    district: 'Bengaluru Urban',
    building: 'Gate 2',
    security_access_code: '1234#',
    country: 'IN',
    latitude: '13.028',
    longitude: '77.505',
    meta: { dock: 'A1' },
    phone: '+91-80-0000-0001',
    remarks: 'Use rear entrance after 6pm',
    type: 'warehouse',
    created_at: new Date(t0 - 86400000 * 14).toISOString(),
    updated_at: new Date(t0 - 86400000 * 2).toISOString(),
    id: 1,
  },
  {
    uuid: 'p2222222-2222-2222-2222-222222222222',
    public_id: null,
    company_uuid: null,
    owner_uuid: null,
    owner_type: null,
    name: 'Customer drop-off',
    street1: '22 MG Road',
    street2: null,
    city: 'Bengaluru',
    province: 'KA',
    postal_code: '560025',
    neighborhood: null,
    district: null,
    building: null,
    security_access_code: null,
    country: 'IN',
    latitude: '12.975',
    longitude: '77.605',
    meta: null,
    phone: null,
    remarks: null,
    type: 'customer',
    created_at: new Date(t0 - 86400000 * 7).toISOString(),
    updated_at: new Date(t0 - 86400000 * 7).toISOString(),
    id: 2,
  },
  {
    uuid: 'p3333333-3333-3333-3333-333333333333',
    public_id: 'PLC-003',
    company_uuid: null,
    owner_uuid: null,
    owner_type: null,
    name: 'Fuel stop (highway)',
    street1: 'NH44 Service Lane',
    street2: null,
    city: 'Hosur',
    province: 'TN',
    postal_code: '635109',
    neighborhood: null,
    district: null,
    building: null,
    security_access_code: null,
    country: 'IN',
    latitude: '12.715',
    longitude: '77.825',
    meta: { fuel_brand: 'IOCL' },
    phone: '+91-4344-000000',
    remarks: null,
    type: 'vendor',
    created_at: new Date(t0 - 86400000 * 60).toISOString(),
    updated_at: new Date(t0 - 86400000 * 10).toISOString(),
    id: 3,
  },
];
