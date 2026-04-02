import React, { useEffect, useMemo, useState } from 'react';
import { AlertCircle, Search, Activity, Trash2 } from 'lucide-react';
import { apiEventsService, type UiApiEvent } from '../../services/apiEventsService';
import { ResponsiveTable } from '../ui/ResponsiveTable';
import RouteDetailsModal from '../common/RouteDetailsModal';

const methodBadgeClass = (method: string): string => {
  const m = method.toUpperCase();
  if (m === 'GET') return 'bg-blue-100 text-blue-700';
  if (m === 'POST') return 'bg-green-100 text-green-700';
  if (m === 'PATCH') return 'bg-amber-100 text-amber-700';
  if (m === 'DELETE') return 'bg-red-100 text-red-700';
  return 'bg-gray-100 text-gray-700';
};

const statusBadgeClass = (statusCode: number | null): string => {
  if (!statusCode) return 'bg-gray-100 text-gray-700';
  if (statusCode >= 200 && statusCode < 300) return 'bg-green-100 text-green-700';
  if (statusCode >= 400 && statusCode < 500) return 'bg-amber-100 text-amber-700';
  if (statusCode >= 500) return 'bg-red-100 text-red-700';
  return 'bg-gray-100 text-gray-700';
};

const ApiEventsList: React.FC = () => {
  const [rows, setRows] = useState<UiApiEvent[]>([]);
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [isDetailsOpen, setIsDetailsOpen] = useState(false);

  const load = async () => {
    try {
      setLoading(true);
      setError(null);
      const list = await apiEventsService.list({ limit: 100, offset: 0 });
      setRows(list);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to load API events');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, []);

  const filtered = useMemo(() => {
    const q = searchTerm.trim().toLowerCase();
    if (!q) return rows;
    return rows.filter((r) => `${r.event} ${r.endpoint}`.toLowerCase().includes(q));
  }, [rows, searchTerm]);

  const onDelete = async (id: string) => {
    if (!window.confirm('Delete this API event?')) return;
    try {
      setBusy(true);
      setError(null);
      await apiEventsService.remove(id);
      setRows((prev) => prev.filter((r) => r.id !== id));
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to delete API event');
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">API Events</h1>
        <p className="text-sm text-gray-600 mt-1">API event logs (read-only)</p>
      </div>

      <div className="relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={18} />
        <input
          type="text"
          placeholder="Search by endpoint or event..."
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
              <Activity size={48} className="mx-auto text-gray-300 mb-4" />
              <p className="text-gray-600">No API events found</p>
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
                  key: 'event',
                  header: 'event/type',
                  render: (row) => <span className="text-sm text-gray-700">{row.event || '—'}</span>,
                },
                {
                  key: 'method',
                  header: 'method',
                  render: (row) => (
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${methodBadgeClass(row.request_method)}`}>
                      {(row.request_method || '—').toUpperCase()}
                    </span>
                  ),
                },
                {
                  key: 'endpoint',
                  header: 'endpoint',
                  render: (row) => <span className="text-sm text-gray-700 table-cell-ellipsis block" title={row.endpoint || '—'}>{row.endpoint || '—'}</span>,
                },
                {
                  key: 'status_code',
                  header: 'status_code',
                  render: (row) => (
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${statusBadgeClass(row.status_code)}`}>
                      {row.status_code ?? '—'}
                    </span>
                  ),
                },
                {
                  key: 'created_at',
                  header: 'created_at',
                  render: (row) => <span className="text-sm text-gray-700">{row.created_at ? new Date(row.created_at).toLocaleString() : '—'}</span>,
                  mobileHidden: true,
                },
                {
                  key: 'actions',
                  header: 'actions',
                  render: (row) => (
                    <button
                      type="button"
                      onClick={(e) => {
                        e.stopPropagation();
                        void onDelete(row.id);
                      }}
                      disabled={busy}
                      className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition disabled:opacity-50"
                      title="Delete"
                    >
                      <Trash2 size={16} />
                    </button>
                  ),
                },
              ]}
            />
          )}
        </div>
      )}
      <RouteDetailsModal
        isOpen={isDetailsOpen}
        onClose={() => setIsDetailsOpen(false)}
        title="API Event Details"
        routePath={selectedId ? `/analytics/api-events/${encodeURIComponent(selectedId)}` : null}
        headerTitle="API Event Details"
        headerSubtitle={selectedId ?? undefined}
      />
    </div>
  );
};

export default ApiEventsList;
