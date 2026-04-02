import React, { useEffect, useState } from 'react';
import { AlertCircle } from 'lucide-react';
import { vendorsService } from '../../../services/vendorsService';
import { formatMeta, parseMetaJson } from '../../../utils/contactHelpers';
import { PH } from '../../../constants/formPlaceholders';
import { FormActions, FormContainer, FormField, FormSection, Input, Textarea } from '../../common/form';

interface VendorFormProps {
  mode: 'create' | 'edit';
  vendorId?: string;
  onSuccess: () => Promise<void> | void;
  onCancel: () => void;
}

const VendorForm: React.FC<VendorFormProps> = ({ mode, vendorId, onSuccess, onCancel }) => {
  const [loading, setLoading] = useState(mode === 'edit');
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [formData, setFormData] = useState({
    name: '',
    type: '',
    email: '',
    phone: '',
    meta_json: '',
  });

  useEffect(() => {
    if (mode !== 'edit' || !vendorId) return;
    const run = async () => {
      try {
        setLoading(true);
        setError(null);
        const v = await vendorsService.getById(vendorId);
        setFormData({
          name: v.name ?? '',
          type: v.type ?? '',
          email: v.email ?? '',
          phone: v.phone ?? '',
          meta_json: formatMeta(v.meta),
        });
      } catch (err: unknown) {
        setError(err instanceof Error ? err.message : 'Failed to load vendor');
      } finally {
        setLoading(false);
      }
    };
    void run();
  }, [mode, vendorId]);

  const submit = async (event: React.FormEvent) => {
    event.preventDefault();
    if (!formData.name.trim()) {
      setError('name is required');
      return;
    }
    let meta: Record<string, unknown> | null = null;
    try {
      meta = formData.meta_json.trim() ? parseMetaJson(formData.meta_json) : null;
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Invalid meta');
      return;
    }

    try {
      setSaving(true);
      setError(null);
      const payload: Record<string, unknown> = {
        name: formData.name.trim(),
        type: formData.type.trim() || null,
        email: formData.email.trim() || null,
        phone: formData.phone.trim() || null,
        meta,
      };
      if (mode === 'edit' && vendorId) await vendorsService.update(vendorId, payload);
      else await vendorsService.create(payload);
      await onSuccess();
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : `Failed to ${mode} vendor`);
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
          <FormField className="md:col-span-2" label="name" required htmlFor="vendor-name">
            <Input
              id="vendor-name"
              required
              value={formData.name}
              onChange={(e) => setFormData((p) => ({ ...p, name: e.target.value }))}
              placeholder={PH.companyName}
            />
          </FormField>
          <FormField label="type" htmlFor="vendor-type">
            <Input
              id="vendor-type"
              value={formData.type}
              onChange={(e) => setFormData((p) => ({ ...p, type: e.target.value }))}
              placeholder={PH.vendorTypeOptional}
            />
          </FormField>
          <FormField label="email" htmlFor="vendor-email">
            <Input
              id="vendor-email"
              value={formData.email}
              onChange={(e) => setFormData((p) => ({ ...p, email: e.target.value }))}
              placeholder={PH.emailOptional}
            />
          </FormField>
          <FormField className="md:col-span-2" label="phone" htmlFor="vendor-phone">
            <Input
              id="vendor-phone"
              value={formData.phone}
              onChange={(e) => setFormData((p) => ({ ...p, phone: e.target.value }))}
              placeholder={PH.phoneOptional}
            />
          </FormField>
          <FormField className="md:col-span-2" label="meta (JSON object, optional)" htmlFor="vendor-meta">
            <Textarea
              id="vendor-meta"
              rows={4}
              value={formData.meta_json}
              onChange={(e) => setFormData((p) => ({ ...p, meta_json: e.target.value }))}
              placeholder={PH.metaJsonOptional}
              className="font-mono text-sm"
            />
          </FormField>
        </FormSection>
        <FormActions onCancel={onCancel} saving={saving} submitLabel={mode === 'edit' ? 'Save' : 'Create'} />
      </form>
    </FormContainer>
  );
};

export default VendorForm;
