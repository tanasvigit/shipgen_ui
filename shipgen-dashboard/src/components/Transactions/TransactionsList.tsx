import React, { useEffect, useMemo, useState } from 'react';
import { AlertCircle, Receipt, Search } from 'lucide-react';
import { transactionsService, type UiTransaction } from '../../services/transactionsService';
import EntityLink from '../common/EntityLink';
import { ResponsiveTable } from '../ui/ResponsiveTable';
import RouteDetailsModal from '../common/RouteDetailsModal';

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

const TransactionsList: React.FC = () => {
  const [rows, setRows] = useState<UiTransaction[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [isDetailsOpen, setIsDetailsOpen] = useState(false);

  useEffect(() => {
    const load = async () => {
      try {
        setLoading(true);
        setError(null);
        const items = await transactionsService.list();
        setRows(items);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load transactions');
      } finally {
        setLoading(false);
      }
    };
    void load();
  }, []);

  const filtered = useMemo(() => {
    const q = searchTerm.trim().toLowerCase();
    if (!q) return rows;
    return rows.filter((row) => `${row.id} ${row.reference}`.toLowerCase().includes(q));
  }, [rows, searchTerm]);

  const getReferenceLink = (row: UiTransaction): { id: string; to: string; label: string } | null => {
    const raw = row.raw as Record<string, unknown>;
    const orderId = String(raw.order_uuid ?? raw.order_id ?? '');
    if (orderId) return { id: orderId, to: '/logistics/orders', label: row.reference || orderId };
    const driverId = String(raw.driver_uuid ?? raw.driver_id ?? '');
    if (driverId) return { id: driverId, to: '/fleet/drivers', label: row.reference || driverId };
    const vehicleId = String(raw.vehicle_uuid ?? raw.vehicle_id ?? '');
    if (vehicleId) return { id: vehicleId, to: '/fleet/vehicles', label: row.reference || vehicleId };
    const vendorId = String(raw.vendor_uuid ?? raw.vendor_id ?? '');
    if (vendorId) return { id: vendorId, to: '/fleet/vendors', label: row.reference || vendorId };
    return row.reference ? { id: '', to: '', label: row.reference } : null;
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold text-gray-900">Transactions</h1>
          <p className="text-sm text-gray-500 mt-1">Read-only financial transactions overview</p>
        </div>
      </div>

      <div className="bg-white border border-gray-200 rounded-lg p-4">
        <div className="relative">
          <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
          <input
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="Search by reference or id"
            className="w-full pl-9 pr-3 py-2 border border-gray-200 rounded-lg outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
      </div>

      <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
        {loading ? (
          <div className="p-8 text-sm text-gray-500">Loading transactions...</div>
        ) : error ? (
          <div className="p-8 text-sm text-red-600 flex items-center gap-2">
            <AlertCircle size={16} />
            {error}
          </div>
        ) : filtered.length === 0 ? (
          <div className="p-10 text-center text-gray-500">
            <Receipt size={28} className="mx-auto mb-2 text-gray-400" />
            No transactions found
          </div>
        ) : (
          <ResponsiveTable
            data={filtered}
            keyExtractor={(row) => row.id}
            onRowClick={(row) => {
              setSelectedId(row.id);
              setIsDetailsOpen(true);
            }}
            columns={[
              {
                key: 'amount',
                header: 'amount',
                render: (row) => <span className="text-sm font-medium text-gray-900">{formatAmount(row.amount, row.currency)}</span>,
              },
              {
                key: 'currency',
                header: 'currency',
                render: (row) => <span className="text-sm text-gray-700">{row.currency || '-'}</span>,
              },
              {
                key: 'type',
                header: 'type',
                render: (row) => (
                  <span className={`inline-flex px-2 py-0.5 rounded-full text-xs font-medium ${typeBadgeClass(row.type)}`}>
                    {row.type || '-'}
                  </span>
                ),
              },
              {
                key: 'status',
                header: 'status',
                render: (row) => (
                  <span className={`inline-flex px-2 py-0.5 rounded-full text-xs font-medium ${statusBadgeClass(row.status)}`}>
                    {row.status || '-'}
                  </span>
                ),
              },
              {
                key: 'reference',
                header: 'reference',
                render: (row) => (
                  <span className="text-sm text-gray-700 table-cell-ellipsis block" title={row.reference || '-'}>
                    {(() => {
                      const link = getReferenceLink(row);
                      if (!link) return '—';
                      if (!link.id || !link.to) return link.label;
                      return <EntityLink id={link.id} label={link.label} to={link.to} title="Open referenced record" />;
                    })()}
                  </span>
                ),
              },
              {
                key: 'created_at',
                header: 'created_at',
                render: (row) => <span className="text-sm text-gray-700">{row.created_at ? new Date(row.created_at).toLocaleString() : '-'}</span>,
                mobileHidden: true,
              },
            ]}
          />
        )}
      </div>
      <RouteDetailsModal
        isOpen={isDetailsOpen}
        onClose={() => setIsDetailsOpen(false)}
        title="Transaction Details"
        routePath={selectedId ? `/analytics/transactions/${encodeURIComponent(selectedId)}` : null}
        headerTitle="Transaction Details"
        headerSubtitle={selectedId ?? undefined}
      />
    </div>
  );
};

export default TransactionsList;
