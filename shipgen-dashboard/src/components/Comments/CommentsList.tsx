import React, { useEffect, useMemo, useState } from 'react';
import { AlertCircle, MessageSquare, Search, Send, Trash2 } from 'lucide-react';
import { commentsService, type UiComment } from '../../services/commentsService';

const CommentsList: React.FC = () => {
  const [rows, setRows] = useState<UiComment[]>([]);
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [form, setForm] = useState({
    body: '',
    subject_uuid: '',
    subject_type: 'order',
  });

  const load = async () => {
    try {
      setLoading(true);
      setError(null);
      const list = await commentsService.list({ limit: 100, offset: 0 });
      setRows(list);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to load comments');
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
    return rows.filter((r) => `${r.body} ${r.user}`.toLowerCase().includes(q));
  }, [rows, searchTerm]);

  const onCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!form.body.trim()) {
      setError('Comment text is required');
      return;
    }
    if (!form.subject_uuid.trim()) {
      setError('subject_uuid is required');
      return;
    }
    if (!form.subject_type.trim()) {
      setError('subject_type is required');
      return;
    }
    try {
      setBusy(true);
      setError(null);
      const created = await commentsService.create({
        body: form.body.trim(),
        subject_uuid: form.subject_uuid.trim(),
        subject_type: form.subject_type.trim(),
      });
      setRows((prev) => [created, ...prev]);
      setForm((p) => ({ ...p, body: '' }));
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to create comment');
    } finally {
      setBusy(false);
    }
  };

  const onDelete = async (id: string) => {
    if (!window.confirm('Delete this comment?')) return;
    try {
      setBusy(true);
      setError(null);
      await commentsService.remove(id);
      setRows((prev) => prev.filter((r) => r.id !== id));
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to delete comment');
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Comments</h1>
        <p className="text-sm text-gray-600 mt-1">Simple comments feed</p>
      </div>

      <form onSubmit={onCreate} className="bg-white rounded-xl border border-gray-200 p-4 space-y-3">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          <input
            type="text"
            placeholder="subject_uuid (required)"
            value={form.subject_uuid}
            onChange={(e) => setForm((p) => ({ ...p, subject_uuid: e.target.value }))}
            className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
          />
          <input
            type="text"
            placeholder="subject_type (required)"
            value={form.subject_type}
            onChange={(e) => setForm((p) => ({ ...p, subject_type: e.target.value }))}
            className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
          />
        </div>
        <div className="flex gap-2">
          <input
            type="text"
            placeholder="Write a comment..."
            value={form.body}
            onChange={(e) => setForm((p) => ({ ...p, body: e.target.value }))}
            className="flex-1 px-3 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
          />
          <button
            type="submit"
            disabled={busy}
            className="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 transition"
          >
            <Send size={16} />
            <span>Post</span>
          </button>
        </div>
      </form>

      <div className="relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={18} />
        <input
          type="text"
          placeholder="Search comments..."
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

      {loading ? (
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600" />
        </div>
      ) : (
        <div className="bg-white rounded-xl border border-gray-200 overflow-hidden divide-y divide-gray-100">
          {filtered.length === 0 ? (
            <div className="p-12 text-center">
              <MessageSquare size={48} className="mx-auto text-gray-300 mb-4" />
              <p className="text-gray-600">No comments found</p>
            </div>
          ) : (
            filtered.map((row) => (
              <div key={row.id} className="p-4 flex items-start justify-between gap-4">
                <div className="min-w-0">
                  <p className="text-sm text-gray-900 whitespace-pre-wrap break-words">{row.body || '—'}</p>
                  <div className="mt-2 text-xs text-gray-500 flex items-center gap-3">
                    <span>user: {row.user || '—'}</span>
                    <span>{row.created_at ? new Date(row.created_at).toLocaleString() : '—'}</span>
                  </div>
                </div>
                <button
                  type="button"
                  onClick={() => onDelete(row.id)}
                  disabled={busy}
                  className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition disabled:opacity-50"
                  title="Delete comment"
                >
                  <Trash2 size={16} />
                </button>
              </div>
            ))
          )}
        </div>
      )}
    </div>
  );
};

export default CommentsList;
