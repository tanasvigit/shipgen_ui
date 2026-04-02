import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { ArrowLeft, FileText, DollarSign, Calendar, Package, AlertCircle, Download } from 'lucide-react';
import { apiClient } from '../../services/apiClient';
import { InvoiceStatus } from '../../types';

interface Invoice {
  id: string;
  invoiceNumber: string;
  invoiceType: string;
  referenceType: string | null;
  referenceId: string | null;
  subtotal: number;
  gstAmount: number;
  totalAmount: number;
  status: InvoiceStatus;
  dueDate: string;
  issuedAt: string | null;
  createdAt: string;
  lineItems?: Array<{
    id: string;
    description: string;
    quantity: number;
    unitPrice: number;
    amount: number;
  }>;
  payments?: Array<{
    id: string;
    amount: number;
    paymentMode: string;
    paidAt: string;
  }>;
}

const InvoiceDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [invoice, setInvoice] = useState<Invoice | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (id) {
      loadInvoice();
    }
  }, [id]);

  const loadInvoice = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await apiClient.get<Invoice>(`/invoices/${id}`);
      setInvoice(response);
      setLoading(false);
    } catch (err: any) {
      setError(err.message || 'Failed to load invoice');
      setLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    const colors: Record<string, string> = {
      'DRAFT': 'bg-gray-100 text-gray-700',
      'GENERATED': 'bg-blue-100 text-blue-700',
      'PAID': 'bg-green-100 text-green-700',
      'CANCELLED': 'bg-red-100 text-red-700',
    };
    return colors[status] || 'bg-gray-100 text-gray-700';
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error || !invoice) {
    return (
      <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
        {error || 'Invoice not found'}
      </div>
    );
  }

  const paidAmount = invoice.payments?.reduce((sum, p) => sum + p.amount, 0) || 0;
  const remainingAmount = invoice.totalAmount - paidAmount;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <Link
            to="/billing/invoices"
            className="p-2 hover:bg-gray-100 rounded-lg transition"
          >
            <ArrowLeft size={20} />
          </Link>
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Invoice Details</h1>
            <p className="text-sm text-gray-600 mt-1">Invoice #{invoice.invoiceNumber}</p>
          </div>
        </div>
        <button className="flex items-center space-x-2 px-4 py-2 border border-gray-200 text-gray-700 rounded-lg hover:bg-gray-50 transition">
          <Download size={18} />
          <span>Download PDF</span>
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          {/* Invoice Header */}
          <div className="bg-white rounded-xl border border-gray-200 p-6">
            <div className="flex items-center justify-between mb-6">
              <div>
                <h2 className="text-lg font-bold text-gray-900">Invoice #{invoice.invoiceNumber}</h2>
                <p className="text-sm text-gray-600 mt-1">{invoice.invoiceType} Invoice</p>
              </div>
              <span className={`px-3 py-1 rounded-full text-xs font-medium ${getStatusColor(invoice.status)}`}>
                {invoice.status}
              </span>
            </div>

            <div className="grid grid-cols-2 gap-4 mb-6">
              <div>
                <label className="text-xs text-gray-500 uppercase">Issue Date</label>
                <p className="text-sm font-medium text-gray-900">
                  {invoice.issuedAt ? new Date(invoice.issuedAt).toLocaleDateString() : '—'}
                </p>
              </div>
              <div>
                <label className="text-xs text-gray-500 uppercase">Due Date</label>
                <p className="text-sm font-medium text-gray-900">
                  {new Date(invoice.dueDate).toLocaleDateString()}
                </p>
              </div>
            </div>

            {invoice.referenceId && (
              <div className="mb-6">
                <label className="text-xs text-gray-500 uppercase">Reference</label>
                <p className="text-sm font-medium text-gray-900">
                  {invoice.referenceType}: {invoice.referenceId.slice(0, 8)}
                </p>
              </div>
            )}
          </div>

          {/* Line Items */}
          <div className="bg-white rounded-xl border border-gray-200 p-6">
            <h3 className="text-lg font-bold text-gray-900 mb-4">Line Items</h3>
            {invoice.lineItems && invoice.lineItems.length > 0 ? (
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-gray-50 border-b border-gray-200">
                    <tr>
                      <th className="text-left py-3 px-4 text-xs font-semibold text-gray-600 uppercase">Description</th>
                      <th className="text-right py-3 px-4 text-xs font-semibold text-gray-600 uppercase">Quantity</th>
                      <th className="text-right py-3 px-4 text-xs font-semibold text-gray-600 uppercase">Unit Price</th>
                      <th className="text-right py-3 px-4 text-xs font-semibold text-gray-600 uppercase">Amount</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-100">
                    {invoice.lineItems.map((item) => (
                      <tr key={item.id}>
                        <td className="py-3 px-4 text-sm text-gray-900">{item.description}</td>
                        <td className="py-3 px-4 text-sm text-gray-700 text-right">{item.quantity}</td>
                        <td className="py-3 px-4 text-sm text-gray-700 text-right">₹{item.unitPrice.toLocaleString()}</td>
                        <td className="py-3 px-4 text-sm font-medium text-gray-900 text-right">₹{item.amount.toLocaleString()}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <p className="text-sm text-gray-600">No line items</p>
            )}
          </div>

          {/* Summary */}
          <div className="bg-white rounded-xl border border-gray-200 p-6">
            <h3 className="text-lg font-bold text-gray-900 mb-4">Summary</h3>
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">Subtotal</span>
                <span className="text-sm font-medium text-gray-900">₹{invoice.subtotal.toLocaleString()}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">GST (18%)</span>
                <span className="text-sm font-medium text-gray-900">₹{invoice.gstAmount.toLocaleString()}</span>
              </div>
              <div className="pt-2 border-t border-gray-200 flex items-center justify-between">
                <span className="text-base font-bold text-gray-900">Total Amount</span>
                <span className="text-base font-bold text-gray-900">₹{invoice.totalAmount.toLocaleString()}</span>
              </div>
              {paidAmount > 0 && (
                <>
                  <div className="flex items-center justify-between pt-2">
                    <span className="text-sm text-green-600">Paid</span>
                    <span className="text-sm font-medium text-green-600">₹{paidAmount.toLocaleString()}</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-orange-600">Remaining</span>
                    <span className="text-sm font-medium text-orange-600">₹{remainingAmount.toLocaleString()}</span>
                  </div>
                </>
              )}
            </div>
          </div>

          {/* Payments */}
          {invoice.payments && invoice.payments.length > 0 && (
            <div className="bg-white rounded-xl border border-gray-200 p-6">
              <h3 className="text-lg font-bold text-gray-900 mb-4">Payment History</h3>
              <div className="space-y-3">
                {invoice.payments.map((payment) => (
                  <div key={payment.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                    <div>
                      <p className="text-sm font-medium text-gray-900">₹{payment.amount.toLocaleString()}</p>
                      <p className="text-xs text-gray-600">{payment.paymentMode} • {new Date(payment.paidAt).toLocaleString()}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          <div className="bg-white rounded-xl border border-gray-200 p-6">
            <h3 className="font-semibold text-gray-900 mb-4">Quick Actions</h3>
            <div className="space-y-2">
              {invoice.status === 'GENERATED' && remainingAmount > 0 && (
                <Link
                  to={`/billing/payments/record?invoiceId=${invoice.id}`}
                  className="block w-full px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition text-center text-sm font-medium"
                >
                  Record Payment
                </Link>
              )}
              <button className="w-full px-4 py-2 border border-gray-200 text-gray-700 rounded-lg hover:bg-gray-50 transition text-sm font-medium">
                Download PDF
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default InvoiceDetail;
