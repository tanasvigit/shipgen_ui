import React, { useCallback, useMemo, useState } from 'react';
import { AlertTriangle, Eye, Edit, Trash2 } from 'lucide-react';
import { issuesService } from '../../services/issuesService';
import type { MockIssue } from '../../mocks/data/issues';
import { getIssueRouteId } from '../../utils/issueHelpers';
import EntityLink from '../common/EntityLink';
import { ResponsiveTable } from '../ui/ResponsiveTable';
import useListWithCrud from '../../hooks/useListWithCrud';
import { StandardCrudListLayout } from '../patterns/StandardCrudListLayout';
import { PH, SELECT_PH } from '../../constants/formPlaceholders';
import Modal from '../common/Modal';
import RouteDetailsModal from '../common/RouteDetailsModal';
import IssueForm from './forms/IssueForm';

const IssuesList: React.FC = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [typeFilter, setTypeFilter] = useState('');
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [isCreateOpen, setIsCreateOpen] = useState(false);
  const [isEditOpen, setIsEditOpen] = useState(false);
  const [isDetailsOpen, setIsDetailsOpen] = useState(false);
  const [selectedId, setSelectedId] = useState<string | null>(null);

  const load = useCallback(async () => {
    const response = await issuesService.list({ page, pageSize: 20 });
    let rows = response.data;
    if (statusFilter) rows = rows.filter((i) => i.status === statusFilter);
    if (typeFilter) rows = rows.filter((i) => i.type === typeFilter);
    setTotalPages(Math.max(1, Math.ceil((response.pagination?.total || 0) / 20)));
    return rows;
  }, [page, statusFilter, typeFilter]);

  const { rows: issues, loading, error, actionError, deleteWithConfirm, reload } = useListWithCrud<MockIssue>(load, [load]);

  const q = searchTerm.trim().toLowerCase();
  const filtered = useMemo(() => {
    return issues.filter((i) => {
      if (!q) return true;
      const blob = [i.title, i.report, i.issue_id, i.uuid, String(i.id ?? ''), i.type, i.status]
        .map((x) => (x ?? '').toString().toLowerCase())
        .join(' ');
      return blob.includes(q);
    });
  }, [issues, q]);

  return (
    <>
      <StandardCrudListLayout
        title="Issues"
        subtitle="fleetops-issues (mock: /issues)"
        createOnClick={() => setIsCreateOpen(true)}
        createLabel="New Issue"
        filters={
          <div className="flex max-w-2xl flex-col gap-4 sm:flex-row">
            <select
              value={statusFilter}
              onChange={(e) => {
                setStatusFilter(e.target.value);
                setPage(1);
              }}
              className="w-full rounded-lg border border-gray-200 bg-white px-3 py-2 outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">{SELECT_PH.status}</option>
              <option value="open">open</option>
              <option value="in_progress">in_progress</option>
              <option value="resolved">resolved</option>
            </select>
            <select
              value={typeFilter}
              onChange={(e) => {
                setTypeFilter(e.target.value);
                setPage(1);
              }}
              className="w-full rounded-lg border border-gray-200 bg-white px-3 py-2 outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">All type</option>
              <option value="breakdown">breakdown</option>
              <option value="incident">incident</option>
              <option value="documentation">documentation</option>
            </select>
          </div>
        }
        searchPlaceholder={PH.searchIssues}
        searchTerm={searchTerm}
        onSearchChange={setSearchTerm}
        error={error}
        actionError={actionError}
        loading={loading}
        rowCount={issues.length}
        filteredCount={filtered.length}
        emptyIcon={AlertTriangle}
        emptyTitleNoData="No issues yet"
        emptyTitleNoMatch="No matching issues"
        emptyDescriptionNoData="Log breakdowns, incidents, and operational issues."
        emptyDescriptionNoMatch="Adjust search or filters."
        emptyAction={
          <button
            type="button"
            onClick={() => setIsCreateOpen(true)}
            className="inline-flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2 text-sm text-white hover:bg-blue-700"
          >
            New issue
          </button>
        }
        noMatchAction={
          <button
            type="button"
            onClick={() => {
              setSearchTerm('');
              setStatusFilter('');
              setTypeFilter('');
              setPage(1);
            }}
            className="rounded-lg border border-gray-200 px-4 py-2 text-sm hover:bg-gray-50"
          >
            Clear filters
          </button>
        }
        failedLoadTitle="Could not load issues"
      >
        <ResponsiveTable
          data={filtered}
          keyExtractor={(i) => getIssueRouteId(i) || String(i.id)}
          columns={[
            { key: 'issue_id', header: 'issue_id', render: (i) => <span className="text-sm text-gray-700">{i.issue_id ?? '—'}</span> },
            {
              key: 'title',
              header: 'title',
              render: (i) => (
                <span className="table-cell-ellipsis block text-sm font-medium text-gray-900" title={i.title ?? '—'}>
                  {i.title ?? '—'}
                </span>
              ),
            },
            { key: 'type', header: 'type', render: (i) => <span className="text-sm text-gray-700">{i.type ?? '—'}</span> },
            { key: 'status', header: 'status', render: (i) => <span className="text-sm text-gray-700">{i.status ?? '—'}</span> },
            {
              key: 'priority',
              header: 'priority',
              render: (i) => <span className="text-sm text-gray-700">{i.priority ?? '—'}</span>,
              mobileHidden: true,
            },
            {
              key: 'driver_uuid',
              header: 'driver_uuid',
              render: (i) => (
                <span className="font-mono text-xs text-gray-700">
                  <EntityLink id={i.driver_uuid} label={i.driver_uuid} to="/fleet/drivers" title="View Driver" />
                </span>
              ),
              mobileHidden: true,
            },
            {
              key: 'vehicle_uuid',
              header: 'vehicle_uuid',
              render: (i) => (
                <span className="font-mono text-xs text-gray-700">
                  <EntityLink id={i.vehicle_uuid} label={i.vehicle_uuid} to="/fleet/vehicles" title="View Vehicle" />
                </span>
              ),
              mobileHidden: true,
            },
            {
              key: 'actions',
              header: 'actions',
              render: (i) => {
                const rid = getIssueRouteId(i);
                if (!rid) return <span className="text-gray-400">—</span>;
                return (
                  <div className="flex items-center justify-end gap-2">
                    <button
                      type="button"
                      onClick={() => {
                        setSelectedId(rid);
                        setIsDetailsOpen(true);
                      }}
                      className="inline-flex rounded-lg p-2 text-gray-600 transition hover:bg-gray-100"
                    >
                      <Eye size={16} />
                    </button>
                    <button
                      type="button"
                      onClick={() => {
                        setSelectedId(rid);
                        setIsEditOpen(true);
                      }}
                      className="inline-flex rounded-lg p-2 text-blue-600 transition hover:bg-blue-50"
                    >
                      <Edit size={16} />
                    </button>
                    <button
                      type="button"
                      onClick={() =>
                        void deleteWithConfirm(rid, (id) => issuesService.remove(id), {
                          confirmMessage: 'Delete this issue?',
                          successMessage: 'Issue deleted',
                        })
                      }
                      className="inline-flex rounded-lg p-2 text-red-600 transition hover:bg-red-50"
                    >
                      <Trash2 size={16} />
                    </button>
                  </div>
                );
              },
            },
          ]}
        />
      </StandardCrudListLayout>
      <Modal isOpen={isCreateOpen} onClose={() => setIsCreateOpen(false)} title="Create Issue">
        <IssueForm
          mode="create"
          onCancel={() => setIsCreateOpen(false)}
          onSuccess={async () => {
            setIsCreateOpen(false);
            await reload();
          }}
        />
      </Modal>
      <Modal isOpen={isEditOpen} onClose={() => setIsEditOpen(false)} title="Edit Issue">
        <IssueForm
          mode="edit"
          issueId={selectedId ?? undefined}
          onCancel={() => setIsEditOpen(false)}
          onSuccess={async () => {
            setIsEditOpen(false);
            setSelectedId(null);
            await reload();
          }}
        />
      </Modal>
      <RouteDetailsModal
        isOpen={isDetailsOpen}
        onClose={() => setIsDetailsOpen(false)}
        title="Issue Details"
        routePath={selectedId ? `/fleet/issues/${encodeURIComponent(selectedId)}` : null}
        headerTitle="Issue Details"
        headerSubtitle={selectedId ?? undefined}
        onDelete={async () => {
          if (!selectedId) return;
          await deleteWithConfirm(selectedId, (id) => issuesService.remove(id), {
            confirmMessage: 'Delete this issue?',
            successMessage: 'Issue deleted',
          });
          setIsDetailsOpen(false);
          setSelectedId(null);
          await reload();
        }}
        deleteLabel="Delete"
        onEdit={() => {
          setIsDetailsOpen(false);
          setIsEditOpen(true);
        }}
        editLabel="Edit Issue"
      />

      {totalPages > 1 && (
        <div className="mt-6 flex items-center justify-center gap-2">
          <button
            type="button"
            onClick={() => setPage((p) => Math.max(1, p - 1))}
            disabled={page === 1}
            className="rounded-lg border border-gray-200 px-4 py-2 hover:bg-gray-50 disabled:cursor-not-allowed disabled:opacity-50"
          >
            Previous
          </button>
          <span className="px-4 py-2 text-sm text-gray-600">
            Page {page} of {totalPages}
          </span>
          <button
            type="button"
            onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
            disabled={page === totalPages}
            className="rounded-lg border border-gray-200 px-4 py-2 hover:bg-gray-50 disabled:cursor-not-allowed disabled:opacity-50"
          >
            Next
          </button>
        </div>
      )}
    </>
  );
};

export default IssuesList;
