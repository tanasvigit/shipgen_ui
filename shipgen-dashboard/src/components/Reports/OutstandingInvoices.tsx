import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { DollarSign, Calendar, AlertCircle, Eye, FileText } from 'lucide-react';
import { apiClient, ApiResponse } from '../../services/apiClient';
import RouteDetailsModal from '../common/RouteDetailsModal';

interface OutstandingInvoice {
  id: string;
  invoiceNumber: string;
  totalAmount: number;
  paidAmount: number;
  outstandingAmount: number;
  dueDate: string;
  createdAt: string;
}

const OutstandingInvoices: React.FC = () => {
  const [invoices, setInvoices] = useState<OutstandingInvoice[]>([]);
  const [summary, setSummary] = useState({
    totalOutstanding: 0,
    totalInvoices: 0
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [selectedInvoiceId, setSelectedInvoiceId] = useState<string | null>(null);
  const [isDetailsOpen, setIsDetailsOpen] = useState(false);

  useEffect(() => {
    loadOutstanding();
  }, [page]);

  const loadOutstanding = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await apiClient.get<ApiResponse<OutstandingInvoice[]>>('/reports/outstanding', {
        page,
        pageSize: 20
      });
      setInvoices(response.data);
      setTotalPages(Math.ceil((response.pagination?.total || 0) / 20));
      
      // Calculate summary
      const total = response.data.reduce((sum, inv) => sum + inv.outstandingAmount, 0);
      setSummary({
        totalOutstanding: total,
        totalInvoices: response.pagination?.total || 0
      });
      setLoading(false);
    } catch (err: any) {
      setError(err.message || 'Failed to load outstanding invoices');
      setLoading(false);
    }
  };

  const isOverdue = (dueDate: string) => {
    return new Date(dueDate) < new Date();
  };

  if (loading && invoices.length === 0) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Outstanding Invoices</h1>
        <p className="text-sm text-gray-600 mt-1">Invoices pending payment</p>
      </div>

      {/* Summary */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white rounded-xl border border-gray-200 p-6">
          <div className="flex items-center justify-between mb-2">
            <DollarSign size={24} className="text-orange-600" />
          </div>
          <div className="text-2xl font-bold text-gray-900">₹{summary.totalOutstanding.toLocaleString()}</div>
          <div className="text-sm text-gray-600">Total Outstanding</div>
        </div>
        <div className="bg-white rounded-xl border border-gray-200 p-6">
          <div className="flex items-center justify-between mb-2">
            <FileText size={24} className="text-blue-600" />
          </div>
          <div className="text-2xl font-bold text-gray-900">{summary.totalInvoices}</div>
          <div className="text-sm text-gray-600">Outstanding Invoices</div>
        </div>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg flex items-center space-x-2">
          <AlertCircle size={20} />
          <span>{error}</span>
        </div>
      )}

      <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
        {invoices.length === 0 ? (
          <div className="p-12 text-center">
            <FileText size={48} className="mx-auto text-gray-300 mb-4" />
            <p className="text-gray-600">No outstanding invoices</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50 border-b border-gray-200">
                <tr>
                  <th className="text-left py-3 px-4 text-xs font-semibold text-gray-600 uppercase">Invoice #</th>
                  <th className="text-right py-3 px-4 text-xs font-semibold text-gray-600 uppercase">Total Amount</th>
                  <th className="text-right py-3 px-4 text-xs font-semibold text-gray-600 uppercase">Paid</th>
                  <th className="text-right py-3 px-4 text-xs font-semibold text-gray-600 uppercase">Outstanding</th>
                  <th className="text-left py-3 px-4 text-xs font-semibold text-gray-600 uppercase">Due Date</th>
                  <th className="text-right py-3 px-4 text-xs font-semibold text-gray-600 uppercase">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {invoices.map((invoice) => (
                  <tr key={invoice.id} className="hover:bg-gray-50">
                    <td className="py-3 px-4">
                      <span className="text-sm font-bold text-blue-600">{invoice.invoiceNumber}</span>
                    </td>
                    <td className="py-3 px-4 text-right">
                      <span className="text-sm font-medium text-gray-900">₹{invoice.totalAmount.toLocaleString()}</span>
                    </td>
                    <td className="py-3 px-4 text-right">
                      <span className="text-sm text-gray-700">₹{invoice.paidAmount.toLocaleString()}</span>
                    </td>
                    <td className="py-3 px-4 text-right">
                      <span className="text-sm font-semibold text-orange-600">₹{invoice.outstandingAmount.toLocaleString()}</span>
                    </td>
                    <td className="py-3 px-4">
                      <div className="flex items-center space-x-1">
                        <Calendar size={14} className={isOverdue(invoice.dueDate) ? 'text-red-500' : 'text-gray-500'} />
                        <span className={`text-sm ${isOverdue(invoice.dueDate) ? 'text-red-600 font-medium' : 'text-gray-600'}`}>
                          {new Date(invoice.dueDate).toLocaleDateString()}
                        </span>
                        {isOverdue(invoice.dueDate) && (
                          <span className="px-2 py-0.5 bg-red-100 text-red-700 rounded-full text-xs font-medium">
                            Overdue
                          </span>
                        )}
                      </div>
                    </td>
                    <td className="py-3 px-4">
                      <div className="flex items-center justify-end space-x-2">
                        <button
                          type="button"
                          onClick={() => {
                            setSelectedInvoiceId(invoice.id);
                            setIsDetailsOpen(true);
                          }}
                          className="p-2 text-gray-600 hover:bg-gray-100 rounded-lg transition"
                        >
                          <Eye size={16} />
                        </button>
                        <Link
                          to={`/billing/payments/record?invoiceId=${invoice.id}`}
                          className="px-3 py-1 bg-green-600 text-white rounded-lg hover:bg-green-700 transition text-xs font-medium"
                        >
                          Pay
                        </Link>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

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

export default OutstandingInvoices;
