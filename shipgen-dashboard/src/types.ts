
export enum UserRole {
  ADMIN = 'ADMIN',
  OPERATIONS_MANAGER = 'OPERATIONS_MANAGER',
  DISPATCHER = 'DISPATCHER',
  DRIVER = 'DRIVER',
  // VIEWER: Internal read-only role for stakeholders (NOT external customer)
  VIEWER = 'VIEWER',
}

/**
 * Legacy role mapping for backward compatibility.
 * Maps old/deprecated role names to current logistics roles.
 * 
 * Note: VIEWER is an INTERNAL read-only role, NOT an external customer.
 * External customers should use the Storefront system with separate authentication.
 */
const LEGACY_ROLE_MAP: Record<string, UserRole> = {
  SUPER_ADMIN: UserRole.ADMIN,
  COMPANY_ADMIN: UserRole.ADMIN,
  OPERATIONS_MANAGER: UserRole.OPERATIONS_MANAGER,
  WAREHOUSE_MANAGER: UserRole.VIEWER,  // Internal warehouse staff (read-only)
  FINANCE: UserRole.VIEWER,             // Internal finance team (read-only)
  // CUSTOMER role removed - external customers use Storefront, not internal dashboard
  DRIVER: UserRole.DRIVER,
};

/** Normalize API or legacy role strings to a logistics role. Missing/unknown → DISPATCHER. */
export function normalizeUserRole(raw?: string | null): UserRole {
  if (!raw) return UserRole.DISPATCHER;
  const u = raw.trim().toUpperCase();
  if (LEGACY_ROLE_MAP[u]) return LEGACY_ROLE_MAP[u];
  if ((Object.values(UserRole) as string[]).includes(u)) return u as UserRole;
  return UserRole.DISPATCHER;
}

export enum TransactionType {
  INWARD = 'INWARD',
  OUTWARD = 'OUTWARD',
  TRANSFER = 'TRANSFER',
  ADJUSTMENT = 'ADJUSTMENT'
}

export interface User {
  id: string;
  name: string;
  email: string;
  role: UserRole;
  company_id: string;
}

export interface WarehouseZone {
  id: string;
  name: string;
  type: 'COLD' | 'DRY' | 'HAZARDOUS' | 'GENERAL';
  capacity: number;
  occupied: number;
}

export interface Warehouse {
  id: string;
  company_id: string;
  name: string;
  location: string;
  total_capacity: number;
  occupancy: number;
  zones: WarehouseZone[];
}

export interface InventoryItem {
  id: string;
  warehouse_id: string;
  zone_id: string;
  sku: string;
  name: string;
  quantity: number;
  unit: string;
  batch_no: string;
  expiry_date?: string;
}

export interface InventoryLedger {
  id: string;
  sku: string;
  warehouse_id: string;
  type: TransactionType;
  quantity: number;
  reference_id: string;
  timestamp: string;
  user_id: string;
}

export enum InvoiceStatus {
  DRAFT = 'DRAFT',
  GENERATED = 'GENERATED',
  PAID = 'PAID',
  CANCELLED = 'CANCELLED'
}

export enum PaymentMode {
  CASH = 'CASH',
  BANK = 'BANK',
  UPI = 'UPI',
  CARD = 'CARD'
}

export interface InvoiceLineItem {
  id: string;
  invoiceId: string;
  description: string;
  quantity: number;
  unitPrice: number;
  amount: number;
  createdAt: string;
}

export interface Payment {
  id: string;
  companyId: string;
  invoiceId: string;
  amount: number;
  paymentMode: PaymentMode;
  referenceNumber?: string;
  paidAt: string;
  createdAt: string;
}

export interface Invoice {
  id: string;
  companyId: string;
  invoiceNumber: string;
  invoiceType: string;
  referenceType?: string;
  referenceId?: string;
  subtotal: number;
  gstAmount: number;
  totalAmount: number;
  status: InvoiceStatus;
  dueDate: string;
  issuedAt?: string;
  createdAt: string;
  updatedAt: string;
  lineItems?: InvoiceLineItem[];
  payments?: Payment[];
}
