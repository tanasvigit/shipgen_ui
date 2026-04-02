import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { ArrowLeft } from 'lucide-react';
import TrackingNumberForm from './forms/TrackingNumberForm';

const TrackingNumberCreate: React.FC = () => {
  const navigate = useNavigate();
  return (
    <div className="space-y-6">
      <div className="flex items-center space-x-3">
        <Link to="/fleet/tracking-numbers" className="p-2 hover:bg-gray-100 rounded-lg transition">
          <ArrowLeft size={20} />
        </Link>
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Create Tracking Number</h1>
          <p className="text-sm text-gray-600 mt-1">POST /fleetops/v1/tracking-numbers</p>
        </div>
      </div>

      <div className="bg-white rounded-xl border border-gray-200 p-6">
        <TrackingNumberForm mode="create" onCancel={() => navigate('/fleet/tracking-numbers')} onSuccess={() => navigate('/fleet/tracking-numbers')} />
      </div>
    </div>
  );
};

export default TrackingNumberCreate;
