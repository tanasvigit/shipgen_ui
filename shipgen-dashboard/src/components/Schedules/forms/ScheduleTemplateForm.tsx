import React, { useEffect, useState } from 'react';
import { AlertCircle } from 'lucide-react';
import { scheduleTemplatesService } from '../../../services/scheduleTemplatesService';
import { PH } from '../../../constants/formPlaceholders';
import { FormActions, FormContainer, FormField, FormSection, Input } from '../../common/form';

interface Props {
  mode: 'create' | 'edit';
  templateId?: string;
  onSuccess: () => Promise<void> | void;
  onCancel: () => void;
}

const ScheduleTemplateForm: React.FC<Props> = ({ mode, templateId, onSuccess, onCancel }) => {
  const [loading, setLoading] = useState(mode === 'edit');
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [form, setForm] = useState({ name: '', type: '', status: '' });

  useEffect(() => {
    if (mode !== 'edit' || !templateId) return;
    const run = async () => {
      try {
        setLoading(true);
        setError(null);
        const row = await scheduleTemplatesService.getById(templateId);
        setForm({ name: row.name || '', type: row.type || '', status: row.status || '' });
      } catch (err: unknown) {
        setError(err instanceof Error ? err.message : 'Failed to load schedule template');
      } finally {
        setLoading(false);
      }
    };
    void run();
  }, [mode, templateId]);

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!form.name.trim()) return setError('Name is required');
    try {
      setSaving(true);
      setError(null);
      const payload = { name: form.name.trim(), type: form.type.trim() || undefined, status: form.status.trim() || undefined };
      if (mode === 'edit' && templateId) await scheduleTemplatesService.update(templateId, payload);
      else await scheduleTemplatesService.create(payload);
      await onSuccess();
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : `Failed to ${mode} schedule template`);
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
          <FormField className="md:col-span-2" label="name" required htmlFor="st-name">
            <Input
              id="st-name"
              value={form.name}
              onChange={(e) => setForm((p) => ({ ...p, name: e.target.value }))}
              placeholder={PH.scheduleName}
            />
          </FormField>
          <FormField label="type" htmlFor="st-type">
            <Input
              id="st-type"
              value={form.type}
              onChange={(e) => setForm((p) => ({ ...p, type: e.target.value }))}
              placeholder={PH.scheduleTypeOptional}
            />
          </FormField>
          <FormField label="status" htmlFor="st-status">
            <Input
              id="st-status"
              value={form.status}
              onChange={(e) => setForm((p) => ({ ...p, status: e.target.value }))}
              placeholder={PH.statusTextOptional}
            />
          </FormField>
        </FormSection>
        <FormActions onCancel={onCancel} saving={saving} submitLabel={mode === 'edit' ? 'Save Changes' : 'Create Template'} />
      </form>
    </FormContainer>
  );
};

export default ScheduleTemplateForm;
