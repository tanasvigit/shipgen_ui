import React from 'react';
import { Link, useNavigate, useParams } from 'react-router-dom';
import { ArrowLeft } from 'lucide-react';
import IssueForm from './forms/IssueForm';

const IssueEdit: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  return (
    <div className="space-y-6">
      <div className="flex items-center space-x-4">
        <Link to={`/fleet/issues/${id}`} className="p-2 hover:bg-gray-100 rounded-lg transition">
          <ArrowLeft size={20} />
        </Link>
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Edit Issue</h1>
          <p className="text-sm text-gray-600 mt-1">PUT /fleetops/v1/issues/&#123;id&#125; — body: IssueUpdate</p>
        </div>
      </div>

      <div className="surface-card p-6">
        <IssueForm mode="edit" issueId={id} onCancel={() => navigate('/fleet/issues')} onSuccess={() => navigate('/fleet/issues')} />
      </div>
    </div>
  );
};

export default IssueEdit;
