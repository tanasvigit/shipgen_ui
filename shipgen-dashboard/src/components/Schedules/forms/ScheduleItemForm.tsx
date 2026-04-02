import React, { useEffect, useState } from 'react';
import { AlertCircle } from 'lucide-react';
import { scheduleItemsService } from '../../../services/scheduleItemsService';
import { PH } from '../../../constants/formPlaceholders';
import { FormActions, FormContainer, FormField, FormSection, Input } from '../../common/form';

interface Props {
  mode: 'create' | 'edit';
  itemId?: string;
  onSuccess: () => Promise<void> | void;
  onCancel: () => void;
}

const ScheduleItemForm: React.FC<Props> = ({ mode, itemId, onSuccess, onCancel }) => {
  const [loading, setLoading] = useState(mode === 'edit');
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [form, setForm] = useState({ title: '', schedule_id: '', type: '', status: '' });

  useEffect(() => {
    if (mode !== 'edit' || !itemId) return;
    const run = async () => {
      try {
        setLoading(true);
        setError(null);
        const row = await scheduleItemsService.getById(itemId);
        setForm({ title: row.title || '', schedule_id: row.schedule_id || '', type: row.type || '', status: row.status || '' });
      } catch (err: unknown) {
        setError(err instanceof Error ? err.message : 'Failed to load schedule item');
      } finally {
        setLoading(false);
      }
    };
    void run();
  }, [mode, itemId]);

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!form.title.trim()) return setError('Name/Title is required');
    if (!form.schedule_id.trim()) return setError('Schedule ID is required');
    try {
      setSaving(true);
      setError(null);
      const payload = {
        title: form.title.trim(),
        schedule_id: form.schedule_id.trim(),
        type: form.type.trim() || undefined,
        status: form.status.trim() || undefined,
      };
      if (mode === 'edit' && itemId) await scheduleItemsService.update(itemId, payload);
      else await scheduleItemsService.create(payload);
      await onSuccess();
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : `Failed to ${mode} schedule item`);
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
          <FormField className="md:col-span-2" label="name/title" required htmlFor="si-title">
            <Input
              id="si-title"
              value={form.title}
              onChange={(e) => setForm((p) => ({ ...p, title: e.target.value }))}
              placeholder={PH.scheduleTitle}
            />
          </FormField>
          <FormField className="md:col-span-2" label="schedule_id" required htmlFor="si-schedule">
            <Input
              id="si-schedule"
              value={form.schedule_id}
              onChange={(e) => setForm((p) => ({ ...p, schedule_id: e.target.value }))}
              placeholder={PH.scheduleId}
            />
          </FormField>
          <FormField label="type" htmlFor="si-type">
            <Input
              id="si-type"
              value={form.type}
              onChange={(e) => setForm((p) => ({ ...p, type: e.target.value }))}
              placeholder={PH.scheduleTypeOptional}
            />
          </FormField>
          <FormField label="status" htmlFor="si-status">
            <Input
              id="si-status"
              value={form.status}
              onChange={(e) => setForm((p) => ({ ...p, status: e.target.value }))}
              placeholder={PH.statusTextOptional}
            />
          </FormField>
        </FormSection>
        <FormActions onCancel={onCancel} saving={saving} submitLabel={mode === 'edit' ? 'Save Changes' : 'Create Schedule Item'} />
      </form>
    </FormContainer>
  );
};

export default ScheduleItemForm;
