import React, { useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { AlertCircle, ArrowLeft } from 'lucide-react';
import { activitiesService, type UiActivity } from '../../services/activitiesService';

const ActivityDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [item, setItem] = useState<UiActivity | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const load = async () => {
      if (!id) return;
      try {
        setLoading(true);
        setError(null);
        const row = await activitiesService.getById(id);
        setItem(row);
      } catch (err: unknown) {
        setError(err instanceof Error ? err.message : 'Failed to load activity');
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
    return <div className="text-gray-600">Activity not found.</div>;
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center space-x-3">
        <Link to="/analytics/activities" className="p-2 hover:bg-gray-100 rounded-lg transition">
          <ArrowLeft size={20} />
        </Link>
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Activity Detail</h1>
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
        <div><span className="font-medium text-gray-700">action:</span> {item.action || '—'}</div>
        <div><span className="font-medium text-gray-700">description:</span> {item.description || '—'}</div>
        <div><span className="font-medium text-gray-700">user:</span> {item.user || '—'}</div>
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

export default ActivityDetail;
