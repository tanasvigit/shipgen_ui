import { buildMockLoginResponse } from './data/auth';
import { mockInvoices, mockOutstanding, mockPayments } from './data/billing';
import { mockDrivers, mockUsers, mockVehicles } from './data/fleet';
import { mockContacts } from './data/contacts';
import { mockPlaces } from './data/places';
import { mockVendors } from './data/vendors';
import { mockIssues } from './data/issues';
import { mockFuelReports } from './data/fuel_reports';
import { mockOrders } from './data/orders';
import { mockBins, mockInventory, mockRacks, mockWarehouses, mockZones } from './data/warehouse';

const mockTrackingVehicles: Array<{ id: string; plateNumber: string }> = [];

const delay = <T,>(value: T) => new Promise<T>((resolve) => setTimeout(() => resolve(value), 120));

const paginate = (rows: any[], params?: Record<string, any>) => {
  let p = Number(params?.page) || 1;
  let ps = Number(params?.pageSize) || 20;
  if (params != null && params.limit != null) {
    ps = Number(params.limit) || 20;
    const offset = Number(params.offset) || 0;
    p = Math.max(1, Math.floor(offset / ps) + 1);
  }
  const start = (p - 1) * ps;
  return {
    data: rows.slice(start, start + ps),
    pagination: { total: rows.length, page: p, pageSize: ps },
  };
};

/** Strip query string and map versioned API paths → mock resource paths. */
const mockPath = (endpoint: string) => {
  const raw = endpoint.split('?')[0].replace(/\/$/, '');
  if (raw.startsWith('/fleetops/v1')) {
    const suffix = raw.slice('/fleetops/v1'.length);
    return suffix ? `/${suffix.replace(/^\//, '')}` : '/';
  }
  if (raw.startsWith('/int/v1')) {
    const suffix = raw.slice('/int/v1'.length);
    return suffix ? `/${suffix.replace(/^\//, '')}` : '/';
  }
  return raw || '/';
};

const routeOrder = (endpoint: string) => {
  const id = endpoint.split('/')[2];
  return mockOrders.find((o) => o.id === id) ?? null;
};

const routeContact = (endpoint: string) => {
  const id = endpoint.split('/')[2];
  return mockContacts.find((c) => c.uuid === id || String(c.id) === id) ?? null;
};

const routePlace = (endpoint: string) => {
  const id = endpoint.split('/')[2];
  return mockPlaces.find((p) => p.uuid === id || String(p.id) === id) ?? null;
};

const routeVendor = (endpoint: string) => {
  const id = endpoint.split('/')[2];
  return mockVendors.find((v) => v.uuid === id || String(v.id) === id) ?? null;
};

const routeIssue = (endpoint: string) => {
  const id = endpoint.split('/')[2];
  return mockIssues.find((i) => i.uuid === id || String(i.id) === id) ?? null;
};

const routeFuelReport = (endpoint: string) => {
  const id = endpoint.split('/')[2];
  return mockFuelReports.find((r) => r.uuid === id || r.public_id === id || String(r.id) === id) ?? null;
};

