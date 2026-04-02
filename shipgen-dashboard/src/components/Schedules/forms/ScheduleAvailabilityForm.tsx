import React, { useEffect, useState } from 'react';
import { AlertCircle } from 'lucide-react';
import { scheduleAvailabilityService } from '../../../services/scheduleAvailabilityService';
import { PH } from '../../../constants/formPlaceholders';
import { FormActions, FormContainer, FormField, FormSection, Input } from '../../common/form';

interface Props {
  mode: 'create' | 'edit';
  availabilityId?: string;
  onSuccess: () => Promise<void> | void;
  onCancel: () => void;
}

const ScheduleAvailabilityForm: React.FC<Props> = ({ mode, availabilityId, onSuccess, onCancel }) => {
  const [loading, setLoading] = useState(mode === 'edit');
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [form, setForm] = useState({ schedule_id: '', type: '', status: '', start_time: '', end_time: '', day_of_week: '' });

  useEffect(() => {
    if (mode !== 'edit' || !availabilityId) return;
    const run = async () => {
      try {
        setLoading(true);
        setError(null);
        const row = await scheduleAvailabilityService.getById(availabilityId);
        setForm({
          schedule_id: row.schedule_id || '',
          type: row.type || '',
          status: row.status || '',
          start_time: row.start_time || '',
          end_time: row.end_time || '',
          day_of_week: row.day_of_week || '',
        });
      } catch (err: unknown) {
        setError(err instanceof Error ? err.message : 'Failed to load availability');
      } finally {
        setLoading(false);
      }
    };
    void run();
  }, [mode, availabilityId]);

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!form.schedule_id.trim()) return setError('Schedule ID is required');
    try {
      setSaving(true);
      setError(null);
      const payload = {
        schedule_id: form.schedule_id.trim(),
        type: form.type.trim() || undefined,
        status: form.status.trim() || undefined,
        start_time: form.start_time.trim() || undefined,
        end_time: form.end_time.trim() || undefined,
        day_of_week: form.day_of_week.trim() || undefined,
      };
      if (mode === 'edit' && availabilityId) await scheduleAvailabilityService.update(availabilityId, payload);
      else await scheduleAvailabilityService.create(payload);
      await onSuccess();
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : `Failed to ${mode} availability`);
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
          <FormField className="md:col-span-2" label="schedule_id" required htmlFor="sa2-schedule">
            <Input
              id="sa2-schedule"
              value={form.schedule_id}
              onChange={(e) => setForm((p) => ({ ...p, schedule_id: e.target.value }))}
              placeholder={PH.scheduleId}
            />
          </FormField>
          <FormField label="type" htmlFor="sa2-type">
            <Input
              id="sa2-type"
              value={form.type}
              onChange={(e) => setForm((p) => ({ ...p, type: e.target.value }))}
              placeholder={PH.scheduleTypeOptional}
            />
          </FormField>
          <FormField label="status" htmlFor="sa2-status">
            <Input
              id="sa2-status"
              value={form.status}
              onChange={(e) => setForm((p) => ({ ...p, status: e.target.value }))}
              placeholder={PH.statusTextOptional}
            />
          </FormField>
          <FormField label="start_time" htmlFor="sa2-start">
            <Input
              id="sa2-start"
              value={form.start_time}
              onChange={(e) => setForm((p) => ({ ...p, start_time: e.target.value }))}
              placeholder={PH.isoStartOptional}
            />
          </FormField>
          <FormField label="end_time" htmlFor="sa2-end">
            <Input
              id="sa2-end"
              value={form.end_time}
              onChange={(e) => setForm((p) => ({ ...p, end_time: e.target.value }))}
              placeholder={PH.isoEndOptional}
            />
          </FormField>
          <FormField label="day_of_week" htmlFor="sa2-dow">
            <Input
              id="sa2-dow"
              value={form.day_of_week}
              onChange={(e) => setForm((p) => ({ ...p, day_of_week: e.target.value }))}
              placeholder={PH.dayOfWeekOptional}
            />
          </FormField>
        </FormSection>
        <FormActions onCancel={onCancel} saving={saving} submitLabel={mode === 'edit' ? 'Save Changes' : 'Create Availability'} />
      </form>
    </FormContainer>
  );
};

export default ScheduleAvailabilityForm;
