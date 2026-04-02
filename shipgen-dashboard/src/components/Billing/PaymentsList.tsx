import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { DollarSign, Plus, Search, Calendar, AlertCircle } from 'lucide-react';
import { apiClient, ApiResponse } from '../../services/apiClient';
import RouteDetailsModal from '../common/RouteDetailsModal';

interface Payment {
  id: string;
  invoiceId: string;
  amount: number;
  paymentMode: string;
  referenceNumber: string | null;
  paidAt: string;
  invoice: {
    invoiceNumber: string;
  };
}

const PaymentsList: React.FC = () => {
  const [payments, setPayments] = useState<Payment[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [invoiceFilter, setInvoiceFilter] = useState<string>('');
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [selectedInvoiceId, setSelectedInvoiceId] = useState<string | null>(null);
  const [isDetailsOpen, setIsDetailsOpen] = useState(false);

  useEffect(() => {
    loadPayments();
  }, [page, invoiceFilter]);

  const loadPayments = async () => {
    try {
      setLoading(true);
      setError(null);
      const params: any = { page, pageSize: 20 };
      if (invoiceFilter) {
        params.invoiceId = invoiceFilter;
      }
      const response = await apiClient.get<ApiResponse<Payment[]>>('/payments', params);
      setPayments(response.data);
      setTotalPages(Math.ceil((response.pagination?.total || 0) / 20));
      setLoading(false);
    } catch (err: any) {
      setError(err.message || 'Failed to load payments');
      setLoading(false);
    }
  };

  const filteredPayments = payments.filter(p =>
    p.invoice.invoiceNumber.toLowerCase().includes(searchTerm.toLowerCase()) ||
    p.id.toLowerCase().includes(searchTerm.toLowerCase()) ||
    (p.referenceNumber && p.referenceNumber.toLowerCase().includes(searchTerm.toLowerCase()))
  );

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Payments</h1>
          <p className="text-sm text-gray-600 mt-1">Payment records and history</p>
        </div>
        <Link
          to="/billing/payments/record"
          className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
        >
          <Plus size={18} />
          <span>Record Payment</span>
        </Link>
      </div>

      <div className="flex flex-col sm:flex-row gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={18} />
          <input
            type="text"
            placeholder="Search by invoice number, reference..."
            className="w-full pl-10 pr-4 py-2 bg-white border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg flex items-center space-x-2">
          <AlertCircle size={20} />
          <span>{error}</span>
        </div>
      )}

      {loading ? (
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        </div>
      ) : (
        <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
          {filteredPayments.length === 0 ? (
            <div className="p-12 text-center">
              <DollarSign size={48} className="mx-auto text-gray-300 mb-4" />
              <p className="text-gray-600">No payments found</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50 border-b border-gray-200">
                  <tr>
                    <th className="text-left py-3 px-4 text-xs font-semibold text-gray-600 uppercase">Invoice #</th>
                    <th className="text-right py-3 px-4 text-xs font-semibold text-gray-600 uppercase">Amount</th>
                    <th className="text-left py-3 px-4 text-xs font-semibold text-gray-600 uppercase">Payment Mode</th>
                    <th className="text-left py-3 px-4 text-xs font-semibold text-gray-600 uppercase">Reference</th>
                    <th className="text-left py-3 px-4 text-xs font-semibold text-gray-600 uppercase">Date</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-100">
                  {filteredPayments.map((payment) => (
                    <tr key={payment.id} className="hover:bg-gray-50">
                      <td className="py-3 px-4">
                        <button
                          type="button"
                          onClick={() => {
                            setSelectedInvoiceId(payment.invoiceId);
                            setIsDetailsOpen(true);
                          }}
                          className="text-sm font-medium text-blue-600 hover:text-blue-700"
                        >
                          {payment.invoice.invoiceNumber}
                        </button>
                      </td>
                      <td className="py-3 px-4 text-right">
                        <div className="flex items-center justify-end space-x-1">
                          <DollarSign size={14} className="text-gray-500" />
                          <span className="text-sm font-semibold text-gray-900">{payment.amount.toLocaleString()}</span>
                        </div>
                      </td>
                      <td className="py-3 px-4">
                        <span className="text-sm text-gray-700">{payment.paymentMode}</span>
                      </td>
                      <td className="py-3 px-4">
                        <span className="text-sm text-gray-600">{payment.referenceNumber || '—'}</span>
                      </td>
                      <td className="py-3 px-4">
                        <div className="flex items-center space-x-1 text-sm text-gray-600">
                          <Calendar size={14} />
                          <span>{new Date(payment.paidAt).toLocaleDateString()}</span>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      {totalPages > 1 && (
        <div className="flex items-center justify-center space-x-2">
          <button
            onClick={() => setPage(p => Math.max(1, p - 1))}
            disabled={page === 1}
            className="px-4 py-2 border border-gray-200 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
          >
            Previous
          </button>
          <span className="px-4 py-2 text-sm text-gray-600">
            Page {page} of {totalPages}
          </span>
          <button
            onClick={() => setPage(p => Math.min(totalPages, p + 1))}
            disabled={page === totalPages}
            className="px-4 py-2 border border-gray-200 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
          >
            Next
          </button>
        </div>
      )}
      <RouteDetailsModal
        isOpen={isDetailsOpen}
        onClose={() => setIsDetailsOpen(false)}
        title="Invoice Details"
        routePath={selectedInvoiceId ? `/billing/invoices/${encodeURIComponent(selectedInvoiceId)}` : null}
        headerTitle="Invoice Details"
        headerSubtitle={selectedInvoiceId ?? undefined}
      />
    </div>
  );
};

export default PaymentsList;
