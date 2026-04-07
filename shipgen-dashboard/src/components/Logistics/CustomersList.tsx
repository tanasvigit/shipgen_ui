import React, { useCallback, useEffect, useRef, useState } from 'react';
import { Eye, Pencil, Plus, Search, Trash2, Users } from 'lucide-react';
import { customersService } from '../../services/customersService';
import type { UiCustomer } from '../../services/customersService';
import PageContainer from '../ui/PageContainer';
import PageHeader from '../ui/PageHeader';
import Card from '../ui/Card';
import Table, { TableColumn } from '../ui/Table';
import Modal from '../common/Modal';
import CustomerForm from './CustomerForm';
import CustomerDetailsModal from './CustomerDetailsModal';
import { UserRole } from '../../types';
import {
  canDeleteCustomers,
  canMutateCustomers,
  getStoredUserRole,
} from '../../utils/roleAccess';

const pageSize = 20;

const addressOf = (c: UiCustomer): string => {
  const m = (c.meta ?? {}) as Record<string, unknown>;
  return typeof m.address === 'string' ? m.address : '—';
};

const CustomersList: React.FC = () => {
  const role = getStoredUserRole() ?? UserRole.VIEWER;
  const mayMutate = canMutateCustomers(role);
  const mayDelete = canDeleteCustomers(role);

  const [rows, setRows] = useState<UiCustomer[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [debouncedSearch, setDebouncedSearch] = useState('');
  const [page, setPage] = useState(1);
  const [hasMore, setHasMore] = useState(false);
  const [deleteId, setDeleteId] = useState<string | null>(null);
  const [deleting, setDeleting] = useState(false);
  const [isCreateOpen, setIsCreateOpen] = useState(false);
  const [isEditOpen, setIsEditOpen] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [isDetailsOpen, setIsDetailsOpen] = useState(false);
  const [viewingCustomerId, setViewingCustomerId] = useState<string | null>(null);
  const prevDebouncedSearch = useRef<string | null>(null);

  useEffect(() => {
    const t = window.setTimeout(() => {
      const next = searchTerm.trim();
      if (prevDebouncedSearch.current !== null && prevDebouncedSearch.current !== next) {
        setPage(1);
      }
      prevDebouncedSearch.current = next;
      setDebouncedSearch(next);
    }, 300);
    return () => window.clearTimeout(t);
  }, [searchTerm]);

  const load = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const res = await customersService.list({
        page,
        pageSize,
        search: debouncedSearch || undefined,
      });
      setRows(res.data);
      setHasMore(res.data.length === pageSize);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Failed to load customers');
      setRows([]);
    } finally {
      setLoading(false);
    }
  }, [page, debouncedSearch]);

  useEffect(() => {
    void load();
  }, [load]);

  const confirmDelete = async () => {
    if (!deleteId) return;
    try {
      setDeleting(true);
      await customersService.remove(deleteId);
      setDeleteId(null);
      await load();
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Delete failed');
    } finally {
      setDeleting(false);
    }
  };

  const columns: TableColumn<UiCustomer>[] = [
    {
      key: 'name',
      title: 'Name',
      render: (c) => <span className="font-medium text-gray-900">{c.name ?? '—'}</span>,
    },
    { key: 'phone', title: 'Phone', render: (c) => c.phone ?? '—' },
    { key: 'email', title: 'Email', render: (c) => c.email ?? '—' },
    { key: 'address', title: 'Address', render: (c) => <span className="max-w-xs truncate">{addressOf(c)}</span> },
    {
      key: 'actions',
      title: '',
      isActions: true,
      render: (c) => {
        const uuid = c.uuid ?? '';
        return (
          <div className="flex justify-end gap-2">
            <button
              type="button"
              className="inline-flex rounded-lg p-2 text-gray-600 hover:bg-gray-100"
              aria-label="View customer"
              onClick={() => {
                if (!uuid) return;
                setViewingCustomerId(uuid);
                setIsDetailsOpen(true);
              }}
            >
              <Eye size={16} />
            </button>
            {mayMutate ? (
              <button
                type="button"
                className="inline-flex rounded-lg p-2 text-gray-500 hover:bg-gray-100 hover:text-blue-600"
                aria-label="Edit customer"
                onClick={() => {
                  if (!uuid) return;
                  setEditingId(uuid);
                  setIsEditOpen(true);
                }}
              >
                <Pencil size={16} />
              </button>
            ) : null}
            {mayDelete ? (
              <button
                type="button"
                className="inline-flex rounded-lg p-2 text-gray-500 hover:bg-red-50 hover:text-red-600"
                aria-label="Delete customer"
                onClick={() => uuid && setDeleteId(uuid)}
              >
                <Trash2 size={16} />
              </button>
            ) : null}
          </div>
        );
      },
    },
  ];

  return (
    <PageContainer flushHorizontal className="px-4 sm:px-5 lg:px-8">
      <PageHeader
        title="Customers"
        description="Manage customers for logistics orders (fleetops contacts, type customer)."
        action={
          mayMutate ? (
            <button
              type="button"
              onClick={() => setIsCreateOpen(true)}
              className="inline-flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700"
            >
              <Plus size={18} />
              New customer
            </button>
          ) : undefined
        }
      />

      <Card className="mb-4 p-4">
        <div className="relative max-w-md">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-400" />
          <input
            type="search"
            placeholder="Search name, phone, or email…"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full rounded-lg border border-gray-200 py-2 pl-10 pr-3 text-sm outline-none focus:ring-2 focus:ring-blue-500"
            aria-label="Search customers"
          />
        </div>
      </Card>

      {error ? (
        <div className="mb-4 rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">{error}</div>
      ) : null}

      <Card className="overflow-hidden p-0">
        {loading ? (
          <div className="flex h-40 items-center justify-center">
            <div className="h-8 w-8 animate-spin rounded-full border-b-2 border-blue-600" />
          </div>
        ) : rows.length === 0 ? (
          <div className="flex flex-col items-center justify-center gap-2 py-16 text-center text-gray-500">
            <Users className="h-12 w-12 opacity-30" />
            <p className="font-medium">No customers yet</p>
            <p className="text-sm">Create a customer to use in orders.</p>
            {mayMutate ? (
              <button
                type="button"
                onClick={() => setIsCreateOpen(true)}
                className="mt-2 text-sm font-medium text-blue-600 hover:underline"
              >
                Add customer
              </button>
            ) : null}
          </div>
        ) : (
          <Table columns={columns} data={rows} rowKey={(c) => c.uuid ?? String(c.id)} />
        )}
      </Card>

      <div className="mt-4 flex items-center justify-between text-sm text-gray-600">
        <button
          type="button"
          disabled={page <= 1 || loading}
          onClick={() => setPage((p) => Math.max(1, p - 1))}
          className="rounded-lg border border-gray-200 px-3 py-1.5 hover:bg-gray-50 disabled:opacity-40"
        >
          Previous
        </button>
        <span>Page {page}</span>
        <button
          type="button"
          disabled={!hasMore || loading}
          onClick={() => setPage((p) => p + 1)}
          className="rounded-lg border border-gray-200 px-3 py-1.5 hover:bg-gray-50 disabled:opacity-40"
        >
          Next
        </button>
      </div>

      <CustomerDetailsModal
        isOpen={isDetailsOpen}
        customerId={viewingCustomerId}
        onClose={() => {
          setIsDetailsOpen(false);
          setViewingCustomerId(null);
        }}
        onEdit={(id) => {
          setEditingId(id);
          setIsEditOpen(true);
        }}
        onRequestDelete={(id) => {
          setDeleteId(id);
        }}
        allowEdit={mayMutate}
        allowDelete={mayDelete}
      />
      <Modal isOpen={isCreateOpen} onClose={() => setIsCreateOpen(false)} title="New customer">
        <CustomerForm
          key="customer-create"
          mode="create"
          onCancel={() => setIsCreateOpen(false)}
          onSuccess={async () => {
            setIsCreateOpen(false);
            await load();
          }}
        />
      </Modal>
      <Modal
        isOpen={isEditOpen}
        onClose={() => {
          setIsEditOpen(false);
          setEditingId(null);
        }}
        title="Edit customer"
      >
        <CustomerForm
          key={editingId ?? 'edit'}
          mode="edit"
          customerId={editingId ?? undefined}
          onCancel={() => {
            setIsEditOpen(false);
            setEditingId(null);
          }}
          onSuccess={async () => {
            setIsEditOpen(false);
            setEditingId(null);
            await load();
          }}
        />
      </Modal>
      <Modal isOpen={Boolean(deleteId)} onClose={() => !deleting && setDeleteId(null)} title="Delete customer?">
        <p className="text-sm text-gray-600">This soft-deletes the contact. Orders that reference it may need review.</p>
        <div className="mt-4 flex justify-end gap-2">
          <button
            type="button"
            className="rounded-lg border border-gray-200 px-4 py-2 text-sm"
            disabled={deleting}
            onClick={() => setDeleteId(null)}
          >
            Cancel
          </button>
          <button
            type="button"
            className="rounded-lg bg-red-600 px-4 py-2 text-sm text-white hover:bg-red-700 disabled:opacity-50"
            disabled={deleting}
            onClick={() => void confirmDelete()}
          >
            {deleting ? 'Deleting…' : 'Delete'}
          </button>
        </div>
      </Modal>
    </PageContainer>
  );
};

export default CustomersList;
