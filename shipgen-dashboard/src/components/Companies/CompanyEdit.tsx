import React from 'react';
import { Link, useNavigate, useParams } from 'react-router-dom';
import { ArrowLeft } from 'lucide-react';
import CompanyForm from './forms/CompanyForm';

const CompanyEdit: React.FC = () => {
  const navigate = useNavigate();
  const { id } = useParams<{ id: string }>();

  return (
    <div className="space-y-6">
      <div className="flex items-center space-x-3">
        <Link to="/analytics/companies" className="p-2 hover:bg-gray-100 rounded-lg transition">
          <ArrowLeft size={20} />
        </Link>
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Edit Company</h1>
          <p className="text-sm text-gray-600 mt-1">PATCH /int/v1/companies/{'{id}'}</p>
        </div>
      </div>

      <div className="surface-card p-6">
        <CompanyForm mode="edit" companyId={id} onCancel={() => navigate('/analytics/companies')} onSuccess={() => navigate('/analytics/companies')} />
      </div>
    </div>
  );
};

export default CompanyEdit;
