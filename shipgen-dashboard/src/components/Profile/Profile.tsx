import React, { useState } from 'react';
import { AlertCircle, KeyRound, Save } from 'lucide-react';
import { usersService } from '../../services/usersService';

const Profile: React.FC = () => {
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [form, setForm] = useState({
    newPassword: '',
    confirmPassword: '',
  });

  const onChangePassword = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!form.newPassword.trim()) {
      setError('New password is required');
      return;
    }
    if (form.newPassword !== form.confirmPassword) {
      setError('Passwords do not match');
      return;
    }
    try {
      setSaving(true);
      setError(null);
      setSuccess(null);
      await usersService.setCurrentUserPassword(form.newPassword);
      setSuccess('Your password has been updated.');
      setForm({ newPassword: '', confirmPassword: '' });
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to update password');
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">My Account</h1>
        <p className="text-sm text-gray-600 mt-1">Manage your account settings</p>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg flex items-center gap-2">
          <AlertCircle size={18} />
          <span>{error}</span>
        </div>
      )}
      {success && <div className="bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded-lg">{success}</div>}

      <form onSubmit={onChangePassword} className="bg-white rounded-xl border border-gray-200 p-6 space-y-6">
        <div className="flex items-center gap-2 text-gray-900">
          <KeyRound size={18} />
          <h2 className="text-lg font-bold">Change My Password</h2>
        </div>
        <div className="text-sm text-amber-700 bg-amber-50 border border-amber-200 rounded-lg px-3 py-2">
          This will update your account password.
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">new password *</label>
          <input
            type="password"
            value={form.newPassword}
            onChange={(e) => setForm((p) => ({ ...p, newPassword: e.target.value }))}
            className="w-full px-4 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">confirm password *</label>
          <input
            type="password"
            value={form.confirmPassword}
            onChange={(e) => setForm((p) => ({ ...p, confirmPassword: e.target.value }))}
            className="w-full px-4 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
          />
        </div>
        <div className="flex justify-end pt-4 border-t border-gray-200">
          <button
            type="submit"
            disabled={saving}
            className="inline-flex items-center gap-2 px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 transition"
          >
            <Save size={16} />
            <span>{saving ? 'Saving...' : 'Change My Password'}</span>
          </button>
        </div>
      </form>
    </div>
  );
};

export default Profile;
