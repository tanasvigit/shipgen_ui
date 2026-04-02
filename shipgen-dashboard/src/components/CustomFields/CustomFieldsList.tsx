import React, { useEffect, useMemo, useState } from 'react';
import { AlertCircle, Edit, Plus, Search, Trash2, ListChecks } from 'lucide-react';
import { customFieldsService, type UiCustomField } from '../../services/customFieldsService';
import { ResponsiveTable } from '../ui/ResponsiveTable';
import { useToast } from '../ui/ToastProvider';
import Modal from '../common/Modal';
import CustomFieldForm from './forms/CustomFieldForm';

const CustomFieldsList: React.FC = () => {
  const { showToast } = useToast();
  const [rows, setRows] = useState<UiCustomField[]>([]);
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
      const list = await customFieldsService.list({ limit: 100, offset: 0 });
      setRows(list);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to load custom fields');
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
    return rows.filter((r) => r.name.toLowerCase().includes(q));
  }, [rows, searchTerm]);

  const onDelete = async (id: string) => {
    if (!window.confirm('Delete this custom field?')) return;
    try {
      setError(null);
      await customFieldsService.remove(id);
      setRows((prev) => prev.filter((r) => r.id !== id));
      showToast('Custom field deleted', 'success');
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to delete custom field');
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Custom Fields</h1>
          <p className="text-sm text-gray-600 mt-1">Manage custom fields</p>
        </div>
        <button
          type="button"
          onClick={() => setIsCreateOpen(true)}
          className="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
        >
          <Plus size={16} />
          <span>Create Custom Field</span>
        </button>
      </div>

      <div className="relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={18} />
        <input
          type="text"
          placeholder="Search custom fields by name..."
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
              <ListChecks size={48} className="mx-auto text-gray-300 mb-4" />
              <p className="text-gray-600">No custom fields found</p>
            </div>
          ) : (
            <ResponsiveTable
              data={filtered}
              keyExtractor={(row) => row.id}
              columns={[
                {
                  key: 'name',
                  header: 'name',
                  render: (row) => <span className="text-sm font-medium text-gray-900 table-cell-ellipsis block" title={row.name || '—'}>{row.name || '—'}</span>,
                },
                {
                  key: 'type',
                  header: 'type',
                  render: (row) => <span className="text-sm text-gray-700">{row.type || '—'}</span>,
                },
                {
                  key: 'entity',
                  header: 'entity',
                  render: (row) => <span className="text-sm text-gray-700">{row.entity || '—'}</span>,
                },
                {
                  key: 'required',
                  header: 'required',
                  render: (row) => <span className="text-sm text-gray-700">{row.required ? 'Yes' : 'No'}</span>,
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
                        onClick={(e) => {
                          e.stopPropagation();
                          void onDelete(row.id);
                        }}
                        className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition"
                      >
                        <Trash2 size={16} />
                      </button>
                    </div>
                  ),
                },
              ]}
            />
          )}
        </div>
      )}
      <Modal isOpen={isCreateOpen} onClose={() => setIsCreateOpen(false)} title="Create Custom Field">
        <CustomFieldForm
          mode="create"
          onCancel={() => setIsCreateOpen(false)}
          onSuccess={async () => {
            setIsCreateOpen(false);
            showToast('Custom field created successfully', 'success');
            await load();
          }}
        />
      </Modal>
      <Modal isOpen={isEditOpen} onClose={() => setIsEditOpen(false)} title="Edit Custom Field">
        <CustomFieldForm
          mode="edit"
          customFieldId={selectedId ?? undefined}
          onCancel={() => setIsEditOpen(false)}
          onSuccess={async () => {
            setIsEditOpen(false);
            setSelectedId(null);
            showToast('Custom field updated successfully', 'success');
            await load();
          }}
        />
      </Modal>
    </div>
  );
};

export default CustomFieldsList;
