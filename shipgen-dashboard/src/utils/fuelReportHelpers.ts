import type { MockFuelReport } from '../mocks/data/fuel_reports';

export function getFuelReportRouteId(report: MockFuelReport): string {
  if (report.uuid) return report.uuid;
  if (report.id != null) return String(report.id);
  return '';
}
