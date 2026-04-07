import React, { useCallback, useEffect, useMemo, useState } from 'react';
import { User, Eye, Edit, Trash2 } from 'lucide-react';
import { useLocation } from 'react-router-dom';
import { driversService, type UiDriver } from '../../services/driversService';
import { ResponsiveTable } from '../ui/ResponsiveTable';
import useListWithCrud from '../../hooks/useListWithCrud';
import { StandardCrudListLayout } from '../patterns/StandardCrudListLayout';
import { PH, SELECT_PH } from '../../constants/formPlaceholders';
import Modal from '../common/Modal';
import RouteDetailsModal from '../common/RouteDetailsModal';
import DriverForm from './forms/DriverForm';

const PAGE_SIZE = 20;

const DriversList: React.FC = () => {
  const location = useLocation();
  const initialParams = new URLSearchParams(location.search);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState(initialParams.get('status') ?? '');
  const [onlineFilter, setOnlineFilter] = useState<'all' | '1'>(
    initialParams.get('online') === '1' ? '1' : 'all'
  );
  const [unassignedFilter, setUnassignedFilter] = useState(initialParams.get('unassigned') === 'true');
  const [page, setPage] = useState(1);
  const [listTotal, setListTotal] = useState(0);
  const [isCreateOpen, setIsCreateOpen] = useState(false);
  const [isEditOpen, setIsEditOpen] = useState(false);
  const [isDetailsOpen, setIsDetailsOpen] = useState(false);
  const [selectedId, setSelectedId] = useState<string | null>(null);

  useEffect(() => {
    const params = new URLSearchParams(location.search);
    setStatusFilter(params.get('status') ?? '');
    setOnlineFilter(params.get('online') === '1' ? '1' : 'all');
    setUnassignedFilter(params.get('unassigned') === 'true');
    setPage(1);
  }, [location.search]);

  const load = useCallback(async () => {
    const response = await driversService.list({
      page,
      pageSize: PAGE_SIZE,
      status: statusFilter || undefined,
      online: onlineFilter === '1' ? 1 : undefined,
      unassigned: unassignedFilter || undefined,
    });
    setListTotal(response.pagination?.total ?? 0);
    return response.data;
  }, [page, statusFilter, onlineFilter, unassignedFilter]);

  const totalPages = Math.max(1, Math.ceil(listTotal / PAGE_SIZE));

  const { rows, loading, error, actionError, deleteWithConfirm, reload } = useListWithCrud<UiDriver>(load, [load]);

  const filtered = useMemo(() => {
    const q = searchTerm.trim().toLowerCase();
    return rows.filter((d) => {
      const searchOk =
        q.length === 0 ||
        d.id.toLowerCase().includes(q) ||
        d.drivers_license_number.toLowerCase().includes(q);
      return searchOk;
    });
  }, [rows, searchTerm]);

  return (
    <>
      <StandardCrudListLayout
        title="Drivers"
        subtitle="Manage fleet drivers"
        createOnClick={() => setIsCreateOpen(true)}
        createLabel="New Driver"
        filters={
          <div className="grid max-w-xl grid-cols-1 gap-2 sm:grid-cols-3">
            <select
              value={statusFilter}
              onChange={(e) => {
                setStatusFilter(e.target.value);
                setPage(1);
              }}
              className="w-full rounded-lg border border-gray-200 bg-white px-3 py-2 outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">{SELECT_PH.status}</option>
              <option value="active">active</option>
              <option value="inactive">inactive</option>
            </select>
            <select
              value={onlineFilter}
              onChange={(e) => {
                const v = e.target.value === '1' ? '1' : 'all';
                setOnlineFilter(v);
                setPage(1);
              }}
              className="w-full rounded-lg border border-gray-200 bg-white px-3 py-2 outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="all">All connectivity</option>
              <option value="1">online</option>
            </select>
            <label className="inline-flex items-center gap-2 rounded-lg border border-gray-200 bg-white px-3 py-2 text-sm text-gray-700">
              <input
                type="checkbox"
                checked={unassignedFilter}
                onChange={(e) => {
                  setUnassignedFilter(e.target.checked);
                  setPage(1);
                }}
              />
              Unassigned only
            </label>
          </div>
        }
        searchPlaceholder={PH.searchDrivers}
        searchTerm={searchTerm}
        onSearchChange={setSearchTerm}
        error={error}
        actionError={actionError}
        loading={loading}
        rowCount={rows.length}
        filteredCount={filtered.length}
        emptyIcon={User}
        emptyTitleNoData="No drivers yet"
        emptyTitleNoMatch="No matching drivers"
        emptyDescriptionNoData="Add drivers to assign to vehicles and routes."
        emptyDescriptionNoMatch="Try a different search or clear filters."
        emptyAction={
          <button
            type="button"
            data-testid="drivers-empty-create"
            onClick={() => setIsCreateOpen(true)}
            className="inline-flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2 text-sm text-white hover:bg-blue-700"
          >
            New driver
          </button>
        }
        noMatchAction={
          <button
            type="button"
            onClick={() => {
              setSearchTerm('');
              setStatusFilter('');
              setOnlineFilter('all');
              setUnassignedFilter(false);
            }}
            className="rounded-lg border border-gray-200 px-4 py-2 text-sm hover:bg-gray-50"
          >
            Clear filters
          </button>
        }
        failedLoadTitle="Could not load drivers"
      >
        <ResponsiveTable
          data={filtered}
          keyExtractor={(driver) => driver.id}
          onRowClick={(driver) => {
            setSelectedId(driver.id);
            setIsDetailsOpen(true);
          }}
          columns={[
            {
              key: 'driver_id',
              header: 'driver_id',
              render: (driver) => (
                <div className="flex items-center space-x-2">
                  <User size={16} className="text-blue-500" />
                  <span className="text-sm font-medium text-gray-900">{driver.id}</span>
                </div>
              ),
            },
            {
              key: 'drivers_license_number',
              header: 'drivers_license_number',
              render: (driver) => <span className="text-sm text-gray-700">{driver.drivers_license_number}</span>,
            },
            {
              key: 'status',
              header: 'status',
              render: (driver) => <span className="text-sm text-gray-700">{driver.status}</span>,
            },
            {
              key: 'online',
              header: 'online',
              render: (driver) => (
                <span className="text-sm text-gray-700">{driver.online === 1 ? 'online' : 'offline'}</span>
              ),
            },
            {
              key: 'actions',
              header: 'actions',
              render: (driver) => (
                <div className="flex items-center justify-end gap-2">
                  <button
                    type="button"
                    onClick={(e) => {
                      e.stopPropagation();
                      setSelectedId(driver.id);
                      setIsDetailsOpen(true);
                    }}
                    className="rounded-lg p-2 text-gray-600 transition hover:bg-gray-100"
                  >
                    <Eye size={16} />
                  </button>
                  <button
                    type="button"
                    onClick={(e) => {
                      e.stopPropagation();
                      setSelectedId(driver.id);
                      setIsEditOpen(true);
                    }}
                    className="rounded-lg p-2 text-blue-600 transition hover:bg-blue-50"
                  >
                    <Edit size={16} />
                  </button>
                  <button
                    type="button"
                    data-testid={`driver-delete-${driver.id}`}
                    onClick={(e) => {
                      e.stopPropagation();
                      void deleteWithConfirm(driver.id, (id) => driversService.remove(id), {
                        confirmMessage: 'Delete this driver?',
                        successMessage: 'Driver deleted',
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
      </StandardCrudListLayout>
      <Modal isOpen={isCreateOpen} onClose={() => setIsCreateOpen(false)} title="Create Driver">
        <DriverForm mode="create" onCancel={() => setIsCreateOpen(false)} onSuccess={async () => {
          setIsCreateOpen(false);
          await reload();
        }} />
      </Modal>
      <Modal isOpen={isEditOpen} onClose={() => setIsEditOpen(false)} title="Edit Driver">
        <DriverForm mode="edit" driverId={selectedId ?? undefined} onCancel={() => setIsEditOpen(false)} onSuccess={async () => {
          setIsEditOpen(false);
          setSelectedId(null);
          await reload();
        }} />
      </Modal>
      <RouteDetailsModal
        isOpen={isDetailsOpen}
        onClose={() => setIsDetailsOpen(false)}
        title="Driver Details"
        routePath={selectedId ? `/fleet/drivers/${encodeURIComponent(selectedId)}` : null}
        headerTitle="Driver Details"
        headerSubtitle={selectedId ?? undefined}
        onDelete={async () => {
          if (!selectedId) return;
          await deleteWithConfirm(selectedId, (id) => driversService.remove(id), {
            confirmMessage: 'Delete this driver?',
            successMessage: 'Driver deleted',
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
        editLabel="Edit Driver"
      />

      {listTotal > PAGE_SIZE && (
        <div className="flex items-center justify-center space-x-2">
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

export default DriversList;
