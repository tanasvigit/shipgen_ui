import React, { useCallback, useMemo, useState } from 'react';
import { Edit, Truck, Trash2 } from 'lucide-react';
import Modal from '../common/Modal';
import FleetForm from './forms/FleetForm';
import { fleetsService, type UiFleet } from '../../services/fleetsService';
import { ResponsiveTable } from '../ui/ResponsiveTable';
import useListWithCrud from '../../hooks/useListWithCrud';
import { StandardCrudListLayout } from '../patterns/StandardCrudListLayout';
import { PH } from '../../constants/formPlaceholders';

const FleetsList: React.FC = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [isCreateOpen, setIsCreateOpen] = useState(false);
  const [isEditOpen, setIsEditOpen] = useState(false);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const load = useCallback(() => fleetsService.list({ limit: 100, offset: 0 }), []);
  const { rows, loading, error, actionError, deleteWithConfirm, reload } = useListWithCrud<UiFleet>(load, [load]);

  const filtered = useMemo(() => {
    const q = searchTerm.trim().toLowerCase();
    if (!q) return rows;
    return rows.filter((r) => r.name.toLowerCase().includes(q));
  }, [rows, searchTerm]);

  return (
    <StandardCrudListLayout
      title="Fleets"
      subtitle="Fleet groups"
      createOnClick={() => setIsCreateOpen(true)}
      createLabel="Create Fleet"
      searchPlaceholder={PH.searchFleets}
      searchTerm={searchTerm}
      onSearchChange={setSearchTerm}
      error={error}
      actionError={actionError}
      loading={loading}
      rowCount={rows.length}
      filteredCount={filtered.length}
      emptyIcon={Truck}
      emptyTitleNoData="No fleets yet"
      emptyTitleNoMatch="No matching fleets"
      emptyDescriptionNoData="Create a fleet to group vehicles and operations."
      emptyDescriptionNoMatch="Try a different search term or clear the filter."
      emptyAction={<button type="button" data-testid="fleets-empty-create" onClick={() => setIsCreateOpen(true)} className="inline-flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2 text-sm text-white hover:bg-blue-700">Create fleet</button>}
      noMatchAction={
        <button
          type="button"
          onClick={() => setSearchTerm('')}
          className="rounded-lg border border-gray-200 px-4 py-2 text-sm hover:bg-gray-50"
        >
          Clear search
        </button>
      }
      failedLoadTitle="Could not load fleets"
    >
      <ResponsiveTable
        data={filtered}
        keyExtractor={(row) => row.id}
        columns={[
          {
            key: 'name',
            header: 'name',
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
                  data-testid={`fleet-edit-${row.id}`}
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
                  data-testid={`fleet-delete-${row.id}`}
                  aria-label={`Delete fleet ${row.name}`}
                  onClick={(e) => {
                    e.stopPropagation();
                    void deleteWithConfirm(row.id, (id) => fleetsService.remove(id), {
                      confirmMessage: 'Delete this fleet?',
                      successMessage: 'Fleet deleted',
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
      <Modal isOpen={isCreateOpen} onClose={() => setIsCreateOpen(false)} title="Create Fleet">
        <FleetForm mode="create" onCancel={() => setIsCreateOpen(false)} onSuccess={async () => {
          setIsCreateOpen(false);
          await reload();
        }} />
      </Modal>
      <Modal isOpen={isEditOpen} onClose={() => setIsEditOpen(false)} title="Edit Fleet">
        <FleetForm mode="edit" fleetId={selectedId ?? undefined} onCancel={() => setIsEditOpen(false)} onSuccess={async () => {
          setIsEditOpen(false);
          setSelectedId(null);
          await reload();
        }} />
      </Modal>
    </StandardCrudListLayout>
  );
};

export default FleetsList;
