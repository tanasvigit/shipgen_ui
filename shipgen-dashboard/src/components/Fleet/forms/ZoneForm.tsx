import React, { useEffect, useState } from 'react';
import { AlertCircle } from 'lucide-react';
import { zonesService } from '../../../services/zonesService';
import { PH } from '../../../constants/formPlaceholders';
import { FormActions, FormContainer, FormField, FormSection, Input, Textarea } from '../../common/form';

interface ZoneFormProps {
  mode: 'create' | 'edit';
  zoneId?: string;
  onSuccess: () => Promise<void> | void;
  onCancel: () => void;
}

const ZoneForm: React.FC<ZoneFormProps> = ({ mode, zoneId, onSuccess, onCancel }) => {
  const [loading, setLoading] = useState(mode === 'edit');
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [form, setForm] = useState({ name: '', description: '', status: '' });

  useEffect(() => {
    if (mode !== 'edit' || !zoneId) return;
    const run = async () => {
      try {
        setLoading(true);
        setError(null);
        const row = await zonesService.getById(zoneId);
        setForm({ name: row.name || '', description: row.description || '', status: row.status || '' });
      } catch (err: unknown) {
        setError(err instanceof Error ? err.message : 'Failed to load zone');
      } finally {
        setLoading(false);
      }
    };
    void run();
  }, [mode, zoneId]);

  const submit = async (event: React.FormEvent) => {
    event.preventDefault();
    if (!form.name.trim()) {
      setError('Name is required');
      return;
    }
    try {
      setSaving(true);
      setError(null);
      const payload = {
        name: form.name.trim(),
        description: form.description.trim() || undefined,
        status: form.status.trim() || undefined,
      };
      if (mode === 'edit' && zoneId) {
        await zonesService.update(zoneId, payload);
      } else {
        await zonesService.create(payload);
      }
      await onSuccess();
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : `Failed to ${mode} zone`);
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
          <FormField className="md:col-span-2" label="name" required htmlFor="zone-name">
            <Input
              id="zone-name"
              value={form.name}
              onChange={(e) => setForm((p) => ({ ...p, name: e.target.value }))}
              placeholder={PH.zoneName}
            />
          </FormField>
          <FormField className="md:col-span-2" label="description" htmlFor="zone-desc">
            <Textarea
              id="zone-desc"
              rows={4}
              value={form.description}
              onChange={(e) => setForm((p) => ({ ...p, description: e.target.value }))}
              placeholder={PH.descriptionOptional}
            />
          </FormField>
          <FormField label="status" htmlFor="zone-status">
            <Input
              id="zone-status"
              value={form.status}
              onChange={(e) => setForm((p) => ({ ...p, status: e.target.value }))}
              placeholder={PH.statusTextOptional}
            />
          </FormField>
        </FormSection>
        <FormActions onCancel={onCancel} saving={saving} submitLabel={mode === 'edit' ? 'Save Changes' : 'Create Zone'} />
      </form>
    </FormContainer>
  );
};

export default ZoneForm;
