import React, { useEffect, useMemo, useState } from 'react';
import { AlertCircle, FileText, Search } from 'lucide-react';
import { reportsService, type UiReport } from '../../services/reportsService';
import RouteDetailsModal from '../common/RouteDetailsModal';

const ReportsList: React.FC = () => {
  const [reports, setReports] = useState<UiReport[]>([]);
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
        const rows = await reportsService.list({ limit: 100, offset: 0 });
        setReports(rows);
      } catch (err: unknown) {
        setError(err instanceof Error ? err.message : 'Failed to load reports');
      } finally {
        setLoading(false);
      }
    };
    load();
  }, []);

  const filtered = useMemo(() => {
    const q = searchTerm.trim().toLowerCase();
    if (!q) return reports;
    return reports.filter((r) => r.name.toLowerCase().includes(q));
  }, [reports, searchTerm]);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Reports</h1>
        <p className="text-sm text-gray-600 mt-1">Saved reports from `/int/v1/reports`</p>
      </div>

      <div className="relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={18} />
        <input
          type="text"
          placeholder="Search reports by name..."
          className="w-full pl-10 pr-4 py-2 bg-white border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
        />
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg flex items-center space-x-2">
          <AlertCircle size={20} />
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
              <FileText size={48} className="mx-auto text-gray-300 mb-4" />
              <p className="text-gray-600">No reports found</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50 border-b border-gray-200">
                  <tr>
                    <th className="text-left py-3 px-4 text-xs font-semibold text-gray-600 uppercase">name</th>
                    <th className="text-left py-3 px-4 text-xs font-semibold text-gray-600 uppercase">description</th>
                    <th className="text-left py-3 px-4 text-xs font-semibold text-gray-600 uppercase">created_at</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-100">
                  {filtered.map((report) => (
                    <tr
                      key={report.id}
                      className="hover:bg-gray-50 cursor-pointer"
                      onClick={() => {
                        setSelectedId(report.id);
                        setIsDetailsOpen(true);
                      }}
                    >
                      <td className="py-3 px-4 text-sm font-medium text-gray-900">{report.name || '—'}</td>
                      <td className="py-3 px-4 text-sm text-gray-700">{report.description || '—'}</td>
                      <td className="py-3 px-4 text-sm text-gray-700">
                        {report.created_at ? new Date(report.created_at).toLocaleString() : '—'}
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
        title="Report Details"
        routePath={selectedId ? `/analytics/reports/${encodeURIComponent(selectedId)}` : null}
        headerTitle="Report Details"
        headerSubtitle={selectedId ?? undefined}
      />
    </div>
  );
};

export default ReportsList;
