import React from 'react';
import { Link, useNavigate, useParams } from 'react-router-dom';
import { ArrowLeft } from 'lucide-react';
import EntityForm from './forms/EntityForm';

const EntityEdit: React.FC = () => {
  const navigate = useNavigate();
  const { id } = useParams<{ id: string }>();
  return (
    <div className="space-y-6">
      <div className="flex items-center space-x-3">
        <Link to="/fleet/entities" className="p-2 hover:bg-gray-100 rounded-lg transition">
          <ArrowLeft size={20} />
        </Link>
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Edit Entity</h1>
          <p className="text-sm text-gray-600 mt-1">PUT /fleetops/v1/entities/{'{id}'}</p>
        </div>
      </div>

      <div className="rounded-xl border border-gray-200 bg-white p-6">
        <EntityForm mode="edit" entityId={id} onCancel={() => navigate('/fleet/entities')} onSuccess={() => navigate('/fleet/entities')} />
      </div>
    </div>
  );
};

export default EntityEdit;
