import React, { useCallback, useMemo, useState } from 'react';
import { MapPin, Eye, Edit, Trash2 } from 'lucide-react';
import { placesService } from '../../services/placesService';
import type { MockPlace } from '../../mocks/data/places';
import { getPlaceRouteId } from '../../utils/placeHelpers';
import { ResponsiveTable } from '../ui/ResponsiveTable';
import useListWithCrud from '../../hooks/useListWithCrud';
import { StandardCrudListLayout } from '../patterns/StandardCrudListLayout';
import { PH, SELECT_PH } from '../../constants/formPlaceholders';
import Modal from '../common/Modal';
import RouteDetailsModal from '../common/RouteDetailsModal';
import PlaceForm from './forms/PlaceForm';

const PlacesList: React.FC = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [typeFilter, setTypeFilter] = useState('');
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [isCreateOpen, setIsCreateOpen] = useState(false);
  const [isEditOpen, setIsEditOpen] = useState(false);
  const [isDetailsOpen, setIsDetailsOpen] = useState(false);
  const [selectedId, setSelectedId] = useState<string | null>(null);

  const load = useCallback(async () => {
    const response = await placesService.list({ page, pageSize: 20 });
    let rows = response.data;
    if (typeFilter) rows = rows.filter((p) => p.type === typeFilter);
    setTotalPages(Math.max(1, Math.ceil((response.pagination?.total || 0) / 20)));
    return rows;
  }, [page, typeFilter]);

  const { rows: places, loading, error, actionError, deleteWithConfirm, reload } = useListWithCrud<MockPlace>(load, [load]);

  const q = searchTerm.trim().toLowerCase();
  const filtered = useMemo(() => {
    return places.filter((p) => {
      if (!q) return true;
      const blob = [
        p.name,
        p.street1,
        p.street2,
        p.city,
        p.province,
        p.postal_code,
        p.country,
        p.neighborhood,
        p.district,
        p.building,
        p.remarks,
        p.phone,
        p.uuid,
        p.public_id,
        String(p.id ?? ''),
      ]
        .map((x) => (x ?? '').toString().toLowerCase())
        .join(' ');
      return blob.includes(q);
    });
  }, [places, q]);

  return (
    <>
      <StandardCrudListLayout
        title="Places"
        subtitle="fleetops-places (mock: /places)"
        createOnClick={() => setIsCreateOpen(true)}
        createLabel="New Place"
        filters={
          <div className="max-w-xs">
            <select
              value={typeFilter}
              onChange={(e) => {
                setTypeFilter(e.target.value);
                setPage(1);
              }}
              className="w-full rounded-lg border border-gray-200 bg-white px-3 py-2 outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">{SELECT_PH.type}</option>
              <option value="warehouse">warehouse</option>
              <option value="customer">customer</option>
              <option value="vendor">vendor</option>
            </select>
          </div>
        }
        searchPlaceholder={PH.searchPlaces}
        searchTerm={searchTerm}
        onSearchChange={setSearchTerm}
        error={error}
        actionError={actionError}
        loading={loading}
        rowCount={places.length}
        filteredCount={filtered.length}
        emptyIcon={MapPin}
        emptyTitleNoData="No places yet"
        emptyTitleNoMatch="No matching places"
        emptyDescriptionNoData="Add warehouses, customers, and vendor locations."
        emptyDescriptionNoMatch="Try another search or type filter."
        emptyAction={
          <button
            type="button"
            onClick={() => setIsCreateOpen(true)}
            className="inline-flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2 text-sm text-white hover:bg-blue-700"
          >
            New place
          </button>
        }
        noMatchAction={
          <button
            type="button"
            onClick={() => {
              setSearchTerm('');
              setTypeFilter('');
              setPage(1);
            }}
            className="rounded-lg border border-gray-200 px-4 py-2 text-sm hover:bg-gray-50"
          >
            Clear filters
          </button>
        }
        failedLoadTitle="Could not load places"
      >
        <ResponsiveTable
          data={filtered}
          keyExtractor={(p) => getPlaceRouteId(p) || String(p.id)}
          columns={[
            {
              key: 'uuid',
              header: 'uuid',
              render: (p) => (
                <span className="table-cell-ellipsis block font-mono text-xs text-gray-700" title={p.uuid ?? ''}>
                  {p.uuid ?? '—'}
                </span>
              ),
            },
            { key: 'name', header: 'name', render: (p) => <span className="text-sm text-gray-900">{p.name ?? '—'}</span> },
            {
              key: 'street1',
              header: 'street1',
              render: (p) => (
                <span className="table-cell-ellipsis block text-sm text-gray-700" title={p.street1 ?? ''}>
                  {p.street1 ?? '—'}
                </span>
              ),
            },
            { key: 'city', header: 'city', render: (p) => <span className="text-sm text-gray-700">{p.city ?? '—'}</span> },
            {
              key: 'province',
              header: 'province',
              render: (p) => <span className="text-sm text-gray-700">{p.province ?? '—'}</span>,
              mobileHidden: true,
            },
            {
              key: 'country',
              header: 'country',
              render: (p) => <span className="text-sm text-gray-700">{p.country ?? '—'}</span>,
              mobileHidden: true,
            },
            { key: 'type', header: 'type', render: (p) => <span className="text-sm text-gray-700">{p.type ?? '—'}</span> },
            {
              key: 'actions',
              header: 'actions',
              render: (p) => {
                const rid = getPlaceRouteId(p);
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
                        void deleteWithConfirm(rid, (id) => placesService.remove(id), {
                          confirmMessage: 'Delete this place?',
                          successMessage: 'Place deleted',
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
      <Modal isOpen={isCreateOpen} onClose={() => setIsCreateOpen(false)} title="Create Place">
        <PlaceForm mode="create" onCancel={() => setIsCreateOpen(false)} onSuccess={async () => {
          setIsCreateOpen(false);
          await reload();
        }} />
      </Modal>
      <Modal isOpen={isEditOpen} onClose={() => setIsEditOpen(false)} title="Edit Place">
        <PlaceForm mode="edit" placeId={selectedId ?? undefined} onCancel={() => setIsEditOpen(false)} onSuccess={async () => {
          setIsEditOpen(false);
          setSelectedId(null);
          await reload();
        }} />
      </Modal>
      <RouteDetailsModal
        isOpen={isDetailsOpen}
        onClose={() => setIsDetailsOpen(false)}
        title="Place Details"
        routePath={selectedId ? `/fleet/places/${encodeURIComponent(selectedId)}` : null}
        headerTitle="Place Details"
        headerSubtitle={selectedId ?? undefined}
        onDelete={async () => {
          if (!selectedId) return;
          await deleteWithConfirm(selectedId, (id) => placesService.remove(id), {
            confirmMessage: 'Delete this place?',
            successMessage: 'Place deleted',
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
        editLabel="Edit Place"
      />

      {totalPages > 1 && (
        <div className="mt-6 flex items-center justify-center gap-2">
          <button
            type="button"
            onClick={() => setPage((x) => Math.max(1, x - 1))}
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
            onClick={() => setPage((x) => Math.min(totalPages, x + 1))}
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

export default PlacesList;
