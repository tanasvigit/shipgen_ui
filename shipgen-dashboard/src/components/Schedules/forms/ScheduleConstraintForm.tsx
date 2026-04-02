import React, { useEffect, useState } from 'react';
import { AlertCircle } from 'lucide-react';
import { scheduleConstraintsService } from '../../../services/scheduleConstraintsService';
import { PH } from '../../../constants/formPlaceholders';
import { FormActions, FormContainer, FormField, FormSection, Input, Textarea } from '../../common/form';

interface Props {
  mode: 'create' | 'edit';
  constraintId?: string;
  onSuccess: () => Promise<void> | void;
  onCancel: () => void;
}

const ScheduleConstraintForm: React.FC<Props> = ({ mode, constraintId, onSuccess, onCancel }) => {
  const [loading, setLoading] = useState(mode === 'edit');
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [form, setForm] = useState({ schedule_id: '', type: '', value: '', status: '', limit: '', rule_type: '', meta: '' });

  useEffect(() => {
    if (mode !== 'edit' || !constraintId) return;
    const run = async () => {
      try {
        setLoading(true);
        setError(null);
        const row = await scheduleConstraintsService.getById(constraintId);
        setForm({
          schedule_id: row.schedule_id || '',
          type: row.type || '',
          value: row.value || '',
          status: row.status || '',
          limit: row.limit || '',
          rule_type: row.rule_type || '',
          meta: row.meta || '',
        });
      } catch (err: unknown) {
        setError(err instanceof Error ? err.message : 'Failed to load schedule constraint');
      } finally {
        setLoading(false);
      }
    };
    void run();
  }, [mode, constraintId]);

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!form.schedule_id.trim()) return setError('Schedule ID is required');
    try {
      setSaving(true);
      setError(null);
      const payload = {
        schedule_id: form.schedule_id.trim(),
        type: form.type.trim() || undefined,
        value: form.value.trim() || undefined,
        status: form.status.trim() || undefined,
        limit: form.limit.trim() || undefined,
        rule_type: form.rule_type.trim() || undefined,
        meta: form.meta.trim() || undefined,
      };
      if (mode === 'edit' && constraintId) await scheduleConstraintsService.update(constraintId, payload);
      else await scheduleConstraintsService.create(payload);
      await onSuccess();
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : `Failed to ${mode} schedule constraint`);
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
          <FormField className="md:col-span-2" label="schedule_id" required htmlFor="sc-schedule">
            <Input
              id="sc-schedule"
              value={form.schedule_id}
              onChange={(e) => setForm((p) => ({ ...p, schedule_id: e.target.value }))}
              placeholder={PH.scheduleId}
            />
          </FormField>
          <FormField label="type" htmlFor="sc-type">
            <Input
              id="sc-type"
              value={form.type}
              onChange={(e) => setForm((p) => ({ ...p, type: e.target.value }))}
              placeholder={PH.constraintTypeOptional}
            />
          </FormField>
          <FormField label="value" htmlFor="sc-value">
            <Input
              id="sc-value"
              value={form.value}
              onChange={(e) => setForm((p) => ({ ...p, value: e.target.value }))}
              placeholder={PH.constraintValueOptional}
            />
          </FormField>
          <FormField label="status" htmlFor="sc-status">
            <Input
              id="sc-status"
              value={form.status}
              onChange={(e) => setForm((p) => ({ ...p, status: e.target.value }))}
              placeholder={PH.statusTextOptional}
            />
          </FormField>
          <FormField label="limit" htmlFor="sc-limit">
            <Input
              id="sc-limit"
              value={form.limit}
              onChange={(e) => setForm((p) => ({ ...p, limit: e.target.value }))}
              placeholder={PH.limitOptional}
            />
          </FormField>
          <FormField label="rule_type" htmlFor="sc-rule">
            <Input
              id="sc-rule"
              value={form.rule_type}
              onChange={(e) => setForm((p) => ({ ...p, rule_type: e.target.value }))}
              placeholder={PH.ruleTypeOptional}
            />
          </FormField>
          <FormField className="md:col-span-2" label="meta (optional JSON/plain text)" htmlFor="sc-meta">
            <Textarea
              id="sc-meta"
              rows={4}
              value={form.meta}
              onChange={(e) => setForm((p) => ({ ...p, meta: e.target.value }))}
              placeholder={PH.metaPlainOptional}
              className="font-mono text-sm"
            />
          </FormField>
        </FormSection>
        <FormActions onCancel={onCancel} saving={saving} submitLabel={mode === 'edit' ? 'Save Changes' : 'Create Constraint'} />
      </form>
    </FormContainer>
  );
};

export default ScheduleConstraintForm;
