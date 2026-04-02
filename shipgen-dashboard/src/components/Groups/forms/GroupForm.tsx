import React, { useEffect, useState } from 'react';
import { AlertCircle } from 'lucide-react';
import { groupsService } from '../../../services/groupsService';
import { PH } from '../../../constants/formPlaceholders';
import { FormActions, FormContainer, FormField, FormSection, Input, Textarea } from '../../common/form';

interface GroupFormProps {
  mode: 'create' | 'edit';
  groupId?: string;
  onSuccess: () => Promise<void> | void;
  onCancel: () => void;
}

const GroupForm: React.FC<GroupFormProps> = ({ mode, groupId, onSuccess, onCancel }) => {
  const [loading, setLoading] = useState(mode === 'edit');
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [form, setForm] = useState({
    name: '',
    description: '',
  });

  useEffect(() => {
    if (mode !== 'edit' || !groupId) return;
    const load = async () => {
      try {
        setLoading(true);
        setError(null);
        const row = await groupsService.getById(groupId);
        setForm({
          name: row.name || '',
          description: row.description || '',
        });
      } catch (err: unknown) {
        setError(err instanceof Error ? err.message : 'Failed to load group');
      } finally {
        setLoading(false);
      }
    };
    void load();
  }, [mode, groupId]);

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!form.name.trim()) {
      setError('Name is required');
      return;
    }
    try {
      setSaving(true);
      setError(null);
      if (mode === 'edit' && groupId) {
        await groupsService.update(groupId, {
          name: form.name.trim(),
          description: form.description.trim(),
        });
      } else {
        await groupsService.create({
          name: form.name.trim(),
          description: form.description.trim() || undefined,
        });
      }
      await onSuccess();
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : `Failed to ${mode} group`);
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
          <FormField className="md:col-span-2" label="name" required htmlFor="group-name">
            <Input
              id="group-name"
              type="text"
              value={form.name}
              onChange={(e) => setForm((p) => ({ ...p, name: e.target.value }))}
              placeholder={PH.groupName}
            />
          </FormField>
          <FormField className="md:col-span-2" label="description" htmlFor="group-desc">
            <Textarea
              id="group-desc"
              rows={4}
              value={form.description}
              onChange={(e) => setForm((p) => ({ ...p, description: e.target.value }))}
              placeholder={PH.descriptionOptional}
            />
          </FormField>
        </FormSection>
        <FormActions onCancel={onCancel} saving={saving} submitLabel={mode === 'edit' ? 'Save Changes' : 'Create Group'} />
      </form>
    </FormContainer>
  );
};

export default GroupForm;
