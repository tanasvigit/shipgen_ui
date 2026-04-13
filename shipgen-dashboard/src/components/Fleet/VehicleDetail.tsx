import React, { useState, useEffect } from 'react';
import { useParams, Link, useLocation } from 'react-router-dom';
import { ArrowLeft, AlertCircle, Fuel, Pencil, Trash2 } from 'lucide-react';
import { driversService, type UiDriver } from '../../services/driversService';
import { vehiclesService, type UiVehicle } from '../../services/vehiclesService';
import { canManageDriverVehicleMasterData, getStoredUserRole } from '../../utils/roleAccess';
import { UserRole } from '../../types';
import EntityLink from '../common/EntityLink';

const VehicleDetail: React.FC = () => {
  const role = getStoredUserRole() ?? UserRole.VIEWER;
  const canManageMasterData = canManageDriverVehicleMasterData(role);
  const { id } = useParams<{ id: string }>();
  const location = useLocation();
  const isEmbedded = new URLSearchParams(location.search).get('embed') === '1';
  const [vehicle, setVehicle] = useState<UiVehicle | null>(null);
  const [assignedDriver, setAssignedDriver] = useState<UiDriver | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const getVehicleDisplayName = (v: UiVehicle): string => {
    const plate = (v.plate_number || '').trim();
    if (plate.length > 0) return plate;
    const composed = `${v.make || ''} ${v.model || ''}`.trim();
    if (composed.length > 0) return composed;
    return v.id;
  };

  useEffect(() => {
    if (!id) return;
    const loadVehicle = async () => {
      try {
        setLoading(true);
        const response = await vehiclesService.getById(id);
        setVehicle(response);
        const drivers = await driversService.listForVehicle(response.id, 10);
        setAssignedDriver(drivers[0] ?? null);
      } catch (err: unknown) {
        setError(err instanceof Error ? err.message : 'Failed to load vehicle');
      } finally {
        setLoading(false);
      }
    };
    void loadVehicle();
  }, [id]);

  const handleDelete = async () => {
    if (!id) return;
    if (!window.confirm('Delete this vehicle? This cannot be undone.')) return;
    try {
      await vehiclesService.remove(id);
      window.location.hash = '#/fleet/vehicles';
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to delete vehicle');
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error || !vehicle) {
    return (
      <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
        {error || 'Vehicle not found'}
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {!isEmbedded ? (
        <div className="flex items-center space-x-4">
          <Link to="/fleet/vehicles" className="p-2 hover:bg-gray-100 rounded-lg transition">
            <ArrowLeft size={20} />
          </Link>
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Vehicle Details</h1>
            <p className="text-sm text-gray-600 mt-1">{getVehicleDisplayName(vehicle)}</p>
          </div>
          <div className="ml-auto flex items-center gap-2">
            {canManageMasterData ? (
              <>
                <Link
                  to="/fleet/vehicles"
                  className="inline-flex items-center gap-2 px-3 py-2 text-sm bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                >
                  <Pencil size={14} />
                  Open List To Edit
                </Link>
                <button
                  type="button"
                  onClick={() => void handleDelete()}
                  className="inline-flex items-center gap-2 px-3 py-2 text-sm bg-red-600 text-white rounded-lg hover:bg-red-700"
                >
                  <Trash2 size={14} />
                  Delete
                </button>
              </>
            ) : null}
          </div>
        </div>
      ) : null}

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg flex items-center space-x-2">
          <AlertCircle size={20} />
          <span>{error}</span>
        </div>
      )}

      <div className="bg-white rounded-xl border border-gray-200 p-6 space-y-6">
        <div className="flex items-start justify-between gap-3">
          <div>
            <h2 className="text-lg font-bold text-gray-900">Vehicle Profile</h2>
            <p className="text-sm text-gray-500 mt-1">Identity, specifications, and assignment details</p>
          </div>
          <span
            className={`rounded-full px-3 py-1 text-xs font-semibold ${
              vehicle.status === 'active' ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-700'
            }`}
          >
            {vehicle.status || 'unknown'}
          </span>
        </div>

        <div className="rounded-lg border border-gray-100 bg-gray-50 p-4">
          <p className="text-xs uppercase tracking-wide text-gray-500 mb-1">Vehicle Name</p>
          <p className="text-base font-semibold text-gray-900">{getVehicleDisplayName(vehicle)}</p>
          {vehicle.plate_number ? <p className="text-sm text-gray-600 mt-1">Plate: {vehicle.plate_number}</p> : null}
        </div>

        <div className="space-y-3">
          <div className="flex items-center justify-between rounded-lg border border-gray-100 p-3">
            <p className="text-xs uppercase tracking-wide text-gray-500">make</p>
            <p className="text-sm font-medium text-gray-900">{vehicle.make || '-'}</p>
          </div>
          <div className="flex items-center justify-between rounded-lg border border-gray-100 p-3">
            <p className="text-xs uppercase tracking-wide text-gray-500">model</p>
            <p className="text-sm font-medium text-gray-900">{vehicle.model || '-'}</p>
          </div>
          <div className="flex items-center justify-between rounded-lg border border-gray-100 p-3">
            <p className="text-xs uppercase tracking-wide text-gray-500">year</p>
            <p className="text-sm font-medium text-gray-900">{vehicle.year || '-'}</p>
          </div>
          <div className="flex items-center justify-between rounded-lg border border-gray-100 p-3">
            <p className="text-xs uppercase tracking-wide text-gray-500">trim</p>
            <p className="text-sm font-medium text-gray-900">{vehicle.trim || '-'}</p>
          </div>
          <div className="flex items-center justify-between rounded-lg border border-gray-100 p-3">
            <p className="text-xs uppercase tracking-wide text-gray-500">type</p>
            <p className="text-sm font-medium text-gray-900">{vehicle.type || '-'}</p>
          </div>
          <div className="flex items-center justify-between rounded-lg border border-gray-100 p-3">
            <p className="text-xs uppercase tracking-wide text-gray-500">vin</p>
            <p className="text-sm font-medium text-gray-900">{vehicle.vin || '-'}</p>
          </div>
          <div className="flex items-center justify-between rounded-lg border border-gray-100 p-3">
            <p className="text-xs uppercase tracking-wide text-gray-500">company_uuid</p>
            <p className="text-sm font-medium text-gray-900 break-all text-right">{vehicle.company_uuid ?? 'null'}</p>
          </div>
          <div className="flex items-center justify-between rounded-lg border border-gray-100 p-3">
            <p className="text-xs uppercase tracking-wide text-gray-500">vendor_uuid</p>
            <p className="text-sm font-medium text-gray-900 break-all text-right">{vehicle.vendor_uuid ?? 'null'}</p>
          </div>
          <div className="flex items-center justify-between rounded-lg border border-gray-100 p-3">
            <p className="text-xs uppercase tracking-wide text-gray-500">latitude</p>
            <p className="text-sm font-medium text-gray-900">{vehicle.latitude ?? '—'}</p>
          </div>
          <div className="flex items-center justify-between rounded-lg border border-gray-100 p-3">
            <p className="text-xs uppercase tracking-wide text-gray-500">longitude</p>
            <p className="text-sm font-medium text-gray-900">{vehicle.longitude ?? '—'}</p>
          </div>
          <div className="flex items-center justify-between rounded-lg border border-gray-100 p-3">
            <p className="text-xs uppercase tracking-wide text-gray-500">meta.color</p>
            <p className="text-sm font-medium text-gray-900">{vehicle.meta?.color != null ? String(vehicle.meta.color) : '-'}</p>
          </div>
          <div className="flex items-center justify-between rounded-lg border border-gray-100 p-3">
            <p className="text-xs uppercase tracking-wide text-gray-500">meta.notes</p>
            <p className="text-sm font-medium text-gray-900">{vehicle.meta?.notes != null ? String(vehicle.meta.notes) : '-'}</p>
          </div>
          <div className="flex items-center justify-between rounded-lg border border-gray-100 p-3">
            <p className="text-xs uppercase tracking-wide text-gray-500">updated_at</p>
            <p className="text-sm font-medium text-gray-900">{vehicle.updated_at ?? '-'}</p>
          </div>
          <div className="flex items-center justify-between rounded-lg border border-gray-100 p-3">
            <p className="text-xs uppercase tracking-wide text-gray-500">assigned_driver</p>
            <p className="text-sm font-medium text-gray-900 break-all text-right">
              {assignedDriver ? (
                <EntityLink
                  id={assignedDriver.id}
                  label={`${assignedDriver.name || assignedDriver.id}${assignedDriver.drivers_license_number ? ` — ${assignedDriver.drivers_license_number}` : ''}`}
                  to="/fleet/drivers"
                  className="text-blue-600 hover:underline"
                  title="View Driver"
                />
              ) : (
                'none'
              )}
            </p>
          </div>
        </div>
      </div>

      <div className="bg-white rounded-xl border border-gray-200 p-6">
        <h3 className="font-semibold text-gray-900 mb-4">Quick Actions</h3>
        <Link
          to="/fleet/fuel-reports"
          className="inline-flex items-center px-4 py-2 border border-gray-200 text-gray-700 rounded-lg hover:bg-gray-50 transition text-sm font-medium"
          title="Open fuel reports and add a report from the list"
        >
          <Fuel size={14} className="inline mr-1" />
          Log Fuel Report
        </Link>
      </div>
    </div>
  );
};

export default VehicleDetail;
