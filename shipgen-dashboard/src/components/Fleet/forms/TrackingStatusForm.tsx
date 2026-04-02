import React, { useEffect, useState } from 'react';
import { AlertCircle } from 'lucide-react';
import { trackingStatusesService } from '../../../services/trackingStatusesService';
import { PH } from '../../../constants/formPlaceholders';
import { FormActions, FormContainer, FormField, FormSection, Input, Textarea } from '../../common/form';

interface TrackingStatusFormProps {
  mode: 'create' | 'edit';
  trackingStatusId?: string;
  onSuccess: () => Promise<void> | void;
  onCancel: () => void;
}

const TrackingStatusForm: React.FC<TrackingStatusFormProps> = ({ mode, trackingStatusId, onSuccess, onCancel }) => {
  const [loading, setLoading] = useState(mode === 'edit');
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [form, setForm] = useState({
    name: '',
    description: '',
  });

  useEffect(() => {
    if (mode !== 'edit' || !trackingStatusId) return;
    const load = async () => {
      try {
        setLoading(true);
        setError(null);
        const row = await trackingStatusesService.getById(trackingStatusId);
        setForm({
          name: row.name || '',
          description: row.description || '',
        });
      } catch (err: unknown) {
        setError(err instanceof Error ? err.message : 'Failed to load tracking status');
      } finally {
        setLoading(false);
      }
    };
    void load();
  }, [mode, trackingStatusId]);

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!form.name.trim()) {
      setError('Name/Status is required');
      return;
    }
    try {
      setSaving(true);
      setError(null);
      const payload = {
        name: form.name.trim(),
        description: form.description.trim() || undefined,
      };
      if (mode === 'edit' && trackingStatusId) {
        await trackingStatusesService.update(trackingStatusId, payload);
      } else {
        await trackingStatusesService.create(payload);
      }
      await onSuccess();
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : `Failed to ${mode} tracking status`);
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
          <FormField className="md:col-span-2" label="name/status" required htmlFor="ts-name">
            <Input
              id="ts-name"
              type="text"
              value={form.name}
              onChange={(e) => setForm((p) => ({ ...p, name: e.target.value }))}
              placeholder={PH.trackingStatusName}
            />
          </FormField>
          <FormField className="md:col-span-2" label="description" htmlFor="ts-desc">
            <Textarea
              id="ts-desc"
              rows={4}
              value={form.description}
              onChange={(e) => setForm((p) => ({ ...p, description: e.target.value }))}
              placeholder={PH.descriptionOptional}
            />
          </FormField>
        </FormSection>
        <FormActions onCancel={onCancel} saving={saving} submitLabel={mode === 'edit' ? 'Save Changes' : 'Create Status'} />
      </form>
    </FormContainer>
  );
};

export default TrackingStatusForm;
