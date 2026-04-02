import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { ArrowLeft } from 'lucide-react';
import FleetForm from './forms/FleetForm';

const FleetCreate: React.FC = () => {
  const navigate = useNavigate();
  return (
    <div className="space-y-6">
      <div className="flex items-center space-x-3">
        <Link to="/fleet/fleets" className="p-2 hover:bg-gray-100 rounded-lg transition">
          <ArrowLeft size={20} />
        </Link>
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Create Fleet</h1>
          <p className="text-sm text-gray-600 mt-1">POST /fleetops/v1/fleets</p>
        </div>
      </div>

      <div className="rounded-xl border border-gray-200 bg-white p-6">
        <FleetForm mode="create" onCancel={() => navigate('/fleet/fleets')} onSuccess={() => navigate('/fleet/fleets')} />
      </div>
    </div>
  );
};

export default FleetCreate;
