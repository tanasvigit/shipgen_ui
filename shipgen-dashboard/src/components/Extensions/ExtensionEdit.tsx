import React from 'react';
import { Link, useNavigate, useParams } from 'react-router-dom';
import { ArrowLeft } from 'lucide-react';
import ExtensionForm from './forms/ExtensionForm';

const ExtensionEdit: React.FC = () => {
  const navigate = useNavigate();
  const { id } = useParams<{ id: string }>();

  return (
    <div className="space-y-6">
      <div className="flex items-center space-x-3">
        <Link to="/analytics/extensions" className="p-2 hover:bg-gray-100 rounded-lg transition">
          <ArrowLeft size={20} />
        </Link>
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Edit Extension</h1>
          <p className="text-sm text-gray-600 mt-1">PATCH /int/v1/extensions/{'{id}'}</p>
        </div>
      </div>

      <div className="bg-white rounded-xl border border-gray-200 p-6">
        <ExtensionForm mode="edit" extensionId={id} onCancel={() => navigate('/analytics/extensions')} onSuccess={() => navigate('/analytics/extensions')} />
      </div>
    </div>
  );
};

export default ExtensionEdit;
