import React, { useEffect, useState } from 'react';
import { AlertCircle, Calendar, RefreshCw } from 'lucide-react';
import Modal from '../common/Modal';
import { ordersService, orderCustomerLabel, UiOrder, UiOrderLifecycleEvent } from '../../services/ordersService';
import { Button } from '../ui/Button';
import StatusBadge from '../ui/StatusBadge';
import EntityLink from '../common/EntityLink';

interface OrderDetailsModalProps {
  isOpen: boolean;
  orderId: string | null;
  onClose: () => void;
}

const getStatusVariant = (status: string): 'success' | 'pending' | 'failed' | 'neutral' => {
  const normalized = (status || '').toLowerCase();
  if (['completed', 'delivered', 'success', 'paid'].includes(normalized)) return 'success';
  if (['created', 'scheduled', 'pending', 'in_progress'].includes(normalized)) return 'pending';
  if (['cancelled', 'failed', 'error'].includes(normalized)) return 'failed';
  return 'neutral';
};

const formatDateTime = (value?: string) => {
  if (!value) return '-';
  const d = new Date(value);
  return Number.isNaN(d.getTime()) ? '-' : d.toLocaleString();
};

const OrderDetailsModal: React.FC<OrderDetailsModalProps> = ({ isOpen, orderId, onClose }) => {
  const [order, setOrder] = useState<UiOrder | null>(null);
  const [lifecycle, setLifecycle] = useState<UiOrderLifecycleEvent[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const load = async () => {
    if (!orderId || !isOpen) return;
    try {
      setLoading(true);
      setError(null);
      const [orderResponse, lifecycleResponse] = await Promise.all([
        ordersService.getById(orderId),
        ordersService.lifecycle(orderId),
      ]);
      setOrder(orderResponse);
      setLifecycle(lifecycleResponse);
    } catch (err: any) {
      setError(err?.message || 'Failed to load order details');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (!isOpen) return;
    void load();
  }, [isOpen, orderId]);

  const refs = ((order?.meta as unknown) as Record<string, unknown>) ?? {};
  const driverId = String(order?.driver_assigned_uuid || refs.driver_uuid || refs.driver_id || '');
  const vehicleId = String(order?.vehicle_assigned_uuid || refs.vehicle_uuid || refs.vehicle_id || '');
  const vendorId = String(refs.vendor_uuid ?? refs.vendor_id ?? '');
  const pickupPlaceId = String(refs.pickup_place_uuid ?? refs.pickup_place_id ?? '');
  const dropPlaceId = String(refs.drop_place_uuid ?? refs.drop_place_id ?? '');

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Order Details">
      {loading ? <p className="text-sm text-gray-600">Loading details...</p> : null}
      {error ? (
        <div className="rounded-md border border-red-200 bg-red-50 p-3 text-sm text-red-700">{error}</div>
      ) : null}
      {!loading && !error && order ? (
        <div className="space-y-5">
          <div className="flex items-center justify-between">
            <p className="text-sm font-semibold text-primary-700">{order.internal_id || order.public_id || order.id}</p>
            <Button variant="outline" size="sm" icon={RefreshCw} onClick={() => void load()}>
              Refresh
            </Button>
          </div>

          <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
            <div>
              <label className="text-xs uppercase text-gray-500">Status</label>
              <div className="mt-1">
                <StatusBadge label={order.status} variant={getStatusVariant(order.status)} />
              </div>
            </div>
            <div>
              <label className="text-xs uppercase text-gray-500">Type</label>
              <p className="text-sm capitalize">{order.type || '-'}</p>
            </div>
            <div>
              <label className="text-xs uppercase text-gray-500">Customer</label>
              <p className="text-sm">{orderCustomerLabel(order)}</p>
            </div>
            <div>
              <label className="text-xs uppercase text-gray-500">Priority</label>
              <p className="text-sm capitalize">{order.meta?.priority || '-'}</p>
            </div>
            <div>
              <label className="text-xs uppercase text-gray-500">Scheduled At</label>
              <p className="text-sm flex items-center gap-1">
                <Calendar size={12} />
                {formatDateTime(order.scheduled_at)}
              </p>
            </div>
            <div>
              <label className="text-xs uppercase text-gray-500">POD Required</label>
              <p className="text-sm">{order.options?.pod_required ? 'Yes' : 'No'}</p>
            </div>
          </div>

          <div>
            <label className="text-xs uppercase text-gray-500">Related Links</label>
            <div className="mt-1 flex flex-wrap gap-x-4 gap-y-2 text-sm">
              <EntityLink id={driverId} label="Driver" to="/fleet/drivers" title="View Driver" />
              <EntityLink id={vehicleId} label="Vehicle" to="/fleet/vehicles" title="View Vehicle" />
              <EntityLink id={vendorId} label="Vendor" to="/fleet/vendors" title="View Vendor" />
              <EntityLink id={pickupPlaceId} label="Pickup Place" to="/fleet/places" title="View Pickup Place" />
              <EntityLink id={dropPlaceId} label="Drop Place" to="/fleet/places" title="View Drop Place" />
            </div>
          </div>

          <div>
            <label className="text-xs uppercase text-gray-500">Notes</label>
            <p className="text-sm whitespace-pre-wrap">{order.notes || '-'}</p>
          </div>

          <div>
            <p className="mb-2 text-sm font-semibold text-gray-900">Lifecycle Timeline</p>
            {lifecycle.length === 0 ? (
              <p className="text-sm text-gray-500">No lifecycle events captured yet.</p>
            ) : (
              <div className="space-y-2">
                {lifecycle.map((evt) => (
                  <div key={evt.uuid || `${evt.event_type}-${evt.created_at}`} className="rounded-md border border-gray-100 p-3">
                    <div className="flex items-center justify-between gap-3">
                      <p className="text-sm font-medium text-gray-900">{evt.event_type}</p>
                      <p className="text-xs text-gray-500">{formatDateTime(evt.created_at)}</p>
                    </div>
                    <p className="text-xs text-gray-600">
                      {evt.from_status || '-'} {evt.to_status ? `-> ${evt.to_status}` : ''}
                    </p>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      ) : null}
      {!loading && !error && !order ? (
        <div className="flex items-center gap-2 text-sm text-gray-500">
          <AlertCircle size={16} />
          No order selected.
        </div>
      ) : null}
    </Modal>
  );
};

export default OrderDetailsModal;

