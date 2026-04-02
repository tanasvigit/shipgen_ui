import React, { useEffect, useState } from 'react';
import { AlertCircle } from 'lucide-react';
import { fleetsService } from '../../../services/fleetsService';
import { PH } from '../../../constants/formPlaceholders';
import { FormActions, FormContainer, FormField, FormSection, Input, Textarea } from '../../common/form';

interface FleetFormProps {
  mode: 'create' | 'edit';
  fleetId?: string;
  onSuccess: () => Promise<void> | void;
  onCancel: () => void;
}

const FleetForm: React.FC<FleetFormProps> = ({ mode, fleetId, onSuccess, onCancel }) => {
  const [loading, setLoading] = useState(mode === 'edit');
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [form, setForm] = useState({ name: '', description: '' });

  useEffect(() => {
    if (mode !== 'edit' || !fleetId) return;
    const run = async () => {
      try {
        setLoading(true);
        setError(null);
        const row = await fleetsService.getById(fleetId);
        setForm({ name: row.name || '', description: row.description || '' });
      } catch (err: unknown) {
        setError(err instanceof Error ? err.message : 'Failed to load fleet');
      } finally {
        setLoading(false);
      }
    };
    void run();
  }, [mode, fleetId]);

  const submit = async (event: React.FormEvent) => {
    event.preventDefault();
    if (!form.name.trim()) {
      setError('Name is required');
      return;
    }
    try {
      setSaving(true);
      setError(null);
      if (mode === 'edit' && fleetId) {
        await fleetsService.update(fleetId, { name: form.name.trim(), description: form.description.trim() || undefined });
      } else {
        await fleetsService.create({ name: form.name.trim(), description: form.description.trim() || undefined });
      }
      await onSuccess();
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : `Failed to ${mode} fleet`);
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
          <FormField className="md:col-span-2" label="name" required htmlFor="fleet-name">
            <Input
              id="fleet-name"
              value={form.name}
              onChange={(e) => setForm((p) => ({ ...p, name: e.target.value }))}
              placeholder={PH.fleetName}
            />
          </FormField>
          <FormField className="md:col-span-2" label="description" htmlFor="fleet-desc">
            <Textarea
              id="fleet-desc"
              rows={4}
              value={form.description}
              onChange={(e) => setForm((p) => ({ ...p, description: e.target.value }))}
              placeholder={PH.descriptionOptional}
            />
          </FormField>
        </FormSection>
        <FormActions
          onCancel={onCancel}
          saving={saving}
          submitLabel={mode === 'edit' ? 'Save Changes' : 'Create Fleet'}
        />
      </form>
    </FormContainer>
  );
};

export default FleetForm;
