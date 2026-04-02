export const mockInvoices = [
  {
    id: 'INV-01',
    invoiceNumber: 'INV-2026-001',
    invoiceType: 'MANUAL',
    referenceId: 'ORD-2001',
    subtotal: 12000,
    gstAmount: 2160,
    totalAmount: 14160,
    status: 'GENERATED',
    dueDate: new Date(Date.now() + 86400000 * 7).toISOString(),
    createdAt: new Date().toISOString(),
  },
  {
    id: 'INV-02',
    invoiceNumber: 'INV-2026-002',
    invoiceType: 'MANUAL',
    referenceId: null,
    subtotal: 8000,
    gstAmount: 1440,
    totalAmount: 9440,
    status: 'PAID',
    dueDate: new Date(Date.now() - 86400000 * 2).toISOString(),
    createdAt: new Date().toISOString(),
  },
];

export const mockPayments = [
  {
    id: 'PAY-01',
    invoiceId: 'INV-02',
    amount: 9440,
    paymentMode: 'BANK',
    referenceNumber: 'UTR12345',
    paidAt: new Date().toISOString(),
    createdAt: new Date().toISOString(),
  },
];

export const mockOutstanding = { data: mockInvoices.filter((i) => i.status !== 'PAID') };
