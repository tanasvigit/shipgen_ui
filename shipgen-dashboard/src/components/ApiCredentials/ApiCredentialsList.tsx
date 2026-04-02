import React, { useEffect, useMemo, useState } from 'react';
import { AlertCircle, KeyRound, RefreshCw, Search, Trash2, Plus, Eye, EyeOff } from 'lucide-react';
import { apiCredentialsService, type UiApiCredential } from '../../services/apiCredentialsService';
import { ResponsiveTable } from '../ui/ResponsiveTable';
import Modal from '../common/Modal';
import ApiCredentialForm from './forms/ApiCredentialForm';

const ApiCredentialsList: React.FC = () => {
  const [rows, setRows] = useState<UiApiCredential[]>([]);
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [oneTimeKey, setOneTimeKey] = useState<string | null>(null);
  const [showKey, setShowKey] = useState(false);
  const [isCreateOpen, setIsCreateOpen] = useState(false);

  const load = async () => {
    try {
      setLoading(true);
      setError(null);
      const list = await apiCredentialsService.list({ limit: 100, offset: 0 });
      setRows(list);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to load API credentials');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
    const keyFromSession = sessionStorage.getItem('apiCredentialOneTimeKey');
    if (keyFromSession) {
      setOneTimeKey(keyFromSession);
      sessionStorage.removeItem('apiCredentialOneTimeKey');
    }
  }, []);

  const filtered = useMemo(() => {
    const q = searchTerm.trim().toLowerCase();
    if (!q) return rows;
    return rows.filter((r) => r.name.toLowerCase().includes(q));
  }, [rows, searchTerm]);

  const onRotate = async (id: string) => {
    const password = window.prompt('Enter your account password to rotate this key:');
    if (!password) return;
    try {
      setBusy(true);
      setError(null);
      setSuccess(null);
      const rotated = await apiCredentialsService.rotate(id, password);
      setOneTimeKey(rotated.fullKey);
      setShowKey(true);
      await load();
      setSuccess('API key rotated successfully.');
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to rotate key');
    } finally {
      setBusy(false);
    }
  };

  const onDelete = async (id: string) => {
    if (!window.confirm('Delete this API key?')) return;
    try {
      setBusy(true);
      setError(null);
      setSuccess(null);
      await apiCredentialsService.remove(id);
      setRows((prev) => prev.filter((r) => r.id !== id));
      setSuccess('API key deleted.');
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to delete key');
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">API Credentials</h1>
          <p className="text-sm text-gray-600 mt-1">Manage API keys securely</p>
        </div>
        <button
          type="button"
          onClick={() => setIsCreateOpen(true)}
          className="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
        >
          <Plus size={16} />
          <span>Create API Key</span>
        </button>
      </div>

      <div className="bg-amber-50 border border-amber-200 text-amber-800 px-4 py-3 rounded-lg text-sm">
        Security note: Full API key is visible only once after create/rotate.
      </div>

      <div className="relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={18} />
        <input
          type="text"
          placeholder="Search API keys by name..."
          className="w-full pl-10 pr-4 py-2 bg-white border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
        />
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg flex items-center gap-2">
          <AlertCircle size={18} />
          <span>{error}</span>
        </div>
      )}
      {success && <div className="bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded-lg">{success}</div>}

      {loading ? (
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600" />
        </div>
      ) : (
        <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
          {filtered.length === 0 ? (
            <div className="p-12 text-center">
              <KeyRound size={48} className="mx-auto text-gray-300 mb-4" />
              <p className="text-gray-600">No API credentials found</p>
            </div>
          ) : (
            <ResponsiveTable
              data={filtered}
              keyExtractor={(row) => row.id}
              columns={[
                {
                  key: 'name',
                  header: 'name',
                  render: (row) => <span className="text-sm font-medium text-gray-900">{row.name || '—'}</span>,
                },
                {
                  key: 'keyMasked',
                  header: 'masked key',
                  render: (row) => <span className="text-sm font-mono text-gray-700">{row.keyMasked}</span>,
                },
                {
                  key: 'created_at',
                  header: 'created_at',
                  render: (row) => <span className="text-sm text-gray-700">{row.created_at ? new Date(row.created_at).toLocaleString() : '—'}</span>,
                  mobileHidden: true,
                },
                {
                  key: 'actions',
                  header: 'actions',
                  render: (row) => (
                    <div className="inline-flex items-center gap-2">
                      <button
                        type="button"
                        onClick={(e) => {
                          e.stopPropagation();
                          void onRotate(row.id);
                        }}
                        disabled={busy}
                        className="p-2 text-blue-600 hover:bg-blue-50 rounded-lg transition disabled:opacity-50"
                        title="Rotate key"
                      >
                        <RefreshCw size={16} />
                      </button>
                      <button
                        type="button"
                        onClick={(e) => {
                          e.stopPropagation();
                          void onDelete(row.id);
                        }}
                        disabled={busy}
                        className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition disabled:opacity-50"
                        title="Delete key"
                      >
                        <Trash2 size={16} />
                      </button>
                    </div>
                  ),
                },
              ]}
            />
          )}
        </div>
      )}

      {oneTimeKey && (
        <div className="fixed inset-0 bg-black/40 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-xl border border-gray-200 shadow-lg p-6 max-w-xl w-full space-y-4">
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-bold text-gray-900">API Key (Visible Once)</h2>
              <button
                type="button"
                onClick={() => setShowKey((v) => !v)}
                className="inline-flex items-center gap-2 text-sm text-gray-600 hover:text-gray-900"
              >
                {showKey ? <EyeOff size={16} /> : <Eye size={16} />}
                <span>{showKey ? 'Hide' : 'Show'}</span>
              </button>
            </div>
            <p className="text-sm text-gray-600">Copy this key now. It will not be shown again.</p>
            <div className="bg-gray-50 border border-gray-200 rounded-lg p-3 font-mono text-sm break-all">
              {showKey ? oneTimeKey : '********************************'}
            </div>
            <div className="flex justify-end">
              <button
                type="button"
                onClick={() => {
                  setOneTimeKey(null);
                  setShowKey(false);
                }}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
              >
                Done
              </button>
            </div>
          </div>
        </div>
      )}

      <Modal isOpen={isCreateOpen} onClose={() => setIsCreateOpen(false)} title="Create API Key">
        <ApiCredentialForm
          onCancel={() => setIsCreateOpen(false)}
          onSuccess={async (fullKey) => {
            setIsCreateOpen(false);
            setOneTimeKey(fullKey);
            setShowKey(true);
            setSuccess('API key created successfully.');
            await load();
          }}
        />
      </Modal>
    </div>
  );
};

export default ApiCredentialsList;
