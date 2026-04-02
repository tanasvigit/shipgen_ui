import React from 'react';
import { Link, useNavigate, useParams } from 'react-router-dom';
import { ArrowLeft } from 'lucide-react';
import VendorForm from './forms/VendorForm';

/** PATCH body: VendorUpdate only (name, type, email, phone, meta). */
const VendorEdit: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  return (
    <div className="space-y-6">
      <div className="flex items-center space-x-4">
        <Link to={`/fleet/vendors/${id}`} className="p-2 hover:bg-gray-100 rounded-lg transition">
          <ArrowLeft size={20} />
        </Link>
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Edit Vendor</h1>
          <p className="text-sm text-gray-600 mt-1">PATCH /fleetops/v1/vendors/&#123;id&#125; — body: VendorUpdate</p>
        </div>
      </div>

      <div className="rounded-xl border border-gray-200 bg-white p-6">
        <VendorForm mode="edit" vendorId={id} onCancel={() => navigate('/fleet/vendors')} onSuccess={() => navigate('/fleet/vendors')} />
      </div>
    </div>
  );
};

export default VendorEdit;
