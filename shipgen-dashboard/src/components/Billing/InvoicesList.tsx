import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { FileText, Plus, Search, Eye, DollarSign, Calendar, AlertCircle } from 'lucide-react';
import { apiClient, ApiResponse } from '../../services/apiClient';
import { InvoiceStatus } from '../../types';
import RouteDetailsModal from '../common/RouteDetailsModal';

interface Invoice {
  id: string;
  invoiceNumber: string;
  invoiceType: string;
  referenceId: string | null;
  subtotal: number;
  gstAmount: number;
  totalAmount: number;
  status: InvoiceStatus;
  dueDate: string;
  createdAt: string;
}

const InvoicesList: React.FC = () => {
  const [invoices, setInvoices] = useState<Invoice[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [selectedInvoiceId, setSelectedInvoiceId] = useState<string | null>(null);
  const [isDetailsOpen, setIsDetailsOpen] = useState(false);

  useEffect(() => {
    loadInvoices();
  }, [page, statusFilter]);

  const loadInvoices = async () => {
    try {
      setLoading(true);
      setError(null);
      const params: any = { page, pageSize: 20 };
      if (statusFilter !== 'all') {
        params.status = statusFilter;
      }
      const response = await apiClient.get<ApiResponse<Invoice[]>>('/invoices', params);
      setInvoices(response.data);
      setTotalPages(Math.ceil((response.pagination?.total || 0) / 20));
      setLoading(false);
    } catch (err: any) {
      setError(err.message || 'Failed to load invoices');
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

  const filteredInvoices = invoices.filter(inv =>
    inv.invoiceNumber.toLowerCase().includes(searchTerm.toLowerCase()) ||
    inv.id.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Invoices</h1>
          <p className="text-sm text-gray-600 mt-1">Manage invoices and billing</p>
        </div>
        <Link
          to="/billing/invoices/generate"
          className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
        >
          <Plus size={18} />
          <span>Generate Invoice</span>
        </Link>
      </div>

      <div className="flex flex-col sm:flex-row gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={18} />
          <input
            type="text"
            placeholder="Search by invoice number..."
            className="w-full pl-10 pr-4 py-2 bg-white border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>
        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          className="px-4 py-2 bg-white border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
        >
          <option value="all">All Status</option>
          <option value="DRAFT">Draft</option>
          <option value="GENERATED">Generated</option>
          <option value="PAID">Paid</option>
          <option value="CANCELLED">Cancelled</option>
        </select>
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
          {filteredInvoices.length === 0 ? (
            <div className="p-12 text-center">
              <FileText size={48} className="mx-auto text-gray-300 mb-4" />
              <p className="text-gray-600">No invoices found</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50 border-b border-gray-200">
                  <tr>
                    <th className="text-left py-3 px-4 text-xs font-semibold text-gray-600 uppercase">Invoice #</th>
                    <th className="text-left py-3 px-4 text-xs font-semibold text-gray-600 uppercase">Type</th>
                    <th className="text-right py-3 px-4 text-xs font-semibold text-gray-600 uppercase">Amount</th>
                    <th className="text-left py-3 px-4 text-xs font-semibold text-gray-600 uppercase">Status</th>
                    <th className="text-left py-3 px-4 text-xs font-semibold text-gray-600 uppercase">Due Date</th>
                    <th className="text-right py-3 px-4 text-xs font-semibold text-gray-600 uppercase">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-100">
                  {filteredInvoices.map((invoice) => (
                    <tr key={invoice.id} className="hover:bg-gray-50">
                      <td className="py-3 px-4">
                        <span className="text-sm font-bold text-blue-600">{invoice.invoiceNumber}</span>
                      </td>
                      <td className="py-3 px-4">
                        <span className="text-sm text-gray-700">{invoice.invoiceType}</span>
                      </td>
                      <td className="py-3 px-4 text-right">
                        <div className="flex items-center justify-end space-x-1">
                          <DollarSign size={14} className="text-gray-500" />
                          <span className="text-sm font-semibold text-gray-900">{invoice.totalAmount.toLocaleString()}</span>
                        </div>
                      </td>
                      <td className="py-3 px-4">
                        <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(invoice.status)}`}>
                          {invoice.status}
                        </span>
                      </td>
                      <td className="py-3 px-4">
                        <div className="flex items-center space-x-1 text-sm text-gray-600">
                          <Calendar size={14} />
                          <span>{new Date(invoice.dueDate).toLocaleDateString()}</span>
                        </div>
                      </td>
                      <td className="py-3 px-4">
                        <div className="flex items-center justify-end">
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

export default InvoicesList;
