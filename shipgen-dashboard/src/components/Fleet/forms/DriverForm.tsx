import React, { useEffect, useState } from 'react';
import { AlertCircle } from 'lucide-react';
import { driversService } from '../../../services/driversService';
import { PH } from '../../../constants/formPlaceholders';
import { FormActions, FormContainer, FormField, FormSection, Input } from '../../common/form';

interface DriverFormProps {
  mode: 'create' | 'edit';
  driverId?: string;
  onSuccess: () => Promise<void> | void;
  onCancel: () => void;
}

const DriverForm: React.FC<DriverFormProps> = ({ mode, driverId, onSuccess, onCancel }) => {
  const [loading, setLoading] = useState(mode === 'edit');
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [form, setForm] = useState({
    drivers_license_number: '',
    status: 'active',
    online: '0',
  });

  useEffect(() => {
    if (mode !== 'edit' || !driverId) return;
    const run = async () => {
      try {
        setLoading(true);
        setError(null);
        const row = await driversService.getById(driverId);
        setForm({
          drivers_license_number: row.drivers_license_number || '',
          status: row.status || 'active',
          online: String(row.online ?? 0),
        });
      } catch (err: unknown) {
        setError(err instanceof Error ? err.message : 'Failed to load driver');
      } finally {
        setLoading(false);
      }
    };
    void run();
  }, [mode, driverId]);

  const submit = async (event: React.FormEvent) => {
    event.preventDefault();
    if (!form.drivers_license_number.trim()) {
      setError('Driver license number is required');
      return;
    }
    try {
      setSaving(true);
      setError(null);
      if (mode === 'edit' && driverId) {
        await driversService.update(driverId, {
          drivers_license_number: form.drivers_license_number.trim(),
          status: form.status.trim(),
          online: Number(form.online) || 0,
        });
      } else {
        await driversService.create({
          drivers_license_number: form.drivers_license_number.trim(),
          status: form.status.trim() || 'active',
          online: Number(form.online) || 0,
        });
      }
      await onSuccess();
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : `Failed to ${mode} driver`);
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
          <FormField className="md:col-span-2" label="drivers_license_number" required htmlFor="driver-license">
            <Input
              id="driver-license"
              value={form.drivers_license_number}
              onChange={(e) => setForm((p) => ({ ...p, drivers_license_number: e.target.value }))}
              placeholder={PH.licenseNumber}
            />
          </FormField>
          <FormField label="status" htmlFor="driver-status">
            <Input
              id="driver-status"
              value={form.status}
              onChange={(e) => setForm((p) => ({ ...p, status: e.target.value }))}
            />
          </FormField>
          <FormField label="online (0/1)" htmlFor="driver-online">
            <Input
              id="driver-online"
              value={form.online}
              onChange={(e) => setForm((p) => ({ ...p, online: e.target.value }))}
            />
          </FormField>
        </FormSection>
        <FormActions
          onCancel={onCancel}
          saving={saving}
          submitLabel={mode === 'edit' ? 'Save Changes' : 'Create Driver'}
        />
      </form>
    </FormContainer>
  );
};

export default DriverForm;
