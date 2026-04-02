import React from 'react';
import { Link, useNavigate, useParams } from 'react-router-dom';
import { ArrowLeft } from 'lucide-react';
import TrackingNumberForm from './forms/TrackingNumberForm';

const TrackingNumberEdit: React.FC = () => {
  const navigate = useNavigate();
  const { id } = useParams<{ id: string }>();
  return (
    <div className="space-y-6">
      <div className="flex items-center space-x-3">
        <Link to="/fleet/tracking-numbers" className="p-2 hover:bg-gray-100 rounded-lg transition">
          <ArrowLeft size={20} />
        </Link>
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Edit Tracking Number</h1>
          <p className="text-sm text-gray-600 mt-1">PATCH /fleetops/v1/tracking-numbers/{'{id}'}</p>
        </div>
      </div>

      <div className="bg-white rounded-xl border border-gray-200 p-6">
        <TrackingNumberForm mode="edit" trackingNumberId={id} onCancel={() => navigate('/fleet/tracking-numbers')} onSuccess={() => navigate('/fleet/tracking-numbers')} />
      </div>
    </div>
  );
};

export default TrackingNumberEdit;
