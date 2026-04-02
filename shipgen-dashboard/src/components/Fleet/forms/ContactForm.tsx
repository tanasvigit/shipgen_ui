import React, { useEffect, useState } from 'react';
import { AlertCircle } from 'lucide-react';
import { contactsService } from '../../../services/contactsService';
import { formatMeta, parseMetaJson } from '../../../utils/contactHelpers';
import { PH } from '../../../constants/formPlaceholders';
import { FormActions, FormContainer, FormField, FormSection, Input, Textarea } from '../../common/form';

interface ContactFormProps {
  mode: 'create' | 'edit';
  contactId?: string;
  onSuccess: () => Promise<void> | void;
  onCancel: () => void;
}

const ContactForm: React.FC<ContactFormProps> = ({ mode, contactId, onSuccess, onCancel }) => {
  const [loading, setLoading] = useState(mode === 'edit');
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    phone: '',
    type: 'contact',
    title: '',
    meta_json: '',
  });

  useEffect(() => {
    if (mode !== 'edit' || !contactId) return;
    const run = async () => {
      try {
        setLoading(true);
        setError(null);
        const c = await contactsService.getById(contactId);
        setFormData({
          name: c.name ?? '',
          email: c.email ?? '',
          phone: c.phone ?? '',
          type: c.type ?? 'contact',
          title: c.title ?? '',
          meta_json: formatMeta(c.meta),
        });
      } catch (err: unknown) {
        setError(err instanceof Error ? err.message : 'Failed to load contact');
      } finally {
        setLoading(false);
      }
    };
    void run();
  }, [mode, contactId]);

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
        type: formData.type || null,
        title: formData.title.trim() || null,
        email: formData.email.trim() || null,
        phone: formData.phone.trim() || null,
        meta,
      };
      if (mode === 'edit' && contactId) await contactsService.update(contactId, payload);
      else await contactsService.create(payload);
      await onSuccess();
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : `Failed to ${mode} contact`);
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
          <FormField className="md:col-span-2" label="name" required htmlFor="contact-name">
            <Input
              id="contact-name"
              required
              value={formData.name}
              onChange={(e) => setFormData((p) => ({ ...p, name: e.target.value }))}
              placeholder={PH.personName}
            />
          </FormField>
          <FormField label="email" htmlFor="contact-email">
            <Input
              id="contact-email"
              value={formData.email}
              onChange={(e) => setFormData((p) => ({ ...p, email: e.target.value }))}
              placeholder={PH.emailOptional}
            />
          </FormField>
          <FormField label="phone" htmlFor="contact-phone">
            <Input
              id="contact-phone"
              value={formData.phone}
              onChange={(e) => setFormData((p) => ({ ...p, phone: e.target.value }))}
              placeholder={PH.phoneOptional}
            />
          </FormField>
          <FormField label="type" htmlFor="contact-type">
            <Input
              id="contact-type"
              value={formData.type}
              onChange={(e) => setFormData((p) => ({ ...p, type: e.target.value }))}
              placeholder={PH.contactTypeOptional}
            />
          </FormField>
          <FormField label="title" htmlFor="contact-title">
            <Input
              id="contact-title"
              value={formData.title}
              onChange={(e) => setFormData((p) => ({ ...p, title: e.target.value }))}
              placeholder={PH.contactTitleOptional}
            />
          </FormField>
          <FormField className="md:col-span-2" label="meta (JSON object, optional)" htmlFor="contact-meta">
            <Textarea
              id="contact-meta"
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

export default ContactForm;
