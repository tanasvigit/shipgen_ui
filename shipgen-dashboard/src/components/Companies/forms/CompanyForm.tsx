import React, { useEffect, useState } from 'react';
import { AlertCircle } from 'lucide-react';
import { companiesService } from '../../../services/companiesService';
import { PH } from '../../../constants/formPlaceholders';
import { FormActions, FormContainer, FormField, FormSection, Input } from '../../common/form';

interface CompanyFormProps {
  mode: 'create' | 'edit';
  companyId?: string;
  onSuccess: () => Promise<void> | void;
  onCancel: () => void;
}

const CompanyForm: React.FC<CompanyFormProps> = ({ mode, companyId, onSuccess, onCancel }) => {
  const [loading, setLoading] = useState(mode === 'edit');
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [form, setForm] = useState({
    name: '',
    slug: '',
    status: '',
  });

  useEffect(() => {
    if (mode !== 'edit' || !companyId) return;
    const load = async () => {
      try {
        setLoading(true);
        setError(null);
        const row = await companiesService.getById(companyId);
        setForm({
          name: row.name || '',
          slug: row.slug || '',
          status: row.status || '',
        });
      } catch (err: unknown) {
        setError(err instanceof Error ? err.message : 'Failed to load company');
      } finally {
        setLoading(false);
      }
    };
    void load();
  }, [mode, companyId]);

  const submit = async (e: React.FormEvent) => {
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
        slug: form.slug.trim() || undefined,
        status: form.status.trim() || undefined,
      };
      if (mode === 'edit' && companyId) {
        await companiesService.update(companyId, payload);
      } else {
        await companiesService.create(payload);
      }
      await onSuccess();
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : `Failed to ${mode} company`);
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
        {error && (
          <div className="flex items-center gap-2 rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">
            <AlertCircle size={18} />
            <span>{error}</span>
          </div>
        )}
        <FormSection>
          <FormField className="md:col-span-2" label="name" required htmlFor="co-name">
            <Input
              id="co-name"
              type="text"
              value={form.name}
              onChange={(e) => setForm((p) => ({ ...p, name: e.target.value }))}
              placeholder={PH.companyName}
            />
          </FormField>
          <FormField label="slug" htmlFor="co-slug">
            <Input
              id="co-slug"
              type="text"
              value={form.slug}
              onChange={(e) => setForm((p) => ({ ...p, slug: e.target.value }))}
              placeholder={PH.slugOptional}
            />
          </FormField>
          <FormField label="status" htmlFor="co-status">
            <Input
              id="co-status"
              type="text"
              value={form.status}
              onChange={(e) => setForm((p) => ({ ...p, status: e.target.value }))}
              placeholder={PH.statusTextOptional}
            />
          </FormField>
        </FormSection>
        <FormActions onCancel={onCancel} saving={saving} submitLabel={mode === 'edit' ? 'Save Changes' : 'Create Company'} />
      </form>
    </FormContainer>
  );
};

export default CompanyForm;
