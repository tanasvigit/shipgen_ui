import React, { useEffect, useState } from 'react';
import { Link, useLocation, useNavigate, useParams } from 'react-router-dom';
import { ArrowLeft, MapPin, AlertCircle, Pencil, Trash2 } from 'lucide-react';
import { placesService } from '../../services/placesService';
import type { MockPlace } from '../../mocks/data/places';
import { formatMeta } from '../../utils/contactHelpers';

const PlaceDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const location = useLocation();
  const isEmbedded = new URLSearchParams(location.search).get('embed') === '1';
  const [place, setPlace] = useState<MockPlace | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (id) loadPlace();
  }, [id]);

  const loadPlace = async () => {
    try {
      setLoading(true);
      const response = await placesService.getById(id as string);
      setPlace(response);
      setLoading(false);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to load place');
      setLoading(false);
    }
  };

  const handleDelete = async () => {
    if (!id) return;
    if (!window.confirm('Delete this place? This cannot be undone.')) return;
    try {
      await placesService.remove(id);
      navigate('/fleet/places');
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to delete place');
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600" />
      </div>
    );
  }

  if (error || !place) {
    return (
      <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg flex items-center space-x-2">
        <AlertCircle size={20} />
        <span>{error || 'Place not found'}</span>
      </div>
    );
  }

  const row = (label: string, value: React.ReactNode) => (
    <div>
      <div className="text-xs font-medium text-gray-500 uppercase">{label}</div>
      <div className="text-sm text-gray-900 mt-1 break-all">{value ?? '—'}</div>
    </div>
  );

  return (
    <div className="space-y-6">
      {!isEmbedded ? (
        <div className="flex items-center justify-between flex-wrap gap-4">
        <div className="flex items-center space-x-4">
          <Link to="/fleet/places" className="p-2 hover:bg-gray-100 rounded-lg transition">
            <ArrowLeft size={20} />
          </Link>
          <div>
            <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
              <MapPin size={24} className="text-blue-600" />
              Place
            </h1>
            <p className="text-sm text-gray-600 mt-1">GET /fleetops/v1/places/&#123;id&#125;</p>
          </div>
        </div>
        <div className="flex items-center space-x-2">
          {!isEmbedded ? (
            <Link
              to="/fleet/places"
              className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
            >
              <Pencil size={18} />
              <span>Open List To Edit</span>
            </Link>
          ) : null}
          <button
            type="button"
            onClick={handleDelete}
            className="flex items-center space-x-2 px-4 py-2 border border-red-200 text-red-700 rounded-lg hover:bg-red-50 transition"
          >
            <Trash2 size={18} />
            <span>Delete</span>
          </button>
        </div>
        </div>
      ) : null}

      <div className="bg-white rounded-xl border border-gray-200 p-6 space-y-8">
        <section>
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Identifiers</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {row('uuid', place.uuid)}
            {row('public_id', place.public_id)}
            {row('company_uuid', place.company_uuid)}
            {row('id', place.id)}
          </div>
        </section>

        <section>
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Owner</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {row('owner_uuid', place.owner_uuid)}
            {row('owner_type', place.owner_type)}
          </div>
        </section>

        <section>
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Name &amp; type</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {row('name', place.name)}
            {row('type', place.type)}
            {row('phone', place.phone)}
            {row('remarks', place.remarks)}
          </div>
        </section>

        <section>
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Address</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {row('street1', place.street1)}
            {row('street2', place.street2)}
            {row('neighborhood', place.neighborhood)}
            {row('district', place.district)}
            {row('building', place.building)}
            {row('city', place.city)}
            {row('province', place.province)}
            {row('postal_code', place.postal_code)}
            {row('country', place.country)}
            {row('security_access_code', place.security_access_code)}
          </div>
        </section>

        <section>
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Location</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {row('latitude', place.latitude)}
            {row('longitude', place.longitude)}
          </div>
        </section>

        <section>
          <h2 className="text-lg font-semibold text-gray-900 mb-2">meta</h2>
          <pre className="text-sm bg-gray-50 border border-gray-100 rounded-lg p-4 overflow-x-auto whitespace-pre-wrap">
            {place.meta == null ? '—' : formatMeta(place.meta)}
          </pre>
        </section>

        <section>
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Timestamps</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {row('created_at', place.created_at)}
            {row('updated_at', place.updated_at)}
          </div>
        </section>
      </div>
    </div>
  );
};

export default PlaceDetail;
