import React, { useEffect, useMemo, useState } from 'react';
import { AlertCircle, Braces, Search } from 'lucide-react';
import { payloadsService, type UiPayload } from '../../services/payloadsService';
import { ResponsiveTable } from '../ui/ResponsiveTable';
import RouteDetailsModal from '../common/RouteDetailsModal';

const statusBadgeClass = (status: string): string => {
  const s = status.toLowerCase();
  if (s.includes('success')) return 'bg-green-100 text-green-700';
  if (s.includes('failed')) return 'bg-red-100 text-red-700';
  if (s.includes('pending')) return 'bg-amber-100 text-amber-700';
  return 'bg-gray-100 text-gray-700';
};

const shortId = (id: string): string => {
  if (!id) return '-';
  if (id.length <= 12) return id;
  return `${id.slice(0, 8)}...${id.slice(-4)}`;
};

const PayloadsList: React.FC = () => {
  const [rows, setRows] = useState<UiPayload[]>([]);
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
        const list = await payloadsService.list({ limit: 100, offset: 0 });
        setRows(list);
      } catch (err: unknown) {
        setError(err instanceof Error ? err.message : 'Failed to load payloads');
      } finally {
        setLoading(false);
      }
    };
    void load();
  }, []);

  const filtered = useMemo(() => {
    const q = searchTerm.trim().toLowerCase();
    if (!q) return rows;
    return rows.filter((r) => `${r.id} ${r.type}`.toLowerCase().includes(q));
  }, [rows, searchTerm]);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Payloads</h1>
        <p className="text-sm text-gray-600 mt-1">Read-only payload records</p>
      </div>

      <div className="relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={18} />
        <input
          type="text"
          placeholder="Search by id or type..."
          className="w-full pl-10 pr-4 py-2 bg-white border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
        />
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg flex items-center gap-2">
          <AlertCircle size={18} />
          <span>{error}</span>
        </div>
      )}

      {loading ? (
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600" />
        </div>
      ) : (
        <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
          {filtered.length === 0 ? (
            <div className="p-12 text-center">
              <Braces size={48} className="mx-auto text-gray-300 mb-4" />
              <p className="text-gray-600">No payloads found</p>
            </div>
          ) : (
            <ResponsiveTable
              data={filtered}
              keyExtractor={(row) => row.id}
              columns={[
                {
                  key: 'id',
                  header: 'id',
                  render: (row) => (
                    <button
                      type="button"
                      onClick={() => {
                        setSelectedId(row.id);
                        setIsDetailsOpen(true);
                      }}
                      className="text-sm font-medium text-blue-600 hover:underline"
                    >
                      {shortId(row.id)}
                    </button>
                  ),
                },
                {
                  key: 'type',
                  header: 'type',
                  render: (row) => <span className="text-sm text-gray-700">{row.type || '—'}</span>,
                },
                {
                  key: 'status',
                  header: 'status',
                  render: (row) => (
                    <span className={`inline-flex px-2 py-0.5 rounded-full text-xs font-medium ${statusBadgeClass(row.status)}`}>
                      {row.status || '—'}
                    </span>
                  ),
                },
                {
                  key: 'created_at',
                  header: 'created_at',
                  render: (row) => <span className="text-sm text-gray-700">{row.created_at ? new Date(row.created_at).toLocaleString() : '—'}</span>,
                },
              ]}
            />
          )}
        </div>
      )}
      <RouteDetailsModal
        isOpen={isDetailsOpen}
        onClose={() => setIsDetailsOpen(false)}
        title="Payload Details"
        routePath={selectedId ? `/fleet/payloads/${encodeURIComponent(selectedId)}` : null}
        headerTitle="Payload Details"
        headerSubtitle={selectedId ?? undefined}
      />
    </div>
  );
};

export default PayloadsList;
