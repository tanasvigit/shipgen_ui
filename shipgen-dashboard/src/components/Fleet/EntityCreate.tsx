import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { ArrowLeft } from 'lucide-react';
import EntityForm from './forms/EntityForm';

const EntityCreate: React.FC = () => {
  const navigate = useNavigate();
  return (
    <div className="space-y-6">
      <div className="flex items-center space-x-3">
        <Link to="/fleet/entities" className="p-2 hover:bg-gray-100 rounded-lg transition">
          <ArrowLeft size={20} />
        </Link>
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Create Entity</h1>
          <p className="text-sm text-gray-600 mt-1">POST /fleetops/v1/entities</p>
        </div>
      </div>

      <div className="rounded-xl border border-gray-200 bg-white p-6">
        <EntityForm mode="create" onCancel={() => navigate('/fleet/entities')} onSuccess={() => navigate('/fleet/entities')} />
      </div>
    </div>
  );
};

export default EntityCreate;
