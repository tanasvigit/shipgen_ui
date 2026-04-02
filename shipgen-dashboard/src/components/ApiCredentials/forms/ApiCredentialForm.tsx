import React, { useState } from 'react';
import { AlertCircle } from 'lucide-react';
import { apiCredentialsService } from '../../../services/apiCredentialsService';
import { PH } from '../../../constants/formPlaceholders';
import { FormActions, FormContainer, FormField, FormSection, Input } from '../../common/form';

interface ApiCredentialFormProps {
  onSuccess: (fullKey: string) => Promise<void> | void;
  onCancel: () => void;
}

const ApiCredentialForm: React.FC<ApiCredentialFormProps> = ({ onSuccess, onCancel }) => {
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [name, setName] = useState('');

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim()) {
      setError('Name is required');
      return;
    }
    try {
      setSaving(true);
      setError(null);
      const created = await apiCredentialsService.create(name.trim());
      await onSuccess(created.fullKey);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to create API key');
    } finally {
      setSaving(false);
    }
  };

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
          <div className="md:col-span-2 rounded-lg border border-amber-200 bg-amber-50 px-3 py-2 text-sm text-amber-800">
            Security note: API key is visible only once after create/rotate.
          </div>
          <FormField className="md:col-span-2" label="name" required htmlFor="api-key-name">
            <Input id="api-key-name" type="text" value={name} onChange={(e) => setName(e.target.value)} placeholder={PH.apiKeyName} />
          </FormField>
        </FormSection>
        <FormActions onCancel={onCancel} saving={saving} submitLabel="Create Key" />
      </form>
    </FormContainer>
  );
};

export default ApiCredentialForm;
