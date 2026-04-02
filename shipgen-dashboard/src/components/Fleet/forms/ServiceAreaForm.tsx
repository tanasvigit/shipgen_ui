import React, { useEffect, useState } from 'react';
import { AlertCircle } from 'lucide-react';
import { serviceAreasService } from '../../../services/serviceAreasService';
import { PH } from '../../../constants/formPlaceholders';
import { FormActions, FormContainer, FormField, FormSection, Input, Textarea } from '../../common/form';

interface ServiceAreaFormProps {
  mode: 'create' | 'edit';
  serviceAreaId?: string;
  onSuccess: () => Promise<void> | void;
  onCancel: () => void;
}

const ServiceAreaForm: React.FC<ServiceAreaFormProps> = ({ mode, serviceAreaId, onSuccess, onCancel }) => {
  const [loading, setLoading] = useState(mode === 'edit');
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [form, setForm] = useState({ name: '', description: '', status: '' });

  useEffect(() => {
    if (mode !== 'edit' || !serviceAreaId) return;
    const run = async () => {
      try {
        setLoading(true);
        setError(null);
        const row = await serviceAreasService.getById(serviceAreaId);
        setForm({ name: row.name || '', description: row.description || '', status: row.status || '' });
      } catch (err: unknown) {
        setError(err instanceof Error ? err.message : 'Failed to load service area');
      } finally {
        setLoading(false);
      }
    };
    void run();
  }, [mode, serviceAreaId]);

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
      if (mode === 'edit' && serviceAreaId) {
        await serviceAreasService.update(serviceAreaId, payload);
      } else {
        await serviceAreasService.create(payload);
      }
      await onSuccess();
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : `Failed to ${mode} service area`);
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
          <FormField className="md:col-span-2" label="name" required htmlFor="sa-name">
            <Input
              id="sa-name"
              value={form.name}
              onChange={(e) => setForm((p) => ({ ...p, name: e.target.value }))}
              placeholder={PH.serviceAreaName}
            />
          </FormField>
          <FormField className="md:col-span-2" label="description" htmlFor="sa-desc">
            <Textarea
              id="sa-desc"
              rows={4}
              value={form.description}
              onChange={(e) => setForm((p) => ({ ...p, description: e.target.value }))}
              placeholder={PH.descriptionOptional}
            />
          </FormField>
          <FormField label="status" htmlFor="sa-status">
            <Input
              id="sa-status"
              value={form.status}
              onChange={(e) => setForm((p) => ({ ...p, status: e.target.value }))}
              placeholder={PH.statusTextOptional}
            />
          </FormField>
        </FormSection>
        <FormActions
          onCancel={onCancel}
          saving={saving}
          submitLabel={mode === 'edit' ? 'Save Changes' : 'Create Service Area'}
        />
      </form>
    </FormContainer>
  );
};

export default ServiceAreaForm;
