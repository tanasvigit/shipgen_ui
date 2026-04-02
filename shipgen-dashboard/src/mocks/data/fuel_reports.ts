/**
 * Mock fuel reports — keys match OpenAPI FuelReportOut (fleetops-fuel-reports).
 */
export type MockFuelReport = {
  uuid: string | null;
  public_id: string | null;
  company_uuid: string | null;
  driver_uuid: string | null;
  vehicle_uuid: string | null;
  reported_by_uuid: string | null;
  odometer: string | null;
  location: Record<string, unknown> | null;
  latitude: string | null;
  longitude: string | null;
  amount: string | null;
  currency: string | null;
  volume: string | null;
  metric_unit: string | null;
  report: string | null;
  meta: Record<string, unknown> | null;
  status: string | null;
  created_at: string | null;
  updated_at: string | null;
  id: number | null;
  vehicle_name: string | null;
  driver_name: string | null;
  reporter_name: string | null;
};

const t0 = Date.now();

export const mockFuelReports: MockFuelReport[] = [
  {
    uuid: 'fr111111-1111-1111-1111-111111111111',
    public_id: 'fuel_report_001',
    company_uuid: null,
    driver_uuid: 'dbe562ea-0f2b-497c-9d9e-a9d9a5136d6f',
    vehicle_uuid: 'a82290a0-90b6-4fa8-8ac1-d383a6020c66',
    reported_by_uuid: null,
    odometer: '24567',
    location: { latitude: '12.9716', longitude: '77.5946', station: 'Shell MG Road' },
    latitude: '12.9716',
    longitude: '77.5946',
    amount: '4200',
    currency: 'INR',
    volume: '42.5',
    metric_unit: 'litre',
    report: 'Regular top-up before long route.',
    meta: { receipt_no: 'R-1001' },
    status: 'submitted',
    created_at: new Date(t0 - 86400000 * 3).toISOString(),
    updated_at: new Date(t0 - 86400000 * 2).toISOString(),
    id: 1,
    vehicle_name: 'Toyota Hilux',
    driver_name: 'Driver A',
    reporter_name: 'Ops Desk',
  },
  {
    uuid: 'fr222222-2222-2222-2222-222222222222',
    public_id: 'fuel_report_002',
    company_uuid: null,
    driver_uuid: '9f99564b-df48-4512-9ec8-a5c14ef0d4c5',
    vehicle_uuid: '43db2c1f-c6c6-4e6d-a533-7ba2a5dd95ef',
    reported_by_uuid: null,
    odometer: '10980',
    location: null,
    latitude: null,
    longitude: null,
    amount: '2100',
    currency: 'INR',
    volume: '22',
    metric_unit: 'litre',
    report: 'Short-haul delivery refill.',
    meta: null,
    status: 'approved',
    created_at: new Date(t0 - 86400000 * 6).toISOString(),
    updated_at: new Date(t0 - 86400000 * 5).toISOString(),
    id: 2,
    vehicle_name: 'Tata Ace Gold',
    driver_name: 'Driver B',
    reporter_name: 'Fleet Supervisor',
  },
];
