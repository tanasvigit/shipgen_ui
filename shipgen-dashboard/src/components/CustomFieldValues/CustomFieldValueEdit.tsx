import React from 'react';
import { Link, useNavigate, useParams } from 'react-router-dom';
import { ArrowLeft } from 'lucide-react';
import CustomFieldValueForm from './forms/CustomFieldValueForm';

const CustomFieldValueEdit: React.FC = () => {
  const navigate = useNavigate();
  const { id } = useParams<{ id: string }>();

  return (
    <div className="space-y-6">
      <div className="flex items-center space-x-3">
        <Link to="/analytics/custom-field-values" className="p-2 hover:bg-gray-100 rounded-lg transition">
          <ArrowLeft size={20} />
        </Link>
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Edit Custom Field Value</h1>
          <p className="text-sm text-gray-600 mt-1">PATCH /int/v1/custom-field-values/{'{id}'}</p>
        </div>
      </div>

      <div className="surface-card p-6">
        <CustomFieldValueForm mode="edit" customFieldValueId={id} onCancel={() => navigate('/analytics/custom-field-values')} onSuccess={() => navigate('/analytics/custom-field-values')} />
      </div>
    </div>
  );
};

export default CustomFieldValueEdit;
