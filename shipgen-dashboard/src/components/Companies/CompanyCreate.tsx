import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { ArrowLeft } from 'lucide-react';
import CompanyForm from './forms/CompanyForm';

const CompanyCreate: React.FC = () => {
  const navigate = useNavigate();

  return (
    <div className="space-y-6">
      <div className="flex items-center space-x-3">
        <Link to="/analytics/companies" className="p-2 hover:bg-gray-100 rounded-lg transition">
          <ArrowLeft size={20} />
        </Link>
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Create Company</h1>
          <p className="text-sm text-gray-600 mt-1">POST /int/v1/companies</p>
        </div>
      </div>

      <div className="surface-card p-6">
        <CompanyForm mode="create" onCancel={() => navigate('/analytics/companies')} onSuccess={() => navigate('/analytics/companies')} />
      </div>
    </div>
  );
};

export default CompanyCreate;
