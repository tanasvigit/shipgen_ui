import React, { useCallback, useMemo, useState } from 'react';
import { Fuel, Edit, Eye, Trash2 } from 'lucide-react';
import { fuelReportsService } from '../../services/fuelReportsService';
import type { MockFuelReport } from '../../mocks/data/fuel_reports';
import { getFuelReportRouteId } from '../../utils/fuelReportHelpers';
import EntityLink from '../common/EntityLink';
import Modal from '../common/Modal';
import RouteDetailsModal from '../common/RouteDetailsModal';
import { ResponsiveTable } from '../ui/ResponsiveTable';
import useListWithCrud from '../../hooks/useListWithCrud';
import { StandardCrudListLayout } from '../patterns/StandardCrudListLayout';
import { PH, SELECT_PH } from '../../constants/formPlaceholders';
import FuelReportForm from './forms/FuelReportForm';

const FuelReportsList: React.FC = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [metricUnitFilter, setMetricUnitFilter] = useState('');
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);

  const load = useCallback(async () => {
    const response = await fuelReportsService.list({ page, pageSize: 20 });
    let rows = response.data || [];
    if (statusFilter) rows = rows.filter((r) => r.status === statusFilter);
    if (metricUnitFilter) rows = rows.filter((r) => r.metric_unit === metricUnitFilter);
    setTotalPages(Math.max(1, Math.ceil((response.pagination?.total || 0) / 20)));
    return rows;
  }, [page, statusFilter, metricUnitFilter]);

  const [isCreateOpen, setIsCreateOpen] = useState(false);
  const [isEditOpen, setIsEditOpen] = useState(false);
  const [isDetailsOpen, setIsDetailsOpen] = useState(false);
  const [selectedId, setSelectedId] = useState<string | null>(null);

  const { rows: fuel_reports, loading, error, actionError, deleteWithConfirm, reload } =
    useListWithCrud<MockFuelReport>(load, [load]);

  const filtered = useMemo(() => {
    const q = searchTerm.trim().toLowerCase();
    if (!q) return fuel_reports;
    return fuel_reports.filter((r) =>
      [
        r.public_id,
        r.uuid,
        String(r.id ?? ''),
        r.vehicle_name,
        r.driver_name,
        r.report,
        r.status,
      ]
        .map((x) => (x ?? '').toLowerCase())
        .join(' ')
        .includes(q),
    );
  }, [fuel_reports, searchTerm]);

  return (
    <>
      <StandardCrudListLayout
        title="Fuel Reports"
        subtitle="fleetops-fuel-reports (mock: /fuel-reports)"
        createOnClick={() => setIsCreateOpen(true)}
        createLabel="New Fuel Report"
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
              <option value="submitted">submitted</option>
              <option value="approved">approved</option>
              <option value="rejected">rejected</option>
            </select>
            <select
              value={metricUnitFilter}
              onChange={(e) => {
                setMetricUnitFilter(e.target.value);
                setPage(1);
              }}
              className="w-full rounded-lg border border-gray-200 bg-white px-3 py-2 outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">All metric_unit</option>
              <option value="litre">litre</option>
              <option value="gallon">gallon</option>
            </select>
          </div>
        }
        searchPlaceholder={PH.searchFuelReports}
        searchTerm={searchTerm}
        onSearchChange={setSearchTerm}
        error={error}
        actionError={actionError}
        loading={loading}
        rowCount={fuel_reports.length}
        filteredCount={filtered.length}
        emptyIcon={Fuel}
        emptyTitleNoData="No fuel reports yet"
        emptyTitleNoMatch="No matching fuel reports"
        emptyDescriptionNoData="Record fuel purchases and usage."
        emptyDescriptionNoMatch="Adjust search or filters."
        emptyAction={
          <button
            type="button"
            onClick={() => setIsCreateOpen(true)}
            className="inline-flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2 text-sm text-white hover:bg-blue-700"
          >
            New fuel report
          </button>
        }
        noMatchAction={
          <button
            type="button"
            onClick={() => {
              setSearchTerm('');
              setStatusFilter('');
              setMetricUnitFilter('');
              setPage(1);
            }}
            className="rounded-lg border border-gray-200 px-4 py-2 text-sm hover:bg-gray-50"
          >
            Clear filters
          </button>
        }
        failedLoadTitle="Could not load fuel reports"
      >
        <ResponsiveTable
          data={filtered}
          keyExtractor={(r) => getFuelReportRouteId(r) || String(r.id)}
          columns={[
            {
              key: 'public_id',
              header: 'public_id',
              render: (r) => (
                <span className="font-mono text-sm text-gray-800">{r.public_id ?? r.uuid ?? r.id ?? '—'}</span>
              ),
            },
            {
              key: 'driver_name',
              header: 'driver_name',
              render: (r) => (
                <EntityLink
                  id={r.driver_uuid}
                  label={r.driver_name ?? r.driver_uuid}
                  to="/fleet/drivers"
                  title="View Driver"
                />
              ),
            },
            {
              key: 'vehicle_name',
              header: 'vehicle_name',
              render: (r) => (
                <EntityLink
                  id={r.vehicle_uuid}
                  label={r.vehicle_name ?? r.vehicle_uuid}
                  to="/fleet/vehicles"
                  title="View Vehicle"
                />
              ),
            },
            {
              key: 'volume',
              header: 'volume',
              render: (r) => (
                <span className="text-sm text-gray-700">
                  {r.volume ?? '—'} {r.metric_unit ?? ''}
                </span>
              ),
            },
            {
              key: 'amount',
              header: 'amount',
              render: (r) => (
                <span className="text-sm text-gray-700">
                  {r.amount ?? '—'} {r.currency ?? ''}
                </span>
              ),
              mobileHidden: true,
            },
            { key: 'status', header: 'status', render: (r) => <span className="text-sm text-gray-700">{r.status ?? '—'}</span> },
            {
              key: 'created_at',
              header: 'created_at',
              render: (r) => (
                <span className="text-sm text-gray-700">
                  {r.created_at ? new Date(r.created_at).toLocaleString() : '—'}
                </span>
              ),
              mobileHidden: true,
            },
            {
              key: 'actions',
              header: 'actions',
              render: (r) => {
                const rid = getFuelReportRouteId(r);
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
                        void deleteWithConfirm(rid, (id) => fuelReportsService.remove(id), {
                          confirmMessage: 'Delete this fuel report?',
                          successMessage: 'Fuel report deleted',
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

      <Modal isOpen={isCreateOpen} onClose={() => setIsCreateOpen(false)} title="Create Fuel Report">
        <FuelReportForm
          mode="create"
          onCancel={() => setIsCreateOpen(false)}
          onSuccess={async () => {
            setIsCreateOpen(false);
            await reload();
          }}
        />
      </Modal>
      <Modal isOpen={isEditOpen} onClose={() => setIsEditOpen(false)} title="Edit Fuel Report">
        <FuelReportForm
          mode="edit"
          fuelReportId={selectedId ?? undefined}
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
        title="Fuel Report Details"
        routePath={selectedId ? `/fleet/fuel-reports/${encodeURIComponent(selectedId)}` : null}
        headerTitle="Fuel Report Details"
        headerSubtitle={selectedId ?? undefined}
        onDelete={async () => {
          if (!selectedId) return;
          await deleteWithConfirm(selectedId, (id) => fuelReportsService.remove(id), {
            confirmMessage: 'Delete this fuel report?',
            successMessage: 'Fuel report deleted',
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
        editLabel="Edit Fuel Report"
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

export default FuelReportsList;
