import React, { useEffect, useState } from 'react';
import { AlertCircle } from 'lucide-react';
import { vehiclesService } from '../../../services/vehiclesService';
import { PH, SELECT_PH } from '../../../constants/formPlaceholders';
import {
  FormActions,
  FormContainer,
  FormField,
  FormSection,
  Input,
  Select,
  Textarea,
} from '../../common/form';

/** Merge form meta fields into baseline (e.g. GPS from /track) so PATCH does not wipe keys. */
function buildVehicleMetaPayload(
  baseline: Record<string, unknown>,
  color: string,
  notes: string,
): Record<string, unknown> {
  const out = { ...baseline };
  const c = color.trim();
  const n = notes.trim();
  if (c) out.color = c;
  else delete out.color;
  if (n) out.notes = n;
  else delete out.notes;
  return out;
}

interface VehicleFormProps {
  mode: 'create' | 'edit';
  vehicleId?: string;
  onSuccess: () => Promise<void> | void;
  onCancel: () => void;
}

const VehicleForm: React.FC<VehicleFormProps> = ({ mode, vehicleId, onSuccess, onCancel }) => {
  const [loading, setLoading] = useState(mode === 'edit');
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [form, setForm] = useState({
    company_uuid: '',
    vendor_uuid: '',
    make: '',
    model: '',
    year: '',
    trim: '',
    type: '',
    plate_number: '',
    vin: '',
    status: 'active',
    meta_color: '',
    meta_notes: '',
  });
  const [metaBaseline, setMetaBaseline] = useState<Record<string, unknown>>({});

  useEffect(() => {
    if (mode !== 'edit' || !vehicleId) return;
    const run = async () => {
      try {
        setLoading(true);
        setError(null);
        const row = await vehiclesService.getById(vehicleId);
        const rawMeta =
          row.meta && typeof row.meta === 'object' && !Array.isArray(row.meta) ? { ...row.meta } : {};
        setMetaBaseline(rawMeta);
        setForm((prev) => ({
          ...prev,
          vendor_uuid: row.vendor_uuid ?? '',
          status: row.status ?? 'active',
          plate_number: row.plate_number ?? '',
          year: row.year ?? '',
          trim: row.trim ?? '',
          meta_color: row.meta?.color != null ? String(row.meta.color) : '',
          meta_notes: row.meta?.notes != null ? String(row.meta.notes) : '',
          make: row.make ?? '',
          model: row.model ?? '',
          type: row.type ?? '',
          vin: row.vin ?? '',
        }));
      } catch (err: unknown) {
        setError(err instanceof Error ? err.message : 'Failed to load vehicle');
      } finally {
        setLoading(false);
      }
    };
    void run();
  }, [mode, vehicleId]);

  const submit = async (event: React.FormEvent) => {
    event.preventDefault();
    if (!form.plate_number || !form.status) {
      setError('Plate number and status are required');
      return;
    }
    try {
      setSaving(true);
      setError(null);
      if (mode === 'edit' && vehicleId) {
        if (!form.make?.trim() || !form.model?.trim() || !form.type?.trim() || !form.vin?.trim()) {
          setError('Make, model, type, and VIN are required');
          setSaving(false);
          return;
        }
        await vehiclesService.update(vehicleId, {
          vendor_uuid: form.vendor_uuid.trim() || null,
          make: form.make.trim(),
          model: form.model.trim(),
          year: form.year.trim() || null,
          trim: form.trim.trim() || null,
          type: form.type.trim(),
          plate_number: form.plate_number.trim(),
          vin: form.vin.trim(),
          status: form.status,
          meta: buildVehicleMetaPayload(metaBaseline, form.meta_color, form.meta_notes),
        });
      } else {
        if (!form.make || !form.model || !form.type || !form.vin) {
          setError('Please fill all required fields');
          setSaving(false);
          return;
        }
        await vehiclesService.create({
          company_uuid: form.company_uuid.trim() || null,
          vendor_uuid: form.vendor_uuid.trim() || null,
          make: form.make.trim(),
          model: form.model.trim(),
          year: form.year.trim() || '',
          trim: form.trim.trim() || '',
          type: form.type.trim(),
          plate_number: form.plate_number.trim(),
          vin: form.vin.trim(),
          status: form.status,
        });
      }
      await onSuccess();
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : `Failed to ${mode} vehicle`);
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
          {mode === 'create' ? (
            <FormField label="Company UUID (optional)" htmlFor="vehicle-company-uuid">
              <Input
                id="vehicle-company-uuid"
                value={form.company_uuid}
                onChange={(e) => setForm((p) => ({ ...p, company_uuid: e.target.value }))}
                placeholder={PH.uuidOptional}
                autoComplete="off"
              />
            </FormField>
          ) : null}
          <FormField className="md:col-span-2" label="Vendor UUID (optional)" htmlFor="vehicle-vendor-uuid">
            <Input
              id="vehicle-vendor-uuid"
              value={form.vendor_uuid}
              onChange={(e) => setForm((p) => ({ ...p, vendor_uuid: e.target.value }))}
              placeholder={PH.uuidOptional}
              autoComplete="off"
            />
          </FormField>
          <FormField label="Make" required htmlFor="vehicle-make">
            <Input
              id="vehicle-make"
              value={form.make}
              onChange={(e) => setForm((p) => ({ ...p, make: e.target.value }))}
              placeholder={PH.vehicleMake}
              autoComplete="off"
            />
          </FormField>
          <FormField label="Model" required htmlFor="vehicle-model">
            <Input
              id="vehicle-model"
              value={form.model}
              onChange={(e) => setForm((p) => ({ ...p, model: e.target.value }))}
              placeholder={PH.vehicleModel}
              autoComplete="off"
            />
          </FormField>
          <FormField label="Year (optional)" htmlFor="vehicle-year">
            <Input
              id="vehicle-year"
              value={form.year}
              onChange={(e) => setForm((p) => ({ ...p, year: e.target.value }))}
              placeholder={PH.vehicleYearOptional}
              autoComplete="off"
            />
          </FormField>
          <FormField label="Trim (optional)" htmlFor="vehicle-trim">
            <Input
              id="vehicle-trim"
              value={form.trim}
              onChange={(e) => setForm((p) => ({ ...p, trim: e.target.value }))}
              placeholder={PH.vehicleTrimOptional}
              autoComplete="off"
            />
          </FormField>
          <FormField label="Type" required htmlFor="vehicle-type">
            <Input
              id="vehicle-type"
              value={form.type}
              onChange={(e) => setForm((p) => ({ ...p, type: e.target.value }))}
              placeholder={PH.vehicleType}
              autoComplete="off"
            />
          </FormField>
          <FormField label="VIN" required htmlFor="vehicle-vin">
            <Input
              id="vehicle-vin"
              value={form.vin}
              onChange={(e) => setForm((p) => ({ ...p, vin: e.target.value }))}
              placeholder={PH.vin}
              autoComplete="off"
            />
          </FormField>
          <FormField label="Plate number" required htmlFor="vehicle-plate">
            <Input
              id="vehicle-plate"
              value={form.plate_number}
              onChange={(e) => setForm((p) => ({ ...p, plate_number: e.target.value }))}
              placeholder={PH.vehiclePlate}
              autoComplete="off"
            />
          </FormField>
          <FormField label="Status" required htmlFor="vehicle-status">
            <Select
              id="vehicle-status"
              value={form.status}
              onChange={(e) => setForm((p) => ({ ...p, status: e.target.value }))}
            >
              <option value="" disabled>
                {SELECT_PH.status}
              </option>
              <option value="active">active</option>
              <option value="maintenance">maintenance</option>
              <option value="inactive">inactive</option>
            </Select>
          </FormField>
        </FormSection>

        {mode === 'edit' ? (
          <FormSection>
            <FormField label="Color (meta, optional)" htmlFor="vehicle-meta-color">
              <Input
                id="vehicle-meta-color"
                value={form.meta_color}
                onChange={(e) => setForm((p) => ({ ...p, meta_color: e.target.value }))}
                placeholder={PH.vehicleColorOptional}
                autoComplete="off"
              />
            </FormField>
            <FormField className="md:col-span-2" label="Notes (meta, optional)" htmlFor="vehicle-meta-notes">
              <Textarea
                id="vehicle-meta-notes"
                rows={3}
                value={form.meta_notes}
                onChange={(e) => setForm((p) => ({ ...p, meta_notes: e.target.value }))}
                placeholder={PH.vehicleMetaNotesOptional}
                autoComplete="off"
              />
            </FormField>
          </FormSection>
        ) : null}

        <FormActions
          onCancel={onCancel}
          saving={saving}
          submitLabel={mode === 'edit' ? 'Update Vehicle' : 'Create Vehicle'}
        />
      </form>
    </FormContainer>
  );
};

export default VehicleForm;
