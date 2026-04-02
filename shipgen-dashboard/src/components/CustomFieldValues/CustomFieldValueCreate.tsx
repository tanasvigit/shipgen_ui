import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { ArrowLeft } from 'lucide-react';
import CustomFieldValueForm from './forms/CustomFieldValueForm';

const CustomFieldValueCreate: React.FC = () => {
  const navigate = useNavigate();

  return (
    <div className="space-y-6">
      <div className="flex items-center space-x-3">
        <Link to="/analytics/custom-field-values" className="p-2 hover:bg-gray-100 rounded-lg transition">
          <ArrowLeft size={20} />
        </Link>
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Create Custom Field Value</h1>
          <p className="text-sm text-gray-600 mt-1">POST /int/v1/custom-field-values</p>
        </div>
      </div>

      <div className="surface-card p-6">
        <CustomFieldValueForm mode="create" onCancel={() => navigate('/analytics/custom-field-values')} onSuccess={() => navigate('/analytics/custom-field-values')} />
      </div>
    </div>
  );
};

export default CustomFieldValueCreate;
