/**
 * Mock issues — keys match OpenAPI IssueOut (fleetops-issues).
 */
export type MockIssue = {
  uuid: string | null;
  public_id: string | null;
  issue_id: string | null;
  company_uuid: string | null;
  driver_uuid: string | null;
  vehicle_uuid: string | null;
  assigned_to_uuid: string | null;
  reported_by_uuid: string | null;
  location: Record<string, unknown> | null;
  latitude: string | null;
  longitude: string | null;
  category: string | null;
  type: string | null;
  report: string | null;
  title: string | null;
  tags: string[] | null;
  priority: string | null;
  meta: Record<string, unknown> | null;
  resolved_at: string | null;
  status: string | null;
  created_at: string | null;
  updated_at: string | null;
  id: number | null;
  driver_name: string | null;
  vehicle_name: string | null;
  assignee_name: string | null;
  reporter_name: string | null;
};

const t0 = Date.now();

export const mockIssues: MockIssue[] = [
  {
    uuid: 'i1111111-1111-1111-1111-111111111111',
    public_id: 'ISS-PUB-001',
    issue_id: 'ISS-001',
    company_uuid: null,
    driver_uuid: 'dbe562ea-0f2b-497c-9d9e-a9d9a5136d6f',
    vehicle_uuid: 'a82290a0-90b6-4fa8-8ac1-d383a6020c66',
    assigned_to_uuid: null,
    reported_by_uuid: null,
    location: { street1: 'Ring Road', city: 'Bengaluru' },
    latitude: '12.9716',
    longitude: '77.5946',
    category: 'vehicle',
    type: 'breakdown',
    report: 'Engine warning light with power loss.',
    title: 'Vehicle breakdown near depot',
    tags: ['urgent', 'vehicle'],
    priority: 'high',
    meta: { order_uuid: 'c4d86bb6-6a86-480b-bd81-7a7d9e73f106' },
    resolved_at: null,
    status: 'open',
    created_at: new Date(t0 - 86400000 * 2).toISOString(),
    updated_at: new Date(t0 - 86400000).toISOString(),
    id: 1,
    driver_name: 'Driver A',
    vehicle_name: 'Toyota Hilux',
    assignee_name: null,
    reporter_name: 'Ops Desk',
  },
  {
    uuid: 'i2222222-2222-2222-2222-222222222222',
    public_id: null,
    issue_id: 'ISS-002',
    company_uuid: null,
    driver_uuid: null,
    vehicle_uuid: null,
    assigned_to_uuid: null,
    reported_by_uuid: null,
    location: null,
    latitude: null,
    longitude: null,
    category: 'safety',
    type: 'incident',
    report: 'Minor loading bay incident, no injuries.',
    title: 'Loading bay incident',
    tags: ['safety'],
    priority: 'medium',
    meta: null,
    resolved_at: new Date(t0 - 86400000).toISOString(),
    status: 'resolved',
    created_at: new Date(t0 - 86400000 * 10).toISOString(),
    updated_at: new Date(t0 - 86400000).toISOString(),
    id: 2,
    driver_name: null,
    vehicle_name: null,
    assignee_name: 'Fleet Supervisor',
    reporter_name: 'Warehouse Lead',
  },
  {
    uuid: 'i3333333-3333-3333-3333-333333333333',
    public_id: 'ISS-PUB-003',
    issue_id: 'ISS-003',
    company_uuid: null,
    driver_uuid: '9f99564b-df48-4512-9ec8-a5c14ef0d4c5',
    vehicle_uuid: '43db2c1f-c6c6-4e6d-a533-7ba2a5dd95ef',
    assigned_to_uuid: null,
    reported_by_uuid: null,
    location: { city: 'Delhi' },
    latitude: '28.6139',
    longitude: '77.2090',
    category: 'compliance',
    type: 'documentation',
    report: 'POD document missing for completed run.',
    title: 'Missing POD document',
    tags: ['pod', 'compliance'],
    priority: 'low',
    meta: null,
    resolved_at: null,
    status: 'in_progress',
    created_at: new Date(t0 - 86400000 * 3).toISOString(),
    updated_at: new Date(t0 - 86400000 * 2).toISOString(),
    id: 3,
    driver_name: 'Driver B',
    vehicle_name: 'Tata Ace Gold',
    assignee_name: 'Compliance Team',
    reporter_name: 'Billing Team',
  },
];
