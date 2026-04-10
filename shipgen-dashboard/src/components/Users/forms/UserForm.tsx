import React, { useEffect, useState } from 'react';
import { AlertCircle } from 'lucide-react';
import { usersService } from '../../../services/usersService';
import { PH } from '../../../constants/formPlaceholders';
import { FormActions, FormContainer, FormField, FormSection, Input, Select } from '../../common/form';

interface UserFormProps {
  mode: 'create' | 'edit';
  userId?: string;
  initialRole?: 'ADMIN' | 'OPERATIONS_MANAGER' | 'DISPATCHER' | 'DRIVER' | 'VIEWER';
  lockRole?: boolean;
  onSuccess: () => Promise<void> | void;
  onCancel: () => void;
}

const UserForm: React.FC<UserFormProps> = ({ mode, userId, initialRole, lockRole = false, onSuccess, onCancel }) => {
  const [loading, setLoading] = useState(mode === 'edit');
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [form, setForm] = useState({
    name: '',
    email: '',
    password: '',
    role: '',
    status: '',
    drivers_license_number: '',
  });

  useEffect(() => {
    if (mode !== 'edit' || !userId) return;
    const load = async () => {
      try {
        setLoading(true);
        setError(null);
        const row = await usersService.getById(userId);
        setForm({
          name: row.name || '',
          email: row.email || '',
          password: '',
          role: row.role || '',
          status: row.status || '',
          drivers_license_number: '',
        });
      } catch (err: unknown) {
        setError(err instanceof Error ? err.message : 'Failed to load user');
      } finally {
        setLoading(false);
      }
    };
    void load();
  }, [mode, userId]);

  useEffect(() => {
    if (mode !== 'create' || !initialRole) return;
    setForm((prev) => ({ ...prev, role: initialRole }));
  }, [mode, initialRole]);

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!form.name.trim()) {
      setError('Name is required');
      return;
    }
    if (!form.email.trim()) {
      setError('Email is required');
      return;
    }
    if (mode === 'create' && !form.password.trim()) {
      setError('Password is required');
      return;
    }
    if (!form.role.trim()) {
      setError('Role is required');
      return;
    }
    if (mode === 'create' && form.role.trim() === 'DRIVER' && !form.drivers_license_number.trim()) {
      setError('DL Number is required for DRIVER');
      return;
    }
    try {
      setSaving(true);
      setError(null);
      if (mode === 'edit' && userId) {
        await usersService.update(userId, {
          name: form.name.trim(),
          email: form.email.trim(),
          role: form.role.trim() as 'ADMIN' | 'OPERATIONS_MANAGER' | 'DISPATCHER' | 'DRIVER' | 'VIEWER',
          status: form.status.trim() || undefined,
        });
      } else {
        await usersService.create({
          name: form.name.trim(),
          email: form.email.trim(),
          password: form.password,
          role: form.role.trim() as 'ADMIN' | 'OPERATIONS_MANAGER' | 'DISPATCHER' | 'DRIVER' | 'VIEWER',
          drivers_license_number:
            form.role.trim() === 'DRIVER' ? form.drivers_license_number.trim() : undefined,
        });
      }
      await onSuccess();
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : `Failed to ${mode} user`);
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
          <FormField className="md:col-span-2" label="name" required htmlFor="user-name">
            <Input
              id="user-name"
              type="text"
              value={form.name}
              onChange={(e) => setForm((p) => ({ ...p, name: e.target.value }))}
              placeholder={PH.personName}
            />
          </FormField>
          <FormField label="email" required htmlFor="user-email">
            <Input
              id="user-email"
              type="email"
              value={form.email}
              onChange={(e) => setForm((p) => ({ ...p, email: e.target.value }))}
              placeholder={PH.email}
            />
          </FormField>
          <FormField label="role" required htmlFor="user-role">
            <Select
              id="user-role"
              value={form.role}
              onChange={(e) => setForm((p) => ({ ...p, role: e.target.value }))}
              disabled={mode === 'create' && lockRole}
            >
              <option value="" disabled>
                Select role
              </option>
              <option value="ADMIN">ADMIN</option>
              <option value="OPERATIONS_MANAGER">OPERATIONS_MANAGER</option>
              <option value="DISPATCHER">DISPATCHER</option>
              <option value="DRIVER">DRIVER</option>
              <option value="VIEWER">VIEWER (Read-only)</option>
            </Select>
          </FormField>
          {mode === 'create' ? (
            <>
              <FormField className="md:col-span-2" label="password" required htmlFor="user-password">
                <Input
                  id="user-password"
                  type="password"
                  value={form.password}
                  onChange={(e) => setForm((p) => ({ ...p, password: e.target.value }))}
                  placeholder={PH.password}
                />
              </FormField>
              {form.role === 'DRIVER' ? (
                <FormField className="md:col-span-2" label="DL Number" required htmlFor="user-driver-dl-number">
                  <Input
                    id="user-driver-dl-number"
                    type="text"
                    value={form.drivers_license_number}
                    onChange={(e) => setForm((p) => ({ ...p, drivers_license_number: e.target.value }))}
                    placeholder={PH.licenseNumber}
                  />
                </FormField>
              ) : null}
            </>
          ) : (
            <FormField className="md:col-span-2" label="status" htmlFor="user-status">
              <Input
                id="user-status"
                type="text"
                value={form.status}
                onChange={(e) => setForm((p) => ({ ...p, status: e.target.value }))}
                placeholder={PH.statusTextOptional}
              />
            </FormField>
          )}
        </FormSection>
        <FormActions onCancel={onCancel} saving={saving} submitLabel={mode === 'edit' ? 'Save Changes' : 'Create User'} />
      </form>
    </FormContainer>
  );
};

export default UserForm;
