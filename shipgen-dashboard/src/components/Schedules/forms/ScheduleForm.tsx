import React, { useEffect, useState } from 'react';
import { AlertCircle } from 'lucide-react';
import { schedulesService } from '../../../services/schedulesService';
import { PH } from '../../../constants/formPlaceholders';
import { FormActions, FormContainer, FormField, FormSection, Input } from '../../common/form';

interface Props {
  mode: 'create' | 'edit';
  scheduleId?: string;
  onSuccess: () => Promise<void> | void;
  onCancel: () => void;
}

const ScheduleForm: React.FC<Props> = ({ mode, scheduleId, onSuccess, onCancel }) => {
  const [loading, setLoading] = useState(mode === 'edit');
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [form, setForm] = useState({ name: '', type: '', status: '' });

  useEffect(() => {
    if (mode !== 'edit' || !scheduleId) return;
    const run = async () => {
      try {
        setLoading(true);
        setError(null);
        const row = await schedulesService.getById(scheduleId);
        setForm({ name: row.name || '', type: row.type || '', status: row.status || '' });
      } catch (err: unknown) {
        setError(err instanceof Error ? err.message : 'Failed to load schedule');
      } finally {
        setLoading(false);
      }
    };
    void run();
  }, [mode, scheduleId]);

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!form.name.trim()) return setError('Name is required');
    try {
      setSaving(true);
      setError(null);
      const payload = { name: form.name.trim(), type: form.type.trim() || undefined, status: form.status.trim() || undefined };
      if (mode === 'edit' && scheduleId) await schedulesService.update(scheduleId, payload);
      else await schedulesService.create(payload);
      await onSuccess();
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : `Failed to ${mode} schedule`);
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
          <FormField className="md:col-span-2" label="name" required htmlFor="sched-name">
            <Input
              id="sched-name"
              value={form.name}
              onChange={(e) => setForm((p) => ({ ...p, name: e.target.value }))}
              placeholder={PH.scheduleName}
            />
          </FormField>
          <FormField label="type" htmlFor="sched-type">
            <Input
              id="sched-type"
              value={form.type}
              onChange={(e) => setForm((p) => ({ ...p, type: e.target.value }))}
              placeholder={PH.scheduleTypeOptional}
            />
          </FormField>
          <FormField label="status" htmlFor="sched-status">
            <Input
              id="sched-status"
              value={form.status}
              onChange={(e) => setForm((p) => ({ ...p, status: e.target.value }))}
              placeholder={PH.statusTextOptional}
            />
          </FormField>
        </FormSection>
        <FormActions onCancel={onCancel} saving={saving} submitLabel={mode === 'edit' ? 'Save Changes' : 'Create Schedule'} />
      </form>
    </FormContainer>
  );
};

export default ScheduleForm;
