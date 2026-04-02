import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { ArrowLeft } from 'lucide-react';
import ExtensionForm from './forms/ExtensionForm';

const ExtensionCreate: React.FC = () => {
  const navigate = useNavigate();

  return (
    <div className="space-y-6">
      <div className="flex items-center space-x-3">
        <Link to="/analytics/extensions" className="p-2 hover:bg-gray-100 rounded-lg transition">
          <ArrowLeft size={20} />
        </Link>
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Create Extension</h1>
          <p className="text-sm text-gray-600 mt-1">POST /int/v1/extensions</p>
        </div>
      </div>

      <div className="bg-white rounded-xl border border-gray-200 p-6">
        <ExtensionForm mode="create" onCancel={() => navigate('/analytics/extensions')} onSuccess={() => navigate('/analytics/extensions')} />
      </div>
    </div>
  );
};

export default ExtensionCreate;
