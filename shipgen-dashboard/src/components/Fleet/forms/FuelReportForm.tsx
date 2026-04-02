import React, { useEffect, useState } from 'react';
import { AlertCircle } from 'lucide-react';
import { fuelReportsService } from '../../../services/fuelReportsService';
import { PH, SELECT_PH } from '../../../constants/formPlaceholders';
import { useToast } from '../../ui/ToastProvider';
import { FormActions, FormContainer, FormField, FormSection, Input, Select, Textarea } from '../../common/form';

interface FuelReportFormProps {
  mode: 'create' | 'edit';
  fuelReportId?: string;
  onSuccess: () => Promise<void> | void;
  onCancel: () => void;
}

const initialCreate = {
  driver: '',
  status: 'submitted',
  metric_unit: 'litre',
  volume: '',
  odometer: '',
  amount: '',
  currency: 'INR',
  report: '',
  location_latitude: '',
  location_longitude: '',
  meta: '',
};

const FuelReportForm: React.FC<FuelReportFormProps> = ({ mode, fuelReportId, onSuccess, onCancel }) => {
  const { showToast } = useToast();
  const [loading, setLoading] = useState(mode === 'edit');
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [createForm, setCreateForm] = useState(initialCreate);
  const [editForm, setEditForm] = useState({
    odometer: '',
    volume: '',
    metric_unit: '',
    amount: '',
    currency: '',
    status: '',
    report: '',
    meta: '',
  });

  useEffect(() => {
    if (mode !== 'edit' || !fuelReportId) return;
    const loadFuelReport = async () => {
      try {
        setLoading(true);
        setError(null);
        const response = await fuelReportsService.getById(fuelReportId);
        setEditForm({
          odometer: response.odometer ?? '',
          volume: response.volume ?? '',
          metric_unit: response.metric_unit ?? '',
          amount: response.amount ?? '',
          currency: response.currency ?? '',
          status: response.status ?? '',
          report: response.report ?? '',
          meta: response.meta ? JSON.stringify(response.meta, null, 2) : '',
        });
      } catch (err: unknown) {
        setError(err instanceof Error ? err.message : 'Failed to load fuel report');
      } finally {
        setLoading(false);
      }
    };
    void loadFuelReport();
  }, [mode, fuelReportId]);

  const handleCreateChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setCreateForm((prev) => ({ ...prev, [name]: value }));
  };

  const submitCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      setSaving(true);
      setError(null);
      const payload = {
        driver: createForm.driver || undefined,
        location:
          createForm.location_latitude || createForm.location_longitude
            ? {
                latitude: createForm.location_latitude || null,
                longitude: createForm.location_longitude || null,
              }
            : undefined,
        odometer: createForm.odometer || undefined,
        volume: createForm.volume || undefined,
        metric_unit: createForm.metric_unit || undefined,
        amount: createForm.amount || undefined,
        currency: createForm.currency || undefined,
        status: createForm.status,
        report: createForm.report || undefined,
        meta: createForm.meta ? JSON.parse(createForm.meta) : undefined,
      };
      await fuelReportsService.create(payload);
      showToast('Fuel report created successfully', 'success');
      setCreateForm(initialCreate);
      await onSuccess();
    } catch (err: unknown) {
      if (err instanceof SyntaxError) {
        setError('meta must be valid JSON');
        return;
      }
      setError(err instanceof Error ? err.message : 'Failed to create fuel report');
    } finally {
      setSaving(false);
    }
  };

  const submitEdit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!fuelReportId) return;
    try {
      setSaving(true);
      setError(null);
      const payload = {
        odometer: editForm.odometer || undefined,
        volume: editForm.volume || undefined,
        metric_unit: editForm.metric_unit || undefined,
        amount: editForm.amount || undefined,
        currency: editForm.currency || undefined,
        status: editForm.status || undefined,
        report: editForm.report || undefined,
        meta: editForm.meta ? JSON.parse(editForm.meta) : undefined,
      };
      await fuelReportsService.updatePut(fuelReportId, payload);
      showToast('Fuel report updated successfully', 'success');
      await onSuccess();
    } catch (err: unknown) {
      if (err instanceof SyntaxError) {
        setError('meta must be valid JSON');
      } else {
        setError(err instanceof Error ? err.message : 'Failed to update fuel report');
      }
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

  if (mode === 'create') {
    return (
      <FormContainer>
        <form onSubmit={submitCreate} className="space-y-5">
          {error && (
            <div className="flex items-center gap-2 rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">
              <AlertCircle size={18} />
              <span>{error}</span>
            </div>
          )}
          <FormSection>
            <FormField label="driver" htmlFor="frc-driver">
              <Input
                id="frc-driver"
                type="text"
                name="driver"
                placeholder={PH.driverRefOptional}
                value={createForm.driver}
                onChange={handleCreateChange}
              />
            </FormField>
            <FormField label="status" htmlFor="frc-status">
              <Select id="frc-status" name="status" value={createForm.status} onChange={handleCreateChange}>
                <option value="" disabled>
                  {SELECT_PH.status}
                </option>
                <option value="submitted">submitted</option>
                <option value="approved">approved</option>
                <option value="rejected">rejected</option>
              </Select>
            </FormField>
            <FormField label="metric_unit" htmlFor="frc-metric">
              <Select id="frc-metric" name="metric_unit" value={createForm.metric_unit} onChange={handleCreateChange}>
                <option value="" disabled>
                  {SELECT_PH.metricUnit}
                </option>
                <option value="litre">litre</option>
                <option value="gallon">gallon</option>
              </Select>
            </FormField>
            <FormField label="volume" htmlFor="frc-volume">
              <Input
                id="frc-volume"
                type="text"
                name="volume"
                placeholder={PH.fuelVolumeOptional}
                value={createForm.volume}
                onChange={handleCreateChange}
              />
            </FormField>
            <FormField label="odometer" htmlFor="frc-odo">
              <Input
                id="frc-odo"
                type="text"
                name="odometer"
                placeholder={PH.fuelOdometerOptional}
                value={createForm.odometer}
                onChange={handleCreateChange}
              />
            </FormField>
            <FormField label="amount" htmlFor="frc-amount">
              <Input
                id="frc-amount"
                type="text"
                name="amount"
                placeholder={PH.fuelAmountOptional}
                value={createForm.amount}
                onChange={handleCreateChange}
              />
            </FormField>
            <FormField label="currency" htmlFor="frc-currency">
              <Input
                id="frc-currency"
                type="text"
                name="currency"
                placeholder={PH.fuelCurrencyOptional}
                value={createForm.currency}
                onChange={handleCreateChange}
              />
            </FormField>
            <FormField label="location.latitude" htmlFor="frc-lat">
              <Input
                id="frc-lat"
                type="text"
                name="location_latitude"
                placeholder={PH.latOptional}
                value={createForm.location_latitude}
                onChange={handleCreateChange}
              />
            </FormField>
            <FormField label="location.longitude" htmlFor="frc-lng">
              <Input
                id="frc-lng"
                type="text"
                name="location_longitude"
                placeholder={PH.lngOptional}
                value={createForm.location_longitude}
                onChange={handleCreateChange}
              />
            </FormField>
            <FormField label="report" className="md:col-span-2" htmlFor="frc-report">
              <Textarea
                id="frc-report"
                name="report"
                rows={3}
                placeholder={PH.fuelReportOptional}
                value={createForm.report}
                onChange={(e) => setCreateForm((prev) => ({ ...prev, report: e.target.value }))}
              />
            </FormField>
            <FormField label="meta (JSON object)" className="md:col-span-2" htmlFor="frc-meta">
              <Textarea
                id="frc-meta"
                name="meta"
                rows={3}
                className="font-mono text-sm"
                placeholder={PH.metaJsonOptional}
                value={createForm.meta}
                onChange={(e) => setCreateForm((prev) => ({ ...prev, meta: e.target.value }))}
              />
            </FormField>
          </FormSection>
          <FormActions onCancel={onCancel} saving={saving} submitLabel="Create Fuel Report" />
        </form>
      </FormContainer>
    );
  }

  return (
    <FormContainer>
      <form onSubmit={submitEdit} className="space-y-5">
        {error && (
          <div className="flex items-center gap-2 rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">
            <AlertCircle size={18} />
            <span>{error}</span>
          </div>
        )}
        <FormSection>
          <FormField label="odometer" htmlFor="fre-odo">
            <Input
              id="fre-odo"
              placeholder={PH.fuelOdometerOptional}
              value={editForm.odometer}
              onChange={(e) => setEditForm((p) => ({ ...p, odometer: e.target.value }))}
            />
          </FormField>
          <FormField label="volume" htmlFor="fre-vol">
            <Input
              id="fre-vol"
              placeholder={PH.fuelVolumeOptional}
              value={editForm.volume}
              onChange={(e) => setEditForm((p) => ({ ...p, volume: e.target.value }))}
            />
          </FormField>
          <FormField label="metric_unit" htmlFor="fre-metric">
            <Input
              id="fre-metric"
              placeholder={PH.metricUnitOptional}
              value={editForm.metric_unit}
              onChange={(e) => setEditForm((p) => ({ ...p, metric_unit: e.target.value }))}
            />
          </FormField>
          <FormField label="amount" htmlFor="fre-amount">
            <Input
              id="fre-amount"
              placeholder={PH.fuelAmountOptional}
              value={editForm.amount}
              onChange={(e) => setEditForm((p) => ({ ...p, amount: e.target.value }))}
            />
          </FormField>
          <FormField label="currency" htmlFor="fre-currency">
            <Input
              id="fre-currency"
              placeholder={PH.fuelCurrencyOptional}
              value={editForm.currency}
              onChange={(e) => setEditForm((p) => ({ ...p, currency: e.target.value }))}
            />
          </FormField>
          <FormField label="status" htmlFor="fre-status">
            <Input
              id="fre-status"
              placeholder={PH.statusTextOptional}
              value={editForm.status}
              onChange={(e) => setEditForm((p) => ({ ...p, status: e.target.value }))}
            />
          </FormField>
          <FormField label="report" className="md:col-span-2" htmlFor="fre-report">
            <Textarea
              id="fre-report"
              rows={3}
              placeholder={PH.fuelReportOptional}
              value={editForm.report}
              onChange={(e) => setEditForm((p) => ({ ...p, report: e.target.value }))}
            />
          </FormField>
          <FormField label="meta (JSON object)" className="md:col-span-2" htmlFor="fre-meta">
            <Textarea
              id="fre-meta"
              rows={4}
              className="font-mono text-sm"
              placeholder={PH.metaJsonOptional}
              value={editForm.meta}
              onChange={(e) => setEditForm((p) => ({ ...p, meta: e.target.value }))}
            />
          </FormField>
        </FormSection>
        <FormActions onCancel={onCancel} saving={saving} submitLabel="Save Changes" />
      </form>
    </FormContainer>
  );
};

export default FuelReportForm;
