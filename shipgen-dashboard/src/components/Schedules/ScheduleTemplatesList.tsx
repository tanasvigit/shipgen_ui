import React, { useCallback, useMemo, useState } from 'react';
import { Edit, FileText, Trash2 } from 'lucide-react';
import { scheduleTemplatesService, type UiScheduleTemplate } from '../../services/scheduleTemplatesService';
import { ResponsiveTable } from '../ui/ResponsiveTable';
import useListWithCrud from '../../hooks/useListWithCrud';
import { StandardCrudListLayout } from '../patterns/StandardCrudListLayout';
import { PH } from '../../constants/formPlaceholders';
import Modal from '../common/Modal';
import ScheduleTemplateForm from './forms/ScheduleTemplateForm';

const ScheduleTemplatesList: React.FC = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [isCreateOpen, setIsCreateOpen] = useState(false);
  const [isEditOpen, setIsEditOpen] = useState(false);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const load = useCallback(() => scheduleTemplatesService.list({ limit: 100, offset: 0 }), []);
  const { rows, loading, error, actionError, deleteWithConfirm, reload } = useListWithCrud<UiScheduleTemplate>(load, [load]);

  const filtered = useMemo(() => {
    const q = searchTerm.trim().toLowerCase();
    if (!q) return rows;
    return rows.filter((r) => r.name.toLowerCase().includes(q));
  }, [rows, searchTerm]);

  return (
    <StandardCrudListLayout
      title="Schedule Templates"
      subtitle="Basic template records"
      createOnClick={() => setIsCreateOpen(true)}
      createLabel="Create Template"
      searchPlaceholder={PH.searchTemplates}
      searchTerm={searchTerm}
      onSearchChange={setSearchTerm}
      error={error}
      actionError={actionError}
      loading={loading}
      rowCount={rows.length}
      filteredCount={filtered.length}
      emptyIcon={FileText}
      emptyTitleNoData="No schedule templates yet"
      emptyTitleNoMatch="No matching templates"
      emptyDescriptionNoData="Create a template to reuse scheduling patterns."
      emptyDescriptionNoMatch="Try a different search or clear the filter."
      emptyAction={<button type="button" onClick={() => setIsCreateOpen(true)} className="inline-flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2 text-sm text-white hover:bg-blue-700">Create template</button>}
      noMatchAction={
        <button
          type="button"
          onClick={() => setSearchTerm('')}
          className="rounded-lg border border-gray-200 px-4 py-2 text-sm hover:bg-gray-50"
        >
          Clear search
        </button>
      }
      failedLoadTitle="Could not load schedule templates"
    >
      <ResponsiveTable
        data={filtered}
        keyExtractor={(row) => row.id}
        columns={[
          {
            key: 'name',
            header: 'name',
            render: (row) => (
              <span className="table-cell-ellipsis block text-sm font-medium text-gray-900" title={row.name || '—'}>
                {row.name || '—'}
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
                    void deleteWithConfirm(row.id, (id) => scheduleTemplatesService.remove(id), {
                      confirmMessage: 'Delete this schedule template?',
                      successMessage: 'Schedule template deleted',
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
      <Modal isOpen={isCreateOpen} onClose={() => setIsCreateOpen(false)} title="Create Schedule Template">
        <ScheduleTemplateForm mode="create" onCancel={() => setIsCreateOpen(false)} onSuccess={async () => {
          setIsCreateOpen(false);
          await reload();
        }} />
      </Modal>
      <Modal isOpen={isEditOpen} onClose={() => setIsEditOpen(false)} title="Edit Schedule Template">
        <ScheduleTemplateForm mode="edit" templateId={selectedId ?? undefined} onCancel={() => setIsEditOpen(false)} onSuccess={async () => {
          setIsEditOpen(false);
          setSelectedId(null);
          await reload();
        }} />
      </Modal>
    </StandardCrudListLayout>
  );
};

export default ScheduleTemplatesList;
