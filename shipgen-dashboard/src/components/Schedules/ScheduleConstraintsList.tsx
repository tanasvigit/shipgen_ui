import React, { useEffect, useMemo, useState } from 'react';
import { AlertCircle, Edit, Scale, Search, Trash2 } from 'lucide-react';
import { scheduleConstraintsService, type UiScheduleConstraint } from '../../services/scheduleConstraintsService';
import { useToast } from '../ui/ToastProvider';
import Modal from '../common/Modal';
import ScheduleConstraintForm from './forms/ScheduleConstraintForm';

const ScheduleConstraintsList: React.FC = () => {
  const { showToast } = useToast();
  const [rows, setRows] = useState<UiScheduleConstraint[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [isCreateOpen, setIsCreateOpen] = useState(false);
  const [isEditOpen, setIsEditOpen] = useState(false);
  const [selectedId, setSelectedId] = useState<string | null>(null);

  const load = async () => {
    try {
      setLoading(true);
      setError(null);
      const list = await scheduleConstraintsService.list({ limit: 100, offset: 0 });
      setRows(list);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to load schedule constraints');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    void load();
  }, []);

  const filtered = useMemo(() => {
    const q = searchTerm.trim().toLowerCase();
    if (!q) return rows;
    return rows.filter(
      (r) => r.schedule_id.toLowerCase().includes(q) || r.type.toLowerCase().includes(q),
    );
  }, [rows, searchTerm]);

  const onDelete = async (id: string) => {
    if (!window.confirm('Delete this schedule constraint?')) return;
    try {
      setError(null);
      await scheduleConstraintsService.remove(id);
      setRows((prev) => prev.filter((r) => r.id !== id));
      showToast('Schedule constraint deleted', 'success');
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to delete schedule constraint');
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Schedule Constraints</h1>
          <p className="text-sm text-gray-600 mt-1">Basic constraint records</p>
        </div>
        <button type="button" onClick={() => setIsCreateOpen(true)} className="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition">
          <span>Create Constraint</span>
        </button>
      </div>

      <div className="relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={18} />
        <input
          type="text"
          placeholder="Search by schedule_id or type..."
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
              <Scale size={48} className="mx-auto text-gray-300 mb-4" />
              <p className="text-gray-600">No schedule constraints found</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full table-fixed">
                <thead className="bg-gray-50 border-b border-gray-200">
                  <tr>
                    <th className="text-left py-3 px-4 text-xs font-semibold text-gray-600 uppercase">schedule_id</th>
                    <th className="text-left py-3 px-4 text-xs font-semibold text-gray-600 uppercase">type</th>
                    <th className="text-left py-3 px-4 text-xs font-semibold text-gray-600 uppercase">value</th>
                    <th className="text-left py-3 px-4 text-xs font-semibold text-gray-600 uppercase">status</th>
                    <th className="text-left py-3 px-4 text-xs font-semibold text-gray-600 uppercase">created_at</th>
                    <th className="text-right py-3 px-4 text-xs font-semibold text-gray-600 uppercase">actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-100">
                  {filtered.map((row) => (
                    <tr key={row.id} className="table-row table-row-zebra">
                      <td className="py-3 px-4 text-sm font-medium text-gray-900">{row.schedule_id || '—'}</td>
                      <td className="py-3 px-4 text-sm text-gray-700">{row.type || '—'}</td>
                      <td className="py-3 px-4 text-sm text-gray-700">{row.value || '—'}</td>
                      <td className="py-3 px-4 text-sm text-gray-700">{row.status || '—'}</td>
                      <td className="py-3 px-4 text-sm text-gray-700">{row.created_at ? new Date(row.created_at).toLocaleString() : '—'}</td>
                      <td className="py-3 px-4 text-right">
                        <div className="inline-flex items-center gap-2">
                          <button
                            type="button"
                            onClick={() => {
                              setSelectedId(row.id);
                              setIsEditOpen(true);
                            }}
                            className="p-2 text-blue-600 hover:bg-blue-50 rounded-lg transition"
                          >
                            <Edit size={16} />
                          </button>
                          <button
                            type="button"
                            onClick={() => onDelete(row.id)}
                            className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition"
                          >
                            <Trash2 size={16} />
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
      <Modal isOpen={isCreateOpen} onClose={() => setIsCreateOpen(false)} title="Create Schedule Constraint">
        <ScheduleConstraintForm mode="create" onCancel={() => setIsCreateOpen(false)} onSuccess={async () => {
          setIsCreateOpen(false);
          await load();
        }} />
      </Modal>
      <Modal isOpen={isEditOpen} onClose={() => setIsEditOpen(false)} title="Edit Schedule Constraint">
        <ScheduleConstraintForm mode="edit" constraintId={selectedId ?? undefined} onCancel={() => setIsEditOpen(false)} onSuccess={async () => {
          setIsEditOpen(false);
          setSelectedId(null);
          await load();
        }} />
      </Modal>
    </div>
  );
};

export default ScheduleConstraintsList;
