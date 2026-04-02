import React, { useCallback, useMemo, useState } from 'react';
import { Boxes, Edit, Trash2 } from 'lucide-react';
import Modal from '../common/Modal';
import EntityForm from './forms/EntityForm';
import { entitiesService, type UiEntity } from '../../services/entitiesService';
import { ResponsiveTable } from '../ui/ResponsiveTable';
import useListWithCrud from '../../hooks/useListWithCrud';
import { StandardCrudListLayout } from '../patterns/StandardCrudListLayout';
import { PH } from '../../constants/formPlaceholders';

const EntitiesList: React.FC = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [isCreateOpen, setIsCreateOpen] = useState(false);
  const [isEditOpen, setIsEditOpen] = useState(false);
  const [selectedId, setSelectedId] = useState<string | null>(null);

  const load = useCallback(() => entitiesService.list({ limit: 100, offset: 0 }), []);
  const { rows, loading, error, actionError, deleteWithConfirm, reload } = useListWithCrud<UiEntity>(load, [load]);

  const filtered = useMemo(() => {
    const q = searchTerm.trim().toLowerCase();
    if (!q) return rows;
    return rows.filter((r) => r.name.toLowerCase().includes(q));
  }, [rows, searchTerm]);

  return (
    <StandardCrudListLayout
      title="Entities"
      subtitle="Fleet entities"
      createOnClick={() => setIsCreateOpen(true)}
      createLabel="Create Entity"
      searchPlaceholder={PH.searchEntities}
      searchTerm={searchTerm}
      onSearchChange={setSearchTerm}
      error={error}
      actionError={actionError}
      loading={loading}
      rowCount={rows.length}
      filteredCount={filtered.length}
      emptyIcon={Boxes}
      emptyTitleNoData="No entities yet"
      emptyTitleNoMatch="No matching entities"
      emptyDescriptionNoData="Create an entity to model business units in fleet operations."
      emptyDescriptionNoMatch="Try a different search or clear the filter."
      emptyAction={<button type="button" onClick={() => setIsCreateOpen(true)} className="inline-flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2 text-sm text-white hover:bg-blue-700">Create entity</button>}
      noMatchAction={
        <button
          type="button"
          onClick={() => setSearchTerm('')}
          className="rounded-lg border border-gray-200 px-4 py-2 text-sm hover:bg-gray-50"
        >
          Clear search
        </button>
      }
      failedLoadTitle="Could not load entities"
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
                    void deleteWithConfirm(row.id, (id) => entitiesService.remove(id), {
                      confirmMessage: 'Delete this entity?',
                      successMessage: 'Entity deleted',
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
      <Modal isOpen={isCreateOpen} onClose={() => setIsCreateOpen(false)} title="Create Entity">
        <EntityForm mode="create" onCancel={() => setIsCreateOpen(false)} onSuccess={async () => {
          setIsCreateOpen(false);
          await reload();
        }} />
      </Modal>
      <Modal isOpen={isEditOpen} onClose={() => setIsEditOpen(false)} title="Edit Entity">
        <EntityForm mode="edit" entityId={selectedId ?? undefined} onCancel={() => setIsEditOpen(false)} onSuccess={async () => {
          setIsEditOpen(false);
          setSelectedId(null);
          await reload();
        }} />
      </Modal>
    </StandardCrudListLayout>
  );
};

export default EntitiesList;
