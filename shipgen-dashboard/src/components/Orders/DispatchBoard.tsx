import React, { useEffect, useMemo, useState } from 'react';
import { ArrowLeft, Check, RefreshCw } from 'lucide-react';
import { useLocation } from 'react-router-dom';
import { useNavigate } from 'react-router-dom';
import { driversService, UiDriver } from '../../services/driversService';
import { ordersService, UiOrder } from '../../services/ordersService';
import { vehiclesService, UiVehicle } from '../../services/vehiclesService';
import { Button } from '../ui/Button';
import PageContainer from '../ui/PageContainer';
import PageHeader from '../ui/PageHeader';
import SelectField from '../ui/SelectField';
import StatusBadge from '../ui/StatusBadge';
import { useToast } from '../ui/ToastProvider';
import Modal from '../common/Modal';

const STATUS_COLUMNS = [
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

const statusVariant = (status: string): 'success' | 'pending' | 'failed' | 'info' | 'neutral' => {
  const normalized = (status || '').toLowerCase();
  if (['completed', 'delivered'].includes(normalized)) return 'success';
  if (['cancelled', 'failed'].includes(normalized)) return 'failed';
  if (['created', 'assigned', 'dispatched', 'in_transit', 'out_for_delivery', 'delayed', 'reassigned'].includes(normalized)) return 'pending';
  return 'info';
};

const allowedTransitions = (status: string): string[] => {
  const flow = [
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
  const normalized = (status || 'created').toLowerCase();
  const idx = flow.indexOf(normalized);
  if (idx === -1) {
    return ['assigned', 'dispatched', 'in_transit', 'out_for_delivery', 'delivered', 'completed', 'failed', 'cancelled'];
  }
  return [...flow.slice(idx + 1), 'failed', 'cancelled'];
};

const hasAssignment = (order: UiOrder): boolean =>
  Boolean(order.driver_assigned_uuid && order.vehicle_assigned_uuid);

const lifecycleStepIndex = (status: string): number => {
  const normalized = (status || 'created').toLowerCase();
  const i = STATUS_COLUMNS.indexOf(normalized);
  if (i >= 0) return i;
  if (normalized === 'delayed') return STATUS_COLUMNS.indexOf('in_transit');
  if (normalized === 'reassigned') return STATUS_COLUMNS.indexOf('assigned');
  return -1;
};

const formatStepLabel = (step: string) =>
  step
    .split('_')
    .map((w) => w.charAt(0).toUpperCase() + w.slice(1))
    .join(' ');

const OrderStatusFlowStepper: React.FC<{ status: string }> = ({ status }) => {
  const normalized = (status || 'created').toLowerCase();
  const terminal = normalized === 'cancelled' || normalized === 'failed';
  const idx = terminal ? -1 : lifecycleStepIndex(status);

  return (
    <div className="rounded-lg border border-gray-100 bg-gray-50/80 p-3">
      <p className="mb-3 text-xs font-semibold uppercase tracking-wide text-gray-500">Order status flow</p>
      {terminal ? (
        <p className="text-xs text-gray-600">
          This order is <span className="font-medium text-gray-800">{normalized}</span> — lifecycle steps are not shown.
        </p>
      ) : (
        <div className="-mx-1 overflow-x-auto pb-1">
          <div className="flex min-w-max items-center px-1">
            {STATUS_COLUMNS.map((step, i) => {
              const done = idx >= 0 && i <= idx;
              const lineToNextGreen = idx >= 0 && i < idx;
              return (
                <React.Fragment key={step}>
                  <div className="flex w-[72px] shrink-0 flex-col items-center">
                    <div
                      className={`flex h-8 w-8 shrink-0 items-center justify-center rounded-full border-2 transition-colors ${
                        done
                          ? 'border-emerald-600 bg-emerald-600 text-white'
                          : 'border-gray-300 bg-white text-transparent'
                      }`}
                      aria-hidden
                    >
                      {done ? <Check className="h-4 w-4 stroke-[3]" /> : null}
                    </div>
                    <span className="mt-1.5 line-clamp-2 text-center text-[10px] font-medium leading-tight text-gray-600">
                      {formatStepLabel(step)}
                    </span>
                  </div>
                  {i < STATUS_COLUMNS.length - 1 ? (
                    <div
                      className={`mx-0.5 h-0.5 min-w-[12px] flex-1 max-w-[40px] shrink ${lineToNextGreen ? 'bg-emerald-600' : 'bg-gray-200'}`}
                      aria-hidden
                    />
                  ) : null}
                </React.Fragment>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
};

const DispatchBoard: React.FC = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const { showToast } = useToast();
  const [statusCounts, setStatusCounts] = useState<Record<string, number>>({});
  const [drivers, setDrivers] = useState<UiDriver[]>([]);
  const [vehicles, setVehicles] = useState<UiVehicle[]>([]);
  const [loading, setLoading] = useState(true);
  const [modalLoading, setModalLoading] = useState(false);
  const [isStatusModalOpen, setIsStatusModalOpen] = useState(false);
  const [selectedStatus, setSelectedStatus] = useState<string | null>(null);
  const [viewMode, setViewMode] = useState<'list' | 'detail'>('list');
  const [statusOrders, setStatusOrders] = useState<UiOrder[]>([]);
  const [selectedOrder, setSelectedOrder] = useState<UiOrder | null>(null);
  const [orderSearch, setOrderSearch] = useState('');
  const [assignDriverByOrder, setAssignDriverByOrder] = useState<Record<string, string>>({});
  const [assignVehicleByOrder, setAssignVehicleByOrder] = useState<Record<string, string>>({});
  const [nextStatusByOrder, setNextStatusByOrder] = useState<Record<string, string>>({});
  const [actingOrderId, setActingOrderId] = useState<string | null>(null);

  const loadStatusCounts = async () => {
    try {
      setLoading(true);
      const [driversResponse, vehiclesResponse, countResponses] = await Promise.all([
        driversService.list({ page: 1, pageSize: 100, status: 'active' }),
        vehiclesService.list({ page: 1, pageSize: 100, status: 'active' }),
        Promise.all(
          STATUS_COLUMNS.map(async (status) => ({
            status,
            response: await ordersService.list({ page: 1, pageSize: 100, status }),
          })),
        ),
      ]);
      setDrivers(driversResponse.data);
      setVehicles(vehiclesResponse.data);
      const nextCounts: Record<string, number> = {};
      for (const { status, response } of countResponses) nextCounts[status] = response.data.length;
      setStatusCounts(nextCounts);
    } catch (err: any) {
      showToast(err?.message || 'Failed to load dispatch board', 'error');
    } finally {
      setLoading(false);
    }
  };

  const loadStatusOrders = async (status: string) => {
    try {
      setModalLoading(true);
      const response = await ordersService.list({ page: 1, pageSize: 100, status });
      setStatusOrders(response.data);
    } catch (err: any) {
      showToast(err?.message || 'Failed to load orders for status', 'error');
      setStatusOrders([]);
    } finally {
      setModalLoading(false);
    }
  };

  const loadOrderDetail = async (orderId: string) => {
    try {
      setModalLoading(true);
      const order = await ordersService.getById(orderId);
      setSelectedOrder(order);
      setAssignDriverByOrder((prev) => ({ ...prev, [order.id]: order.driver_assigned_uuid || '' }));
      setAssignVehicleByOrder((prev) => ({ ...prev, [order.id]: order.vehicle_assigned_uuid || '' }));
    } catch (err: any) {
      showToast(err?.message || 'Failed to load order details', 'error');
    } finally {
      setModalLoading(false);
    }
  };

  const openStatusModal = async (status: string) => {
    setSelectedStatus(status);
    setViewMode('list');
    setSelectedOrder(null);
    setOrderSearch('');
    setIsStatusModalOpen(true);
    await loadStatusOrders(status);
  };

  useEffect(() => {
    void loadStatusCounts();
  }, []);

  useEffect(() => {
    const params = new URLSearchParams(location.search);
    const queryStatus = (params.get('status') || '').toLowerCase();
    const queryOrderId = params.get('orderId');
    if (!queryStatus || !queryOrderId) return;
    if (!STATUS_COLUMNS.includes(queryStatus)) return;

    const openFromQuery = async () => {
      setSelectedStatus(queryStatus);
      setViewMode('detail');
      setIsStatusModalOpen(true);
      await loadStatusOrders(queryStatus);
      await loadOrderDetail(queryOrderId);
    };
    void openFromQuery();
  }, [location.search]);

  const filteredStatusOrders = useMemo(() => {
    const q = orderSearch.trim().toLowerCase();
    if (!q) return statusOrders;
    return statusOrders.filter((order) => {
      const blob = `${order.internal_id || ''} ${order.public_id || ''} ${order.id} ${order.meta?.customer_name || ''}`.toLowerCase();
      return blob.includes(q);
    });
  }, [statusOrders, orderSearch]);

  const handleAssign = async (order: UiOrder) => {
    try {
      setActingOrderId(order.id);
      const selectedDriver = assignDriverByOrder[order.id];
      const selectedVehicle = assignVehicleByOrder[order.id];
      await ordersService.assign(order.id, {
        driver_uuid: selectedDriver || undefined,
        vehicle_uuid: selectedVehicle || undefined,
        mode: selectedDriver || selectedVehicle ? 'manual' : 'auto',
      });
      showToast('Order assigned', 'success');
      if (selectedStatus) await loadStatusOrders(selectedStatus);
      await loadOrderDetail(order.id);
      await loadStatusCounts();
    } catch (err: any) {
      showToast(err?.message || 'Assignment failed', 'error');
    } finally {
      setActingOrderId(null);
    }
  };

  const handleTransition = async (order: UiOrder) => {
    if (!hasAssignment(order)) {
      showToast('Assign driver and vehicle before proceeding', 'info');
      return;
    }
    const toStatus = nextStatusByOrder[order.id];
    if (!toStatus) {
      showToast('Select next status first', 'info');
      return;
    }
    try {
      setActingOrderId(order.id);
      await ordersService.transition(order.id, { to_status: toStatus });
      showToast(`Moved to ${toStatus}`, 'success');
      await loadOrderDetail(order.id);
      if (selectedStatus) await loadStatusOrders(selectedStatus);
      await loadStatusCounts();
    } catch (err: any) {
      showToast(err?.message || 'Status transition failed', 'error');
    } finally {
      setActingOrderId(null);
    }
  };

  return (
    <PageContainer flushHorizontal className="px-4 sm:px-5 lg:px-8">
      <PageHeader
        title="Dispatcher Board"
        description="Status overview board for order execution."
        action={
          <Button variant="outline" icon={RefreshCw} onClick={() => void loadStatusCounts()} loading={loading}>
            Refresh
          </Button>
        }
      />

      <div className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-3 2xl:grid-cols-4">
        {STATUS_COLUMNS.map((columnStatus) => (
          <button
            key={columnStatus}
            type="button"
            onClick={() => void openStatusModal(columnStatus)}
            className="rounded-xl border border-gray-200 bg-white p-4 text-left transition hover:border-primary-300 hover:shadow-sm"
          >
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-semibold uppercase tracking-wide text-gray-700">{columnStatus.replaceAll('_', ' ')}</h3>
              <StatusBadge label={String(statusCounts[columnStatus] || 0)} variant="neutral" />
            </div>
          </button>
        ))}
      </div>

      <Modal
        isOpen={isStatusModalOpen}
        onClose={() => {
          const params = new URLSearchParams(location.search);
          const source = params.get('source');
          setIsStatusModalOpen(false);
          setViewMode('list');
          setSelectedOrder(null);
          if (source === 'orders') {
            navigate('/logistics/orders');
          }
        }}
        title={`${(selectedStatus || '').replaceAll('_', ' ').toUpperCase()} ORDERS`}
        titleEnd={
          viewMode === 'detail' ? (
            <Button
              size="sm"
              variant="outline"
              icon={ArrowLeft}
              className="w-9 px-0"
              aria-label="Back to list"
              onClick={() => {
                setViewMode('list');
                setSelectedOrder(null);
              }}
            />
          ) : undefined
        }
      >
        {viewMode === 'list' ? (
          <div className="space-y-3 pt-1">
            <div className="rounded-lg bg-white p-0.5">
              <input
                type="text"
                placeholder="Search by order ID or customer..."
                value={orderSearch}
                onChange={(e) => setOrderSearch(e.target.value)}
                className="h-10 w-full rounded-md border border-border bg-white px-3 text-sm text-neutral-900"
              />
            </div>
            {modalLoading ? <p className="text-sm text-gray-600">Loading orders...</p> : null}
            {!modalLoading && filteredStatusOrders.length === 0 ? (
              <div className="rounded-md border border-dashed border-gray-200 p-4 text-center text-sm text-gray-500">No orders in this status</div>
            ) : null}
            <div className="max-h-[52vh] space-y-2 overflow-y-auto">
              {filteredStatusOrders.map((order) => (
                <button
                  key={order.id}
                  type="button"
                  className="w-full rounded-lg border border-gray-100 p-3 text-left transition hover:border-primary-300"
                  onClick={() => {
                    setViewMode('detail');
                    void loadOrderDetail(order.id);
                  }}
                >
                  <p className="text-sm font-semibold text-primary-700">{order.internal_id || order.public_id || order.id}</p>
                  <p className="text-xs text-gray-500">{order.meta?.customer_name || 'No customer'}</p>
                  <div className="mt-1">
                    <StatusBadge label={order.status} variant={statusVariant(order.status)} />
                  </div>
                </button>
              ))}
            </div>
          </div>
        ) : (
          <div className="space-y-3 pt-1">
            {modalLoading || !selectedOrder ? (
              <p className="text-sm text-gray-600">Loading order details...</p>
            ) : (
              <>
                <div className="rounded-lg border border-gray-100 p-3">
                  <p className="text-sm font-semibold text-primary-700">{selectedOrder.internal_id || selectedOrder.public_id || selectedOrder.id}</p>
                  <p className="text-xs text-gray-500">{selectedOrder.meta?.customer_name || 'No customer'}</p>
                  <div className="mt-1">
                    <StatusBadge label={selectedOrder.status} variant={statusVariant(selectedOrder.status)} />
                  </div>
                </div>

                <OrderStatusFlowStepper status={selectedOrder.status} />

                <div className="space-y-2">
                  <SelectField
                    id={`assign-driver-${selectedOrder.id}`}
                    value={assignDriverByOrder[selectedOrder.id] || ''}
                    onChange={(e) => setAssignDriverByOrder((prev) => ({ ...prev, [selectedOrder.id]: e.target.value }))}
                    options={[
                      { value: '', label: 'Auto assign' },
                      ...drivers.map((driver) => ({
                        value: driver.id,
                        label: `${driver.id} (${driver.status})`,
                      })),
                    ]}
                  />
                  <SelectField
                    id={`assign-vehicle-${selectedOrder.id}`}
                    value={assignVehicleByOrder[selectedOrder.id] || ''}
                    onChange={(e) => setAssignVehicleByOrder((prev) => ({ ...prev, [selectedOrder.id]: e.target.value }))}
                    options={[
                      { value: '', label: 'Auto / Driver linked vehicle' },
                      ...vehicles.map((vehicle) => ({
                        value: vehicle.id,
                        label: `${vehicle.plate_number || vehicle.id} (${vehicle.status})`,
                      })),
                    ]}
                  />
                  <Button
                    size="sm"
                    fullWidth
                    loading={actingOrderId === selectedOrder.id}
                    onClick={() => void handleAssign(selectedOrder)}
                  >
                    Assign
                  </Button>
                </div>

                <div className="space-y-2">
                  <SelectField
                    id={`next-status-${selectedOrder.id}`}
                    value={nextStatusByOrder[selectedOrder.id] || ''}
                    onChange={(e) => setNextStatusByOrder((prev) => ({ ...prev, [selectedOrder.id]: e.target.value }))}
                    options={[
                      { value: '', label: 'Next status' },
                      ...allowedTransitions(selectedOrder.status).map((status) => ({
                        value: status,
                        label: status,
                      })),
                    ]}
                  />
                  <Button
                    size="sm"
                    variant="secondary"
                    fullWidth
                    disabled={!hasAssignment(selectedOrder)}
                    loading={actingOrderId === selectedOrder.id}
                    onClick={() => void handleTransition(selectedOrder)}
                  >
                    Move
                  </Button>
                  {!hasAssignment(selectedOrder) ? (
                    <p className="text-xs text-amber-700">Assign driver and vehicle before proceeding</p>
                  ) : null}
                </div>
              </>
            )}
          </div>
        )}
      </Modal>
    </PageContainer>
  );
};

export default DispatchBoard;

