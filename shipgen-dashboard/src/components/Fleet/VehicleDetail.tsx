import React, { useState, useEffect } from 'react';
import { useParams, Link, useLocation } from 'react-router-dom';
import { ArrowLeft, AlertCircle, Fuel, Pencil, Trash2 } from 'lucide-react';
import { driversService, type UiDriver } from '../../services/driversService';
import { vehiclesService, type UiVehicle } from '../../services/vehiclesService';
import { canManageDriverVehicleMasterData, getStoredUserRole } from '../../utils/roleAccess';
import { UserRole } from '../../types';

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
            <p className="text-sm text-gray-600 mt-1">{vehicle.id}</p>
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

      <div className="bg-white rounded-xl border border-gray-200 p-6">
        <h2 className="text-lg font-bold text-gray-900 mb-4">Vehicle Information</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div><label className="text-xs text-gray-500 uppercase">id</label><p className="text-sm font-medium">{vehicle.id}</p></div>
          <div><label className="text-xs text-gray-500 uppercase">plate_number</label><p className="text-sm font-medium">{vehicle.plate_number}</p></div>
          <div><label className="text-xs text-gray-500 uppercase">make</label><p className="text-sm font-medium">{vehicle.make}</p></div>
          <div><label className="text-xs text-gray-500 uppercase">model</label><p className="text-sm font-medium">{vehicle.model}</p></div>
          <div><label className="text-xs text-gray-500 uppercase">year</label><p className="text-sm font-medium">{vehicle.year}</p></div>
          <div><label className="text-xs text-gray-500 uppercase">trim</label><p className="text-sm font-medium">{vehicle.trim}</p></div>
          <div><label className="text-xs text-gray-500 uppercase">type</label><p className="text-sm font-medium">{vehicle.type}</p></div>
          <div><label className="text-xs text-gray-500 uppercase">vin</label><p className="text-sm font-medium">{vehicle.vin}</p></div>
          <div><label className="text-xs text-gray-500 uppercase">status</label><p className="text-sm font-medium">{vehicle.status}</p></div>
          <div><label className="text-xs text-gray-500 uppercase">company_uuid</label><p className="text-sm font-medium break-all">{vehicle.company_uuid ?? 'null'}</p></div>
          <div><label className="text-xs text-gray-500 uppercase">vendor_uuid</label><p className="text-sm font-medium break-all">{vehicle.vendor_uuid ?? 'null'}</p></div>
          <div><label className="text-xs text-gray-500 uppercase">latitude</label><p className="text-sm font-medium">{vehicle.latitude ?? '—'}</p></div>
          <div><label className="text-xs text-gray-500 uppercase">longitude</label><p className="text-sm font-medium">{vehicle.longitude ?? '—'}</p></div>
          <div><label className="text-xs text-gray-500 uppercase">meta.color</label><p className="text-sm font-medium">{vehicle.meta?.color != null ? String(vehicle.meta.color) : '-'}</p></div>
          <div><label className="text-xs text-gray-500 uppercase">meta.notes</label><p className="text-sm font-medium">{vehicle.meta?.notes != null ? String(vehicle.meta.notes) : '-'}</p></div>
          <div><label className="text-xs text-gray-500 uppercase">updated_at</label><p className="text-sm font-medium">{vehicle.updated_at ?? '-'}</p></div>
          <div>
            <label className="text-xs text-gray-500 uppercase">assigned_driver (driver.vehicle_uuid)</label>
            <p className="text-sm font-medium break-all">
              {assignedDriver ? (
                <Link to={`/fleet/drivers/${encodeURIComponent(assignedDriver.id)}`} className="text-blue-600 hover:underline">
                  {assignedDriver.id} — {assignedDriver.drivers_license_number || 'no license'}
                </Link>
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
