import React, { useEffect, useState } from 'react';
import { AlertCircle } from 'lucide-react';
import { customFieldsService } from '../../../services/customFieldsService';
import { PH, SELECT_PH } from '../../../constants/formPlaceholders';
import { FormActions, FormContainer, FormField, FormSection, Input, Select } from '../../common/form';

const TYPE_OPTIONS = ['text', 'number', 'date', 'boolean'];

interface CustomFieldFormProps {
  mode: 'create' | 'edit';
  customFieldId?: string;
  onSuccess: () => Promise<void> | void;
  onCancel: () => void;
}

const CustomFieldForm: React.FC<CustomFieldFormProps> = ({ mode, customFieldId, onSuccess, onCancel }) => {
  const [loading, setLoading] = useState(mode === 'edit');
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [form, setForm] = useState({
    name: '',
    type: 'text',
    entity: '',
    required: false,
  });

  useEffect(() => {
    if (mode !== 'edit' || !customFieldId) return;
    const load = async () => {
      try {
        setLoading(true);
        setError(null);
        const row = await customFieldsService.getById(customFieldId);
        setForm({
          name: row.name || '',
          type: row.type || 'text',
          entity: row.entity || '',
          required: !!row.required,
        });
      } catch (err: unknown) {
        setError(err instanceof Error ? err.message : 'Failed to load custom field');
      } finally {
        setLoading(false);
      }
    };
    void load();
  }, [mode, customFieldId]);

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!form.name.trim()) {
      setError('Name is required');
      return;
    }
    try {
      setSaving(true);
      setError(null);
      const payload = {
        name: form.name.trim(),
        type: form.type,
        entity: form.entity.trim() || undefined,
        required: form.required,
      };
      if (mode === 'edit' && customFieldId) await customFieldsService.update(customFieldId, payload);
      else await customFieldsService.create(payload);
      await onSuccess();
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : `Failed to ${mode} custom field`);
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
          <FormField className="md:col-span-2" label="name" required htmlFor="cf-name">
            <Input
              id="cf-name"
              type="text"
              value={form.name}
              onChange={(e) => setForm((p) => ({ ...p, name: e.target.value }))}
              placeholder={PH.customFieldName}
            />
          </FormField>
          <FormField label="type" htmlFor="cf-type">
            <Select
              id="cf-type"
              value={form.type}
              onChange={(e) => setForm((p) => ({ ...p, type: e.target.value }))}
            >
              <option value="" disabled>
                {SELECT_PH.fieldType}
              </option>
              {TYPE_OPTIONS.map((t) => (
                <option key={t} value={t}>
                  {t}
                </option>
              ))}
            </Select>
          </FormField>
          <FormField label="entity" htmlFor="cf-entity">
            <Input
              id="cf-entity"
              type="text"
              placeholder={PH.customFieldEntityOptional}
              value={form.entity}
              onChange={(e) => setForm((p) => ({ ...p, entity: e.target.value }))}
            />
          </FormField>
          <FormField className="md:col-span-2" label="required" htmlFor="cf-required">
            <input
              id="cf-required"
              type="checkbox"
              checked={form.required}
              onChange={(e) => setForm((p) => ({ ...p, required: e.target.checked }))}
              className="h-4 w-4 rounded border-gray-200 text-blue-600 transition focus:ring-1 focus:ring-blue-500"
            />
          </FormField>
        </FormSection>
        <FormActions onCancel={onCancel} saving={saving} submitLabel={mode === 'edit' ? 'Save Changes' : 'Create Custom Field'} />
      </form>
    </FormContainer>
  );
};

export default CustomFieldForm;
