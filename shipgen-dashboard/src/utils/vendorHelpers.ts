import type { MockVendor } from '../mocks/data/vendors';

export function getVendorRouteId(vendor: MockVendor): string {
  if (vendor.uuid) return vendor.uuid;
  if (vendor.id != null) return String(vendor.id);
  return '';
}
