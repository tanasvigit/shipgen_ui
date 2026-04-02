import React, { useEffect, useState } from 'react';
import { AlertCircle } from 'lucide-react';
import { trackingNumbersService } from '../../../services/trackingNumbersService';
import { PH } from '../../../constants/formPlaceholders';
import { FormActions, FormContainer, FormField, FormSection, Input } from '../../common/form';

interface TrackingNumberFormProps {
  mode: 'create' | 'edit';
  trackingNumberId?: string;
  onSuccess: () => Promise<void> | void;
  onCancel: () => void;
}

const TrackingNumberForm: React.FC<TrackingNumberFormProps> = ({ mode, trackingNumberId, onSuccess, onCancel }) => {
  const [loading, setLoading] = useState(mode === 'edit');
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [form, setForm] = useState({
    tracking_number: '',
    type: '',
    status: '',
  });

  useEffect(() => {
    if (mode !== 'edit' || !trackingNumberId) return;
    const load = async () => {
      try {
        setLoading(true);
        setError(null);
        const row = await trackingNumbersService.getById(trackingNumberId);
        setForm({
          tracking_number: row.tracking_number || '',
          type: row.type || '',
          status: row.status || '',
        });
      } catch (err: unknown) {
        setError(err instanceof Error ? err.message : 'Failed to load tracking number');
      } finally {
        setLoading(false);
      }
    };
    void load();
  }, [mode, trackingNumberId]);

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!form.tracking_number.trim()) {
      setError('Tracking number is required');
      return;
    }
    try {
      setSaving(true);
      setError(null);
      const payload = {
        tracking_number: form.tracking_number.trim(),
        type: form.type.trim() || undefined,
        status: form.status.trim() || undefined,
      };
      if (mode === 'edit' && trackingNumberId) {
        await trackingNumbersService.update(trackingNumberId, payload);
      } else {
        await trackingNumbersService.create(payload);
      }
      await onSuccess();
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : `Failed to ${mode} tracking number`);
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
          <FormField className="md:col-span-2" label="tracking_number" required htmlFor="tn-num">
            <Input
              id="tn-num"
              type="text"
              value={form.tracking_number}
              onChange={(e) => setForm((p) => ({ ...p, tracking_number: e.target.value }))}
              placeholder={PH.trackingNumber}
            />
          </FormField>
          <FormField label="type" htmlFor="tn-type">
            <Input
              id="tn-type"
              type="text"
              value={form.type}
              onChange={(e) => setForm((p) => ({ ...p, type: e.target.value }))}
              placeholder={PH.trackingTypeOptional}
            />
          </FormField>
          <FormField label="status" htmlFor="tn-status">
            <Input
              id="tn-status"
              type="text"
              value={form.status}
              onChange={(e) => setForm((p) => ({ ...p, status: e.target.value }))}
              placeholder={PH.statusTextOptional}
            />
          </FormField>
        </FormSection>
        <FormActions
          onCancel={onCancel}
          saving={saving}
          submitLabel={mode === 'edit' ? 'Save Changes' : 'Create Tracking Number'}
        />
      </form>
    </FormContainer>
  );
};

export default TrackingNumberForm;
