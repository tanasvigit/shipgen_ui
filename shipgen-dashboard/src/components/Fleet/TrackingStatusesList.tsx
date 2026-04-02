import React, { useCallback, useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
import { Edit, Tag, Trash2 } from 'lucide-react';
import { trackingStatusesService, type UiTrackingStatus } from '../../services/trackingStatusesService';
import { ResponsiveTable } from '../ui/ResponsiveTable';
import useListWithCrud from '../../hooks/useListWithCrud';
import { StandardCrudListLayout } from '../patterns/StandardCrudListLayout';
import { PH } from '../../constants/formPlaceholders';
import Modal from '../common/Modal';
import TrackingStatusForm from './forms/TrackingStatusForm';
import { useToast } from '../ui/ToastProvider';

const TrackingStatusesList: React.FC = () => {
  const { showToast } = useToast();
  const [searchTerm, setSearchTerm] = useState('');
  const [isCreateOpen, setIsCreateOpen] = useState(false);
  const [isEditOpen, setIsEditOpen] = useState(false);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const load = useCallback(() => trackingStatusesService.list({ limit: 100, offset: 0 }), []);
  const { rows, loading, error, actionError, deleteWithConfirm, reload } = useListWithCrud<UiTrackingStatus>(load, [load]);

  const filtered = useMemo(() => {
    const q = searchTerm.trim().toLowerCase();
    if (!q) return rows;
    return rows.filter((r) => r.name.toLowerCase().includes(q));
  }, [rows, searchTerm]);

  return (
    <StandardCrudListLayout
      title="Tracking Statuses"
      subtitle="Tracking status list"
      createOnClick={() => setIsCreateOpen(true)}
      createLabel="Create Status"
      searchPlaceholder={PH.searchTrackingStatuses}
      searchTerm={searchTerm}
      onSearchChange={setSearchTerm}
      error={error}
      actionError={actionError}
      loading={loading}
      rowCount={rows.length}
      filteredCount={filtered.length}
      emptyIcon={Tag}
      emptyTitleNoData="No tracking statuses yet"
      emptyTitleNoMatch="No matching statuses"
      emptyDescriptionNoData="Define statuses used for tracking."
      emptyDescriptionNoMatch="Try a different search term."
      emptyAction={
        <button
          type="button"
          onClick={() => setIsCreateOpen(true)}
          className="inline-flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2 text-sm text-white hover:bg-blue-700"
        >
          Create status
        </button>
      }
      noMatchAction={
        <button
          type="button"
          onClick={() => setSearchTerm('')}
          className="rounded-lg border border-gray-200 px-4 py-2 text-sm hover:bg-gray-50"
        >
          Clear search
        </button>
      }
      failedLoadTitle="Could not load tracking statuses"
    >
      <ResponsiveTable
        data={filtered}
        keyExtractor={(row) => row.id}
        columns={[
          {
            key: 'name',
            header: 'name/status',
            render: (row) => <span className="text-sm font-medium text-gray-900">{row.name || '—'}</span>,
          },
          {
            key: 'description',
            header: 'description',
            render: (row) => (
              <span className="table-cell-ellipsis block text-sm text-gray-700" title={row.description || '—'}>
                {row.description || '—'}
              </span>
            ),
          },
          {
            key: 'created_at',
            header: 'created_at',
            render: (row) => (
              <span className="text-sm text-gray-700">
                {row.created_at ? new Date(row.created_at).toLocaleString() : '—'}
              </span>
            ),
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
                  className="rounded-lg p-2 text-blue-600 transition hover:bg-blue-50"
                >
                  <Edit size={16} />
                </button>
                <button
                  type="button"
                  onClick={(e) => {
                    e.stopPropagation();
                    void deleteWithConfirm(row.id, (id) => trackingStatusesService.remove(id), {
                      confirmMessage: 'Delete this tracking status?',
                      successMessage: 'Tracking status deleted',
                    });
                  }}
                  className="rounded-lg p-2 text-red-600 transition hover:bg-red-50"
                >
                  <Trash2 size={16} />
                </button>
              </div>
            ),
          },
        ]}
      />
      <Modal isOpen={isCreateOpen} onClose={() => setIsCreateOpen(false)} title="Create Tracking Status">
        <TrackingStatusForm
          mode="create"
          onCancel={() => setIsCreateOpen(false)}
          onSuccess={async () => {
            setIsCreateOpen(false);
            showToast('Tracking status created', 'success');
            await reload();
          }}
        />
      </Modal>
      <Modal isOpen={isEditOpen} onClose={() => setIsEditOpen(false)} title="Edit Tracking Status">
        <TrackingStatusForm
          mode="edit"
          trackingStatusId={selectedId ?? undefined}
          onCancel={() => setIsEditOpen(false)}
          onSuccess={async () => {
            setIsEditOpen(false);
            setSelectedId(null);
            showToast('Tracking status updated', 'success');
            await reload();
          }}
        />
      </Modal>
    </StandardCrudListLayout>
  );
};

export default TrackingStatusesList;
