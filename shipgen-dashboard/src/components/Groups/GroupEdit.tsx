import React from 'react';
import { Link, useNavigate, useParams } from 'react-router-dom';
import { ArrowLeft } from 'lucide-react';
import GroupForm from './forms/GroupForm';

const GroupEdit: React.FC = () => {
  const navigate = useNavigate();
  const { id } = useParams<{ id: string }>();

  return (
    <div className="space-y-6">
      <div className="flex items-center space-x-3">
        <Link to="/analytics/groups" className="p-2 hover:bg-gray-100 rounded-lg transition">
          <ArrowLeft size={20} />
        </Link>
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Edit Group</h1>
          <p className="text-sm text-gray-600 mt-1">PATCH /int/v1/groups/{'{id}'}</p>
        </div>
      </div>

      <div className="surface-card p-6">
        <GroupForm mode="edit" groupId={id} onCancel={() => navigate('/analytics/groups')} onSuccess={() => navigate('/analytics/groups')} />
      </div>
    </div>
  );
};

export default GroupEdit;
