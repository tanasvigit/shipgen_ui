export type MockOrder = {
  id: string;
  type: string;
  internal_id: string;
  notes: string;
  scheduled_at: string;
  status: string;
  meta: {
    customer_name: string;
    priority: string;
  };
  options: {
    pod_required: boolean;
  };
  created_at: string;
  updated_at: string;
};

const now = Date.now();

export const mockOrders: MockOrder[] = [
  {
    id: 'c4d86bb6-6a86-480b-bd81-7a7d9e73f106',
    type: 'pickup',
    internal_id: 'ORD-001',
    notes: 'Test order for API',
    scheduled_at: new Date(now + 86400000).toISOString(),
    status: 'created',
    meta: {
      customer_name: 'Acme Corp',
      priority: 'normal',
    },
    options: {
      pod_required: true,
    },
    created_at: new Date(now - 86400000).toISOString(),
    updated_at: new Date(now - 86400000).toISOString(),
  },
  {
    id: '9b4d101e-3f54-47c8-9d37-f4a15ce7b6f4',
    type: 'pickup',
    internal_id: 'ORD-002',
    notes: 'High priority dispatch',
    scheduled_at: new Date(now + 172800000).toISOString(),
    status: 'scheduled',
    meta: {
      customer_name: 'Nova Electronics',
      priority: 'high',
    },
    options: {
      pod_required: true,
    },
    created_at: new Date(now - 43200000).toISOString(),
    updated_at: new Date(now - 21600000).toISOString(),
  },
  {
    id: '7489d172-bf2d-4f18-8c01-5be09f8ddf1f',
    type: 'delivery',
    internal_id: 'ORD-003',
    notes: 'Legacy completed order',
    scheduled_at: new Date(now - 259200000).toISOString(),
    status: 'completed',
    meta: {
      customer_name: 'Metro Distributors',
      priority: 'normal',
    },
    options: {
      pod_required: false,
    },
    created_at: new Date(now - 345600000).toISOString(),
    updated_at: new Date(now - 172800000).toISOString(),
  },
];
