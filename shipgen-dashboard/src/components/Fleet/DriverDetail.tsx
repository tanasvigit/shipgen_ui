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
  const driverDisplayName = (driver?.name || '').trim() || driver?.drivers_license_number || driver?.id || '-';

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
          <p className="text-sm text-gray-600 mt-1">{driverDisplayName}</p>
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

      <div className="bg-white rounded-xl border border-gray-200 p-6 space-y-6">
        <div className="flex items-start justify-between gap-3">
          <div>
            <h2 className="text-lg font-bold text-gray-900">Driver Profile</h2>
            <p className="text-sm text-gray-500 mt-1">Operational identity and assignment metadata</p>
          </div>
          <span
            className={`rounded-full px-3 py-1 text-xs font-semibold ${
              driver.status === 'active' ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-700'
            }`}
          >
            {driver.status || 'unknown'}
          </span>
        </div>

        <div className="rounded-lg border border-gray-100 bg-gray-50 p-4">
          <p className="text-xs uppercase tracking-wide text-gray-500 mb-1">Driver Name</p>
          <p className="text-base font-semibold text-gray-900">{driverDisplayName}</p>
        </div>

        <div className="space-y-3">
          <div className="flex items-center justify-between rounded-lg border border-gray-100 p-3">
            <p className="text-xs uppercase tracking-wide text-gray-500 flex items-center gap-1">
              <User size={12} />
              drivers_license_number
            </p>
            <p className="text-sm font-medium text-gray-900">{driver.drivers_license_number || '-'}</p>
          </div>
          <div className="flex items-center justify-between rounded-lg border border-gray-100 p-3">
            <p className="text-xs uppercase tracking-wide text-gray-500">online</p>
            <p className="text-sm font-medium text-gray-900">{driver.online === 1 ? 'online' : 'offline'}</p>
          </div>
          <div className="flex items-center justify-between rounded-lg border border-gray-100 p-3">
            <p className="text-xs uppercase tracking-wide text-gray-500">company_uuid</p>
            <p className="text-sm font-medium text-gray-900 break-all text-right">{driver.company_uuid ?? 'null'}</p>
          </div>
          <div className="flex items-center justify-between rounded-lg border border-gray-100 p-3">
            <p className="text-xs uppercase tracking-wide text-gray-500">user_uuid</p>
            <p className="text-sm font-medium text-gray-900 break-all text-right">{driver.user_uuid ?? 'null'}</p>
          </div>
          <div className="flex items-center justify-between rounded-lg border border-gray-100 p-3">
            <p className="text-xs uppercase tracking-wide text-gray-500">latitude</p>
            <p className="text-sm font-medium text-gray-900">{driver.latitude != null ? String(driver.latitude) : '-'}</p>
          </div>
          <div className="flex items-center justify-between rounded-lg border border-gray-100 p-3">
            <p className="text-xs uppercase tracking-wide text-gray-500">longitude</p>
            <p className="text-sm font-medium text-gray-900">{driver.longitude != null ? String(driver.longitude) : '-'}</p>
          </div>
          <div className="flex items-center justify-between rounded-lg border border-gray-100 p-3">
            <p className="text-xs uppercase tracking-wide text-gray-500">heading</p>
            <p className="text-sm font-medium text-gray-900">{driver.heading ?? '-'}</p>
          </div>
          <div className="flex items-center justify-between rounded-lg border border-gray-100 p-3">
            <p className="text-xs uppercase tracking-wide text-gray-500">speed</p>
            <p className="text-sm font-medium text-gray-900">{driver.speed ?? '-'}</p>
          </div>
          <div className="flex items-center justify-between rounded-lg border border-gray-100 p-3">
            <p className="text-xs uppercase tracking-wide text-gray-500">altitude</p>
            <p className="text-sm font-medium text-gray-900">{driver.altitude ?? '-'}</p>
          </div>
          <div className="flex items-center justify-between rounded-lg border border-gray-100 p-3">
            <p className="text-xs uppercase tracking-wide text-gray-500">updated_at</p>
            <p className="text-sm font-medium text-gray-900">{driver.updated_at ?? '-'}</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DriverDetail;
