import React, { useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { AlertCircle } from 'lucide-react';
import { transactionsService, type UiTransaction } from '../../services/transactionsService';
import EntityLink from '../common/EntityLink';

const typeBadgeClass = (type: string): string => {
  const t = type.toLowerCase();
  if (t === 'credit') return 'bg-green-100 text-green-700';
  if (t === 'debit') return 'bg-red-100 text-red-700';
  return 'bg-gray-100 text-gray-700';
};

const statusBadgeClass = (status: string): string => {
  const s = status.toLowerCase();
  if (s.includes('success')) return 'bg-green-100 text-green-700';
  if (s.includes('pending')) return 'bg-amber-100 text-amber-700';
  if (s.includes('failed')) return 'bg-red-100 text-red-700';
  return 'bg-gray-100 text-gray-700';
};

const formatAmount = (amount: number, currency: string): string => {
  const code = (currency || 'USD').toUpperCase();
  try {
    return new Intl.NumberFormat('en-IN', { style: 'currency', currency: code }).format(amount);
  } catch {
    return `${amount.toFixed(2)} ${code}`;
  }
};

const TransactionDetail: React.FC = () => {
  const { id = '' } = useParams();
  const [item, setItem] = useState<UiTransaction | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const load = async () => {
      try {
        setLoading(true);
        setError(null);
        const tx = await transactionsService.getById(id);
        setItem(tx);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load transaction');
      } finally {
        setLoading(false);
      }
    };
    if (id) {
      void load();
    }
  }, [id]);

  if (loading) {
    return <div className="text-sm text-gray-500">Loading transaction...</div>;
  }

  if (error) {
    return (
      <div className="text-sm text-red-600 flex items-center gap-2">
        <AlertCircle size={16} />
        {error}
      </div>
    );
  }

  if (!item) {
    return <div className="text-sm text-gray-500">Transaction not found.</div>;
  }

  const raw = item.raw as Record<string, unknown>;
  const orderId = String(raw.order_uuid ?? raw.order_id ?? '');
  const driverId = String(raw.driver_uuid ?? raw.driver_id ?? '');
  const vehicleId = String(raw.vehicle_uuid ?? raw.vehicle_id ?? '');
  const vendorId = String(raw.vendor_uuid ?? raw.vendor_id ?? '');

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold text-gray-900">Transaction Detail</h1>
          <p className="text-sm text-gray-500 mt-1">Reference: {item.reference || item.id}</p>
        </div>
        <Link to="/analytics/transactions" className="px-4 py-2 border border-gray-200 rounded-lg text-sm hover:bg-gray-50">
          Back
        </Link>
      </div>

      <div className="bg-white border border-gray-200 rounded-lg p-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <p className="text-xs text-gray-500 uppercase tracking-wide">Amount</p>
            <p className="text-2xl font-semibold text-gray-900 mt-1">{formatAmount(item.amount, item.currency)}</p>
          </div>
          <div>
            <p className="text-xs text-gray-500 uppercase tracking-wide">Currency</p>
            <p className="text-sm font-medium text-gray-900 mt-1">{item.currency || '-'}</p>
          </div>
          <div>
            <p className="text-xs text-gray-500 uppercase tracking-wide">Type</p>
            <span className={`inline-flex mt-1 px-2 py-0.5 rounded-full text-xs font-medium ${typeBadgeClass(item.type)}`}>
              {item.type || '-'}
            </span>
          </div>
          <div>
            <p className="text-xs text-gray-500 uppercase tracking-wide">Status</p>
            <span className={`inline-flex mt-1 px-2 py-0.5 rounded-full text-xs font-medium ${statusBadgeClass(item.status)}`}>
              {item.status || '-'}
            </span>
          </div>
          <div>
            <p className="text-xs text-gray-500 uppercase tracking-wide">Transaction ID</p>
            <p className="text-sm text-gray-900 mt-1 break-all">{item.id}</p>
          </div>
          <div>
            <p className="text-xs text-gray-500 uppercase tracking-wide">Created At</p>
            <p className="text-sm text-gray-900 mt-1">{item.created_at ? new Date(item.created_at).toLocaleString() : '-'}</p>
          </div>
          <div className="md:col-span-2">
            <p className="text-xs text-gray-500 uppercase tracking-wide">Reference</p>
            <p className="text-sm text-gray-900 mt-1 break-all">{item.reference || '-'}</p>
          </div>
          <div className="md:col-span-2">
            <p className="text-xs text-gray-500 uppercase tracking-wide">Related Links</p>
            <div className="mt-1 flex flex-wrap gap-x-4 gap-y-2 text-sm">
              <EntityLink id={orderId} label="Order" to="/logistics/orders" title="View Order" />
              <EntityLink id={driverId} label="Driver" to="/fleet/drivers" title="View Driver" />
              <EntityLink id={vehicleId} label="Vehicle" to="/fleet/vehicles" title="View Vehicle" />
              <EntityLink id={vendorId} label="Vendor" to="/fleet/vendors" title="View Vendor" />
            </div>
          </div>
        </div>
      </div>

      <div className="bg-white border border-gray-200 rounded-lg p-6">
        <h2 className="text-sm font-semibold text-gray-900 mb-3">Raw Payload</h2>
        <pre className="text-xs bg-gray-50 border border-gray-200 rounded-md p-3 overflow-x-auto">
          {JSON.stringify(item.raw, null, 2)}
        </pre>
      </div>
    </div>
  );
};

export default TransactionDetail;
