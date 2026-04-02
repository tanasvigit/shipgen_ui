import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { ArrowLeft } from 'lucide-react';
import GroupForm from './forms/GroupForm';

const GroupCreate: React.FC = () => {
  const navigate = useNavigate();

  return (
    <div className="space-y-6">
      <div className="flex items-center space-x-3">
        <Link to="/analytics/groups" className="p-2 hover:bg-gray-100 rounded-lg transition">
          <ArrowLeft size={20} />
        </Link>
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Create Group</h1>
          <p className="text-sm text-gray-600 mt-1">POST /int/v1/groups</p>
        </div>
      </div>

      <div className="surface-card p-6">
        <GroupForm mode="create" onCancel={() => navigate('/analytics/groups')} onSuccess={() => navigate('/analytics/groups')} />
      </div>
    </div>
  );
};

export default GroupCreate;
