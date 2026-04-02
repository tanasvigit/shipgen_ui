import React, { useState, useEffect } from 'react';
import { useNavigate, useSearchParams, Link } from 'react-router-dom';
import { ArrowLeft, Save, AlertCircle, DollarSign, FileText } from 'lucide-react';
import { apiClient } from '../../services/apiClient';

const PaymentRecord: React.FC = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const invoiceId = searchParams.get('invoiceId');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [invoice, setInvoice] = useState<any>(null);
  const [formData, setFormData] = useState({
    invoiceId: invoiceId || '',
    amount: '',
    paymentMode: 'CASH',
    referenceNumber: ''
  });

  useEffect(() => {
    if (invoiceId) {
      loadInvoice();
      setFormData(prev => ({ ...prev, invoiceId }));
    }
  }, [invoiceId]);

  const loadInvoice = async () => {
    try {
      const response = await apiClient.get(`/invoices/${invoiceId}`);
      setInvoice(response);
      // Set default amount to remaining amount if available
      const paidAmount = response.payments?.reduce((sum: number, p: any) => sum + p.amount, 0) || 0;
      const remaining = response.totalAmount - paidAmount;
      if (remaining > 0) {
        setFormData(prev => ({ ...prev, amount: remaining.toString() }));
      }
    } catch (err) {
      // Ignore
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.invoiceId || !formData.amount) {
      setError('Please fill all required fields');
      return;
    }
    try {
      setLoading(true);
      setError(null);
      const payload: any = {
        invoiceId: formData.invoiceId,
        amount: parseFloat(formData.amount),
        paymentMode: formData.paymentMode
      };
      if (formData.referenceNumber) {
        payload.referenceNumber = formData.referenceNumber;
      }
      await apiClient.post('/payments', payload);
      navigate(`/billing/invoices/${formData.invoiceId}`);
    } catch (err: any) {
      setError(err.message || 'Failed to record payment');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center space-x-4">
        <Link
          to="/billing/payments"
          className="p-2 hover:bg-gray-100 rounded-lg transition"
        >
          <ArrowLeft size={20} />
        </Link>
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Record Payment</h1>
          <p className="text-sm text-gray-600 mt-1">Record payment against an invoice</p>
        </div>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg flex items-center space-x-2">
          <AlertCircle size={20} />
          <span>{error}</span>
        </div>
      )}

      {invoice && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div className="flex items-center space-x-2 mb-2">
            <FileText size={18} className="text-blue-600" />
            <span className="font-semibold text-blue-900">Invoice #{invoice.invoiceNumber}</span>
          </div>
          <div className="text-sm text-blue-700">
            Total: ₹{invoice.totalAmount.toLocaleString()} • 
            Paid: ₹{(invoice.payments?.reduce((sum: number, p: any) => sum + p.amount, 0) || 0).toLocaleString()} • 
            Remaining: ₹{(invoice.totalAmount - (invoice.payments?.reduce((sum: number, p: any) => sum + p.amount, 0) || 0)).toLocaleString()}
          </div>
        </div>
      )}

      <form onSubmit={handleSubmit} className="bg-white rounded-xl border border-gray-200 p-6">
        <div className="space-y-6">
          {!invoiceId && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Invoice ID <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                required
                className="w-full px-4 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
                value={formData.invoiceId}
                onChange={(e) => setFormData({ ...formData, invoiceId: e.target.value })}
                placeholder="Enter invoice ID"
              />
            </div>
          )}

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2 flex items-center space-x-2">
              <DollarSign size={16} className="text-green-500" />
              <span>Amount <span className="text-red-500">*</span></span>
            </label>
            <input
              type="number"
              required
              min="0.01"
              step="0.01"
              className="w-full px-4 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
              value={formData.amount}
              onChange={(e) => setFormData({ ...formData, amount: e.target.value })}
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Payment Mode <span className="text-red-500">*</span>
            </label>
            <select
              required
              className="w-full px-4 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
              value={formData.paymentMode}
              onChange={(e) => setFormData({ ...formData, paymentMode: e.target.value })}
            >
              <option value="CASH">Cash</option>
              <option value="BANK">Bank Transfer</option>
              <option value="UPI">UPI</option>
              <option value="CARD">Card</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Reference Number (Optional)
            </label>
            <input
              type="text"
              className="w-full px-4 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
              value={formData.referenceNumber}
              onChange={(e) => setFormData({ ...formData, referenceNumber: e.target.value })}
              placeholder="Transaction ID, Cheque No, etc."
            />
          </div>

          <div className="flex items-center justify-end space-x-4 pt-4 border-t border-gray-200">
            <Link
              to="/billing/payments"
              className="px-6 py-2 border border-gray-200 text-gray-700 rounded-lg hover:bg-gray-50 transition"
            >
              Cancel
            </Link>
            <button
              type="submit"
              disabled={loading}
              className="flex items-center space-x-2 px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition disabled:opacity-50"
            >
              <Save size={18} />
              <span>{loading ? 'Recording...' : 'Record Payment'}</span>
            </button>
          </div>
        </div>
      </form>
    </div>
  );
};

export default PaymentRecord;
