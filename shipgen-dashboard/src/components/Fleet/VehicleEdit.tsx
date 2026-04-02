import React from 'react';
import { Link, useNavigate, useParams } from 'react-router-dom';
import { ArrowLeft } from 'lucide-react';
import VehicleForm from './forms/VehicleForm';

const VehicleEdit: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  return (
    <div className="space-y-6">
      <div className="flex items-center space-x-4">
        <Link to={`/fleet/vehicles/${id}`} className="p-2 hover:bg-gray-100 rounded-lg transition">
          <ArrowLeft size={20} />
        </Link>
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Edit Vehicle</h1>
          <p className="text-sm text-gray-600 mt-1">PATCH /fleetops/v1/vehicles/{'{vehicle_id}'}</p>
        </div>
      </div>

      <div className="rounded-xl border border-gray-200 bg-white p-6">
        <VehicleForm mode="edit" vehicleId={id} onCancel={() => navigate('/fleet/vehicles')} onSuccess={() => navigate('/fleet/vehicles')} />
      </div>
    </div>
  );
};

export default VehicleEdit;
