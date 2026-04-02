import React, { useEffect, useState } from 'react';
import { Link, useLocation, useNavigate, useParams } from 'react-router-dom';
import { ArrowLeft, Store, AlertCircle, Pencil, Trash2 } from 'lucide-react';
import { vendorsService } from '../../services/vendorsService';
import type { MockVendor } from '../../mocks/data/vendors';
import { formatMeta } from '../../utils/contactHelpers';

const VendorDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const location = useLocation();
  const isEmbedded = new URLSearchParams(location.search).get('embed') === '1';
  const [vendor, setVendor] = useState<MockVendor | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (id) loadVendor();
  }, [id]);

  const loadVendor = async () => {
    try {
      setLoading(true);
      const response = await vendorsService.getById(id as string);
      setVendor(response);
      setLoading(false);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to load vendor');
      setLoading(false);
    }
  };

  const handleDelete = async () => {
    if (!id) return;
    if (!window.confirm('Delete this vendor? This cannot be undone.')) return;
    try {
      await vendorsService.remove(id);
      navigate('/fleet/vendors');
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to delete vendor');
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600" />
      </div>
    );
  }

  if (error || !vendor) {
    return (
      <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg flex items-center space-x-2">
        <AlertCircle size={20} />
        <span>{error || 'Vendor not found'}</span>
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
          <Link to="/fleet/vendors" className="p-2 hover:bg-gray-100 rounded-lg transition">
            <ArrowLeft size={20} />
          </Link>
          <div>
            <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
              <Store size={24} className="text-blue-600" />
              Vendor
            </h1>
            <p className="text-sm text-gray-600 mt-1">GET /fleetops/v1/vendors/&#123;id&#125;</p>
          </div>
        </div>
        <div className="flex items-center space-x-2">
          {!isEmbedded ? (
            <Link
              to="/fleet/vendors"
              data-testid="vendor-detail-edit"
              className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
            >
              <Pencil size={18} />
              <span>Open List To Edit</span>
            </Link>
          ) : null}
          <button
            type="button"
            data-testid="vendor-detail-delete"
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
            {row('uuid', vendor.uuid)}
            {row('public_id', vendor.public_id)}
            {row('company_uuid', vendor.company_uuid)}
            {row('place_uuid', vendor.place_uuid)}
            {row('internal_id', vendor.internal_id)}
            {row('business_id', vendor.business_id)}
            {row('id', vendor.id)}
            {row('slug', vendor.slug)}
          </div>
        </section>

        <section>
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Vendor</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {row('name', vendor.name)}
            {row('type', vendor.type)}
            {row('status', vendor.status)}
            {row('connected', vendor.connected)}
            {row('email', vendor.email)}
            {row('phone', vendor.phone)}
            {row('website_url', vendor.website_url)}
            {row('country', vendor.country)}
          </div>
        </section>

        <section>
          <h2 className="text-lg font-semibold text-gray-900 mb-2">meta</h2>
          <pre className="text-sm bg-gray-50 border border-gray-100 rounded-lg p-4 overflow-x-auto whitespace-pre-wrap">
            {vendor.meta == null ? '—' : formatMeta(vendor.meta)}
          </pre>
        </section>

        <section>
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Timestamps</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {row('created_at', vendor.created_at)}
            {row('updated_at', vendor.updated_at)}
          </div>
        </section>
      </div>
    </div>
  );
};

export default VendorDetail;
