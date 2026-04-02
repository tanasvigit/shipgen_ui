import React, { useEffect, useState } from 'react';
import { Link, useLocation, useParams } from 'react-router-dom';
import { AlertCircle, ArrowLeft } from 'lucide-react';
import { payloadsService, type UiPayload } from '../../services/payloadsService';

const statusBadgeClass = (status: string): string => {
  const s = status.toLowerCase();
  if (s.includes('success')) return 'bg-green-100 text-green-700';
  if (s.includes('failed')) return 'bg-red-100 text-red-700';
  if (s.includes('pending')) return 'bg-amber-100 text-amber-700';
  return 'bg-gray-100 text-gray-700';
};

const PayloadDetail: React.FC = () => {
  const { id = '' } = useParams<{ id: string }>();
  const location = useLocation();
  const isEmbedded = new URLSearchParams(location.search).get('embed') === '1';
  const [row, setRow] = useState<UiPayload | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const load = async () => {
      try {
        setLoading(true);
        setError(null);
        const item = await payloadsService.getById(id);
        setRow(item);
      } catch (err: unknown) {
        setError(err instanceof Error ? err.message : 'Failed to load payload');
      } finally {
        setLoading(false);
      }
    };
    if (id) void load();
  }, [id]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg flex items-center gap-2">
        <AlertCircle size={18} />
        <span>{error}</span>
      </div>
    );
  }

  if (!row) {
    return <div className="text-sm text-gray-600">Payload not found</div>;
  }

  return (
    <div className="space-y-6">
      {!isEmbedded ? (
        <div className="flex items-center space-x-3">
          <Link to="/fleet/payloads" className="p-2 hover:bg-gray-100 rounded-lg transition">
            <ArrowLeft size={20} />
          </Link>
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Payload Detail</h1>
            <p className="text-sm text-gray-600 mt-1">{row.id}</p>
          </div>
        </div>
      ) : null}

      <div className="bg-white rounded-xl border border-gray-200 p-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div>
            <p className="text-xs text-gray-500 uppercase">Type</p>
            <p className="text-sm text-gray-900 mt-1">{row.type || '—'}</p>
          </div>
          <div>
            <p className="text-xs text-gray-500 uppercase">Status</p>
            <span className={`inline-flex mt-1 px-2 py-0.5 rounded-full text-xs font-medium ${statusBadgeClass(row.status)}`}>
              {row.status || '—'}
            </span>
          </div>
          <div>
            <p className="text-xs text-gray-500 uppercase">Created At</p>
            <p className="text-sm text-gray-900 mt-1">{row.created_at ? new Date(row.created_at).toLocaleString() : '—'}</p>
          </div>
        </div>
      </div>

      <div className="bg-white rounded-xl border border-gray-200 p-6">
        <h2 className="text-sm font-semibold text-gray-900 mb-3">Payload JSON</h2>
        <div className="border border-gray-200 rounded-lg bg-gray-50 max-h-[520px] overflow-auto">
          <pre className="p-4 text-xs font-mono text-gray-800 whitespace-pre-wrap break-words">
            {JSON.stringify(row.raw, null, 2)}
          </pre>
        </div>
      </div>
    </div>
  );
};

export default PayloadDetail;
