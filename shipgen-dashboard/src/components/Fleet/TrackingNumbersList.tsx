import React, { useCallback, useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
import { Edit, Hash, Trash2 } from 'lucide-react';
import { trackingNumbersService, type UiTrackingNumber } from '../../services/trackingNumbersService';
import EntityLink from '../common/EntityLink';
import { ResponsiveTable } from '../ui/ResponsiveTable';
import useListWithCrud from '../../hooks/useListWithCrud';
import { StandardCrudListLayout } from '../patterns/StandardCrudListLayout';
import { PH } from '../../constants/formPlaceholders';
import Modal from '../common/Modal';
import TrackingNumberForm from './forms/TrackingNumberForm';
import { useToast } from '../ui/ToastProvider';

const TrackingNumbersList: React.FC = () => {
  const { showToast } = useToast();
  const [searchTerm, setSearchTerm] = useState('');
  const [isCreateOpen, setIsCreateOpen] = useState(false);
  const [isEditOpen, setIsEditOpen] = useState(false);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const load = useCallback(() => trackingNumbersService.list({ limit: 100, offset: 0 }), []);
  const { rows, loading, error, actionError, deleteWithConfirm, reload } = useListWithCrud<UiTrackingNumber>(load, [load]);

  const filtered = useMemo(() => {
    const q = searchTerm.trim().toLowerCase();
    if (!q) return rows;
    return rows.filter((r) => r.tracking_number.toLowerCase().includes(q));
  }, [rows, searchTerm]);

  return (
    <StandardCrudListLayout
      title="Tracking Numbers"
      subtitle="Tracking number records"
      createOnClick={() => setIsCreateOpen(true)}
      createLabel="Create Tracking Number"
      searchPlaceholder={PH.searchTrackingNumbers}
      searchTerm={searchTerm}
      onSearchChange={setSearchTerm}
      error={error}
      actionError={actionError}
      loading={loading}
      rowCount={rows.length}
      filteredCount={filtered.length}
      emptyIcon={Hash}
      emptyTitleNoData="No tracking numbers yet"
      emptyTitleNoMatch="No matching tracking numbers"
      emptyDescriptionNoData="Create tracking numbers to link with orders."
      emptyDescriptionNoMatch="Try another search."
      emptyAction={
        <button
          type="button"
          onClick={() => setIsCreateOpen(true)}
          className="inline-flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2 text-sm text-white hover:bg-blue-700"
        >
          Create tracking number
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
      failedLoadTitle="Could not load tracking numbers"
    >
      <ResponsiveTable
        data={filtered}
        keyExtractor={(row) => row.id}
        columns={[
          {
            key: 'tracking_number',
            header: 'tracking_number',
            render: (row) => (
              <span className="table-cell-ellipsis block text-sm font-medium text-gray-900" title={row.tracking_number || '—'}>
                {row.tracking_number || '—'}
              </span>
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
            render: (row) => <span className="text-sm text-gray-700">{row.status || '—'}</span>,
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
            key: 'related_order',
            header: 'related_order',
            render: (row) => (
              <EntityLink
                id={row.related_order_id}
                label={row.related_order_id}
                to="/logistics/orders"
                title="View Related Order"
              />
            ),
            mobileHidden: true,
          },
          {
            key: 'actions',
            header: 'actions',
            render: (row) => (
              <div className="inline-flex items-center justify-end gap-2">
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
                  onClick={() =>
                    void deleteWithConfirm(row.id, (id) => trackingNumbersService.remove(id), {
                      confirmMessage: 'Delete this tracking number?',
                      successMessage: 'Tracking number deleted',
                    })
                  }
                  className="rounded-lg p-2 text-red-600 transition hover:bg-red-50"
                >
                  <Trash2 size={16} />
                </button>
              </div>
            ),
          },
        ]}
      />
      <Modal isOpen={isCreateOpen} onClose={() => setIsCreateOpen(false)} title="Create Tracking Number">
        <TrackingNumberForm
          mode="create"
          onCancel={() => setIsCreateOpen(false)}
          onSuccess={async () => {
            setIsCreateOpen(false);
            showToast('Tracking number created', 'success');
            await reload();
          }}
        />
      </Modal>
      <Modal isOpen={isEditOpen} onClose={() => setIsEditOpen(false)} title="Edit Tracking Number">
        <TrackingNumberForm
          mode="edit"
          trackingNumberId={selectedId ?? undefined}
          onCancel={() => setIsEditOpen(false)}
          onSuccess={async () => {
            setIsEditOpen(false);
            setSelectedId(null);
            showToast('Tracking number updated', 'success');
            await reload();
          }}
        />
      </Modal>
    </StandardCrudListLayout>
  );
};

export default TrackingNumbersList;
