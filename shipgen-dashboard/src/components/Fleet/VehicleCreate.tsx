import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { ArrowLeft } from 'lucide-react';
import VehicleForm from './forms/VehicleForm';

const VehicleCreate: React.FC = () => {
  const navigate = useNavigate();
  return (
    <div className="space-y-6">
      <div className="flex items-center space-x-4">
        <Link to="/fleet/vehicles" className="p-2 hover:bg-gray-100 rounded-lg transition">
          <ArrowLeft size={20} />
        </Link>
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Create Vehicle</h1>
          <p className="text-sm text-gray-600 mt-1">POST /fleetops/v1/vehicles fields only</p>
        </div>
      </div>

      <div className="rounded-xl border border-gray-200 bg-white p-6">
        <VehicleForm mode="create" onCancel={() => navigate('/fleet/vehicles')} onSuccess={() => navigate('/fleet/vehicles')} />
      </div>
    </div>
  );
};

export default VehicleCreate;
