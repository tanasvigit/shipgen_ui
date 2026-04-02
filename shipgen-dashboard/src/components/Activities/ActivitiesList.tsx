import React, { useEffect, useMemo, useState } from 'react';
import { AlertCircle, Search, Activity } from 'lucide-react';
import { activitiesService, type UiActivity } from '../../services/activitiesService';
import RouteDetailsModal from '../common/RouteDetailsModal';

const badgeClass = (action: string): string => {
  const a = action.toLowerCase();
  if (a.includes('create')) return 'bg-green-100 text-green-700';
  if (a.includes('update')) return 'bg-blue-100 text-blue-700';
  if (a.includes('delete')) return 'bg-red-100 text-red-700';
  return 'bg-gray-100 text-gray-700';
};

const ActivitiesList: React.FC = () => {
  const [rows, setRows] = useState<UiActivity[]>([]);
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
        const list = await activitiesService.list({ limit: 100, offset: 0 });
        setRows(list);
      } catch (err: unknown) {
        setError(err instanceof Error ? err.message : 'Failed to load activities');
      } finally {
        setLoading(false);
      }
    };
    load();
  }, []);

  const filtered = useMemo(() => {
    const q = searchTerm.trim().toLowerCase();
    if (!q) return rows;
    return rows.filter((r) => `${r.action} ${r.description}`.toLowerCase().includes(q));
  }, [rows, searchTerm]);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Activities</h1>
        <p className="text-sm text-gray-600 mt-1">System activity logs (read-only)</p>
      </div>

      <div className="relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={18} />
        <input
          type="text"
          placeholder="Search by action or description..."
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
              <p className="text-gray-600">No activities found</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50 border-b border-gray-200">
                  <tr>
                    <th className="text-left py-3 px-4 text-xs font-semibold text-gray-600 uppercase">action/type</th>
                    <th className="text-left py-3 px-4 text-xs font-semibold text-gray-600 uppercase">description</th>
                    <th className="text-left py-3 px-4 text-xs font-semibold text-gray-600 uppercase">user</th>
                    <th className="text-left py-3 px-4 text-xs font-semibold text-gray-600 uppercase">created_at</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-100">
                  {filtered.map((row) => (
                    <tr
                      key={row.id}
                      className="hover:bg-gray-50 cursor-pointer"
                      onClick={() => {
                        setSelectedId(row.id);
                        setIsDetailsOpen(true);
                      }}
                    >
                      <td className="py-3 px-4 text-sm">
                        <span className={`px-2 py-1 rounded-full text-xs font-medium ${badgeClass(row.action)}`}>{row.action || '—'}</span>
                      </td>
                      <td className="py-3 px-4 text-sm text-gray-700">{row.description || '—'}</td>
                      <td className="py-3 px-4 text-sm text-gray-700">{row.user || '—'}</td>
                      <td className="py-3 px-4 text-sm text-gray-700">
                        {row.created_at ? new Date(row.created_at).toLocaleString() : '—'}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}
      <RouteDetailsModal
        isOpen={isDetailsOpen}
        onClose={() => setIsDetailsOpen(false)}
        title="Activity Details"
        routePath={selectedId ? `/analytics/activities/${encodeURIComponent(selectedId)}` : null}
        headerTitle="Activity Details"
        headerSubtitle={selectedId ?? undefined}
      />
    </div>
  );
};

export default ActivitiesList;
