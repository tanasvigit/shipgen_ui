import React, { useCallback, useMemo, useState } from 'react';
import { BookUser, Eye, Edit, Trash2 } from 'lucide-react';
import { contactsService } from '../../services/contactsService';
import type { MockContact } from '../../mocks/data/contacts';
import { getContactRouteId } from '../../utils/contactHelpers';
import { ResponsiveTable } from '../ui/ResponsiveTable';
import useListWithCrud from '../../hooks/useListWithCrud';
import { StandardCrudListLayout } from '../patterns/StandardCrudListLayout';
import { PH, SELECT_PH } from '../../constants/formPlaceholders';
import Modal from '../common/Modal';
import RouteDetailsModal from '../common/RouteDetailsModal';
import ContactForm from './forms/ContactForm';

const ContactsList: React.FC = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [typeFilter, setTypeFilter] = useState<string>('');
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [isCreateOpen, setIsCreateOpen] = useState(false);
  const [isEditOpen, setIsEditOpen] = useState(false);
  const [isDetailsOpen, setIsDetailsOpen] = useState(false);
  const [selectedId, setSelectedId] = useState<string | null>(null);

  const load = useCallback(async () => {
    const response = await contactsService.list({ page, pageSize: 20 });
    let rows = response.data;
    if (typeFilter) rows = rows.filter((c) => c.type === typeFilter);
    setTotalPages(Math.max(1, Math.ceil((response.pagination?.total || 0) / 20)));
    return rows;
  }, [page, typeFilter]);

  const { rows: contacts, loading, error, actionError, deleteWithConfirm, reload } = useListWithCrud<MockContact>(load, [load]);

  const q = searchTerm.trim().toLowerCase();
  const filtered = useMemo(() => {
    return contacts.filter((c) => {
      if (!q) return true;
      const name = (c.name ?? '').toLowerCase();
      const phone = (c.phone ?? '').toLowerCase();
      const email = (c.email ?? '').toLowerCase();
      const uuid = (c.uuid ?? '').toLowerCase();
      return (
        name.includes(q) ||
        phone.includes(q) ||
        email.includes(q) ||
        uuid.includes(q) ||
        String(c.id ?? '').includes(q)
      );
    });
  }, [contacts, q]);

  return (
    <>
      <StandardCrudListLayout
        title="Contacts"
        subtitle="fleetops-contacts (mock: /contacts)"
        createOnClick={() => setIsCreateOpen(true)}
        createLabel="New Contact"
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
              <option value="">All types</option>
              <option value="contact">contact</option>
              <option value="vendor">vendor</option>
            </select>
          </div>
        }
        searchPlaceholder={PH.searchContacts}
        searchTerm={searchTerm}
        onSearchChange={setSearchTerm}
        error={error}
        actionError={actionError}
        loading={loading}
        rowCount={contacts.length}
        filteredCount={filtered.length}
        emptyIcon={BookUser}
        emptyTitleNoData="No contacts yet"
        emptyTitleNoMatch="No matching contacts"
        emptyDescriptionNoData="Create contacts for drivers, customers, and partners."
        emptyDescriptionNoMatch="Try another search or type filter."
        emptyAction={
          <button
            type="button"
            onClick={() => setIsCreateOpen(true)}
            className="inline-flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2 text-sm text-white hover:bg-blue-700"
          >
            New contact
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
        failedLoadTitle="Could not load contacts"
      >
        <ResponsiveTable
          data={filtered}
          keyExtractor={(c) => getContactRouteId(c) || String(c.id)}
          columns={[
            {
              key: 'uuid',
              header: 'uuid',
              render: (c) => (
                <span className="table-cell-ellipsis block font-mono text-xs text-gray-700" title={c.uuid ?? ''}>
                  {c.uuid ?? '—'}
                </span>
              ),
            },
            { key: 'name', header: 'name', render: (c) => <span className="text-sm text-gray-900">{c.name ?? '—'}</span> },
            {
              key: 'title',
              header: 'title',
              render: (c) => <span className="text-sm text-gray-700">{c.title ?? '—'}</span>,
              mobileHidden: true,
            },
            {
              key: 'email',
              header: 'email',
              render: (c) => (
                <span className="table-cell-ellipsis block text-sm text-gray-700" title={c.email ?? ''}>
                  {c.email ?? '—'}
                </span>
              ),
            },
            { key: 'phone', header: 'phone', render: (c) => <span className="text-sm text-gray-700">{c.phone ?? '—'}</span> },
            {
              key: 'type',
              header: 'type',
              render: (c) => <span className="text-sm text-gray-700">{c.type ?? '—'}</span>,
              mobileHidden: true,
            },
            {
              key: 'actions',
              header: 'actions',
              render: (c) => {
                const rid = getContactRouteId(c);
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
                        void deleteWithConfirm(rid, (id) => contactsService.remove(id), {
                          confirmMessage: 'Delete this contact?',
                          successMessage: 'Contact deleted',
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
      <Modal isOpen={isCreateOpen} onClose={() => setIsCreateOpen(false)} title="Create Contact">
        <ContactForm mode="create" onCancel={() => setIsCreateOpen(false)} onSuccess={async () => {
          setIsCreateOpen(false);
          await reload();
        }} />
      </Modal>
      <Modal isOpen={isEditOpen} onClose={() => setIsEditOpen(false)} title="Edit Contact">
        <ContactForm mode="edit" contactId={selectedId ?? undefined} onCancel={() => setIsEditOpen(false)} onSuccess={async () => {
          setIsEditOpen(false);
          setSelectedId(null);
          await reload();
        }} />
      </Modal>
      <RouteDetailsModal
        isOpen={isDetailsOpen}
        onClose={() => setIsDetailsOpen(false)}
        title="Contact Details"
        routePath={selectedId ? `/fleet/contacts/${encodeURIComponent(selectedId)}` : null}
        headerTitle="Contact Details"
        headerSubtitle={selectedId ?? undefined}
        onDelete={async () => {
          if (!selectedId) return;
          await deleteWithConfirm(selectedId, (id) => contactsService.remove(id), {
            confirmMessage: 'Delete this contact?',
            successMessage: 'Contact deleted',
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
        editLabel="Edit Contact"
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

export default ContactsList;
