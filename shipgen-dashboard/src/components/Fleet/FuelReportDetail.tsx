import React, { useEffect, useState } from 'react';
import { Link, useLocation, useNavigate, useParams } from 'react-router-dom';
import { AlertCircle, ArrowLeft, Edit, Trash2 } from 'lucide-react';
import { fuelReportsService } from '../../services/fuelReportsService';
import type { MockFuelReport } from '../../mocks/data/fuel_reports';
import { getFuelReportRouteId } from '../../utils/fuelReportHelpers';
import EntityLink from '../common/EntityLink';

const FuelReportDetail: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const isEmbedded = new URLSearchParams(location.search).get('embed') === '1';
  const { id } = useParams<{ id: string }>();
  const [fuel_report, setFuelReport] = useState<MockFuelReport | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [deleting, setDeleting] = useState(false);

  useEffect(() => {
    const loadFuelReport = async () => {
      if (!id) return;
      try {
        setLoading(true);
        setError(null);
        const response = await fuelReportsService.getById(id);
        setFuelReport(response);
      } catch (err: unknown) {
        setError(err instanceof Error ? err.message : 'Failed to load fuel report');
      } finally {
        setLoading(false);
      }
    };
    loadFuelReport();
  }, [id]);

  const onDelete = async () => {
    if (!fuel_report) return;
    const routeId = getFuelReportRouteId(fuel_report);
    if (!routeId) return;
    if (!window.confirm('Delete this fuel report?')) return;
    try {
      setDeleting(true);
      setError(null);
      await fuelReportsService.remove(routeId);
      navigate('/fleet/fuel-reports');
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to delete fuel report');
    } finally {
      setDeleting(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600" />
      </div>
    );
  }

  if (!fuel_report) {
    return <div className="text-gray-600">Fuel report not found.</div>;
  }

  const routeId = getFuelReportRouteId(fuel_report);

  return (
    <div className="space-y-6">
      {!isEmbedded ? (
        <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <Link to="/fleet/fuel-reports" className="p-2 hover:bg-gray-100 rounded-lg transition">
            <ArrowLeft size={20} />
          </Link>
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Fuel Report Detail</h1>
            <p className="text-sm text-gray-600 mt-1">{fuel_report.public_id ?? fuel_report.uuid ?? fuel_report.id}</p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          {!isEmbedded ? (
            <Link
              to="/fleet/fuel-reports"
              className="inline-flex items-center gap-2 px-4 py-2 border border-gray-200 text-gray-700 rounded-lg hover:bg-gray-50 transition"
              title="Open the fuel reports list and use Edit on a row"
            >
              <Edit size={16} />
              <span>Open list to edit</span>
            </Link>
          ) : null}
          <button
            type="button"
            onClick={onDelete}
            disabled={deleting}
            className="inline-flex items-center gap-2 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition disabled:opacity-50"
          >
            <Trash2 size={16} />
            <span>{deleting ? 'Deleting...' : 'Delete'}</span>
          </button>
        </div>
        </div>
      ) : null}

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg flex items-center space-x-2">
          <AlertCircle size={20} />
          <span>{error}</span>
        </div>
      )}

      <div className="bg-white rounded-xl border border-gray-200 p-6 grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
        <div><span className="font-medium text-gray-700">uuid:</span> <span className="font-mono">{fuel_report.uuid ?? '—'}</span></div>
        <div><span className="font-medium text-gray-700">public_id:</span> {fuel_report.public_id ?? '—'}</div>
        <div><span className="font-medium text-gray-700">driver_uuid:</span> <span className="font-mono"><EntityLink id={fuel_report.driver_uuid} label={fuel_report.driver_uuid} to="/fleet/drivers" title="View Driver" /></span></div>
        <div><span className="font-medium text-gray-700">vehicle_uuid:</span> <span className="font-mono"><EntityLink id={fuel_report.vehicle_uuid} label={fuel_report.vehicle_uuid} to="/fleet/vehicles" title="View Vehicle" /></span></div>
        <div><span className="font-medium text-gray-700">driver_name:</span> {fuel_report.driver_name ?? '—'}</div>
        <div><span className="font-medium text-gray-700">vehicle_name:</span> {fuel_report.vehicle_name ?? '—'}</div>
        <div><span className="font-medium text-gray-700">reported_by_uuid:</span> <span className="font-mono">{fuel_report.reported_by_uuid ?? '—'}</span></div>
        <div><span className="font-medium text-gray-700">reporter_name:</span> {fuel_report.reporter_name ?? '—'}</div>
        <div><span className="font-medium text-gray-700">odometer:</span> {fuel_report.odometer ?? '—'}</div>
        <div><span className="font-medium text-gray-700">volume:</span> {fuel_report.volume ?? '—'} {fuel_report.metric_unit ?? ''}</div>
        <div><span className="font-medium text-gray-700">amount:</span> {fuel_report.amount ?? '—'} {fuel_report.currency ?? ''}</div>
        <div><span className="font-medium text-gray-700">status:</span> {fuel_report.status ?? '—'}</div>
        <div className="md:col-span-2"><span className="font-medium text-gray-700">location:</span> <span className="font-mono">{JSON.stringify(fuel_report.location ?? null)}</span></div>
        <div className="md:col-span-2"><span className="font-medium text-gray-700">report:</span> {fuel_report.report ?? '—'}</div>
        <div className="md:col-span-2"><span className="font-medium text-gray-700">meta:</span> <span className="font-mono">{JSON.stringify(fuel_report.meta ?? null)}</span></div>
      </div>
    </div>
  );
};

export default FuelReportDetail;
