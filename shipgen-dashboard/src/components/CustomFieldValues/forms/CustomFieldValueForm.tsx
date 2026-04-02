import React, { useEffect, useState } from 'react';
import { AlertCircle } from 'lucide-react';
import { customFieldValuesService } from '../../../services/customFieldValuesService';
import { PH } from '../../../constants/formPlaceholders';
import { FormActions, FormContainer, FormField, FormSection, Input, Textarea } from '../../common/form';

interface CustomFieldValueFormProps {
  mode: 'create' | 'edit';
  customFieldValueId?: string;
  onSuccess: () => Promise<void> | void;
  onCancel: () => void;
}

const CustomFieldValueForm: React.FC<CustomFieldValueFormProps> = ({ mode, customFieldValueId, onSuccess, onCancel }) => {
  const [loading, setLoading] = useState(mode === 'edit');
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [form, setForm] = useState({
    custom_field_id: '',
    entity_id: '',
    entity_type: 'order',
    value: '',
  });

  useEffect(() => {
    if (mode !== 'edit' || !customFieldValueId) return;
    const load = async () => {
      try {
        setLoading(true);
        setError(null);
        const row = await customFieldValuesService.getById(customFieldValueId);
        setForm({
          custom_field_id: row.custom_field_id || '',
          entity_id: row.entity_id || '',
          entity_type: 'order',
          value: row.value || '',
        });
      } catch (err: unknown) {
        setError(err instanceof Error ? err.message : 'Failed to load custom field value');
      } finally {
        setLoading(false);
      }
    };
    void load();
  }, [mode, customFieldValueId]);

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!form.custom_field_id.trim() || !form.entity_id.trim()) {
      setError('custom_field_id and entity_id are required');
      return;
    }
    try {
      setSaving(true);
      setError(null);
      const payload = {
        custom_field_id: form.custom_field_id.trim(),
        entity_id: form.entity_id.trim(),
        entity_type: form.entity_type.trim() || 'order',
        value: form.value,
      };
      if (mode === 'edit' && customFieldValueId) await customFieldValuesService.update(customFieldValueId, payload);
      else await customFieldValuesService.create(payload);
      await onSuccess();
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : `Failed to ${mode} custom field value`);
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
      <form onSubmit={onSubmit} className="space-y-5">
        {error && (
          <div className="flex items-center gap-2 rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">
            <AlertCircle size={18} />
            <span>{error}</span>
          </div>
        )}
        <FormSection>
          <FormField className="md:col-span-2" label="custom_field_id" required htmlFor="cfv-field">
            <Input
              id="cfv-field"
              type="text"
              value={form.custom_field_id}
              onChange={(e) => setForm((p) => ({ ...p, custom_field_id: e.target.value }))}
              placeholder={PH.customFieldId}
            />
          </FormField>
          <FormField label="entity_id" required htmlFor="cfv-entity">
            <Input
              id="cfv-entity"
              type="text"
              value={form.entity_id}
              onChange={(e) => setForm((p) => ({ ...p, entity_id: e.target.value }))}
              placeholder={PH.entityId}
            />
          </FormField>
          <FormField label="entity_type" htmlFor="cfv-etype">
            <Input
              id="cfv-etype"
              type="text"
              placeholder={PH.entityTypeValueOptional}
              value={form.entity_type}
              onChange={(e) => setForm((p) => ({ ...p, entity_type: e.target.value }))}
            />
          </FormField>
          <FormField className="md:col-span-2" label="value" htmlFor="cfv-value">
            <Textarea
              id="cfv-value"
              rows={4}
              value={form.value}
              onChange={(e) => setForm((p) => ({ ...p, value: e.target.value }))}
              placeholder={PH.customFieldValueOptional}
            />
          </FormField>
        </FormSection>
        <FormActions onCancel={onCancel} saving={saving} submitLabel={mode === 'edit' ? 'Save Changes' : 'Create Value'} />
      </form>
    </FormContainer>
  );
};

export default CustomFieldValueForm;
