import type { DashboardOverviewData } from '../services/dashboardOverviewService';

export type DashboardRange = 'today' | 'last7' | 'last30';
type GenericRow = Record<string, unknown>;

const toDate = (value: unknown): Date | null => {
  const d = new Date(String(value ?? ''));
  return Number.isNaN(d.getTime()) ? null : d;
};

const getRowDate = (row: GenericRow): Date | null => {
  return toDate(row.created_at) ?? toDate(row.updated_at) ?? toDate(row.scheduled_at);
};

const getTimeValue = (row: GenericRow): number => {
  const d = getRowDate(row);
  return d ? d.getTime() : 0;
};

const startOfToday = (): Date => {
  const d = new Date();
  d.setHours(0, 0, 0, 0);
  return d;
};

const getRangeStart = (range: DashboardRange): Date => {
  const start = startOfToday();
  if (range === 'today') return start;
  const days = range === 'last7' ? 6 : 29;
  start.setDate(start.getDate() - days);
  return start;
};

export const filterByDateRange = (rows: GenericRow[], range: DashboardRange): GenericRow[] => {
  const rangeStart = getRangeStart(range).getTime();
  return rows.filter((row) => {
    const d = getRowDate(row);
    // Keep undated rows so dashboard counts stay aligned with list pages.
    return d ? d.getTime() >= rangeStart : true;
  });
};

export const computeKpis = (orders: GenericRow[], drivers: GenericRow[], vehicles: GenericRow[], issues: GenericRow[], fuelReports: GenericRow[]) => {
  const activeOrderStatuses = new Set(['created', 'scheduled', 'dispatched', 'in_progress', 'started']);
  const activeVehicleStatuses = new Set(['active', 'in_service', 'on_road', 'assigned', 'busy']);
  const resolvedIssueStatuses = new Set(['resolved', 'closed', 'done']);

  const activeOrders = orders.filter((o) => activeOrderStatuses.has(String(o.status ?? '').toLowerCase())).length;
  const vehiclesActive = vehicles.filter((v) => activeVehicleStatuses.has(String(v.status ?? '').toLowerCase())).length;
  const vehiclesAvailable = Math.max(0, vehicles.length - vehiclesActive);
  const driversOnline = drivers.filter((d) => Number(d.online ?? 0) === 1).length;
  const driversOffline = Math.max(0, drivers.length - driversOnline);
  const issuesResolved = issues.filter((i) => resolvedIssueStatuses.has(String(i.status ?? '').toLowerCase())).length;
  const issuesOpen = Math.max(0, issues.length - issuesResolved);
  const totalFuelCost = fuelReports.reduce((sum, row) => {
    const amount = Number(row.amount ?? 0);
    return sum + (Number.isFinite(amount) ? amount : 0);
  }, 0);

  return {
    totalOrders: orders.length,
    activeOrders,
    vehiclesAvailable,
    vehiclesActive,
    driversOnline,
    driversOffline,
    issuesOpen,
    issuesResolved,
    totalFuelCost,
  };
};

const formatDay = (value: unknown): string => {
  const d = toDate(value);
  if (!d) return 'Unknown';
  return d.toLocaleDateString(undefined, { month: 'short', day: '2-digit' });
};

export const buildOrdersOverTime = (orders: GenericRow[]) => {
  const bucket = new Map<string, number>();
  for (const order of orders) {
    const key = formatDay(order.created_at ?? order.updated_at ?? order.scheduled_at);
    bucket.set(key, (bucket.get(key) ?? 0) + 1);
  }
  return Array.from(bucket.entries()).map(([date, count]) => ({ date, count }));
};

export const buildFuelCostTrend = (fuelReports: GenericRow[]) => {
  const bucket = new Map<string, number>();
  for (const report of fuelReports) {
    const key = formatDay(report.created_at ?? report.updated_at ?? report.scheduled_at);
    const amount = Number(report.amount ?? 0);
    const safe = Number.isFinite(amount) ? amount : 0;
    bucket.set(key, (bucket.get(key) ?? 0) + safe);
  }
  return Array.from(bucket.entries()).map(([date, amount]) => ({ date, amount: Number(amount.toFixed(2)) }));
};

export const buildIssuesByStatus = (issues: GenericRow[]) => {
  const resolvedStatuses = new Set(['resolved', 'closed', 'done']);
  let open = 0;
  let resolved = 0;
  for (const issue of issues) {
    if (resolvedStatuses.has(String(issue.status ?? '').toLowerCase())) resolved += 1;
    else open += 1;
  }
  return [
    { name: 'Open', value: open },
    { name: 'Resolved', value: resolved },
  ];
};

export const applyRangeToOverview = (overview: DashboardOverviewData, range: DashboardRange) => {
  // Time-range filters apply to event-like datasets.
  const orders = filterByDateRange(overview.orders, range);
  const issues = filterByDateRange(overview.issues, range);
  const fuelReports = filterByDateRange(overview.fuelReports, range);

  // Snapshot datasets should stay current-state, not be reduced by created_at range.
  const drivers = overview.drivers;
  const vehicles = overview.vehicles;

  return {
    kpis: computeKpis(orders, drivers, vehicles, issues, fuelReports),
    recentOrders: [...orders].sort((a, b) => getTimeValue(b) - getTimeValue(a)).slice(0, 5),
    recentIssues: [...issues].sort((a, b) => getTimeValue(b) - getTimeValue(a)).slice(0, 5),
    recentFuelReports: [...fuelReports].sort((a, b) => getTimeValue(b) - getTimeValue(a)).slice(0, 5),
    ordersOverTime: buildOrdersOverTime(orders),
    fuelCostTrend: buildFuelCostTrend(fuelReports),
    issuesByStatus: buildIssuesByStatus(issues),
  };
};
