import React, { useEffect, useState } from 'react';
import { Link, useLocation, useNavigate, useParams } from 'react-router-dom';
import { ArrowLeft, AlertTriangle, AlertCircle, Pencil, Trash2 } from 'lucide-react';
import { issuesService } from '../../services/issuesService';
import type { MockIssue } from '../../mocks/data/issues';
import { formatMeta } from '../../utils/contactHelpers';
import EntityLink from '../common/EntityLink';

const IssueDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const location = useLocation();
  const isEmbedded = new URLSearchParams(location.search).get('embed') === '1';
  const [issue, setIssue] = useState<MockIssue | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (id) loadIssue();
  }, [id]);

  const loadIssue = async () => {
    try {
      setLoading(true);
      const response = await issuesService.getById(id as string);
      setIssue(response);
      setLoading(false);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to load issue');
      setLoading(false);
    }
  };

  const handleDelete = async () => {
    if (!id) return;
    if (!window.confirm('Delete this issue? This cannot be undone.')) return;
    try {
      await issuesService.remove(id);
      navigate('/fleet/issues');
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to delete issue');
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600" />
      </div>
    );
  }

  if (error || !issue) {
    return (
      <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg flex items-center space-x-2">
        <AlertCircle size={20} />
        <span>{error || 'Issue not found'}</span>
      </div>
    );
  }

  const row = (label: string, value: React.ReactNode) => (
    <div>
      <div className="text-xs font-medium text-gray-500 uppercase">{label}</div>
      <div className="text-sm text-gray-900 mt-1 break-all">{value ?? '—'}</div>
    </div>
  );

  return (
    <div className="space-y-6">
      {!isEmbedded ? (
        <div className="flex items-center justify-between flex-wrap gap-4">
        <div className="flex items-center space-x-4">
          <Link to="/fleet/issues" className="p-2 hover:bg-gray-100 rounded-lg transition">
            <ArrowLeft size={20} />
          </Link>
          <div>
            <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
              <AlertTriangle size={24} className="text-blue-600" />
              Issue
            </h1>
            <p className="text-sm text-gray-600 mt-1">GET /fleetops/v1/issues/&#123;id&#125;</p>
          </div>
        </div>
        <div className="flex items-center space-x-2">
          {!isEmbedded ? (
            <Link to="/fleet/issues" className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition">
              <Pencil size={18} />
              <span>Open List To Edit</span>
            </Link>
          ) : null}
          <button
            type="button"
            onClick={handleDelete}
            className="flex items-center space-x-2 px-4 py-2 border border-red-200 text-red-700 rounded-lg hover:bg-red-50 transition"
          >
            <Trash2 size={18} />
            <span>Delete</span>
          </button>
        </div>
        </div>
      ) : null}

      <div className="bg-white rounded-xl border border-gray-200 p-6 space-y-8">
        <section>
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Identifiers</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {row('uuid', issue.uuid)}
            {row('public_id', issue.public_id)}
            {row('issue_id', issue.issue_id)}
            {row('id', issue.id)}
            {row('company_uuid', issue.company_uuid)}
          </div>
        </section>

        <section>
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Issue</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {row('title', issue.title)}
            {row('category', issue.category)}
            {row('type', issue.type)}
            {row('priority', issue.priority)}
            {row('status', issue.status)}
            {row('report', issue.report)}
            {row('tags', issue.tags ? issue.tags.join(', ') : '—')}
            {row('resolved_at', issue.resolved_at)}
          </div>
        </section>

        <section>
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Related References</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {row('driver_uuid', <EntityLink id={issue.driver_uuid} label={issue.driver_uuid} to="/fleet/drivers" title="View Driver" />)}
            {row('driver_name', issue.driver_name)}
            {row('vehicle_uuid', <EntityLink id={issue.vehicle_uuid} label={issue.vehicle_uuid} to="/fleet/vehicles" title="View Vehicle" />)}
            {row('vehicle_name', issue.vehicle_name)}
            {row('assigned_to_uuid', issue.assigned_to_uuid)}
            {row('assignee_name', issue.assignee_name)}
            {row('reported_by_uuid', issue.reported_by_uuid)}
            {row('reporter_name', issue.reporter_name)}
          </div>
        </section>

        <section>
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Location</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {row('latitude', issue.latitude)}
            {row('longitude', issue.longitude)}
            {row('location', issue.location ? JSON.stringify(issue.location) : '—')}
          </div>
        </section>

        <section>
          <h2 className="text-lg font-semibold text-gray-900 mb-2">meta</h2>
          <pre className="text-sm bg-gray-50 border border-gray-100 rounded-lg p-4 overflow-x-auto whitespace-pre-wrap">
            {issue.meta == null ? '—' : formatMeta(issue.meta)}
          </pre>
        </section>

        <section>
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Timestamps</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {row('created_at', issue.created_at)}
            {row('updated_at', issue.updated_at)}
          </div>
        </section>
      </div>
    </div>
  );
};

export default IssueDetail;
