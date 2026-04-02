import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { ArrowLeft } from 'lucide-react';
import TrackingStatusForm from './forms/TrackingStatusForm';

const TrackingStatusCreate: React.FC = () => {
  const navigate = useNavigate();
  return (
    <div className="space-y-6">
      <div className="flex items-center space-x-3">
        <Link to="/fleet/tracking-statuses" className="p-2 hover:bg-gray-100 rounded-lg transition">
          <ArrowLeft size={20} />
        </Link>
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Create Tracking Status</h1>
          <p className="text-sm text-gray-600 mt-1">POST /fleetops/v1/tracking-statuses</p>
        </div>
      </div>

      <div className="bg-white rounded-xl border border-gray-200 p-6">
        <TrackingStatusForm mode="create" onCancel={() => navigate('/fleet/tracking-statuses')} onSuccess={() => navigate('/fleet/tracking-statuses')} />
      </div>
    </div>
  );
};

export default TrackingStatusCreate;
