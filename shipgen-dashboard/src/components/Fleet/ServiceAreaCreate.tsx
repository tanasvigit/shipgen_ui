import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { ArrowLeft } from 'lucide-react';
import ServiceAreaForm from './forms/ServiceAreaForm';

const ServiceAreaCreate: React.FC = () => {
  const navigate = useNavigate();
  return (
    <div className="space-y-6">
      <div className="flex items-center space-x-3">
        <Link to="/fleet/service-areas" className="p-2 hover:bg-gray-100 rounded-lg transition">
          <ArrowLeft size={20} />
        </Link>
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Create Service Area</h1>
          <p className="text-sm text-gray-600 mt-1">POST /fleetops/v1/service-areas</p>
        </div>
      </div>

      <div className="rounded-xl border border-gray-200 bg-white p-6">
        <ServiceAreaForm mode="create" onCancel={() => navigate('/fleet/service-areas')} onSuccess={() => navigate('/fleet/service-areas')} />
      </div>
    </div>
  );
};

export default ServiceAreaCreate;
