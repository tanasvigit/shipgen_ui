import React, { useEffect, useMemo, useState } from 'react';
import { AlertCircle, Bell, Check, Search, Trash2 } from 'lucide-react';
import { notificationsService, type UiNotification } from '../../services/notificationsService';

const NotificationsList: React.FC = () => {
  const [rows, setRows] = useState<UiNotification[]>([]);
  const [selectedIds, setSelectedIds] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');

  const load = async () => {
    try {
      setLoading(true);
      setError(null);
      const list = await notificationsService.list({ limit: 100, offset: 0 });
      setRows(list);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to load notifications');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, []);

  const filtered = useMemo(() => {
    const q = searchTerm.trim().toLowerCase();
    if (!q) return rows;
    return rows.filter((r) => `${r.title} ${r.message}`.toLowerCase().includes(q));
  }, [rows, searchTerm]);

  const toggleSelection = (id: string) => {
    setSelectedIds((prev) => (prev.includes(id) ? prev.filter((x) => x !== id) : [...prev, id]));
  };

  const unreadIds = useMemo(() => rows.filter((r) => !r.read_at).map((r) => r.id), [rows]);

  const onMarkOneRead = async (id: string) => {
    try {
      setBusy(true);
      setError(null);
      setSuccess(null);
      await notificationsService.markAsRead([id]);
      setRows((prev) => prev.map((n) => (n.id === id ? { ...n, read_at: new Date().toISOString() } : n)));
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to mark as read');
    } finally {
      setBusy(false);
    }
  };

  const onMarkAllRead = async () => {
    try {
      setBusy(true);
      setError(null);
      setSuccess(null);
      await notificationsService.markAllRead();
      const now = new Date().toISOString();
      setRows((prev) => prev.map((n) => ({ ...n, read_at: n.read_at || now })));
      setSuccess('All notifications marked as read.');
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to mark all read');
    } finally {
      setBusy(false);
    }
  };

  const onDeleteSelected = async () => {
    if (selectedIds.length === 0) return;
    if (!window.confirm(`Delete ${selectedIds.length} selected notification(s)?`)) return;
    try {
      setBusy(true);
      setError(null);
      setSuccess(null);
      await notificationsService.bulkDelete(selectedIds);
      setRows((prev) => prev.filter((n) => !selectedIds.includes(n.id)));
      setSelectedIds([]);
      setSuccess('Selected notifications deleted.');
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to delete selected notifications');
    } finally {
      setBusy(false);
    }
  };

  const onClearAll = async () => {
    if (!window.confirm('Delete all notifications?')) return;
    try {
      setBusy(true);
      setError(null);
      setSuccess(null);
      await notificationsService.bulkDelete();
      setRows([]);
      setSelectedIds([]);
      setSuccess('All notifications cleared.');
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to clear notifications');
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between gap-3 flex-wrap">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Notifications</h1>
          <p className="text-sm text-gray-600 mt-1">Inbox style notifications</p>
        </div>
        <div className="flex items-center gap-2">
          <button
            type="button"
            onClick={onMarkAllRead}
            disabled={busy || unreadIds.length === 0}
            className="inline-flex items-center gap-2 px-3 py-2 border border-gray-200 text-gray-700 rounded-lg hover:bg-gray-50 disabled:opacity-50 transition"
          >
            <Check size={16} />
            <span>Mark All Read</span>
          </button>
          <button
            type="button"
            onClick={onDeleteSelected}
            disabled={busy || selectedIds.length === 0}
            className="inline-flex items-center gap-2 px-3 py-2 border border-red-200 text-red-700 rounded-lg hover:bg-red-50 disabled:opacity-50 transition"
          >
            <Trash2 size={16} />
            <span>Delete Selected</span>
          </button>
          <button
            type="button"
            onClick={onClearAll}
            disabled={busy || rows.length === 0}
            className="inline-flex items-center gap-2 px-3 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 disabled:opacity-50 transition"
          >
            <Trash2 size={16} />
            <span>Clear All</span>
          </button>
        </div>
      </div>

      <div className="relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={18} />
        <input
          type="text"
          placeholder="Search notifications..."
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
        <div className="bg-white rounded-xl border border-gray-200 overflow-hidden divide-y divide-gray-100">
          {filtered.length === 0 ? (
            <div className="p-12 text-center">
              <Bell size={48} className="mx-auto text-gray-300 mb-4" />
              <p className="text-gray-600">No notifications found</p>
            </div>
          ) : (
            filtered.map((n) => (
              <div key={n.id} className={`p-4 flex items-start gap-3 ${n.read_at ? 'bg-white' : 'bg-blue-50/40'}`}>
                <input
                  type="checkbox"
                  className="mt-1"
                  checked={selectedIds.includes(n.id)}
                  onChange={() => toggleSelection(n.id)}
                />
                <div className={`mt-1 h-2 w-2 rounded-full ${n.read_at ? 'bg-gray-300' : 'bg-blue-600'}`} />
                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between gap-3">
                    <p className="text-sm font-semibold text-gray-900 truncate">{n.title || 'Notification'}</p>
                    <span className="text-xs text-gray-500 whitespace-nowrap">
                      {n.created_at ? new Date(n.created_at).toLocaleString() : '—'}
                    </span>
                  </div>
                  <p className="text-sm text-gray-700 mt-1">{n.message || '—'}</p>
                  {!n.read_at && (
                    <button
                      type="button"
                      onClick={() => onMarkOneRead(n.id)}
                      disabled={busy}
                      className="mt-2 text-xs text-blue-600 hover:text-blue-700 font-medium disabled:opacity-50"
                    >
                      Mark as read
                    </button>
                  )}
                </div>
              </div>
            ))
          )}
        </div>
      )}
    </div>
  );
};

export default NotificationsList;
