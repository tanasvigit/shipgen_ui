import React, { useCallback, useEffect, useState } from 'react';
import { AlertCircle, RefreshCw } from 'lucide-react';
import Modal from '../common/Modal';
import { Button } from '../ui/Button';
import { customersService } from '../../services/customersService';
import type { UiCustomer } from '../../services/customersService';

const addressLine = (c: UiCustomer | null): string => {
  if (!c) return '—';
  const m = (c.meta ?? {}) as Record<string, unknown>;
  return typeof m.address === 'string' ? m.address : '—';
};

export interface CustomerDetailsModalProps {
  isOpen: boolean;
  customerId: string | null;
  onClose: () => void;
  onEdit: (customerId: string) => void;
  /** Called when user confirms delete from the toolbar; parent should open confirm dialog. */
  onRequestDelete: (id: string) => void;
  allowEdit?: boolean;
  allowDelete?: boolean;
}

const CustomerDetailsModal: React.FC<CustomerDetailsModalProps> = ({
  isOpen,
  customerId,
  onClose,
  onEdit,
  onRequestDelete,
  allowEdit = true,
  allowDelete = true,
}) => {
  const [customer, setCustomer] = useState<UiCustomer | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    if (!customerId || !isOpen) return;
    try {
      setLoading(true);
      setError(null);
      const c = await customersService.getById(customerId);
      setCustomer(c);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Failed to load customer');
      setCustomer(null);
    } finally {
      setLoading(false);
    }
  }, [customerId, isOpen]);

  useEffect(() => {
    if (!isOpen) {
      setCustomer(null);
      setError(null);
      return;
    }
    void load();
  }, [isOpen, customerId, load]);

  const handleDelete = () => {
    if (!customerId) return;
    onClose();
    onRequestDelete(customerId);
  };

  const handleEdit = () => {
    if (!customerId) return;
    const id = customerId;
    onClose();
    onEdit(id);
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="Customer details"
      titleEnd={
        <div className="flex flex-shrink-0 flex-wrap items-center justify-end gap-2">
          {allowDelete ? (
            <Button size="sm" variant="danger" onClick={handleDelete} disabled={!customerId || loading}>
              Delete
            </Button>
          ) : null}
          {allowEdit ? (
            <Button size="sm" onClick={handleEdit} disabled={!customerId || loading}>
              Edit
            </Button>
          ) : null}
          <Button variant="outline" size="sm" icon={RefreshCw} onClick={() => void load()} disabled={!customerId}>
            Refresh
          </Button>
        </div>
      }
    >
      {loading ? <p className="text-sm text-gray-600">Loading details…</p> : null}
      {error ? (
        <div className="flex items-center gap-2 rounded-md border border-red-200 bg-red-50 p-3 text-sm text-red-700">
          <AlertCircle size={16} />
          {error}
        </div>
      ) : null}
      {!loading && !error && customer ? (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <div className="sm:col-span-2">
            <p className="text-xs font-semibold uppercase text-gray-500">Name</p>
            <p className="mt-1 text-sm text-gray-900">{customer.name ?? '—'}</p>
          </div>
          <div>
            <p className="text-xs font-semibold uppercase text-gray-500">Phone</p>
            <p className="mt-1 text-sm text-gray-900">{customer.phone ?? '—'}</p>
          </div>
          <div>
            <p className="text-xs font-semibold uppercase text-gray-500">Email</p>
            <p className="mt-1 text-sm text-gray-900">{customer.email ?? '—'}</p>
          </div>
          <div className="sm:col-span-2">
            <p className="text-xs font-semibold uppercase text-gray-500">Address</p>
            <p className="mt-1 text-sm text-gray-900 whitespace-pre-wrap">{addressLine(customer)}</p>
          </div>
          <div>
            <p className="text-xs font-semibold uppercase text-gray-500">Public ID</p>
            <p className="mt-1 font-mono text-sm text-gray-700">{customer.public_id ?? '—'}</p>
          </div>
          <div>
            <p className="text-xs font-semibold uppercase text-gray-500">UUID</p>
            <p className="mt-1 break-all font-mono text-xs text-gray-700">{customer.uuid ?? '—'}</p>
          </div>
        </div>
      ) : null}
    </Modal>
  );
};

export default CustomerDetailsModal;
