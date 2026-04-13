import React, { useEffect, useState } from 'react';
import { AlertCircle, Calendar, RefreshCw } from 'lucide-react';
import Modal from '../common/Modal';
import { ordersService, orderCustomerLabel, UiOrder, UiOrderLifecycleEvent } from '../../services/ordersService';
import { Button } from '../ui/Button';
import StatusBadge from '../ui/StatusBadge';
import EntityLink from '../common/EntityLink';
import RouteDetailsModal from '../common/RouteDetailsModal';
import { driversService } from '../../services/driversService';
import { vehiclesService } from '../../services/vehiclesService';
import { UserRole } from '../../types';
import { getStoredUserRole } from '../../utils/roleAccess';

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
  const role = getStoredUserRole() ?? UserRole.VIEWER;
  const isFleetCustomer = role === UserRole.FLEET_CUSTOMER;
  const [order, setOrder] = useState<UiOrder | null>(null);
  const [lifecycle, setLifecycle] = useState<UiOrderLifecycleEvent[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [resolvedDriverName, setResolvedDriverName] = useState<string>('');
  const [resolvedVehicleName, setResolvedVehicleName] = useState<string>('');
  const [resolvedVehicleNumber, setResolvedVehicleNumber] = useState<string>('');
  const [relatedDetailsPath, setRelatedDetailsPath] = useState<string | null>(null);
  const [relatedDetailsTitle, setRelatedDetailsTitle] = useState<string>('Details');
  const [relatedDetailsSubtitle, setRelatedDetailsSubtitle] = useState<string | undefined>(undefined);

  const load = async () => {
    if (!orderId || !isOpen) return;
    try {
      setLoading(true);
      setError(null);
      const orderResponse = await ordersService.getById(orderId);
      // Do not block the whole modal if lifecycle endpoint fails.
      let lifecycleResponse: UiOrderLifecycleEvent[] = [];
      try {
        lifecycleResponse = await ordersService.lifecycle(orderId);
      } catch {
        lifecycleResponse = [];
      }
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

  useEffect(() => {
    let active = true;
    const resolveAssignmentDetails = async () => {
      const refs = ((order?.meta as unknown) as Record<string, unknown>) ?? {};
      const driverId = String(order?.driver_assigned_uuid || refs.driver_uuid || refs.driver_id || '').trim();
      const vehicleId = String(order?.vehicle_assigned_uuid || refs.vehicle_uuid || refs.vehicle_id || '').trim();

      const initialDriverName = String(order?.driver_assigned_name ?? refs.driver_name ?? '').trim();
      const initialVehicleName = String(order?.vehicle_assigned_name ?? refs.vehicle_name ?? '').trim();
      const initialVehicleNumber = String(
        order?.vehicle_assigned_number ?? refs.vehicle_number ?? refs.vehicle_plate ?? refs.plate_number ?? '',
      ).trim();

      if (active) {
        setResolvedDriverName(initialDriverName);
        setResolvedVehicleName(initialVehicleName);
        setResolvedVehicleNumber(initialVehicleNumber);
      }

      if (!initialDriverName && driverId) {
        try {
          const driver = await driversService.getById(driverId);
          if (active && driver.name?.trim()) setResolvedDriverName(driver.name.trim());
        } catch {
          // Keep fallback to id.
        }
      }

      if (vehicleId && (!initialVehicleName || !initialVehicleNumber)) {
        try {
          const vehicle = await vehiclesService.getById(vehicleId);
          const name = [vehicle.make?.trim(), vehicle.model?.trim()].filter(Boolean).join(' ').trim();
          if (active) {
            if (name) setResolvedVehicleName(name);
            if (vehicle.plate_number?.trim()) setResolvedVehicleNumber(vehicle.plate_number.trim());
          }
        } catch {
          // Keep fallback to id.
        }
      }
    };

    if (!order) {
      setResolvedDriverName('');
      setResolvedVehicleName('');
      setResolvedVehicleNumber('');
      return () => {
        active = false;
      };
    }

    void resolveAssignmentDetails();
    return () => {
      active = false;
    };
  }, [order]);

  const refs = ((order?.meta as unknown) as Record<string, unknown>) ?? {};
  const driverId = String(order?.driver_assigned_uuid || refs.driver_uuid || refs.driver_id || '');
  const vehicleId = String(order?.vehicle_assigned_uuid || refs.vehicle_uuid || refs.vehicle_id || '');
  const driverName = resolvedDriverName || String(order?.driver_assigned_name ?? refs.driver_name ?? '').trim();
  const vehicleName = resolvedVehicleName || String(order?.vehicle_assigned_name ?? refs.vehicle_name ?? '').trim();
  const vehicleNumber =
    resolvedVehicleNumber ||
    String(order?.vehicle_assigned_number ?? refs.vehicle_number ?? refs.vehicle_plate ?? refs.plate_number ?? '').trim();
  const vendorId = String(refs.vendor_uuid ?? refs.vendor_id ?? '');
  const pickupPlaceId = String(refs.pickup_place_uuid ?? refs.pickup_place_id ?? '');
  const dropPlaceId = String(refs.drop_place_uuid ?? refs.drop_place_id ?? '');
  const pickupAddr = order?.meta?.pickup?.address?.trim() || String(order?.meta?.pickup_location ?? '').trim();
  const deliveryAddr = order?.meta?.delivery?.address?.trim() || String(order?.meta?.drop_location ?? '').trim();
  const goodsMeta = String(order?.meta?.goods_description ?? '').trim();
  const showGoodsBlock = Boolean(goodsMeta && goodsMeta !== String(order?.notes ?? '').trim());
  const openRelatedDetails = (kind: 'driver' | 'vehicle', entityId?: string) => {
    const value = String(entityId || '').trim();
    if (!value) return;
    if (kind === 'driver') {
      setRelatedDetailsTitle('Driver Details');
      setRelatedDetailsSubtitle(driverName || value);
      setRelatedDetailsPath(`/fleet/drivers/${encodeURIComponent(value)}`);
      return;
    }
    setRelatedDetailsTitle('Vehicle Details');
    setRelatedDetailsSubtitle(`${vehicleName || value}${vehicleNumber ? ` (${vehicleNumber})` : ''}`);
    setRelatedDetailsPath(`/fleet/vehicles/${encodeURIComponent(value)}`);
  };

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
              <label className="text-xs uppercase text-gray-500">Internal ID</label>
              <p className="text-sm">{order.internal_id || '-'}</p>
            </div>
            <div>
              <label className="text-xs uppercase text-gray-500">Public ID</label>
              <p className="text-sm">{order.public_id || '-'}</p>
            </div>
            <div>
              <label className="text-xs uppercase text-gray-500">Status</label>
              <div className="mt-1">
                <StatusBadge label={order.status} variant={getStatusVariant(order.status)} />
              </div>
            </div>
            <div>
              <label className="text-xs uppercase text-gray-500">Driver Name</label>
              <p className="text-sm">{driverName || driverId || '-'}</p>
            </div>
            <div>
              <label className="text-xs uppercase text-gray-500">Vehicle</label>
              <p className="text-sm">
                {vehicleName || vehicleId || '-'}
                {vehicleNumber ? ` (${vehicleNumber})` : ''}
              </p>
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
              <label className="text-xs uppercase text-gray-500">Placed By</label>
              <p className="text-sm">{order.created_by_display_name || order.created_by || '-'}</p>
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
            <div>
              <label className="text-xs uppercase text-gray-500">Name</label>
              <p className="text-sm">{orderCustomerLabel(order)}</p>
            </div>
            <div>
              <label className="text-xs uppercase text-gray-500">Created At</label>
              <p className="text-sm">{formatDateTime(order.created_at)}</p>
            </div>
            <div>
              <label className="text-xs uppercase text-gray-500">Updated At</label>
              <p className="text-sm">{formatDateTime(order.updated_at)}</p>
            </div>
          </div>

          {(pickupAddr || deliveryAddr) && (
            <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
              <div>
                <label className="text-xs uppercase text-gray-500">Pickup</label>
                <p className="text-sm whitespace-pre-wrap">{pickupAddr || '-'}</p>
              </div>
              <div>
                <label className="text-xs uppercase text-gray-500">Delivery</label>
                <p className="text-sm whitespace-pre-wrap">{deliveryAddr || '-'}</p>
              </div>
            </div>
          )}

          {showGoodsBlock ? (
            <div>
              <label className="text-xs uppercase text-gray-500">Goods / Service</label>
              <p className="text-sm whitespace-pre-wrap">{goodsMeta}</p>
            </div>
          ) : null}

          {isFleetCustomer ? (
            driverName || vehicleName || vehicleNumber ? (
              <div>
                <label className="text-xs uppercase text-gray-500">Assignment</label>
                <div className="mt-2 grid grid-cols-1 gap-2 text-sm md:grid-cols-2">
                  {driverName ? (
                    <p className="text-gray-700">
                      <span className="font-medium">Driver:</span> {driverName}
                    </p>
                  ) : null}
                  {vehicleName || vehicleNumber ? (
                    <p className="text-gray-700">
                      <span className="font-medium">Vehicle:</span> {vehicleName || 'Vehicle'}
                      {vehicleNumber ? ` (${vehicleNumber})` : ''}
                    </p>
                  ) : null}
                </div>
              </div>
            ) : null
          ) : (
            <div>
              <label className="text-xs uppercase text-gray-500">Related Links</label>
              <div className="mt-2 grid grid-cols-1 gap-2 text-sm md:grid-cols-2">
                <p className="text-gray-700">
                  <span className="font-medium">Driver:</span> {driverName || driverId || '-'}
                </p>
                <p className="text-gray-700">
                  <span className="font-medium">Vehicle:</span> {vehicleName || vehicleId || '-'}
                  {vehicleNumber ? ` (${vehicleNumber})` : ''}
                </p>
              </div>
              <div className="mt-1 flex flex-wrap gap-x-4 gap-y-2 text-sm">
                {driverId ? (
                  <button
                    type="button"
                    onClick={() => openRelatedDetails('driver', driverId)}
                    className="text-blue-600 hover:underline cursor-pointer"
                    title="View Driver"
                  >
                    Driver
                  </button>
                ) : (
                  <span className="text-gray-500">Driver —</span>
                )}
                {vehicleId ? (
                  <button
                    type="button"
                    onClick={() => openRelatedDetails('vehicle', vehicleId)}
                    className="text-blue-600 hover:underline cursor-pointer"
                    title="View Vehicle"
                  >
                    Vehicle
                  </button>
                ) : (
                  <span className="text-gray-500">Vehicle —</span>
                )}
                <EntityLink id={vendorId} label="Vendor" to="/fleet/vendors" title="View Vendor" />
                <EntityLink id={pickupPlaceId} label="Pickup Place" to="/fleet/places" title="View Pickup Place" />
                <EntityLink id={dropPlaceId} label="Drop Place" to="/fleet/places" title="View Drop Place" />
              </div>
            </div>
          )}

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
      <RouteDetailsModal
        isOpen={Boolean(relatedDetailsPath)}
        onClose={() => setRelatedDetailsPath(null)}
        title={relatedDetailsTitle}
        routePath={relatedDetailsPath}
        headerTitle={relatedDetailsTitle}
        headerSubtitle={relatedDetailsSubtitle}
      />
    </Modal>
  );
};

export default OrderDetailsModal;

