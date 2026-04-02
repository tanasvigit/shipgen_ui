import React, { useEffect, useState } from 'react';
import { AlertCircle } from 'lucide-react';
import { entitiesService } from '../../../services/entitiesService';
import { PH } from '../../../constants/formPlaceholders';
import { FormActions, FormContainer, FormField, FormSection, Input } from '../../common/form';

interface EntityFormProps {
  mode: 'create' | 'edit';
  entityId?: string;
  onSuccess: () => Promise<void> | void;
  onCancel: () => void;
}

const EntityForm: React.FC<EntityFormProps> = ({ mode, entityId, onSuccess, onCancel }) => {
  const [loading, setLoading] = useState(mode === 'edit');
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [form, setForm] = useState({ name: '', type: '', status: '' });

  useEffect(() => {
    if (mode !== 'edit' || !entityId) return;
    const run = async () => {
      try {
        setLoading(true);
        setError(null);
        const row = await entitiesService.getById(entityId);
        setForm({ name: row.name || '', type: row.type || '', status: row.status || '' });
      } catch (err: unknown) {
        setError(err instanceof Error ? err.message : 'Failed to load entity');
      } finally {
        setLoading(false);
      }
    };
    void run();
  }, [mode, entityId]);

  const submit = async (event: React.FormEvent) => {
    event.preventDefault();
    if (!form.name.trim()) {
      setError('Name is required');
      return;
    }
    try {
      setSaving(true);
      setError(null);
      const payload = { name: form.name.trim(), type: form.type.trim() || undefined, status: form.status.trim() || undefined };
      if (mode === 'edit' && entityId) {
        await entitiesService.update(entityId, payload);
      } else {
        await entitiesService.create(payload);
      }
      await onSuccess();
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : `Failed to ${mode} entity`);
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
          <FormField className="md:col-span-2" label="name" required htmlFor="entity-name">
            <Input
              id="entity-name"
              value={form.name}
              onChange={(e) => setForm((p) => ({ ...p, name: e.target.value }))}
              placeholder={PH.entityName}
            />
          </FormField>
          <FormField label="type" htmlFor="entity-type">
            <Input
              id="entity-type"
              value={form.type}
              onChange={(e) => setForm((p) => ({ ...p, type: e.target.value }))}
              placeholder={PH.entityTypeOptional}
            />
          </FormField>
          <FormField label="status" htmlFor="entity-status">
            <Input
              id="entity-status"
              value={form.status}
              onChange={(e) => setForm((p) => ({ ...p, status: e.target.value }))}
              placeholder={PH.statusTextOptional}
            />
          </FormField>
        </FormSection>
        <FormActions
          onCancel={onCancel}
          saving={saving}
          submitLabel={mode === 'edit' ? 'Save Changes' : 'Create Entity'}
        />
      </form>
    </FormContainer>
  );
};

export default EntityForm;
