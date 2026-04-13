import React, { useMemo, useState, useEffect, useCallback } from 'react';
import { Link } from 'react-router-dom';
import { Package, Search, Calendar, Edit, Eye } from 'lucide-react';
import { ordersService, orderCustomerLabel, UiOrder } from '../../services/ordersService';
import { Button } from '../ui/Button';
import InputField from '../ui/InputField';
import StatusBadge from '../ui/StatusBadge';
import EntityLink from '../common/EntityLink';
import type { DashboardRange } from '../../utils/dashboardHelpers';
import Card from '../ui/Card';
import Table, { TableColumn } from '../ui/Table';
import PageContainer from '../ui/PageContainer';
import PageHeader from '../ui/PageHeader';
import FiltersBar from '../ui/FiltersBar';
import SelectField from '../ui/SelectField';
import { PH, SELECT_PH } from '../../constants/formPlaceholders';
import Modal from '../common/Modal';
import OrderForm from './forms/OrderForm';
import OrderDetailsModal from './OrderDetailsModal';
import { UserRole } from '../../types';
import {
  canAssignOrDispatchOrders,
  canCreateOrders,
  canEditOrders,
  getStoredUserRole,
} from '../../utils/roleAccess';

const OrdersList: React.FC = () => {
  const role = getStoredUserRole() ?? UserRole.VIEWER;
  const mayCreate = canCreateOrders(role);
  const mayEdit = canEditOrders(role);
  const mayDispatch = canAssignOrDispatchOrders(role);

  // Track user ID to trigger refetch on login/logout
  const [userKey, setUserKey] = useState(() => {
    try {
      const userStr = localStorage.getItem('user');
      return userStr ? JSON.parse(userStr)?.id || '' : '';
    } catch {
      return '';
    }
  });

  const [orders, setOrders] = useState<UiOrder[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [dateRange, setDateRange] = useState<DashboardRange>('last30');
  const pageSize = 20;
  const [page, setPage] = useState(1);
  const [totalCount, setTotalCount] = useState(0);
  const [isCreateOpen, setIsCreateOpen] = useState(false);
  const [isEditOpen, setIsEditOpen] = useState(false);
  const [isDetailsOpen, setIsDetailsOpen] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [selectedOrderId, setSelectedOrderId] = useState<string | null>(null);
  const openDetails = (orderId: string) => {
    setSelectedOrderId(orderId);
    setIsDetailsOpen(true);
  };


  useEffect(() => {
    loadOrders();
  }, [page, statusFilter, dateRange, userKey]); // Added userKey to refetch on login

  // Detect user changes (login/logout) and refetch
  useEffect(() => {
    const checkUserChange = () => {
      try {
        const userStr = localStorage.getItem('user');
        const currentUserId = userStr ? JSON.parse(userStr)?.id || '' : '';
        if (currentUserId !== userKey) {
          setUserKey(currentUserId);
        }
      } catch {
        // Ignore parse errors
      }
    };

    // Check periodically for user changes
    const interval = setInterval(checkUserChange, 1000);
    return () => clearInterval(interval);
  }, [userKey]);

  // Debounce search → backend.
  useEffect(() => {
    const handle = window.setTimeout(() => {
      setPage(1);
      void loadOrders();
    }, 250);
    return () => window.clearTimeout(handle);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [searchTerm]);

  const loadOrders = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const now = new Date();
      const start = new Date(now);
      start.setHours(0, 0, 0, 0);
      if (dateRange === 'last7') start.setDate(now.getDate() - 6);
      if (dateRange === 'last30') start.setDate(now.getDate() - 29);

      const response = await ordersService.list({
        page,
        pageSize,
        status: statusFilter !== 'all' ? statusFilter : undefined,
        search: searchTerm.trim() ? searchTerm.trim() : undefined,
        start_date: start.toISOString(),
        end_date: now.toISOString(),
      });
      setOrders(response.data);
      setTotalCount(response.pagination?.total || 0);
      setLoading(false);
    } catch (err: any) {
      setError(err.message || 'Failed to load orders');
      setLoading(false);
    }
  }, [page, statusFilter, dateRange, searchTerm]);

  const getStatusVariant = (status: string): 'success' | 'pending' | 'failed' | 'info' => {
    const normalized = (status || '').toLowerCase();
    if (['completed', 'delivered', 'success', 'paid'].includes(normalized)) return 'success';
    if (['created', 'scheduled', 'pending', 'in_progress'].includes(normalized)) return 'pending';
    if (['cancelled', 'failed', 'error'].includes(normalized)) return 'failed';
    return 'info';
  };

  const getOrderRefs = (order: UiOrder): Record<string, string> => {
    const meta = (order.meta as unknown as Record<string, unknown>) ?? {};
    return {
      driverId: String(meta.driver_uuid ?? meta.driver_id ?? ''),
      vehicleId: String(meta.vehicle_uuid ?? meta.vehicle_id ?? ''),
      vendorId: String(meta.vendor_uuid ?? meta.vendor_id ?? ''),
      pickupPlaceId: String(meta.pickup_place_uuid ?? meta.pickup_place_id ?? ''),
      dropPlaceId: String(meta.drop_place_uuid ?? meta.drop_place_id ?? ''),
    };
  };

  const resetFilters = () => {
    setSearchTerm('');
    setStatusFilter('all');
    setDateRange('last30');
    setPage(1);
  };

  const formatDate = (value?: string) => {
    if (!value) return '—';
    const d = new Date(value);
    return Number.isNaN(d.getTime()) ? '—' : d.toLocaleDateString();
  };

  const formatDateTime = (value?: string) => {
    if (!value) return '—';
    const d = new Date(value);
    return Number.isNaN(d.getTime()) ? '—' : d.toLocaleString();
  };

  const columns: TableColumn<UiOrder>[] = useMemo(
    () => [
      {
        key: 'internal_id',
        title: 'Internal ID',
        render: (order) => (
          <button
            type="button"
            onClick={() => openDetails(order.id)}
            className="block max-w-[220px] truncate font-medium text-primary-600 transition-colors duration-200 hover:text-primary-700 hover:underline"
            title={order.internal_id}
          >
            {order.internal_id}
          </button>
        ),
      },
      { key: 'type', title: 'Type', render: (order) => <span className="font-medium capitalize text-neutral-900">{order.type || '-'}</span> },
      {
        key: 'customer',
        title: 'Customer',
        render: (order) => (
          <span className="block max-w-[220px] truncate" title={orderCustomerLabel(order)}>
            {orderCustomerLabel(order)}
          </span>
        ),
      },
      { key: 'priority', title: 'Priority', render: (order) => <span className="capitalize">{order.meta?.priority || '-'}</span> },
      { key: 'pod_required', title: 'POD', render: (order) => <span>{order.options?.pod_required ? 'Yes' : 'No'}</span> },
      {
        key: 'scheduled_at',
        title: 'Scheduled',
        render: (order) => <span className="block max-w-[220px] truncate">{formatDateTime(order.scheduled_at)}</span>,
      },
      { key: 'status', title: 'Status', render: (order) => <StatusBadge label={order.status} variant={getStatusVariant(order.status)} /> },
      {
        key: 'created_at',
        title: 'Created',
        render: (order) => (
          <div className="flex items-center gap-1">
            <Calendar size={14} />
            <span>{formatDate(order.created_at)}</span>
          </div>
        ),
      },
      {
        key: 'related',
        title: 'Related',
        render: (order) => {
          const refs = getOrderRefs(order);
          const isFleetCustomer = role === UserRole.FLEET_CUSTOMER;
          if (isFleetCustomer) return null;
          return (
            <div className="flex flex-wrap gap-x-3 gap-y-1 text-xs">
              <EntityLink id={refs.driverId} label="Driver" to="/fleet/drivers" title="View Driver" />
              <EntityLink id={refs.vehicleId} label="Vehicle" to="/fleet/vehicles" title="View Vehicle" />
              <EntityLink id={refs.vendorId} label="Vendor" to="/fleet/vendors" title="View Vendor" />
              <EntityLink id={refs.pickupPlaceId} label="Pickup" to="/fleet/places" title="View Pickup Place" />
              <EntityLink id={refs.dropPlaceId} label="Drop" to="/fleet/places" title="View Drop Place" />
            </div>
          );
        },
      },
      ...(mayDispatch
        ? [
            {
              key: 'dispatch',
              title: 'Dispatch',
              isActions: true,
              render: (order: UiOrder) => (
                <div className="flex items-center justify-center" onClick={(e) => e.stopPropagation()}>
                  <Link
                    to={`/logistics/orders/dispatch-board?status=${encodeURIComponent((order.status || 'created').toLowerCase())}&orderId=${encodeURIComponent(order.id)}&source=orders`}
                    className="rounded-lg border border-gray-200 px-2 py-1 text-xs font-medium text-gray-700 transition hover:bg-gray-50"
                  >
                    Open
                  </Link>
                </div>
              ),
            } as TableColumn<UiOrder>,
          ]
        : []),
      {
        key: 'actions',
        title: 'Actions',
        isActions: true,
        render: (order) => (
          <div className="flex items-center justify-end gap-2" onClick={(e) => e.stopPropagation()}>
            <Button variant="ghost" size="sm" aria-label="View order" className="w-9 px-0" onClick={() => openDetails(order.id)}>
              <Eye size={16} />
            </Button>
            {mayEdit ? (
              <Button
                variant="outline"
                size="sm"
                aria-label="Edit order"
                type="button"
                className="w-9 px-0"
                onClick={(e) => {
                  e.stopPropagation();
                  setEditingId(order.id);
                  setIsEditOpen(true);
                }}
              >
                <Edit size={16} />
              </Button>
            ) : null}
          </div>
        ),
      },
    ],
    [openDetails, mayDispatch, mayEdit]
  );

  return (
    <PageContainer flushHorizontal className="px-4 sm:px-5 lg:px-8">
      <PageHeader
        title="Orders"
        description="Manage customer orders"
        action={mayCreate ? <Button onClick={() => setIsCreateOpen(true)}>Create Order</Button> : undefined}
      />

      <FiltersBar>
        <InputField
          label="Search"
          id="orders-search"
          leftIcon={Search}
          placeholder={PH.searchOrders}
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
        />
        <SelectField
          id="orders-status"
          label="Status"
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          options={[
            { value: 'all', label: SELECT_PH.status },
            { value: 'created', label: 'Created' },
            { value: 'scheduled', label: 'Scheduled' },
            { value: 'completed', label: 'Completed' },
            { value: 'cancelled', label: 'Cancelled' },
          ]}
        />
        <SelectField
          id="orders-range"
          label="Date"
          value={dateRange}
          onChange={(e) => setDateRange(e.target.value as DashboardRange)}
          options={[
            { value: 'today', label: 'Today' },
            { value: 'last7', label: 'Last 7 days' },
            { value: 'last30', label: 'Last 30 days' },
          ]}
        />
        <div className="flex items-end">
          <Button variant="secondary" fullWidth onClick={resetFilters}>
            Reset Filters
          </Button>
        </div>
      </FiltersBar>

      {error ? (
        <Card className="border-danger-100 bg-danger-50 text-danger-700" padding="sm">
          {error}
        </Card>
      ) : null}

      <Card padding="none">
        <Table
          columns={columns}
          data={orders}
          rowKey={(row) => row.id}
          fillWidth
          loading={loading}
          emptyState={{
            title: 'No orders found',
            description: mayCreate
              ? 'Try adjusting your filters or create a new order to get started.'
              : 'Try adjusting your filters.',
            action: mayCreate ? <Button onClick={() => setIsCreateOpen(true)}>Create Order</Button> : undefined,
          }}
          pagination={{
            page,
            pageSize,
            total: totalCount,
            onPageChange: setPage,
          }}
          onRowClick={(row) => openDetails(row.id)}
        />
      </Card>
      <Modal isOpen={isCreateOpen} onClose={() => setIsCreateOpen(false)} title="Create Order">
        <OrderForm
          mode="create"
          onCancel={() => setIsCreateOpen(false)}
          onSuccess={async () => {
            setIsCreateOpen(false);
            setPage(1);
            await loadOrders();
          }}
        />
      </Modal>
      <Modal isOpen={isEditOpen} onClose={() => setIsEditOpen(false)} title="Edit Order">
        <OrderForm
          mode="edit"
          orderId={editingId ?? undefined}
          onCancel={() => setIsEditOpen(false)}
          onSuccess={async () => {
            setIsEditOpen(false);
            setEditingId(null);
            await loadOrders();
          }}
        />
      </Modal>
      <OrderDetailsModal
        isOpen={isDetailsOpen}
        orderId={selectedOrderId}
        onClose={() => {
          setIsDetailsOpen(false);
          setSelectedOrderId(null);
        }}
      />
    </PageContainer>
  );
};

export default OrdersList;
