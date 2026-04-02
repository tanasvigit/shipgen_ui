import React from 'react';
import { Link, useNavigate, useParams } from 'react-router-dom';
import { ArrowLeft } from 'lucide-react';
import TrackingStatusForm from './forms/TrackingStatusForm';

const TrackingStatusEdit: React.FC = () => {
  const navigate = useNavigate();
  const { id } = useParams<{ id: string }>();
  return (
    <div className="space-y-6">
      <div className="flex items-center space-x-3">
        <Link to="/fleet/tracking-statuses" className="p-2 hover:bg-gray-100 rounded-lg transition">
          <ArrowLeft size={20} />
        </Link>
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Edit Tracking Status</h1>
          <p className="text-sm text-gray-600 mt-1">PATCH /fleetops/v1/tracking-statuses/{'{id}'}</p>
        </div>
      </div>

      <div className="bg-white rounded-xl border border-gray-200 p-6">
        <TrackingStatusForm mode="edit" trackingStatusId={id} onCancel={() => navigate('/fleet/tracking-statuses')} onSuccess={() => navigate('/fleet/tracking-statuses')} />
      </div>
    </div>
  );
};

export default TrackingStatusEdit;
