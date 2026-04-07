import React, { useEffect, useState } from 'react';
import { AlertCircle, Calendar, DollarSign, Gauge, Package, Truck, Wrench } from 'lucide-react';
import { Link } from 'react-router-dom';
import { KPISkeleton, Skeleton } from '../ui/LoadingSkeleton';
import { EmptyState } from '../ui/EmptyState';
import { dashboardOverviewService, type DashboardOverviewData } from '../../services/dashboardOverviewService';
import { Bar, BarChart, CartesianGrid, Cell, Legend, Line, LineChart, Pie, PieChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';
import { applyRangeToOverview, type DashboardRange } from '../../utils/dashboardHelpers';
import { orderCustomerLabel, type UiOrder } from '../../services/ordersService';

const DashboardOverview: React.FC = () => {
  const [overview, setOverview] = useState<DashboardOverviewData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [range, setRange] = useState<DashboardRange>('last30');

  const loadDashboardData = async (): Promise<void> => {
    try {
      setError(null);
      const payload = await dashboardOverviewService.fetchOverview();
      setOverview(payload);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDashboardData();
    const interval = setInterval(loadDashboardData, 60000);
    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <div className="space-y-6 animate-fade-in">
        <div className="flex items-center justify-between">
          <div>
            <Skeleton variant="text" width={200} height={32} className="mb-2" />
            <Skeleton variant="text" width={300} height={16} />
          </div>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {Array.from({ length: 4 }).map((_, i) => (
            <KPISkeleton key={i} />
          ))}
        </div>
      </div>
    );
  }

  const filtered = overview ? applyRangeToOverview(overview, range) : null;

  const kpis = filtered
    ? [
        { label: 'Total Orders', value: String(filtered.kpis.totalOrders), icon: Package, link: '/logistics/orders' },
        { label: 'Active Orders', value: String(filtered.kpis.activeOrders), icon: Gauge, link: '/logistics/orders' },
        {
          label: 'Vehicles (Avail / Active)',
          value: `${filtered.kpis.vehiclesAvailable} / ${filtered.kpis.vehiclesActive}`,
          icon: Truck,
          link: '/fleet/vehicles',
        },
        {
          label: 'Drivers (Online / Offline)',
          value: `${filtered.kpis.driversOnline} / ${filtered.kpis.driversOffline}`,
          icon: Wrench,
          link: '/fleet/drivers',
        },
        {
          label: 'Issues (Open / Resolved)',
          value: `${filtered.kpis.issuesOpen} / ${filtered.kpis.issuesResolved}`,
          icon: AlertCircle,
          link: '/fleet/issues',
        },
        {
          label: 'Total Fuel Cost',
          value: filtered.kpis.totalFuelCost.toLocaleString(undefined, { maximumFractionDigits: 2 }),
          icon: DollarSign,
          link: '/fleet/fuel-reports',
        },
      ]
    : [];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Dashboard Overview</h1>
          <p className="text-sm text-gray-600 mt-1">Real backend operational metrics</p>
        </div>
        <div className="flex items-center space-x-2 text-sm text-gray-600 flex-wrap justify-end">
          <div className="inline-flex rounded-lg border border-gray-200 bg-white p-1">
            {([
              { id: 'today', label: 'Today' },
              { id: 'last7', label: 'Last 7 days' },
              { id: 'last30', label: 'Last 30 days' },
            ] as const).map((item) => (
              <button
                key={item.id}
                type="button"
                onClick={() => setRange(item.id)}
                className={`px-3 py-1.5 rounded-md text-xs font-medium ${range === item.id ? 'bg-blue-600 text-white' : 'text-gray-600 hover:bg-gray-100'}`}
              >
                {item.label}
              </button>
            ))}
          </div>
          <Calendar size={16} />
          <span>{new Date().toLocaleDateString()}</span>
        </div>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg flex items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            <AlertCircle size={18} />
            <span>{error}</span>
          </div>
          <button
            type="button"
            onClick={loadDashboardData}
            className="px-3 py-1.5 rounded-md border border-red-300 text-red-700 hover:bg-red-100"
          >
            Retry
          </button>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
        {kpis.map((kpi, idx) => (
          <Link key={kpi.label} to={kpi.link} className="card-base p-6 cursor-pointer animate-scale-in" style={{ animationDelay: `${idx * 100}ms` }}>
            <div className="w-12 h-12 rounded-lg bg-blue-100 flex items-center justify-center mb-4">
              <kpi.icon className="text-blue-600" size={24} />
            </div>
            <div className="text-2xl font-bold text-gray-900 mb-1">{kpi.value}</div>
            <div className="text-sm text-gray-600">{kpi.label}</div>
          </Link>
        ))}
      </div>

      <div className="bg-white rounded-xl border border-gray-200 p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-bold text-gray-900">Module Data Coverage (Live)</h2>
          <span className="text-xs text-gray-500">{overview?.moduleCounts.length ?? 0} modules</span>
        </div>
        {(overview?.moduleCounts.length ?? 0) === 0 ? (
          <EmptyState icon={Package} title="No module data available" description="Module counts will appear when APIs respond" />
        ) : (
          <div className="grid grid-cols-2 md:grid-cols-3 xl:grid-cols-5 gap-3">
            {overview?.moduleCounts.map((module) => (
              <Link
                key={module.key}
                to={module.route}
                className="rounded-lg border border-gray-200 bg-gray-50 hover:bg-gray-100 transition-colors p-3"
                title={`Open ${module.label}`}
              >
                <div className="text-xs text-gray-600 truncate">{module.label}</div>
                <div className="text-xl font-semibold text-gray-900 mt-1">{module.count}</div>
              </Link>
            ))}
          </div>
        )}
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
        <div className="bg-white rounded-xl border border-gray-200 p-6 xl:col-span-2">
          <h2 className="text-lg font-bold text-gray-900 mb-4">Orders Over Time</h2>
          {!filtered || filtered.ordersOverTime.length === 0 ? (
            <Skeleton height={260} />
          ) : (
            <ResponsiveContainer width="100%" height={260}>
              <LineChart data={filtered.ordersOverTime}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis allowDecimals={false} />
                <Tooltip />
                <Line type="monotone" dataKey="count" stroke="#2563eb" strokeWidth={2} dot={false} />
              </LineChart>
            </ResponsiveContainer>
          )}
        </div>
        <div className="bg-white rounded-xl border border-gray-200 p-6">
          <h2 className="text-lg font-bold text-gray-900 mb-4">Issues By Status</h2>
          {!filtered || filtered.issuesByStatus.every((x) => x.value === 0) ? (
            <Skeleton height={260} />
          ) : (
            <ResponsiveContainer width="100%" height={260}>
              <PieChart>
                <Pie data={filtered.issuesByStatus} dataKey="value" nameKey="name" outerRadius={90} label>
                  {filtered.issuesByStatus.map((_, index) => (
                    <Cell key={index} fill={index === 0 ? '#f59e0b' : '#10b981'} />
                  ))}
                </Pie>
                <Tooltip />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          )}
        </div>
      </div>

      <div className="bg-white rounded-xl border border-gray-200 p-6">
        <h2 className="text-lg font-bold text-gray-900 mb-4">Fuel Cost Trend</h2>
        {!filtered || filtered.fuelCostTrend.length === 0 ? (
          <Skeleton height={260} />
        ) : (
          <ResponsiveContainer width="100%" height={260}>
            <BarChart data={filtered.fuelCostTrend}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="amount" fill="#7c3aed" radius={[6, 6, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        )}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-xl border border-gray-200 p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-bold text-gray-900">Recent Orders</h2>
            <Link to="/logistics/orders" className="text-sm text-blue-600 hover:text-blue-700 font-medium">View All →</Link>
          </div>
          {(filtered?.recentOrders.length ?? 0) === 0 ? (
            <EmptyState icon={Package} title="No recent orders" description="Orders will appear here once created" />
          ) : (
            <div className="space-y-3">
              {filtered?.recentOrders.map((order, idx) => (
                (() => {
                  const orderId = String(order.uuid ?? order.public_id ?? order.id ?? '');
                  return (
                <div
                  key={String(order.uuid ?? order.public_id ?? order.id ?? idx)}
                  className="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors animate-fade-in-up"
                  style={{ animationDelay: `${idx * 50}ms` }}
                >
                  <div className="flex-1">
                    <div className="flex items-center space-x-2 mb-1">
                      {orderId ? (
                        <Link
                          to={`/logistics/orders/${encodeURIComponent(orderId)}`}
                          title="View Order"
                          className="text-xs font-bold text-blue-600 hover:underline cursor-pointer"
                        >
                          {String(order.public_id ?? order.uuid ?? order.id ?? '—')}
                        </Link>
                      ) : (
                        <span className="text-xs font-bold text-blue-600">{String(order.public_id ?? order.uuid ?? order.id ?? '—')}</span>
                      )}
                      <span className="px-2 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-700">{String(order.status ?? '—')}</span>
                    </div>
                    <p className="text-sm font-medium text-gray-900">{orderCustomerLabel(order as unknown as UiOrder)}</p>
                    <p className="text-xs text-gray-600 truncate">{String(order.internal_id ?? order.uuid ?? order.id ?? '—')}</p>
                  </div>
                  <div className="text-xs text-gray-500">{order.created_at ? new Date(String(order.created_at)).toLocaleDateString() : '—'}</div>
                </div>
                  );
                })()
              ))}
            </div>
          )}
        </div>

        <div className="bg-white rounded-xl border border-gray-200 p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-bold text-gray-900">Recent Issues</h2>
            <Link to="/fleet/issues" className="text-sm text-blue-600 hover:text-blue-700 font-medium">View All →</Link>
          </div>
          {(filtered?.recentIssues.length ?? 0) === 0 ? (
            <EmptyState icon={AlertCircle} title="No recent issues" description="Issues will appear here once created" />
          ) : (
            <div className="space-y-3">
              {filtered?.recentIssues.map((issue, idx) => (
                (() => {
                  const issueId = String(issue.uuid ?? issue.public_id ?? issue.id ?? '');
                  return (
                <div
                  key={String(issue.uuid ?? issue.public_id ?? issue.id ?? idx)}
                  className="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors animate-fade-in-up"
                  style={{ animationDelay: `${idx * 50}ms` }}
                >
                  <div className="flex-1">
                    <div className="flex items-center space-x-2 mb-1">
                      {issueId ? (
                        <Link
                          to={`/fleet/issues/${encodeURIComponent(issueId)}`}
                          title="View Issue"
                          className="text-xs font-bold text-blue-600 hover:underline cursor-pointer"
                        >
                          {String(issue.issue_id ?? issue.public_id ?? issue.uuid ?? issue.id ?? '—')}
                        </Link>
                      ) : (
                        <span className="text-xs font-bold text-blue-600">{String(issue.issue_id ?? issue.public_id ?? issue.uuid ?? issue.id ?? '—')}</span>
                      )}
                      <span className="px-2 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-700">{String(issue.status ?? '—')}</span>
                    </div>
                    <p className="text-sm font-medium text-gray-900">{String(issue.title ?? '—')}</p>
                    <p className="text-xs text-gray-600">{String(issue.type ?? '—')}</p>
                  </div>
                  <div className="text-xs text-gray-500">{issue.created_at ? new Date(String(issue.created_at)).toLocaleDateString() : '—'}</div>
                </div>
                  );
                })()
              ))}
            </div>
          )}
        </div>
      </div>

      <div className="bg-white rounded-xl border border-gray-200 p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-bold text-gray-900">Recent Fuel Reports</h2>
          <Link to="/fleet/fuel-reports" className="text-sm text-blue-600 hover:text-blue-700 font-medium">View All →</Link>
        </div>
        {(filtered?.recentFuelReports.length ?? 0) === 0 ? (
          <EmptyState icon={Truck} title="No recent fuel reports" description="Fuel reports will appear here once created" />
        ) : (
          <div className="space-y-3">
            {filtered?.recentFuelReports.map((report, idx) => (
              (() => {
                const reportId = String(report.uuid ?? report.public_id ?? report.id ?? '');
                const driverId = String(report.driver_uuid ?? '');
                const vehicleId = String(report.vehicle_uuid ?? '');
                return (
              <div
                key={String(report.uuid ?? report.public_id ?? report.id ?? idx)}
                className="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors animate-fade-in-up"
                style={{ animationDelay: `${idx * 50}ms` }}
              >
                <div className="flex-1">
                  <div className="flex items-center space-x-2 mb-1">
                    {reportId ? (
                      <Link
                        to={`/fleet/fuel-reports/${encodeURIComponent(reportId)}`}
                        title="View Fuel Report"
                        className="text-xs font-bold text-blue-600 hover:underline cursor-pointer"
                      >
                        {String(report.public_id ?? report.uuid ?? report.id ?? '—')}
                      </Link>
                    ) : (
                      <span className="text-xs font-bold text-blue-600">{String(report.public_id ?? report.uuid ?? report.id ?? '—')}</span>
                    )}
                    <span className="px-2 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-700">{String(report.status ?? '—')}</span>
                  </div>
                  <p className="text-sm font-medium text-gray-900">
                    {driverId ? (
                      <Link to={`/fleet/drivers/${encodeURIComponent(driverId)}`} title="View Driver" className="text-blue-600 hover:underline cursor-pointer">
                        {String(report.driver_name ?? driverId)}
                      </Link>
                    ) : (
                      String(report.driver_name ?? '—')
                    )}{' '}
                    •{' '}
                    {vehicleId ? (
                      <Link to={`/fleet/vehicles/${encodeURIComponent(vehicleId)}`} title="View Vehicle" className="text-blue-600 hover:underline cursor-pointer">
                        {String(report.vehicle_name ?? vehicleId)}
                      </Link>
                    ) : (
                      String(report.vehicle_name ?? '—')
                    )}
                  </p>
                  <p className="text-xs text-gray-600">{String(report.amount ?? '0')} {String(report.currency ?? '')}</p>
                </div>
                <div className="text-xs text-gray-500">{report.created_at ? new Date(String(report.created_at)).toLocaleDateString() : '—'}</div>
              </div>
                );
              })()
            ))}
          </div>
        )}
      </div>

    </div>
  );
};

export default DashboardOverview;
