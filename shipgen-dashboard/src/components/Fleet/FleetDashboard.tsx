import React, { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { LayoutDashboard, Loader2 } from 'lucide-react';
import PageContainer from '../ui/PageContainer';
import { ResponsiveTable } from '../ui/ResponsiveTable';
import {
  fleetDashboardService,
  formatLatLng,
  type FleetDashboardPayload,
  type FleetDashboardDriverRow,
  type FleetDashboardVehicleRow,
} from '../../services/fleetDashboardService';

function KpiCard({
  label,
  value,
  onClick,
}: {
  label: string;
  value: number;
  onClick: () => void;
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      className="w-full cursor-pointer rounded-xl border border-gray-200 bg-white p-4 text-left shadow-sm transition hover:-translate-y-0.5 hover:border-blue-200 hover:shadow"
    >
      <p className="text-xs font-medium uppercase tracking-wide text-gray-500">{label}</p>
      <p className="mt-1 text-2xl font-semibold text-gray-900">{value}</p>
    </button>
  );
}

const FleetDashboard: React.FC = () => {
  const navigate = useNavigate();
  const [data, setData] = useState<FleetDashboardPayload | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    void (async () => {
      try {
        setLoading(true);
        setError(null);
        const res = await fleetDashboardService.get();
        if (!cancelled) setData(res);
      } catch (e: unknown) {
        if (!cancelled) setError(e instanceof Error ? e.message : 'Failed to load fleet dashboard');
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, []);

  if (loading) {
    return (
      <PageContainer>
        <div className="flex min-h-[240px] flex-col items-center justify-center gap-3 text-gray-600">
          <Loader2 className="h-10 w-10 animate-spin text-blue-600" />
          <p className="text-sm">Loading fleet dashboard…</p>
        </div>
      </PageContainer>
    );
  }

  if (error) {
    return (
      <PageContainer>
        <div className="rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">{error}</div>
      </PageContainer>
    );
  }

  if (!data) {
    return (
      <PageContainer>
        <p className="text-center text-gray-600">No data.</p>
      </PageContainer>
    );
  }

  const { kpis, drivers, vehicles } = data;
  const isEmpty = drivers.length === 0 && vehicles.length === 0;

  return (
    <PageContainer>
      <div className="mb-6 flex items-start gap-3">
        <div className="rounded-lg bg-blue-50 p-2 text-blue-600">
          <LayoutDashboard size={24} />
        </div>
        <div>
          <h1 className="text-xl font-bold text-gray-900 sm:text-2xl">Fleet Dashboard</h1>
          <p className="mt-1 text-sm text-gray-600">Drivers, vehicles, and assignments for your company.</p>
        </div>
      </div>

      <div className="mb-8 grid grid-cols-2 gap-3 sm:grid-cols-4 lg:grid-cols-4">
        <KpiCard label="Total drivers" value={kpis.drivers_total} onClick={() => navigate('/fleet/drivers')} />
        <KpiCard
          label="Active drivers"
          value={kpis.drivers_active}
          onClick={() => navigate('/fleet/drivers?status=active')}
        />
        <KpiCard label="Online drivers" value={kpis.drivers_online} onClick={() => navigate('/fleet/drivers?online=1')} />
        <KpiCard
          label="Unassigned drivers"
          value={kpis.drivers_unassigned}
          onClick={() => navigate('/fleet/drivers?unassigned=true')}
        />
        <KpiCard label="Total vehicles" value={kpis.vehicles_total} onClick={() => navigate('/fleet/vehicles')} />
        <KpiCard
          label="Active vehicles"
          value={kpis.vehicles_active}
          onClick={() => navigate('/fleet/vehicles?status=active')}
        />
        <KpiCard
          label="Vehicles in use"
          value={kpis.vehicles_in_use}
          onClick={() => navigate('/logistics/orders?vehicle_assigned=true')}
        />
        <KpiCard
          label="Unassigned vehicles"
          value={kpis.vehicles_unassigned}
          onClick={() => navigate('/fleet/vehicles?unassigned=true')}
        />
      </div>

      {isEmpty ? (
        <div className="rounded-xl border border-dashed border-gray-200 bg-gray-50 py-16 text-center text-sm text-gray-600">
          No drivers or vehicles yet. Add them from the Drivers and Vehicles lists.
        </div>
      ) : null}

      <section className="mb-10 space-y-3">
        <h2 className="text-lg font-semibold text-gray-900">Drivers</h2>
        <div className="rounded-xl border border-gray-200 bg-white p-2 md:p-0">
          <ResponsiveTable<FleetDashboardDriverRow>
            data={drivers}
            keyExtractor={(d) => d.driver_uuid}
            emptyMessage="No drivers"
            columns={[
              {
                key: 'id',
                header: 'Driver ID',
                render: (d) => (
                  <Link
                    to={`/fleet/drivers/${encodeURIComponent(d.driver_uuid)}`}
                    className="text-sm font-medium text-blue-600 hover:underline"
                  >
                    {d.public_id || d.driver_uuid}
                  </Link>
                ),
              },
              {
                key: 'status',
                header: 'Status',
                render: (d) => <span className="text-sm text-gray-700">{d.status ?? '—'}</span>,
              },
              {
                key: 'online',
                header: 'Online',
                render: (d) => (
                  <span className="text-sm text-gray-700">{d.online === 1 ? 'Yes' : 'No'}</span>
                ),
              },
              {
                key: 'vehicle',
                header: 'Assigned vehicle',
                render: (d) => (
                  <span className="text-sm text-gray-700">
                    {d.vehicle_plate && d.vehicle_uuid ? (
                      <Link
                        to={`/fleet/vehicles/${encodeURIComponent(d.vehicle_uuid)}`}
                        className="text-blue-600 hover:underline"
                      >
                        {d.vehicle_plate}
                      </Link>
                    ) : d.vehicle_plate ? (
                      d.vehicle_plate
                    ) : (
                      '—'
                    )}
                  </span>
                ),
              },
              {
                key: 'loc',
                header: 'Location',
                render: (d) => (
                  <span className="font-mono text-xs text-gray-700">{formatLatLng(d.latitude, d.longitude)}</span>
                ),
              },
            ]}
          />
        </div>
      </section>

      <section className="space-y-3">
        <h2 className="text-lg font-semibold text-gray-900">Vehicles</h2>
        <div className="rounded-xl border border-gray-200 bg-white p-2 md:p-0">
          <ResponsiveTable<FleetDashboardVehicleRow>
            data={vehicles}
            keyExtractor={(v) => v.vehicle_uuid}
            emptyMessage="No vehicles"
            columns={[
              {
                key: 'plate',
                header: 'Plate',
                render: (v) => (
                  <Link
                    to={`/fleet/vehicles/${encodeURIComponent(v.vehicle_uuid)}`}
                    className="text-sm font-medium text-blue-600 hover:underline"
                  >
                    {v.plate_number || v.vehicle_uuid}
                  </Link>
                ),
              },
              {
                key: 'status',
                header: 'Status',
                render: (v) => <span className="text-sm text-gray-700">{v.status ?? '—'}</span>,
              },
              {
                key: 'driver',
                header: 'Assigned driver',
                render: (v) =>
                  v.assigned_driver_uuid ? (
                    <Link
                      to={`/fleet/drivers/${encodeURIComponent(v.assigned_driver_uuid)}`}
                      className="text-sm text-blue-600 hover:underline"
                    >
                      {v.assigned_driver_name || v.assigned_driver_uuid}
                    </Link>
                  ) : (
                    <span className="text-sm text-gray-500">—</span>
                  ),
              },
              {
                key: 'loc',
                header: 'Last location',
                render: (v) => (
                  <span className="font-mono text-xs text-gray-700">{formatLatLng(v.latitude, v.longitude)}</span>
                ),
              },
            ]}
          />
        </div>
      </section>
    </PageContainer>
  );
};

export default FleetDashboard;
