import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { 
  Calendar, ArrowLeft, AlertCircle, Edit
} from 'lucide-react';
import { driversService, UiDriver } from '../../services/driversService';
import { vehiclesService } from '../../services/vehiclesService';
import { ordersService, orderCustomerLabel, UiOrder, UiOrderLifecycleEvent } from '../../services/ordersService';
import { Skeleton } from '../ui/LoadingSkeleton';
import { EmptyState } from '../ui/EmptyState';
import { Button } from '../ui/Button';
import StatusBadge from '../ui/StatusBadge';
import EntityLink from '../common/EntityLink';
import RouteDetailsModal from '../common/RouteDetailsModal';
import SelectField from '../ui/SelectField';
import { useToast } from '../ui/ToastProvider';
import { UserRole } from '../../types';
import { canAssignOrDispatchOrders, getStoredUserRole } from '../../utils/roleAccess';

const OrderDetail: React.FC = () => {
  const { showToast } = useToast();
  const role = getStoredUserRole() ?? UserRole.VIEWER;
  const isStaffAssign = canAssignOrDispatchOrders(role);
  const isDriver = role === UserRole.DRIVER;
  const isViewer = role === UserRole.VIEWER;
  const isFleetCustomer = role === UserRole.FLEET_CUSTOMER;
  const { id } = useParams<{ id: string }>();
  const [order, setOrder] = useState<UiOrder | null>(null);
  const [drivers, setDrivers] = useState<UiDriver[]>([]);
  const [lifecycle, setLifecycle] = useState<UiOrderLifecycleEvent[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [assignDriverId, setAssignDriverId] = useState('');
  const [assigning, setAssigning] = useState(false);
  const [transitioning, setTransitioning] = useState(false);
  const [nextStatus, setNextStatus] = useState('dispatched');
  const [creatingException, setCreatingException] = useState(false);
  const [exceptionTitle, setExceptionTitle] = useState('');
  const [exceptionReport, setExceptionReport] = useState('');
  const [exceptionPriority, setExceptionPriority] = useState('medium');
  const [reassignDriverId, setReassignDriverId] = useState('');
  const [resolvedDriverName, setResolvedDriverName] = useState<string>('');
  const [resolvedVehicleName, setResolvedVehicleName] = useState<string>('');
  const [resolvedVehicleNumber, setResolvedVehicleNumber] = useState<string>('');
  const [relatedDetailsPath, setRelatedDetailsPath] = useState<string | null>(null);
  const [relatedDetailsTitle, setRelatedDetailsTitle] = useState<string>('Details');
  const [relatedDetailsSubtitle, setRelatedDetailsSubtitle] = useState<string | undefined>(undefined);

  useEffect(() => {
    if (id) {
      void loadOrder();
    }
  }, [id]);

  useEffect(() => {
    let active = true;
    const resolveAssignmentDetails = async () => {
      setResolvedDriverName('');
      setResolvedVehicleName('');
      setResolvedVehicleNumber('');
      if (!order) return;

      const meta = ((order.meta as unknown) as Record<string, unknown>) ?? {};
      const initialDriverName =
        String(order.driver_assigned_name ?? '').trim() || String(meta.driver_name ?? '').trim();
      const initialVehicleName =
        String(order.vehicle_assigned_name ?? '').trim() || String(meta.vehicle_name ?? '').trim();
      const initialVehicleNumber =
        String(order.vehicle_assigned_number ?? '').trim() ||
        String(meta.vehicle_number ?? meta.vehicle_plate ?? meta.plate_number ?? '').trim();

      if (active) {
        setResolvedDriverName(initialDriverName);
        setResolvedVehicleName(initialVehicleName);
        setResolvedVehicleNumber(initialVehicleNumber);
      }

      if (!initialDriverName && order.driver_assigned_uuid) {
        const fromLoadedDrivers = drivers.find((d) => d.id === order.driver_assigned_uuid);
        if (fromLoadedDrivers?.name?.trim()) {
          if (active) setResolvedDriverName(fromLoadedDrivers.name.trim());
        } else {
          try {
            const driver = await driversService.getById(order.driver_assigned_uuid);
            if (active && driver.name?.trim()) setResolvedDriverName(driver.name.trim());
          } catch {
            // Keep fallback UUID rendering in UI.
          }
        }
      }

      if (order.vehicle_assigned_uuid && (!initialVehicleName || !initialVehicleNumber)) {
        try {
          const vehicle = await vehiclesService.getById(order.vehicle_assigned_uuid);
          const name = [vehicle.make?.trim(), vehicle.model?.trim()].filter(Boolean).join(' ').trim();
          if (active) {
            if (name) setResolvedVehicleName(name);
            if (vehicle.plate_number?.trim()) setResolvedVehicleNumber(vehicle.plate_number.trim());
          }
        } catch {
          // Keep fallback UUID rendering in UI.
        }
      }
    };
    void resolveAssignmentDetails();
    return () => {
      active = false;
    };
  }, [order, drivers]);

  const loadOrder = async () => {
    try {
      setLoading(true);
      setError(null);
      const r = getStoredUserRole() ?? UserRole.VIEWER;
      const needDrivers = r !== UserRole.DRIVER;
      const [orderResponse, driverResponse] = await Promise.all([
        ordersService.getById(id!),
        needDrivers
          ? driversService.list({ page: 1, pageSize: 100, status: 'active' })
          : Promise.resolve({
              data: [] as UiDriver[],
              pagination: { total: 0, page: 1, pageSize: 100 },
            }),
      ]);
      let lifecycleResponse: UiOrderLifecycleEvent[] = [];
      try {
        lifecycleResponse = await ordersService.lifecycle(id!);
      } catch {
        lifecycleResponse = [];
      }
      setOrder(orderResponse);
      setLifecycle(lifecycleResponse);
      setDrivers(driverResponse.data);
      setAssignDriverId(orderResponse.driver_assigned_uuid || '');
      setLoading(false);
    } catch (err: any) {
      setError(err.message || 'Failed to load order');
      setLoading(false);
    }
  };

  const refreshOrder = async () => {
    const orderResponse = await ordersService.getById(id!);
    let lifecycleResponse: UiOrderLifecycleEvent[] = [];
    try {
      lifecycleResponse = await ordersService.lifecycle(id!);
    } catch {
      lifecycleResponse = [];
    }
    setOrder(orderResponse);
    setLifecycle(lifecycleResponse);
    setAssignDriverId(orderResponse.driver_assigned_uuid || '');
  };

  const transitionCandidates = (currentStatus: string): string[] => {
    const all = [
      'assigned',
      'dispatched',
      'arrived_at_pickup',
      'picked_up',
      'in_transit',
      'out_for_delivery',
      'delivered',
      'completed',
      'cancelled',
      'failed',
    ];
    const status = (currentStatus || 'created').toLowerCase();
    const ordered = [
      'created',
      'assigned',
      'dispatched',
      'arrived_at_pickup',
      'picked_up',
      'in_transit',
      'out_for_delivery',
      'delivered',
      'completed',
    ];
    const idx = ordered.indexOf(status);
    if (idx === -1) return all;
    return [...ordered.slice(idx + 1), 'cancelled', 'failed'];
  };

  const handleAssign = async () => {
    if (!id) return;
    try {
      setAssigning(true);
      if (assignDriverId) {
        await ordersService.assign(id, { driver_uuid: assignDriverId, mode: 'manual' });
      } else {
        await ordersService.assign(id, { mode: 'auto' });
      }
      await refreshOrder();
      showToast('Order assigned successfully', 'success');
    } catch (err: any) {
      showToast(err?.message || 'Failed to assign order', 'error');
    } finally {
      setAssigning(false);
    }
  };

  const handleTransition = async () => {
    if (!id || !nextStatus) return;
    const r = getStoredUserRole() ?? UserRole.VIEWER;
    if (r !== UserRole.DRIVER && (!order?.driver_assigned_uuid || !order?.vehicle_assigned_uuid)) {
      showToast('Assign driver and vehicle before proceeding', 'info');
      return;
    }
    if (r === UserRole.DRIVER && !order?.driver_assigned_uuid) {
      showToast('Order is not assigned to you', 'info');
      return;
    }
    try {
      setTransitioning(true);
      await ordersService.transition(id, { to_status: nextStatus });
      await refreshOrder();
      showToast(`Order moved to ${nextStatus}`, 'success');
    } catch (err: any) {
      showToast(err?.message || 'Failed to transition order', 'error');
    } finally {
      setTransitioning(false);
    }
  };

  const handleException = async () => {
    if (!id || !exceptionTitle.trim() || !exceptionReport.trim()) return;
    try {
      setCreatingException(true);
      await ordersService.createException(id, {
        title: exceptionTitle.trim(),
        report: exceptionReport.trim(),
        priority: exceptionPriority,
        reassign_driver_uuid: reassignDriverId || undefined,
      });
      setExceptionTitle('');
      setExceptionReport('');
      setExceptionPriority('medium');
      setReassignDriverId('');
      await refreshOrder();
      showToast('Order exception created', 'success');
    } catch (err: any) {
      showToast(err?.message || 'Failed to create order exception', 'error');
    } finally {
      setCreatingException(false);
    }
  };

  if (loading) {
    return (
      <div className="p-6 space-y-6">
        <div className="bg-white rounded-xl border border-gray-200 shadow-soft p-6">
          <Skeleton variant="text" width={220} height={28} className="mb-4" />
          <Skeleton variant="text" width="100%" height={16} className="mb-2" />
          <Skeleton variant="text" width="85%" height={16} className="mb-2" />
          <Skeleton variant="text" width="70%" height={16} />
        </div>
      </div>
    );
  }

  if (error || !order) {
    return (
      <div className="p-6">
        <div className="bg-white rounded-xl border border-gray-200 shadow-soft">
          <EmptyState
            icon={AlertCircle}
            title="Order not found"
            description={error || 'The requested order could not be loaded.'}
            action={
              <Link to="/logistics/orders">
                <Button variant="outline" icon={ArrowLeft}>Back to Orders</Button>
              </Link>
            }
          />
        </div>
      </div>
    );
  }

  const getStatusVariant = (status: string): 'success' | 'pending' | 'failed' | 'neutral' => {
    const normalized = (status || '').toLowerCase();
    if (['completed', 'delivered', 'success', 'paid'].includes(normalized)) return 'success';
    if (['created', 'scheduled', 'pending', 'in_progress'].includes(normalized)) return 'pending';
    if (['cancelled', 'failed', 'error'].includes(normalized)) return 'failed';
    return 'neutral';
  };

  const formatDateTime = (value?: string) => {
    if (!value) return '—';
    const d = new Date(value);
    return Number.isNaN(d.getTime()) ? '—' : d.toLocaleString();
  };

  const refs = ((order.meta as unknown) as Record<string, unknown>) ?? {};
  const driverId = String(refs.driver_uuid ?? refs.driver_id ?? '');
  const vehicleId = String(refs.vehicle_uuid ?? refs.vehicle_id ?? '');
  const vendorId = String(refs.vendor_uuid ?? refs.vendor_id ?? '');
  const pickupPlaceId = String(refs.pickup_place_uuid ?? refs.pickup_place_id ?? '');
  const dropPlaceId = String(refs.drop_place_uuid ?? refs.drop_place_id ?? '');
  const hasAssignment = Boolean(order.driver_assigned_uuid && order.vehicle_assigned_uuid);
  const pickupAddr = order.meta?.pickup?.address?.trim() || String(order.meta?.pickup_location ?? '').trim();
  const deliveryAddr = order.meta?.delivery?.address?.trim() || String(order.meta?.drop_location ?? '').trim();
  const goodsMeta = String(order.meta?.goods_description ?? '').trim();
  const showGoodsBlock = Boolean(goodsMeta && goodsMeta !== (order.notes || '').trim());
  const openRelatedDetails = (kind: 'driver' | 'vehicle', entityId?: string) => {
    const value = String(entityId || '').trim();
    if (!value) return;
    if (kind === 'driver') {
      setRelatedDetailsTitle('Driver Details');
      setRelatedDetailsSubtitle(resolvedDriverName || value);
      setRelatedDetailsPath(`/fleet/drivers/${encodeURIComponent(value)}`);
      return;
    }
    setRelatedDetailsTitle('Vehicle Details');
    setRelatedDetailsSubtitle(
      `${resolvedVehicleName || value}${resolvedVehicleNumber ? ` (${resolvedVehicleNumber})` : ''}`,
    );
    setRelatedDetailsPath(`/fleet/vehicles/${encodeURIComponent(value)}`);
  };

  return (
    <div className="p-6 space-y-6">
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          {/* Order Information */}
          <div className="bg-white rounded-xl border border-gray-200 shadow-soft p-6">
            <h2 className="text-lg font-bold text-gray-900 mb-4">Order Information</h2>
            <div className="space-y-4">
              <div>
                <label className="text-xs font-medium text-gray-500 uppercase">Internal ID</label>
                <p className="text-sm font-medium text-primary-600 mt-1 table-cell-ellipsis" title={order.internal_id}>{order.internal_id}</p>
              </div>
              <div>
                <label className="text-xs font-medium text-gray-500 uppercase">Public ID</label>
                <p className="text-sm text-gray-900 mt-1">{order.public_id || '—'}</p>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="text-xs font-medium text-gray-500 uppercase mb-1 block">Type</label>
                  <p className="text-sm text-gray-900 capitalize">{order.type}</p>
                </div>
                <div>
                  <label className="text-xs font-medium text-gray-500 uppercase mb-1 block">Customer</label>
                  <p className="text-sm text-gray-900">{orderCustomerLabel(order)}</p>
                </div>
                {order.created_by_display_name ? (
                  <div>
                    <label className="text-xs font-medium text-gray-500 uppercase mb-1 block">Placed by</label>
                    <p className="text-sm text-gray-900">{order.created_by_display_name}</p>
                  </div>
                ) : null}
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="text-xs font-medium text-gray-500 uppercase mb-1 block">Driver Name</label>
                  <p className="text-sm text-gray-900">{resolvedDriverName || order.driver_assigned_uuid || '—'}</p>
                </div>
                <div>
                  <label className="text-xs font-medium text-gray-500 uppercase mb-1 block">Vehicle</label>
                  <p className="text-sm text-gray-900">
                    {resolvedVehicleName || order.vehicle_assigned_uuid || '—'}
                    {resolvedVehicleNumber ? ` (${resolvedVehicleNumber})` : ''}
                  </p>
                </div>
                <div>
                  <label className="text-xs font-medium text-gray-500 uppercase">Status</label>
                  <div className="mt-1">
                    <StatusBadge label={order.status} variant={getStatusVariant(order.status)} />
                  </div>
                </div>
                <div>
                  <label className="text-xs font-medium text-gray-500 uppercase flex items-center space-x-1 mb-1">
                    <Calendar size={12} />
                    <span>Scheduled At</span>
                  </label>
                  <p className="text-sm text-gray-900 table-cell-ellipsis" title={formatDateTime(order.scheduled_at)}>
                    {formatDateTime(order.scheduled_at)}
                  </p>
                </div>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="text-xs font-medium text-gray-500 uppercase mb-1 block">Priority</label>
                  <p className="text-sm text-gray-900 capitalize">{order.meta?.priority || '-'}</p>
                </div>
                <div>
                  <label className="text-xs font-medium text-gray-500 uppercase mb-1 block">POD Required</label>
                  <p className="text-sm text-gray-900">{order.options?.pod_required ? 'Yes' : 'No'}</p>
                </div>
              </div>
              {(pickupAddr || deliveryAddr) && (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="text-xs font-medium text-gray-500 uppercase mb-1 block">Pickup</label>
                    <p className="text-sm text-gray-900 whitespace-pre-wrap">{pickupAddr || '—'}</p>
                  </div>
                  <div>
                    <label className="text-xs font-medium text-gray-500 uppercase mb-1 block">Delivery</label>
                    <p className="text-sm text-gray-900 whitespace-pre-wrap">{deliveryAddr || '—'}</p>
                  </div>
                </div>
              )}
              {showGoodsBlock ? (
                <div>
                  <label className="text-xs font-medium text-gray-500 uppercase mb-1 block">Goods / service</label>
                  <p className="text-sm text-gray-900 whitespace-pre-wrap">{goodsMeta}</p>
                </div>
              ) : null}
              <div>
                <label className="text-xs font-medium text-gray-500 uppercase mb-1 block">Notes</label>
                <p className="text-sm text-gray-900 whitespace-pre-wrap">{order.notes || '—'}</p>
              </div>
              {isFleetCustomer ? (
                resolvedDriverName || resolvedVehicleName || resolvedVehicleNumber ? (
                  <div>
                    <label className="text-xs font-medium text-gray-500 uppercase mb-2 block">Assignment</label>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                      {resolvedDriverName ? (
                        <p className="text-gray-800">
                          <span className="font-medium">Driver:</span> {resolvedDriverName}
                        </p>
                      ) : null}
                      {resolvedVehicleName || resolvedVehicleNumber ? (
                        <p className="text-gray-800">
                          <span className="font-medium">Vehicle:</span> {resolvedVehicleName || 'Vehicle'}
                          {resolvedVehicleNumber ? ` (${resolvedVehicleNumber})` : ''}
                        </p>
                      ) : null}
                    </div>
                  </div>
                ) : null
              ) : (
                <div>
                  <label className="text-xs font-medium text-gray-500 uppercase mb-2 block">Related Links</label>
                  <div className="flex flex-wrap gap-x-4 gap-y-2 text-sm">
                    {order.driver_assigned_uuid || driverId ? (
                      <button
                        type="button"
                        onClick={() => openRelatedDetails('driver', order.driver_assigned_uuid || driverId)}
                        className="text-blue-600 hover:underline cursor-pointer"
                        title="View Driver"
                      >
                        {resolvedDriverName || 'Driver'}
                      </button>
                    ) : (
                      <span className="text-gray-500">Driver —</span>
                    )}
                    {order.vehicle_assigned_uuid || vehicleId ? (
                      <button
                        type="button"
                        onClick={() => openRelatedDetails('vehicle', order.vehicle_assigned_uuid || vehicleId)}
                        className="text-blue-600 hover:underline cursor-pointer"
                        title="View Vehicle"
                      >
                        {resolvedVehicleName
                          ? `${resolvedVehicleName}${resolvedVehicleNumber ? ` (${resolvedVehicleNumber})` : ''}`
                          : 'Vehicle'}
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
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="text-xs font-medium text-gray-500 uppercase mb-1 block">Created At</label>
                  <p className="text-sm text-gray-900">{formatDateTime(order.created_at)}</p>
                </div>
                <div>
                  <label className="text-xs font-medium text-gray-500 uppercase mb-1 block">Updated At</label>
                  <p className="text-sm text-gray-900">{formatDateTime(order.updated_at)}</p>
                </div>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-xl border border-gray-200 shadow-soft p-6">
            <h2 className="text-lg font-bold text-gray-900 mb-4">Lifecycle Timeline</h2>
            {lifecycle.length === 0 ? (
              <p className="text-sm text-gray-500">No lifecycle events captured yet.</p>
            ) : (
              <div className="space-y-3">
                {lifecycle.map((evt) => (
                  <div key={evt.uuid || `${evt.event_type}-${evt.created_at}`} className="rounded-md border border-gray-100 p-3">
                    <div className="flex items-center justify-between gap-3">
                      <p className="text-sm font-semibold text-gray-900">{evt.event_type}</p>
                      <p className="text-xs text-gray-500">{formatDateTime(evt.created_at)}</p>
                    </div>
                    <p className="text-xs text-gray-600 mt-1">
                      {evt.from_status || '—'} {evt.to_status ? `-> ${evt.to_status}` : ''}
                    </p>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          <div className="bg-white rounded-xl border border-gray-200 shadow-soft p-6">
            <h3 className="font-semibold text-gray-900 mb-4">Quick Actions</h3>
            <div className="space-y-3">
              {!isViewer && isStaffAssign ? (
                <div>
                  <SelectField
                    id="assign-driver"
                    label="Assign Driver"
                    value={assignDriverId}
                    onChange={(e) => setAssignDriverId(e.target.value)}
                    options={[
                      { value: '', label: 'Auto assign (best available)' },
                      ...drivers.map((driver) => ({
                        value: driver.id,
                        label: `${driver.id} (${driver.status}, online:${driver.online})`,
                      })),
                    ]}
                  />
                  <Button className="mt-2" fullWidth loading={assigning} onClick={handleAssign}>
                    Assign Order
                  </Button>
                </div>
              ) : null}

              {!isViewer && (isStaffAssign || isDriver) ? (
                <div className={isStaffAssign ? 'border-t border-gray-100 pt-3' : ''}>
                  <SelectField
                    id="next-status"
                    label="Transition Status"
                    value={nextStatus}
                    onChange={(e) => setNextStatus(e.target.value)}
                    options={transitionCandidates(order.status).map((s) => ({
                      value: s,
                      label: s,
                    }))}
                  />
                  <Button
                    className="mt-2"
                    fullWidth
                    disabled={!isDriver && !hasAssignment}
                    loading={transitioning}
                    onClick={handleTransition}
                  >
                    Move Status
                  </Button>
                  {!isDriver && !hasAssignment ? (
                    <p className="mt-2 text-xs text-amber-700">Assign driver and vehicle before proceeding</p>
                  ) : null}
                </div>
              ) : null}

              {!isViewer && isStaffAssign ? (
                <div className="border-t border-gray-100 pt-3 space-y-2">
                  <p className="text-sm font-medium text-gray-800">Raise Exception</p>
                  <input
                    className="h-10 w-full rounded-md border border-border bg-white px-3 text-sm text-neutral-900"
                    placeholder="Exception title"
                    value={exceptionTitle}
                    onChange={(e) => setExceptionTitle(e.target.value)}
                  />
                  <textarea
                    className="w-full rounded-md border border-border bg-white px-3 py-2 text-sm text-neutral-900"
                    rows={3}
                    placeholder="Exception report"
                    value={exceptionReport}
                    onChange={(e) => setExceptionReport(e.target.value)}
                  />
                  <SelectField
                    id="exception-priority"
                    label="Priority"
                    value={exceptionPriority}
                    onChange={(e) => setExceptionPriority(e.target.value)}
                    options={[
                      { value: 'low', label: 'low' },
                      { value: 'medium', label: 'medium' },
                      { value: 'high', label: 'high' },
                      { value: 'critical', label: 'critical' },
                    ]}
                  />
                  <SelectField
                    id="reassign-driver"
                    label="Reassign Driver (optional)"
                    value={reassignDriverId}
                    onChange={(e) => setReassignDriverId(e.target.value)}
                    options={[
                      { value: '', label: 'No reassignment (mark delayed)' },
                      ...drivers.map((driver) => ({
                        value: driver.id,
                        label: `${driver.id} (${driver.status}, online:${driver.online})`,
                      })),
                    ]}
                  />
                  <Button variant="danger" fullWidth loading={creatingException} onClick={handleException}>
                    Raise Exception
                  </Button>
                </div>
              ) : null}

              <Link to="/logistics/orders" className="block">
                <Button variant="outline" fullWidth icon={Edit}>
                  {isViewer || isDriver ? 'Back to orders' : 'Open List To Edit'}
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </div>
      <RouteDetailsModal
        isOpen={Boolean(relatedDetailsPath)}
        onClose={() => setRelatedDetailsPath(null)}
        title={relatedDetailsTitle}
        routePath={relatedDetailsPath}
        headerTitle={relatedDetailsTitle}
        headerSubtitle={relatedDetailsSubtitle}
      />
    </div>
  );
};

export default OrderDetail;
