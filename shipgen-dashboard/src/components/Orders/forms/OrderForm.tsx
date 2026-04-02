import React, { useEffect, useState } from 'react';
import { AlertCircle } from 'lucide-react';
import { ordersService } from '../../../services/ordersService';
import { PH, SELECT_PH } from '../../../constants/formPlaceholders';
import { FormActions, FormContainer, FormField, FormSection, Input, Select, Textarea } from '../../common/form';

interface OrderFormProps {
  mode: 'create' | 'edit';
  orderId?: string;
  onSuccess: () => Promise<void> | void;
  onCancel: () => void;
}

const OrderForm: React.FC<OrderFormProps> = ({ mode, orderId, onSuccess, onCancel }) => {
  const [loading, setLoading] = useState(mode === 'edit');
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [formData, setFormData] = useState({
    type: '',
    internal_id: '',
    notes: '',
    scheduled_at: '',
    status: '',
    customer_name: '',
    priority: '',
    pod_required: false,
  });

  useEffect(() => {
    if (mode !== 'edit' || !orderId) return;
    const run = async () => {
      try {
        setLoading(true);
        setError(null);
        const order = await ordersService.getById(orderId);
        setFormData({
          type: order.type ?? 'pickup',
          internal_id: order.internal_id ?? '',
          notes: order.notes ?? '',
          scheduled_at: order.scheduled_at ? order.scheduled_at.slice(0, 16) : '',
          status: order.status ?? 'created',
          customer_name: order.meta?.customer_name ?? '',
          priority: order.meta?.priority ?? 'normal',
          pod_required: !!order.options?.pod_required,
        });
      } catch (err: unknown) {
        setError(err instanceof Error ? err.message : 'Failed to load order');
      } finally {
        setLoading(false);
      }
    };
    void run();
  }, [mode, orderId]);

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      setSaving(true);
      setError(null);
      const payload = {
        type: formData.type,
        internal_id: formData.internal_id,
        notes: formData.notes,
        scheduled_at: formData.scheduled_at,
        status: formData.status || 'created',
        meta: { customer_name: formData.customer_name, priority: formData.priority || 'normal' },
        options: { pod_required: formData.pod_required },
      };
      if (mode === 'edit' && orderId) await ordersService.update(orderId, payload);
      else await ordersService.create(payload);
      await onSuccess();
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : `Failed to ${mode} order`);
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="flex h-40 items-center justify-center">
        <div className="h-10 w-10 animate-spin rounded-full border-b-2 border-blue-600" />
      </div>
    );
  }

  return (
    <FormContainer>
      <form onSubmit={submit} className="space-y-5">
        {error ? (
          <div className="flex items-center gap-2 rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">
            <AlertCircle size={16} />
            <span>{error}</span>
          </div>
        ) : null}
        <FormSection>
          <FormField className="md:col-span-2" label="Internal ID" required htmlFor="order-internal-id">
            <Input
              id="order-internal-id"
              required
              placeholder={PH.orderInternalId}
              value={formData.internal_id}
              onChange={(e) => setFormData((p) => ({ ...p, internal_id: e.target.value }))}
            />
          </FormField>
          <FormField label="Type" required htmlFor="order-type">
            <Select
              id="order-type"
              required
              value={formData.type}
              onChange={(e) => setFormData((p) => ({ ...p, type: e.target.value }))}
            >
              <option value="" disabled>
                {SELECT_PH.orderType}
              </option>
              <option value="pickup">pickup</option>
              <option value="delivery">delivery</option>
            </Select>
          </FormField>
          <FormField className="md:col-span-2" label="Customer Name (meta.customer_name)" required htmlFor="order-customer">
            <Input
              id="order-customer"
              required
              placeholder={PH.customerName}
              value={formData.customer_name}
              onChange={(e) => setFormData((p) => ({ ...p, customer_name: e.target.value }))}
            />
          </FormField>
          <FormField className="md:col-span-2" label="Scheduled At" required htmlFor="order-scheduled">
            <Input
              id="order-scheduled"
              type="datetime-local"
              required
              value={formData.scheduled_at}
              onChange={(e) => setFormData((p) => ({ ...p, scheduled_at: e.target.value }))}
            />
          </FormField>
          <FormField label="Priority (meta.priority)" htmlFor="order-priority">
            <Select
              id="order-priority"
              value={formData.priority}
              onChange={(e) => setFormData((p) => ({ ...p, priority: e.target.value }))}
            >
              <option value="">{SELECT_PH.priority} (optional)</option>
              <option value="normal">normal</option>
              <option value="high">high</option>
            </Select>
          </FormField>
          <FormField label="Status" htmlFor="order-status">
            <Select
              id="order-status"
              value={formData.status}
              onChange={(e) => setFormData((p) => ({ ...p, status: e.target.value }))}
            >
              <option value="">{SELECT_PH.status} (optional)</option>
              <option value="created">created</option>
              <option value="scheduled">scheduled</option>
              <option value="completed">completed</option>
              <option value="cancelled">cancelled</option>
            </Select>
          </FormField>
          <FormField className="md:col-span-2" label="Notes" htmlFor="order-notes">
            <Textarea
              id="order-notes"
              rows={3}
              placeholder={PH.notesOptional}
              value={formData.notes}
              onChange={(e) => setFormData((p) => ({ ...p, notes: e.target.value }))}
            />
          </FormField>
          <div className="flex items-center gap-2 pt-1 md:col-span-2">
            <input
              id="pod_required_order_form"
              type="checkbox"
              checked={formData.pod_required}
              onChange={(e) => setFormData((p) => ({ ...p, pod_required: e.target.checked }))}
              className="h-4 w-4 rounded border-gray-200 text-blue-600 focus:ring-1 focus:ring-blue-500"
            />
            <label htmlFor="pod_required_order_form" className="text-sm font-medium text-gray-700">
              POD Required (options.pod_required)
            </label>
          </div>
        </FormSection>
        <FormActions
          onCancel={onCancel}
          saving={saving}
          submitLabel={mode === 'edit' ? 'Save Changes' : 'Create Order'}
        />
      </form>
    </FormContainer>
  );
};

export default OrderForm;
