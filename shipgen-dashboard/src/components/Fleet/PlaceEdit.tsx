import React from 'react';
import { Link, useNavigate, useParams } from 'react-router-dom';
import { ArrowLeft } from 'lucide-react';
import PlaceForm from './forms/PlaceForm';

/** PlaceUpdate fields only (OpenAPI) — extra PlaceOut fields are view-only on detail. */
const PlaceEdit: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  return (
    <div className="space-y-6">
      <div className="flex items-center space-x-4">
        <Link to={`/fleet/places/${id}`} className="p-2 hover:bg-gray-100 rounded-lg transition">
          <ArrowLeft size={20} />
        </Link>
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Edit Place</h1>
          <p className="text-sm text-gray-600 mt-1">PATCH /fleetops/v1/places/&#123;id&#125; — body: PlaceUpdate</p>
        </div>
      </div>

      <div className="rounded-xl border border-gray-200 bg-white p-6">
        <PlaceForm mode="edit" placeId={id} onCancel={() => navigate('/fleet/places')} onSuccess={() => navigate('/fleet/places')} />
      </div>
    </div>
  );
};

export default PlaceEdit;