export const mockApi = {
  async get(endpoint: string, params?: Record<string, any>) {
    const path = mockPath(endpoint);

    if (path === '/orders') return delay(paginate(mockOrders, params));
    if (path.startsWith('/orders/')) return delay(routeOrder(path) ?? {});

    if (path === '/vehicles') {
      let rows = [...mockVehicles];
      if (params?.status) rows = rows.filter((v) => v.status === params.status);
      if (params?.unassigned === 'true' || params?.unassigned === true) {
        const activeVehicleIds = new Set(
          mockOrders
            .filter((o) => !['completed', 'cancelled', 'failed'].includes(String(o.status ?? '').toLowerCase()))
            .map((o) => String((o as { vehicle_assigned_uuid?: string | null }).vehicle_assigned_uuid ?? ''))
            .filter(Boolean)
        );
        const linkedVehicleIds = new Set(
          mockDrivers
            .map((d: { vehicle_uuid?: string | null }) => String(d.vehicle_uuid ?? ''))
            .filter(Boolean)
        );
        rows = rows.filter((v) => !linkedVehicleIds.has(String(v.id)) && !activeVehicleIds.has(String(v.id)));
      }
      return delay(paginate(rows, params));
    }
    if (path.startsWith('/vehicles/')) {
      const id = path.split('/')[2];
      return delay(mockVehicles.find((v) => v.id === id) ?? {});
    }

    if (path === '/drivers') {
      let rows = [...mockDrivers];
      if (params?.status) rows = rows.filter((d: { status?: string }) => d.status === params.status);
      if (String(params?.online ?? '') === '1') rows = rows.filter((d: { online?: number }) => d.online === 1);
      if (params?.unassigned === 'true' || params?.unassigned === true) {
        const activeDriverIds = new Set(
          mockOrders
            .filter((o) => !['completed', 'cancelled', 'failed'].includes(String(o.status ?? '').toLowerCase()))
            .map((o) => String((o as { driver_assigned_uuid?: string | null }).driver_assigned_uuid ?? ''))
            .filter(Boolean)
        );
        rows = rows.filter(
          (d: { id?: string; vehicle_uuid?: string | null }) =>
            !d.vehicle_uuid && !activeDriverIds.has(String(d.id ?? ''))
        );
      }
      if (params?.vehicle_uuid) {
        rows = rows.filter((d: { vehicle_uuid?: string }) => d.vehicle_uuid === params.vehicle_uuid);
      }
      return delay(paginate(rows, params));
    }
    if (path.startsWith('/drivers/')) {
      const id = path.split('/')[2];
      return delay(mockDrivers.find((d) => d.id === id) ?? {});
    }

    if (path === '/fleet/dashboard') {
      const terminalStatuses = ['completed', 'cancelled', 'failed'];
      const activeOrders = mockOrders.filter(
        (o) => !terminalStatuses.includes(String(o.status ?? '').toLowerCase())
      );
      const driversOnActiveOrders = new Set(
        activeOrders
          .map((o) => String((o as { driver_assigned_uuid?: string | null }).driver_assigned_uuid ?? ''))
          .filter(Boolean)
      ).size;
      const driversUnassigned = mockDrivers.filter((d: { vehicle_uuid?: string }) => !d.vehicle_uuid).length;
      const driverByVehicle: Record<string, (typeof mockDrivers)[0]> = {};
      mockDrivers.forEach((d: (typeof mockDrivers)[0] & { vehicle_uuid?: string }) => {
        if (d.vehicle_uuid && !driverByVehicle[d.vehicle_uuid]) driverByVehicle[d.vehicle_uuid] = d;
      });
      const vehiclesUnassigned = mockVehicles.filter((v) => !driverByVehicle[v.id]).length;
      const kpis = {
        drivers_total: mockDrivers.length,
        drivers_active: mockDrivers.filter((d: { status?: string }) => d.status === 'active').length,
        drivers_online: mockDrivers.filter((d: { online?: number }) => d.online === 1).length,
        drivers_on_active_orders: driversOnActiveOrders,
        drivers_unassigned: driversUnassigned,
        vehicles_total: mockVehicles.length,
        vehicles_active: mockVehicles.filter((v) => v.status === 'active').length,
        vehicles_unassigned: vehiclesUnassigned,
        vehicles_in_use: 0,
      };
      const drivers = mockDrivers.map((d: (typeof mockDrivers)[0] & { vehicle_uuid?: string }) => {
        const veh = mockVehicles.find((v) => v.id === d.vehicle_uuid);
        const lat = d.latitude != null ? Number(d.latitude) : null;
        const lng = d.longitude != null ? Number(d.longitude) : null;
        return {
          driver_uuid: d.id,
          public_id: d.id,
          status: d.status ?? null,
          online: d.online ?? 0,
          vehicle_uuid: d.vehicle_uuid ?? null,
          vehicle_plate: veh?.plate_number ?? null,
          latitude: Number.isFinite(lat) ? lat : null,
          longitude: Number.isFinite(lng) ? lng : null,
        };
      });
      const vehicles = mockVehicles.map((v) => {
        const dr = driverByVehicle[v.id];
        const m = v.meta as Record<string, unknown> | undefined;
        const lat = m?.latitude != null ? Number(m.latitude) : null;
        const lng = m?.longitude != null ? Number(m.longitude) : null;
        return {
          vehicle_uuid: v.id,
          plate_number: v.plate_number ?? null,
          status: v.status ?? null,
          assigned_driver_uuid: dr?.id ?? null,
          assigned_driver_name: (dr as { drivers_license_number?: string } | undefined)?.drivers_license_number ?? null,
          latitude: Number.isFinite(lat) ? lat : null,
          longitude: Number.isFinite(lng) ? lng : null,
        };
      });
      return delay({ kpis, drivers, vehicles });
    }

    if (path === '/contacts') {
      let rows = [...mockContacts];
      const kind = params?.kind ?? params?.type;
      if (kind) rows = rows.filter((c) => c.type === kind);
      const q = params?.search != null ? String(params.search).trim().toLowerCase() : '';
      if (q) {
        rows = rows.filter((c) => {
          const name = (c.name ?? '').toLowerCase();
          const phone = (c.phone ?? '').toLowerCase();
          const email = (c.email ?? '').toLowerCase();
          return name.includes(q) || phone.includes(q) || email.includes(q);
        });
      }
      const limit = Number(params?.limit) || 50;
      const offset = Number(params?.offset) || 0;
      return delay({ contacts: rows.slice(offset, offset + limit) });
    }
    if (path.startsWith('/contacts/')) return delay(routeContact(path) ?? {});

    if (path === '/places') {
      let rows = [...mockPlaces];
      if (params?.type) rows = rows.filter((p) => p.type === params.type);
      return delay(paginate(rows, params));
    }
    if (path.startsWith('/places/')) return delay(routePlace(path) ?? {});

    // Mock-only: OpenAPI list vendors has limit/offset only; type/status filters are for UI convenience.
    if (path === '/vendors') {
      let rows = [...mockVendors];
      if (params?.type) rows = rows.filter((v) => v.type === params.type);
      if (params?.status) rows = rows.filter((v) => v.status === params.status);
      return delay(paginate(rows, params));
    }
    if (path.startsWith('/vendors/')) return delay(routeVendor(path) ?? {});

    // Mock-only: OpenAPI list issues has limit/offset only; status/type filters are for UI convenience.
    if (path === '/issues') {
      let rows = [...mockIssues];
      if (params?.status) rows = rows.filter((i) => i.status === params.status);
      if (params?.type) rows = rows.filter((i) => i.type === params.type);
      return delay(paginate(rows, params));
    }
    if (path.startsWith('/issues/')) return delay(routeIssue(path) ?? {});

    if (path === '/warehouses') return delay(paginate(mockWarehouses, params));
    if (path === '/zones') {
      const rows = params?.warehouseId ? mockZones.filter((z) => z.warehouseId === params.warehouseId) : mockZones;
      return delay(paginate(rows, params));
    }
    if (path.startsWith('/zones/warehouse/')) {
      const warehouseId = path.split('/')[3];
      return delay(mockZones.filter((z) => z.warehouseId === warehouseId));
    }
    if (path === '/racks') return delay(paginate(mockRacks, params));
    if (path === '/bins') return delay(paginate(mockBins, params));
    if (path === '/inventory') {
      const rows = params?.warehouseId ? mockInventory.filter((i) => i.warehouseId === params.warehouseId) : mockInventory;
      return delay(paginate(rows, params));
    }

    if (path === '/invoices') {
      let rows = [...mockInvoices];
      if (params?.status) rows = rows.filter((i) => i.status === params.status);
      return delay(paginate(rows, params));
    }
    if (path.startsWith('/invoices/')) {
      const id = path.split('/')[2];
      return delay(mockInvoices.find((i) => i.id === id) ?? {});
    }
    if (path === '/payments') return delay(paginate(mockPayments, params));
    if (path === '/reports/outstanding') return delay(mockOutstanding);

    if (path === '/tracking/vehicles') return delay({ data: mockTrackingVehicles });

    if (path === '/customers') return delay(paginate([], params));
    if (path === '/users') return delay(paginate(mockUsers, params));
    // Mock-only: OpenAPI fuel-reports list has limit/offset only; status/metric_unit filters are UI convenience.
    if (path === '/fuel-reports') {
      let rows = [...mockFuelReports];
      if (params?.status) rows = rows.filter((r) => r.status === params.status);
      if (params?.metric_unit) rows = rows.filter((r) => r.metric_unit === params.metric_unit);
      return delay(paginate(rows, params));
    }
    if (path.startsWith('/fuel-reports/')) return delay(routeFuelReport(path) ?? {});

    return delay({ data: [], pagination: { total: 0, page: 1, pageSize: 20 } });
  },

  async post(endpoint: string, body?: any) {
    const path = mockPath(endpoint);

    if (path === '/auth/login') return delay(buildMockLoginResponse());
    if (path === '/orders') {
      const created = {
        id: crypto.randomUUID(),
        type: body?.type ?? 'pickup',
        internal_id: body?.internal_id ?? `ORD-${Date.now().toString().slice(-6)}`,
        notes: body?.notes ?? '',
        scheduled_at: body?.scheduled_at ?? new Date().toISOString(),
        status: body?.status ?? 'created',
        meta: {
          customer_name: body?.meta?.customer_name ?? '',
          priority: body?.meta?.priority ?? 'normal',
        },
        options: {
          pod_required: body?.options?.pod_required ?? false,
        },
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      };
      mockOrders.unshift(created);
      return delay(created);
    }
    if (path === '/vehicles') {
      const created = {
        id: crypto.randomUUID(),
        company_uuid: body?.company_uuid ?? null,
        vendor_uuid: body?.vendor_uuid ?? null,
        make: body?.make ?? '',
        model: body?.model ?? '',
        year: body?.year ?? '',
        trim: body?.trim ?? '',
        type: body?.type ?? '',
        plate_number: body?.plate_number ?? '',
        vin: body?.vin ?? '',
        status: body?.status ?? 'active',
        meta: body?.meta ?? {},
        driver_uuid: body?.driver_uuid ?? null,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      };
      mockVehicles.unshift(created);
      return delay(created);
    }
    if (path === '/drivers') {
      const created = {
        id: crypto.randomUUID(),
        company_uuid: body?.company_uuid ?? null,
        user_uuid: body?.user_uuid ?? null,
        drivers_license_number: body?.drivers_license_number ?? '',
        status: body?.status ?? 'active',
        online: 0,
        latitude: '0',
        longitude: '0',
        heading: '0',
        speed: '0',
        altitude: '0',
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      };
      mockDrivers.unshift(created);
      return delay(created);
    }
    if (path === '/contacts') {
      const nextId =
        mockContacts.length === 0
          ? 1
          : Math.max(...mockContacts.map((c) => Number(c.id) || 0)) + 1;
      const created = {
        uuid: crypto.randomUUID(),
        public_id: null,
        company_uuid: null,
        user_uuid: null,
        name: body?.name ?? '',
        title: body?.title ?? null,
        email: body?.email ?? null,
        phone: body?.phone ?? null,
        type: body?.type ?? 'contact',
        slug: null,
        meta: body?.meta ?? null,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
        id: nextId,
      };
      mockContacts.unshift(created);
      return delay(created);
    }
    if (path === '/places') {
      const nextId =
        mockPlaces.length === 0
          ? 1
          : Math.max(...mockPlaces.map((p) => Number(p.id) || 0)) + 1;
      const created = {
        uuid: crypto.randomUUID(),
        public_id: null,
        company_uuid: null,
        owner_uuid: null,
        owner_type: null,
        name: body?.name ?? null,
        street1: body?.street1 ?? null,
        street2: body?.street2 ?? null,
        city: body?.city ?? null,
        province: body?.province ?? null,
        postal_code: body?.postal_code ?? null,
        neighborhood: null,
        district: null,
        building: null,
        security_access_code: null,
        country: body?.country ?? null,
        latitude: body?.latitude ?? null,
        longitude: body?.longitude ?? null,
        meta: body?.meta ?? null,
        phone: body?.phone ?? null,
        remarks: null,
        type: body?.type ?? null,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
        id: nextId,
      };
      mockPlaces.unshift(created);
      return delay(created);
    }
    if (path === '/vendors') {
      const nextId =
        mockVendors.length === 0
          ? 1
          : Math.max(...mockVendors.map((v) => Number(v.id) || 0)) + 1;
      const created = {
        uuid: crypto.randomUUID(),
        public_id: null,
        company_uuid: null,
        place_uuid: null,
        name: body?.name ?? '',
        internal_id: null,
        business_id: null,
        connected: null,
        email: body?.email ?? null,
        phone: body?.phone ?? null,
        website_url: null,
        country: null,
        meta: body?.meta ?? null,
        type: body?.type ?? null,
        status: null,
        slug: null,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
        id: nextId,
      };
      mockVendors.unshift(created);
      return delay(created);
    }
    if (path === '/issues') {
      const nextId =
        mockIssues.length === 0
          ? 1
          : Math.max(...mockIssues.map((i) => Number(i.id) || 0)) + 1;
      const created = {
        uuid: crypto.randomUUID(),
        public_id: null,
        issue_id: `ISS-${String(nextId).padStart(3, '0')}`,
        company_uuid: null,
        driver_uuid: body?.driver ?? null,
        vehicle_uuid: null,
        assigned_to_uuid: null,
        reported_by_uuid: null,
        location: body?.location ?? null,
        latitude: null,
        longitude: null,
        category: body?.category ?? null,
        type: body?.type ?? null,
        report: body?.report ?? null,
        title: body?.title ?? null,
        tags: body?.tags ?? null,
        priority: body?.priority ?? null,
        meta: body?.meta ?? null,
        resolved_at: null,
        status: body?.status ?? null,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
        id: nextId,
        driver_name: null,
        vehicle_name: null,
        assignee_name: null,
        reporter_name: null,
      };
      mockIssues.unshift(created);
      return delay(created);
    }
    if (path === '/payments') {
      const payment = {
        id: `PAY-${Date.now().toString().slice(-6)}`,
        invoiceId: body?.invoiceId ?? 'INV-01',
        amount: Number(body?.amount ?? 0),
        paymentMode: body?.paymentMode ?? 'CASH',
        referenceNumber: body?.referenceNumber ?? '',
        paidAt: new Date().toISOString(),
        createdAt: new Date().toISOString(),
      };
      mockPayments.unshift(payment);
      return delay(payment);
    }
    if (path === '/fuel-reports') {
      const nextId =
        mockFuelReports.length === 0
          ? 1
          : Math.max(...mockFuelReports.map((r) => Number(r.id) || 0)) + 1;
      const created = {
        uuid: crypto.randomUUID(),
        public_id: `fuel_report_${crypto.randomUUID().replace(/-/g, '').slice(0, 12)}`,
        company_uuid: null,
        driver_uuid: body?.driver ?? null,
        vehicle_uuid: null,
        reported_by_uuid: null,
        odometer: body?.odometer ?? null,
        location: body?.location ?? null,
        latitude: body?.location?.latitude ?? body?.location?.lat ?? null,
        longitude: body?.location?.longitude ?? body?.location?.lng ?? null,
        amount: body?.amount ?? null,
        currency: body?.currency ?? null,
        volume: body?.volume ?? null,
        metric_unit: body?.metric_unit ?? null,
        report: body?.report ?? null,
        meta: body?.meta ?? null,
        status: body?.status ?? null,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
        id: nextId,
        vehicle_name: null,
        driver_name: null,
        reporter_name: null,
      };
      mockFuelReports.unshift(created);
      return delay(created);
    }

    return delay({ success: true });
  },

  async patch(endpoint: string, body?: any) {
    const path = mockPath(endpoint);

    if (path.startsWith('/orders/')) {
      const id = path.split('/')[2];
      const order = mockOrders.find((o) => o.id === id);
      if (!order) return delay({});
      Object.assign(order, body);
      order.updated_at = new Date().toISOString();
      return delay(order);
    }
    if (path.startsWith('/drivers/')) {
      const id = path.split('/')[2];
      const driver = mockDrivers.find((d) => d.id === id);
      if (!driver) return delay({});
      Object.assign(driver, body);
      driver.updated_at = new Date().toISOString();
      return delay(driver);
    }
    if (path.startsWith('/vehicles/')) {
      const id = path.split('/')[2];
      const vehicle = mockVehicles.find((v) => v.id === id);
      if (!vehicle) return delay({});
      Object.assign(vehicle, body);
      vehicle.updated_at = new Date().toISOString();
      return delay(vehicle);
    }
    if (path.startsWith('/contacts/')) {
      const id = path.split('/')[2];
      const contact = mockContacts.find((c) => c.uuid === id || String(c.id) === id);
      if (!contact) return delay({});
      if (body.name !== undefined) contact.name = body.name;
      if (body.email !== undefined) contact.email = body.email;
      if (body.phone !== undefined) contact.phone = body.phone;
      if (body.type !== undefined) contact.type = body.type;
      if (body.title !== undefined) contact.title = body.title;
      if (body.meta !== undefined) contact.meta = body.meta;
      contact.updated_at = new Date().toISOString();
      return delay(contact);
    }
    if (path.startsWith('/places/')) {
      const id = path.split('/')[2];
      const place = mockPlaces.find((p) => p.uuid === id || String(p.id) === id);
      if (!place) return delay({});
      const u = body as Record<string, unknown>;
      if (u.name !== undefined) place.name = u.name as string | null;
      if (u.street1 !== undefined) place.street1 = u.street1 as string | null;
      if (u.street2 !== undefined) place.street2 = u.street2 as string | null;
      if (u.city !== undefined) place.city = u.city as string | null;
      if (u.province !== undefined) place.province = u.province as string | null;
      if (u.postal_code !== undefined) place.postal_code = u.postal_code as string | null;
      if (u.country !== undefined) place.country = u.country as string | null;
      if (u.latitude !== undefined) place.latitude = u.latitude as string | null;
      if (u.longitude !== undefined) place.longitude = u.longitude as string | null;
      if (u.phone !== undefined) place.phone = u.phone as string | null;
      if (u.type !== undefined) place.type = u.type as string | null;
      if (u.meta !== undefined) place.meta = u.meta as Record<string, unknown> | null;
      place.updated_at = new Date().toISOString();
      return delay(place);
    }
    if (path.startsWith('/vendors/')) {
      const id = path.split('/')[2];
      const vendor = mockVendors.find((v) => v.uuid === id || String(v.id) === id);
      if (!vendor) return delay({});
      const u = body as Record<string, unknown>;
      if (u.name !== undefined) vendor.name = u.name as string | null;
      if (u.type !== undefined) vendor.type = u.type as string | null;
      if (u.email !== undefined) vendor.email = u.email as string | null;
      if (u.phone !== undefined) vendor.phone = u.phone as string | null;
      if (u.meta !== undefined) vendor.meta = u.meta as Record<string, unknown> | null;
      vendor.updated_at = new Date().toISOString();
      return delay(vendor);
    }

    return delay({ success: true });
  },

  async put(endpoint: string, body?: any) {
    const path = mockPath(endpoint);
    if (path.startsWith('/fuel-reports/')) {
      const id = path.split('/')[2];
      const report = mockFuelReports.find((r) => r.uuid === id || r.public_id === id || String(r.id) === id);
      if (!report) return delay({});
      report.odometer = body?.odometer ?? null;
      report.volume = body?.volume ?? null;
      report.metric_unit = body?.metric_unit ?? null;
      report.amount = body?.amount ?? null;
      report.currency = body?.currency ?? null;
      report.status = body?.status ?? null;
      report.report = body?.report ?? null;
      report.meta = body?.meta ?? null;
      report.updated_at = new Date().toISOString();
      return delay(report);
    }
    if (path.startsWith('/issues/')) {
      const id = path.split('/')[2];
      const issue = mockIssues.find((i) => i.uuid === id || String(i.id) === id);
      if (!issue) return delay({});
      issue.category = body?.category ?? null;
      issue.type = body?.type ?? null;
      issue.report = body?.report ?? null;
      issue.priority = body?.priority ?? null;
      issue.status = body?.status ?? null;
      issue.title = body?.title ?? null;
      issue.tags = body?.tags ?? null;
      issue.meta = body?.meta ?? null;
      issue.resolved_at = body?.resolved_at ?? null;
      issue.updated_at = new Date().toISOString();
      return delay(issue);
    }
    return delay({ success: true });
  },

  async delete(endpoint?: string) {
    const path = mockPath(endpoint ?? '');
    if (path.startsWith('/drivers/')) {
      const id = path.split('/')[2];
      const index = mockDrivers.findIndex((d) => d.id === id);
      if (index > -1) {
        mockDrivers.splice(index, 1);
      }
      return delay({ success: true });
    }
    if (path.startsWith('/vehicles/')) {
      const id = path.split('/')[2];
      const index = mockVehicles.findIndex((v) => v.id === id);
      if (index > -1) {
        mockVehicles.splice(index, 1);
      }
      return delay({ success: true });
    }
    if (path.startsWith('/contacts/')) {
      const id = path.split('/')[2];
      const index = mockContacts.findIndex((c) => c.uuid === id || String(c.id) === id);
      if (index > -1) {
        mockContacts.splice(index, 1);
      }
      return delay({ success: true });
    }
    if (path.startsWith('/places/')) {
      const id = path.split('/')[2];
      const index = mockPlaces.findIndex((p) => p.uuid === id || String(p.id) === id);
      if (index > -1) {
        mockPlaces.splice(index, 1);
      }
      return delay({ success: true });
    }
    if (path.startsWith('/vendors/')) {
      const id = path.split('/')[2];
      const index = mockVendors.findIndex((v) => v.uuid === id || String(v.id) === id);
      if (index > -1) {
        mockVendors.splice(index, 1);
      }
      return delay({ success: true });
    }
    if (path.startsWith('/issues/')) {
      const id = path.split('/')[2];
      const index = mockIssues.findIndex((i) => i.uuid === id || String(i.id) === id);
      if (index > -1) {
        mockIssues.splice(index, 1);
      }
      return delay({ success: true });
    }
    if (path.startsWith('/fuel-reports/')) {
      const id = path.split('/')[2];
      const index = mockFuelReports.findIndex((r) => r.uuid === id || r.public_id === id || String(r.id) === id);
      if (index > -1) {
        mockFuelReports.splice(index, 1);
      }
      return delay({ success: true });
    }
    return delay({ success: true });
  },
};
