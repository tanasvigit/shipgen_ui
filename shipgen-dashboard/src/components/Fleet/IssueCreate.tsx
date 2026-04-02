import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { ArrowLeft } from 'lucide-react';
import IssueForm from './forms/IssueForm';

const IssueCreate: React.FC = () => {
  const navigate = useNavigate();

  return (
    <div className="space-y-6">
      <div className="flex items-center space-x-4">
        <Link to="/fleet/issues" className="p-2 hover:bg-gray-100 rounded-lg transition">
          <ArrowLeft size={20} />
        </Link>
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Create Issue</h1>
          <p className="text-sm text-gray-600 mt-1">POST /fleetops/v1/issues — body: IssueCreate</p>
        </div>
      </div>

      <div className="surface-card p-6">
        <IssueForm mode="create" onCancel={() => navigate('/fleet/issues')} onSuccess={() => navigate('/fleet/issues')} />
      </div>
    </div>
  );
};

export default IssueCreate;
