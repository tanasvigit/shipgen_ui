import React, { useCallback, useMemo, useState } from 'react';
import { Store, Eye, Edit, Trash2 } from 'lucide-react';
import { vendorsService } from '../../services/vendorsService';
import type { MockVendor } from '../../mocks/data/vendors';
import { getVendorRouteId } from '../../utils/vendorHelpers';
import { ResponsiveTable } from '../ui/ResponsiveTable';
import useListWithCrud from '../../hooks/useListWithCrud';
import { StandardCrudListLayout } from '../patterns/StandardCrudListLayout';
import { PH } from '../../constants/formPlaceholders';
import Modal from '../common/Modal';
import RouteDetailsModal from '../common/RouteDetailsModal';
import VendorForm from '../Fleet/forms/VendorForm';

const VendorsList: React.FC = () => {
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [searchTerm, setSearchTerm] = useState('');
  const [isCreateOpen, setIsCreateOpen] = useState(false);
  const [isEditOpen, setIsEditOpen] = useState(false);
  const [isDetailsOpen, setIsDetailsOpen] = useState(false);
  const [editingVendorId, setEditingVendorId] = useState<string | null>(null);

  const load = useCallback(async () => {
    const response = await vendorsService.list({ page, pageSize: 20 });
    setTotalPages(Math.max(1, Math.ceil((response.pagination?.total || 0) / 20)));
    return response.data;
  }, [page]);

  const { rows: vendors, loading, error, actionError, deleteWithConfirm, reload } =
    useListWithCrud<MockVendor>(load, [load]);

  const q = searchTerm.trim().toLowerCase();
  const filtered = useMemo(() => {
    return vendors.filter((v) => {
      if (!q) return true;
      const blob = [v.name, v.email, v.phone, v.uuid, v.public_id, v.internal_id, String(v.id ?? '')]
        .map((x) => (x ?? '').toString().toLowerCase())
        .join(' ');
      return blob.includes(q);
    });
  }, [vendors, q]);

  const openEdit = (vendor: MockVendor) => {
    const rid = getVendorRouteId(vendor);
    if (!rid) return;
    setEditingVendorId(rid);
    setIsEditOpen(true);
  };

  return (
    <>
      <StandardCrudListLayout
        title="Vendors"
        subtitle="Integrated with real backend: /fleetops/v1/vendors"
        createOnClick={() => setIsCreateOpen(true)}
        createLabel="New Vendor"
        searchPlaceholder={PH.searchVendor}
        searchTerm={searchTerm}
        onSearchChange={setSearchTerm}
        error={error}
        actionError={actionError}
        loading={loading}
        rowCount={vendors.length}
        filteredCount={filtered.length}
        emptyIcon={Store}
        emptyTitleNoData="No vendors yet"
        emptyTitleNoMatch="No matching vendors"
        emptyDescriptionNoData="Add vendors to manage partners and suppliers."
        emptyDescriptionNoMatch="Try a different search or clear the filter."
        emptyAction={
          <button
            type="button"
            data-testid="vendors-empty-create"
            onClick={() => setIsCreateOpen(true)}
            className="inline-flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2 text-sm text-white hover:bg-blue-700"
          >
            New vendor
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
        failedLoadTitle="Could not load vendors"
      >
        <ResponsiveTable
          data={filtered}
          keyExtractor={(v) => getVendorRouteId(v) || String(v.id)}
          columns={[
            { key: 'name', header: 'name', render: (v) => <span className="text-sm font-medium text-gray-900">{v.name ?? '—'}</span> },
            { key: 'type', header: 'type', render: (v) => <span className="text-sm text-gray-700">{v.type ?? '—'}</span> },
            {
              key: 'email',
              header: 'email',
              render: (v) => (
                <span className="table-cell-ellipsis block text-sm text-gray-700" title={v.email ?? ''}>
                  {v.email ?? '—'}
                </span>
              ),
              mobileHidden: true,
            },
            {
              key: 'actions',
              header: 'actions',
              render: (v) => {
                const rid = getVendorRouteId(v);
                if (!rid) {
                  return <span className="text-sm text-gray-400">—</span>;
                }
                return (
                  <div className="flex items-center justify-end gap-2">
                    <button
                      type="button"
                      onClick={() => {
                        setEditingVendorId(rid);
                        setIsDetailsOpen(true);
                      }}
                      className="inline-flex rounded-lg p-2 text-gray-600 transition hover:bg-gray-100"
                    >
                      <Eye size={16} />
                    </button>
                    <button
                      type="button"
                      data-testid={`vendor-quick-edit-${rid}`}
                      onClick={() => openEdit(v)}
                      className="inline-flex rounded-lg p-2 text-blue-600 transition hover:bg-blue-50"
                      title="Quick Edit"
                    >
                      <Edit size={16} />
                    </button>
                    <button
                      type="button"
                      data-testid={`vendor-delete-${rid}`}
                      onClick={() =>
                        void deleteWithConfirm(rid, (id) => vendorsService.remove(id), {
                          confirmMessage: `Delete vendor "${v.name ?? rid}"?`,
                          successMessage: 'Vendor deleted',
                        })
                      }
                      className="inline-flex rounded-lg p-2 text-red-600 transition hover:bg-red-50"
                      title="Delete Vendor"
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

      <Modal isOpen={isCreateOpen} onClose={() => setIsCreateOpen(false)} title="Create Vendor">
        <VendorForm mode="create" onCancel={() => setIsCreateOpen(false)} onSuccess={async () => {
          setIsCreateOpen(false);
          await reload();
        }} />
      </Modal>
      <Modal isOpen={isEditOpen} onClose={() => setIsEditOpen(false)} title="Edit Vendor">
        <VendorForm mode="edit" vendorId={editingVendorId ?? undefined} onCancel={() => setIsEditOpen(false)} onSuccess={async () => {
          setIsEditOpen(false);
          setEditingVendorId(null);
          await reload();
        }} />
      </Modal>
      <RouteDetailsModal
        isOpen={isDetailsOpen}
        onClose={() => setIsDetailsOpen(false)}
        title="Vendor Details"
        routePath={editingVendorId ? `/fleet/vendors/${encodeURIComponent(editingVendorId)}` : null}
        headerTitle="Vendor Details"
        headerSubtitle={editingVendorId ?? undefined}
        onDelete={async () => {
          if (!editingVendorId) return;
          await deleteWithConfirm(editingVendorId, (id) => vendorsService.remove(id), {
            confirmMessage: 'Delete this vendor?',
            successMessage: 'Vendor deleted',
          });
          setIsDetailsOpen(false);
          setEditingVendorId(null);
          await reload();
        }}
        deleteLabel="Delete"
        onEdit={() => {
          setIsDetailsOpen(false);
          setIsEditOpen(true);
        }}
        editLabel="Edit Vendor"
      />
    </>
  );
};

export default VendorsList;
