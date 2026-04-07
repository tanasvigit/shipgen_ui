import React, { useEffect, useState } from 'react';
import { AlertCircle } from 'lucide-react';
import { customersService, type CustomerInput } from '../../services/customersService';
import { FormActions, FormContainer, FormField, FormSection, Input, Textarea } from '../common/form';

export interface CustomerFormProps {
  mode: 'create' | 'edit';
  customerId?: string;
  onSuccess: () => Promise<void> | void;
  onCancel: () => void;
}

const empty: CustomerInput = { name: '', phone: '', email: '', address: '' };

const CustomerForm: React.FC<CustomerFormProps> = ({ mode, customerId, onSuccess, onCancel }) => {
  const [loading, setLoading] = useState(mode === 'edit');
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [form, setForm] = useState<CustomerInput>(empty);

  useEffect(() => {
    if (mode !== 'edit' || !customerId) {
      setForm(empty);
      setLoading(false);
      setError(null);
      return;
    }
    let cancelled = false;
    void (async () => {
      try {
        setLoading(true);
        setError(null);
        const c = await customersService.getById(customerId);
        if (cancelled) return;
        const meta = (c.meta ?? {}) as Record<string, unknown>;
        setForm({
          name: c.name ?? '',
          phone: c.phone ?? '',
          email: c.email ?? '',
          address: typeof meta.address === 'string' ? meta.address : '',
        });
      } catch (e: unknown) {
        if (!cancelled) setError(e instanceof Error ? e.message : 'Failed to load customer');
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [mode, customerId]);

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!form.name.trim() || !form.phone.trim()) {
      setError('Name and phone are required.');
      return;
    }
    try {
      setSaving(true);
      setError(null);
      if (mode === 'edit' && customerId) {
        await customersService.update(customerId, {
          name: form.name,
          phone: form.phone,
          email: form.email?.trim() || null,
          address: form.address?.trim() || null,
        });
      } else {
        await customersService.create({
          name: form.name,
          phone: form.phone,
          email: form.email?.trim() || null,
          address: form.address?.trim() || null,
        });
      }
      await onSuccess();
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Save failed');
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
          <FormField label="Name" required htmlFor="cust-modal-name">
            <Input
              id="cust-modal-name"
              required
              value={form.name}
              onChange={(e) => setForm((p) => ({ ...p, name: e.target.value }))}
            />
          </FormField>
          <FormField label="Phone" required htmlFor="cust-modal-phone">
            <Input
              id="cust-modal-phone"
              required
              value={form.phone}
              onChange={(e) => setForm((p) => ({ ...p, phone: e.target.value }))}
            />
          </FormField>
          <FormField className="md:col-span-2" label="Email" htmlFor="cust-modal-email">
            <Input
              id="cust-modal-email"
              type="email"
              value={form.email ?? ''}
              onChange={(e) => setForm((p) => ({ ...p, email: e.target.value }))}
            />
          </FormField>
          <FormField className="md:col-span-2" label="Address" htmlFor="cust-modal-address">
            <Textarea
              id="cust-modal-address"
              rows={3}
              value={form.address ?? ''}
              onChange={(e) => setForm((p) => ({ ...p, address: e.target.value }))}
            />
          </FormField>
        </FormSection>
        <FormActions
          onCancel={onCancel}
          saving={saving}
          submitDisabled={saving}
          submitLabel={mode === 'edit' ? 'Save customer' : 'Create customer'}
        />
      </form>
    </FormContainer>
  );
};

export default CustomerForm;
