import React, { useState, useEffect } from 'react';
import { useParams, Link, useLocation } from 'react-router-dom';
import { ArrowLeft, User, AlertCircle, Pencil, Trash2 } from 'lucide-react';
import { driversService, type UiDriver } from '../../services/driversService';
import { canManageDriverVehicleMasterData, getStoredUserRole } from '../../utils/roleAccess';
import { UserRole } from '../../types';

const DriverDetail: React.FC = () => {
  const role = getStoredUserRole() ?? UserRole.VIEWER;
  const canManageMasterData = canManageDriverVehicleMasterData(role);
  const { id } = useParams<{ id: string }>();
  const location = useLocation();
  const isEmbedded = new URLSearchParams(location.search).get('embed') === '1';
  const [driver, setDriver] = useState<UiDriver | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (id) {
      loadDriver();
    }
  }, [id]);

  const loadDriver = async () => {
    try {
      const response = await driversService.getById(id);
      setDriver(response);
      setLoading(false);
    } catch (err: any) {
      setError(err.message || 'Failed to load driver');
      setLoading(false);
    }
  };

  const handleDelete = async () => {
    if (!id) return;
    if (!window.confirm('Delete this driver? This cannot be undone.')) return;
    try {
      await driversService.remove(id);
      window.location.hash = '#/fleet/drivers';
    } catch (err: any) {
      setError(err.message || 'Failed to delete driver');
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error || !driver) {
    return (
      <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
        {error || 'Driver not found'}
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {!isEmbedded ? (
        <div className="flex items-center space-x-4">
        <Link
          to="/fleet/drivers"
          className="p-2 hover:bg-gray-100 rounded-lg transition"
        >
          <ArrowLeft size={20} />
        </Link>
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Driver Details</h1>
          <p className="text-sm text-gray-600 mt-1">{driver.id}</p>
        </div>
        <div className="ml-auto flex items-center gap-2">
          {canManageMasterData && !isEmbedded ? (
            <Link
              to="/fleet/drivers"
              className="inline-flex items-center gap-2 px-3 py-2 text-sm bg-blue-600 text-white rounded-lg hover:bg-blue-700"
            >
              <Pencil size={14} />
              Open List To Edit
            </Link>
          ) : null}
          {canManageMasterData ? (
            <button
              onClick={handleDelete}
              className="inline-flex items-center gap-2 px-3 py-2 text-sm bg-red-600 text-white rounded-lg hover:bg-red-700"
            >
              <Trash2 size={14} />
              Delete
            </button>
          ) : null}
        </div>
        </div>
      ) : null}

      <div className="bg-white rounded-xl border border-gray-200 p-6">
        <h2 className="text-lg font-bold text-gray-900 mb-4">Driver Information</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="text-xs text-gray-500 uppercase mb-1 block">id</label>
            <p className="text-sm font-medium text-gray-900">{driver.id}</p>
          </div>
          <div>
            <label className="text-xs text-gray-500 uppercase flex items-center space-x-1 mb-1">
              <User size={12} />
              <span>drivers_license_number</span>
            </label>
            <p className="text-sm font-medium text-gray-900">{driver.drivers_license_number}</p>
          </div>
          <div>
            <label className="text-xs text-gray-500 uppercase mb-1 block">status</label>
            <p className="text-sm font-medium text-gray-900">{driver.status}</p>
          </div>
          <div>
            <label className="text-xs text-gray-500 uppercase mb-1 block">online</label>
            <p className="text-sm font-medium text-gray-900">{driver.online === 1 ? 'online' : 'offline'}</p>
          </div>
          <div>
            <label className="text-xs text-gray-500 uppercase mb-1 block">company_uuid</label>
            <p className="text-sm font-medium text-gray-900 break-all">{driver.company_uuid ?? 'null'}</p>
          </div>
          <div>
            <label className="text-xs text-gray-500 uppercase mb-1 block">user_uuid</label>
            <p className="text-sm font-medium text-gray-900 break-all">{driver.user_uuid ?? 'null'}</p>
          </div>
          <div>
            <label className="text-xs text-gray-500 uppercase mb-1 block">latitude</label>
            <p className="text-sm font-medium text-gray-900">{driver.latitude != null ? String(driver.latitude) : '-'}</p>
          </div>
          <div>
            <label className="text-xs text-gray-500 uppercase mb-1 block">longitude</label>
            <p className="text-sm font-medium text-gray-900">{driver.longitude != null ? String(driver.longitude) : '-'}</p>
          </div>
          <div>
            <label className="text-xs text-gray-500 uppercase mb-1 block">heading</label>
            <p className="text-sm font-medium text-gray-900">{driver.heading ?? '-'}</p>
          </div>
          <div>
            <label className="text-xs text-gray-500 uppercase mb-1 block">speed</label>
            <p className="text-sm font-medium text-gray-900">{driver.speed ?? '-'}</p>
          </div>
          <div>
            <label className="text-xs text-gray-500 uppercase mb-1 block">altitude</label>
            <p className="text-sm font-medium text-gray-900">{driver.altitude ?? '-'}</p>
          </div>
          <div>
            <label className="text-xs text-gray-500 uppercase mb-1 block">updated_at</label>
            <p className="text-sm font-medium text-gray-900">{driver.updated_at ?? '-'}</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DriverDetail;
