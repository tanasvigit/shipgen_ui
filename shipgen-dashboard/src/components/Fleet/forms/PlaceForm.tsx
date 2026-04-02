import React, { useEffect, useState } from 'react';
import { AlertCircle } from 'lucide-react';
import { placesService } from '../../../services/placesService';
import { formatMeta, parseMetaJson } from '../../../utils/contactHelpers';
import { PH } from '../../../constants/formPlaceholders';
import { FormActions, FormContainer, FormField, FormSection, Input, Textarea } from '../../common/form';

interface PlaceFormProps {
  mode: 'create' | 'edit';
  placeId?: string;
  onSuccess: () => Promise<void> | void;
  onCancel: () => void;
}

const PlaceForm: React.FC<PlaceFormProps> = ({ mode, placeId, onSuccess, onCancel }) => {
  const [loading, setLoading] = useState(mode === 'edit');
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [formData, setFormData] = useState({
    name: '',
    street1: '',
    street2: '',
    city: '',
    province: '',
    postal_code: '',
    country: '',
    latitude: '',
    longitude: '',
    phone: '',
    type: '',
    meta_json: '',
  });

  useEffect(() => {
    if (mode !== 'edit' || !placeId) return;
    const run = async () => {
      try {
        setLoading(true);
        setError(null);
        const p = await placesService.getById(placeId);
        setFormData({
          name: p.name ?? '',
          street1: p.street1 ?? '',
          street2: p.street2 ?? '',
          city: p.city ?? '',
          province: p.province ?? '',
          postal_code: p.postal_code ?? '',
          country: p.country ?? '',
          latitude: p.latitude ?? '',
          longitude: p.longitude ?? '',
          phone: p.phone ?? '',
          type: p.type ?? '',
          meta_json: formatMeta(p.meta),
        });
      } catch (err: unknown) {
        setError(err instanceof Error ? err.message : 'Failed to load place');
      } finally {
        setLoading(false);
      }
    };
    void run();
  }, [mode, placeId]);

  const submit = async (event: React.FormEvent) => {
    event.preventDefault();
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
      const payload: Record<string, unknown> = {};
      const setIf = (k: string, v: string) => {
        const t = v.trim();
        payload[k] = t || null;
      };
      setIf('name', formData.name);
      setIf('street1', formData.street1);
      setIf('street2', formData.street2);
      setIf('city', formData.city);
      setIf('province', formData.province);
      setIf('postal_code', formData.postal_code);
      setIf('country', formData.country);
      setIf('latitude', formData.latitude);
      setIf('longitude', formData.longitude);
      setIf('phone', formData.phone);
      setIf('type', formData.type);
      payload.meta = meta;
      if (mode === 'edit' && placeId) await placesService.update(placeId, payload);
      else await placesService.create(payload);
      await onSuccess();
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : `Failed to ${mode} place`);
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

  const field = (id: string, label: string, key: keyof typeof formData, ph?: string, fieldClassName?: string) => (
    <FormField label={label} htmlFor={id} className={fieldClassName}>
      <Input
        id={id}
        value={formData[key]}
        onChange={(e) => setFormData((p) => ({ ...p, [key]: e.target.value }))}
        placeholder={ph}
      />
    </FormField>
  );

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
          {field('place-name', 'name', 'name', PH.placeNameOptional, 'md:col-span-2')}
          {field('place-street1', 'street1', 'street1', PH.addressLineOptional, 'md:col-span-2')}
          {field('place-street2', 'street2', 'street2', PH.street2Optional, 'md:col-span-2')}
          {field('place-city', 'city', 'city', PH.cityOptional)}
          {field('place-province', 'province', 'province', PH.provinceOptional)}
          {field('place-postal', 'postal_code', 'postal_code', PH.postalOptional)}
          {field('place-country', 'country', 'country', PH.countryOptional)}
          {field('place-lat', 'latitude', 'latitude', PH.latOptional)}
          {field('place-lng', 'longitude', 'longitude', PH.lngOptional)}
          {field('place-phone', 'phone', 'phone', PH.phoneOptional)}
          {field('place-type', 'type', 'type', PH.placeTypeOptional)}
          <FormField className="md:col-span-2" label="meta (JSON object, optional)" htmlFor="place-meta">
            <Textarea
              id="place-meta"
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

export default PlaceForm;
