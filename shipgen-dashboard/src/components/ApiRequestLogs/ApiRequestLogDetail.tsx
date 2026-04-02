import React, { useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { AlertCircle, ArrowLeft } from 'lucide-react';
import { apiRequestLogsService, type UiApiRequestLog } from '../../services/apiRequestLogsService';

const methodBadgeClass = (method: string): string => {
  const m = method.toUpperCase();
  if (m === 'GET') return 'bg-blue-100 text-blue-700';
  if (m === 'POST') return 'bg-green-100 text-green-700';
  if (m === 'PATCH') return 'bg-amber-100 text-amber-700';
  if (m === 'DELETE') return 'bg-red-100 text-red-700';
  return 'bg-gray-100 text-gray-700';
};

const statusBadgeClass = (statusCode: number | null): string => {
  if (!statusCode) return 'bg-gray-100 text-gray-700';
  if (statusCode >= 200 && statusCode < 300) return 'bg-green-100 text-green-700';
  if (statusCode >= 400 && statusCode < 500) return 'bg-amber-100 text-amber-700';
  if (statusCode >= 500) return 'bg-red-100 text-red-700';
  return 'bg-gray-100 text-gray-700';
};

const ApiRequestLogDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [item, setItem] = useState<UiApiRequestLog | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const load = async () => {
      if (!id) return;
      try {
        setLoading(true);
        setError(null);
        const row = await apiRequestLogsService.getById(id);
        setItem(row);
      } catch (err: unknown) {
        setError(err instanceof Error ? err.message : 'Failed to load API request log');
      } finally {
        setLoading(false);
      }
    };
    load();
  }, [id]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600" />
      </div>
    );
  }

  if (!item) {
    return <div className="text-gray-600">API request log not found.</div>;
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center space-x-3">
        <Link to="/analytics/api-request-logs" className="p-2 hover:bg-gray-100 rounded-lg transition">
          <ArrowLeft size={20} />
        </Link>
        <div>
          <h1 className="text-2xl font-bold text-gray-900">API Request Log Detail</h1>
          <p className="text-sm text-gray-600 mt-1">{item.id}</p>
        </div>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg flex items-center gap-2">
          <AlertCircle size={18} />
          <span>{error}</span>
        </div>
      )}

      <div className="bg-white rounded-xl border border-gray-200 p-6 space-y-3 text-sm">
        <div>
          <span className="font-medium text-gray-700">method:</span>{' '}
          <span className={`px-2 py-1 rounded-full text-xs font-medium ${methodBadgeClass(item.method)}`}>
            {(item.method || '—').toUpperCase()}
          </span>
        </div>
        <div><span className="font-medium text-gray-700">endpoint/url:</span> {item.endpoint || '—'}</div>
        <div>
          <span className="font-medium text-gray-700">status_code:</span>{' '}
          <span className={`px-2 py-1 rounded-full text-xs font-medium ${statusBadgeClass(item.status_code)}`}>
            {item.status_code ?? '—'}
          </span>
        </div>
        <div><span className="font-medium text-gray-700">response_time:</span> {item.response_time || '—'}</div>
        <div><span className="font-medium text-gray-700">created_at:</span> {item.created_at ? new Date(item.created_at).toLocaleString() : '—'}</div>
      </div>

      <div className="bg-white rounded-xl border border-gray-200 p-6">
        <h2 className="text-lg font-bold text-gray-900 mb-4">Raw JSON</h2>
        <pre className="text-sm bg-gray-50 border border-gray-100 rounded-lg p-4 overflow-x-auto whitespace-pre-wrap">
          {JSON.stringify(item.raw, null, 2)}
        </pre>
      </div>
    </div>
  );
};

export default ApiRequestLogDetail;
