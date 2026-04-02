
export enum UserRole {
  SUPER_ADMIN = 'SUPER_ADMIN',
  COMPANY_ADMIN = 'COMPANY_ADMIN',
  OPERATIONS_MANAGER = 'OPERATIONS_MANAGER',
  WAREHOUSE_MANAGER = 'WAREHOUSE_MANAGER',
  DRIVER = 'DRIVER',
  CUSTOMER = 'CUSTOMER',
  FINANCE = 'FINANCE'
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
  invoiceType: InvoiceType;
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
