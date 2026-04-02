import React, { useEffect, useState } from 'react';
import { AlertCircle } from 'lucide-react';
import { extensionsService } from '../../../services/extensionsService';
import { PH, SELECT_PH } from '../../../constants/formPlaceholders';
import { FormActions, FormContainer, FormField, FormSection, Input, Select } from '../../common/form';

interface ExtensionFormProps {
  mode: 'create' | 'edit';
  extensionId?: string;
  onSuccess: () => Promise<void> | void;
  onCancel: () => void;
}

const ExtensionForm: React.FC<ExtensionFormProps> = ({ mode, extensionId, onSuccess, onCancel }) => {
  const [loading, setLoading] = useState(mode === 'edit');
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [form, setForm] = useState({
    name: '',
    type: '',
    status: mode === 'create' ? 'active' : '',
  });

  useEffect(() => {
    if (mode !== 'edit' || !extensionId) return;
    const load = async () => {
      try {
        setLoading(true);
        setError(null);
        const row = await extensionsService.getById(extensionId);
        setForm({
          name: row.name || '',
          type: row.type || '',
          status: row.status || 'active',
        });
      } catch (err: unknown) {
        setError(err instanceof Error ? err.message : 'Failed to load extension');
      } finally {
        setLoading(false);
      }
    };
    void load();
  }, [mode, extensionId]);

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
        type: form.type.trim() || undefined,
        status: form.status || undefined,
      };
      if (mode === 'edit' && extensionId) await extensionsService.update(extensionId, payload);
      else await extensionsService.create(payload);
      await onSuccess();
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : `Failed to ${mode} extension`);
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
          <FormField className="md:col-span-2" label="name" required htmlFor="ext-name">
            <Input
              id="ext-name"
              type="text"
              value={form.name}
              onChange={(e) => setForm((p) => ({ ...p, name: e.target.value }))}
              placeholder={PH.extensionName}
            />
          </FormField>
          <FormField label="type" htmlFor="ext-type">
            <Input
              id="ext-type"
              type="text"
              value={form.type}
              onChange={(e) => setForm((p) => ({ ...p, type: e.target.value }))}
              placeholder={PH.extensionTypeOptional}
            />
          </FormField>
          <FormField label="status" htmlFor="ext-status">
            <Select
              id="ext-status"
              value={form.status}
              onChange={(e) => setForm((p) => ({ ...p, status: e.target.value }))}
            >
              <option value="" disabled>
                {SELECT_PH.status}
              </option>
              <option value="active">active</option>
              <option value="inactive">inactive</option>
              <option value="disabled">disabled</option>
            </Select>
          </FormField>
        </FormSection>
        <FormActions onCancel={onCancel} saving={saving} submitLabel={mode === 'edit' ? 'Save Changes' : 'Create Extension'} />
      </form>
    </FormContainer>
  );
};

export default ExtensionForm;
