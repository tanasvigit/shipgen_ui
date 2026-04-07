import React, { useCallback, useEffect, useMemo, useState } from 'react';
import { Truck, Eye, Edit, Trash2 } from 'lucide-react';
import { useLocation } from 'react-router-dom';
import { vehiclesService, type UiVehicle } from '../../services/vehiclesService';
import { ResponsiveTable } from '../ui/ResponsiveTable';
import useListWithCrud from '../../hooks/useListWithCrud';
import { StandardCrudListLayout } from '../patterns/StandardCrudListLayout';
import { PH, SELECT_PH } from '../../constants/formPlaceholders';
import Modal from '../common/Modal';
import RouteDetailsModal from '../common/RouteDetailsModal';
import VehicleForm from './forms/VehicleForm';

const PAGE_SIZE = 20;

const VehiclesList: React.FC = () => {
  const location = useLocation();
  const initialParams = new URLSearchParams(location.search);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>(initialParams.get('status') ?? 'all');
  const [unassignedFilter, setUnassignedFilter] = useState(initialParams.get('unassigned') === 'true');
  const [page, setPage] = useState(1);
  const [listTotal, setListTotal] = useState(0);
  const [isCreateOpen, setIsCreateOpen] = useState(false);
  const [isEditOpen, setIsEditOpen] = useState(false);
  const [isDetailsOpen, setIsDetailsOpen] = useState(false);
  const [selectedId, setSelectedId] = useState<string | null>(null);

  useEffect(() => {
    const params = new URLSearchParams(location.search);
    setStatusFilter(params.get('status') ?? 'all');
    setUnassignedFilter(params.get('unassigned') === 'true');
    setPage(1);
  }, [location.search]);

  const load = useCallback(async () => {
    const response = await vehiclesService.list({
      page,
      pageSize: PAGE_SIZE,
      status: statusFilter !== 'all' ? statusFilter : undefined,
      unassigned: unassignedFilter || undefined,
    });
    setListTotal(response.pagination?.total ?? 0);
    return response.data;
  }, [page, statusFilter, unassignedFilter]);

  const { rows, loading, error, actionError, deleteWithConfirm, reload } = useListWithCrud<UiVehicle>(load, [load]);

  const totalPages = Math.max(1, Math.ceil(listTotal / PAGE_SIZE));

  const getStatusColor = (status: string) => {
    const colors: Record<string, string> = {
      active: 'bg-green-100 text-green-700',
      maintenance: 'bg-red-100 text-red-700',
      inactive: 'bg-gray-100 text-gray-700',
    };
    return colors[status] || 'bg-gray-100 text-gray-700';
  };

  const filtered = useMemo(() => {
    const q = searchTerm.trim().toLowerCase();
    return rows.filter(
      (v) =>
        q.length === 0 ||
        v.id.toLowerCase().includes(q) ||
        v.plate_number.toLowerCase().includes(q) ||
        v.type.toLowerCase().includes(q),
    );
  }, [rows, searchTerm]);

  return (
    <>
      <StandardCrudListLayout
        title="Vehicles"
        subtitle="Manage fleet vehicles"
        createOnClick={() => setIsCreateOpen(true)}
        createLabel="New Vehicle"
        filters={
          <div className="grid max-w-md grid-cols-1 gap-2 sm:grid-cols-2">
            <select
              value={statusFilter}
              onChange={(e) => {
                setStatusFilter(e.target.value);
                setPage(1);
              }}
              className="w-full rounded-lg border border-gray-200 bg-white px-3 py-2 outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="all">All Status</option>
              <option value="active">active</option>
              <option value="inactive">inactive</option>
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
        searchPlaceholder={PH.searchVehicles}
        searchTerm={searchTerm}
        onSearchChange={setSearchTerm}
        error={error}
        actionError={actionError}
        loading={loading}
        rowCount={rows.length}
        filteredCount={filtered.length}
        emptyIcon={Truck}
        emptyTitleNoData="No vehicles yet"
        emptyTitleNoMatch="No matching vehicles"
        emptyDescriptionNoData="Add vehicles to your fleet."
        emptyDescriptionNoMatch="Try a different search or status filter."
        emptyAction={
          <button
            type="button"
            onClick={() => setIsCreateOpen(true)}
            className="inline-flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2 text-sm text-white hover:bg-blue-700"
          >
            New vehicle
          </button>
        }
        noMatchAction={
          <button
            type="button"
            onClick={() => {
              setSearchTerm('');
              setStatusFilter('all');
              setUnassignedFilter(false);
              setPage(1);
            }}
            className="rounded-lg border border-gray-200 px-4 py-2 text-sm hover:bg-gray-50"
          >
            Clear filters
          </button>
        }
        failedLoadTitle="Could not load vehicles"
      >
        <ResponsiveTable
          data={filtered}
          keyExtractor={(vehicle) => vehicle.id}
          onRowClick={(vehicle) => {
            setSelectedId(vehicle.id);
            setIsDetailsOpen(true);
          }}
          columns={[
            {
              key: 'vehicle_id',
              header: 'vehicle_id',
              render: (vehicle) => (
                <div className="flex items-center gap-2">
                  <Truck size={16} className="text-indigo-500" />
                  <span className="text-sm font-medium text-gray-900">{vehicle.id}</span>
                </div>
              ),
            },
            {
              key: 'plate_number',
              header: 'plate_number',
              render: (vehicle) => <span className="text-sm text-gray-700">{vehicle.plate_number}</span>,
            },
            {
              key: 'type',
              header: 'type',
              render: (vehicle) => <span className="text-sm text-gray-700">{vehicle.type}</span>,
            },
            {
              key: 'status',
              header: 'status',
              render: (vehicle) => (
                <span className={`rounded-full px-2 py-1 text-xs font-medium ${getStatusColor(vehicle.status)}`}>
                  {vehicle.status}
                </span>
              ),
            },
            {
              key: 'actions',
              header: 'actions',
              render: (vehicle) => (
                <div className="flex items-center justify-end gap-2">
                  <button
                    type="button"
                    onClick={(e) => {
                      e.stopPropagation();
                      setSelectedId(vehicle.id);
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
                      setSelectedId(vehicle.id);
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
                      void deleteWithConfirm(vehicle.id, (id) => vehiclesService.remove(id), {
                        confirmMessage: 'Delete this vehicle?',
                        successMessage: 'Vehicle deleted',
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
      <Modal isOpen={isCreateOpen} onClose={() => setIsCreateOpen(false)} title="Create Vehicle">
        <VehicleForm mode="create" onCancel={() => setIsCreateOpen(false)} onSuccess={async () => {
          setIsCreateOpen(false);
          await reload();
        }} />
      </Modal>
      <Modal isOpen={isEditOpen} onClose={() => setIsEditOpen(false)} title="Edit Vehicle">
        <VehicleForm mode="edit" vehicleId={selectedId ?? undefined} onCancel={() => setIsEditOpen(false)} onSuccess={async () => {
          setIsEditOpen(false);
          setSelectedId(null);
          await reload();
        }} />
      </Modal>
      <RouteDetailsModal
        isOpen={isDetailsOpen}
        onClose={() => setIsDetailsOpen(false)}
        title="Vehicle Details"
        routePath={selectedId ? `/fleet/vehicles/${encodeURIComponent(selectedId)}` : null}
        headerTitle="Vehicle Details"
        headerSubtitle={selectedId ?? undefined}
        onDelete={async () => {
          if (!selectedId) return;
          await deleteWithConfirm(selectedId, (id) => vehiclesService.remove(id), {
            confirmMessage: 'Delete this vehicle?',
            successMessage: 'Vehicle deleted',
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
        editLabel="Edit Vehicle"
      />

      {listTotal > PAGE_SIZE && (
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

export default VehiclesList;
