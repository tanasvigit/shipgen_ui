import React, { useEffect, useState } from 'react';
import { Link, useNavigate, useParams } from 'react-router-dom';
import { AlertCircle, ArrowLeft, HeartPulse, MapPin, Trash2 } from 'lucide-react';
import { devicesService, type UiDevice } from '../../services/devicesService';

const DeviceDetail: React.FC = () => {
  const navigate = useNavigate();
  const { id } = useParams<{ id: string }>();
  const [device, setDevice] = useState<UiDevice | null>(null);
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [latitude, setLatitude] = useState('');
  const [longitude, setLongitude] = useState('');

  useEffect(() => {
    const load = async () => {
      if (!id) return;
      try {
        setLoading(true);
        setError(null);
        const row = await devicesService.getById(id);
        setDevice(row);
        setLatitude(row.latitude || '');
        setLongitude(row.longitude || '');
      } catch (err: unknown) {
        setError(err instanceof Error ? err.message : 'Failed to load device');
      } finally {
        setLoading(false);
      }
    };
    load();
  }, [id]);

  const refresh = async () => {
    if (!id) return;
    const row = await devicesService.getById(id);
    setDevice(row);
  };

  const handleHeartbeat = async () => {
    if (!id) return;
    try {
      setBusy(true);
      setError(null);
      setSuccess(null);
      await devicesService.heartbeat(id);
      await refresh();
      setSuccess('Heartbeat sent.');
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Heartbeat failed');
    } finally {
      setBusy(false);
    }
  };

  const handleLocation = async () => {
    if (!id) return;
    const lat = Number(latitude);
    const lng = Number(longitude);
    if (!Number.isFinite(lat) || !Number.isFinite(lng)) {
      setError('Please enter valid latitude/longitude');
      return;
    }
    try {
      setBusy(true);
      setError(null);
      setSuccess(null);
      await devicesService.updateLocation(id, lat, lng);
      await refresh();
      setSuccess('Location updated.');
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Location update failed');
    } finally {
      setBusy(false);
    }
  };

  const handleDelete = async () => {
    if (!id) return;
    if (!window.confirm('Delete this device?')) return;
    try {
      setBusy(true);
      setError(null);
      await devicesService.remove(id);
      navigate('/analytics/devices');
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Delete failed');
      setBusy(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600" />
      </div>
    );
  }

  if (!device) {
    return <div className="text-gray-600">Device not found.</div>;
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <Link to="/analytics/devices" className="p-2 hover:bg-gray-100 rounded-lg transition">
            <ArrowLeft size={20} />
          </Link>
          <div>
            <h1 className="text-2xl font-bold text-gray-900">{device.name || 'Device'}</h1>
            <p className="text-sm text-gray-600 mt-1">{device.id}</p>
          </div>
        </div>
        <button
          type="button"
          onClick={handleDelete}
          disabled={busy}
          className="inline-flex items-center gap-2 px-4 py-2 border border-red-200 text-red-700 rounded-lg hover:bg-red-50 disabled:opacity-50 transition"
        >
          <Trash2 size={16} />
          <span>Delete</span>
        </button>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg flex items-center gap-2">
          <AlertCircle size={18} />
          <span>{error}</span>
        </div>
      )}
      {success && <div className="bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded-lg">{success}</div>}

      <div className="bg-white rounded-xl border border-gray-200 p-6 grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
        <div><span className="font-medium text-gray-700">name:</span> {device.name || '—'}</div>
        <div><span className="font-medium text-gray-700">device_id:</span> {device.device_id || '—'}</div>
        <div><span className="font-medium text-gray-700">status:</span> {device.status || '—'}</div>
        <div><span className="font-medium text-gray-700">connection_status:</span> {device.connection_status || '—'}</div>
        <div><span className="font-medium text-gray-700">last_seen:</span> {device.last_seen ? new Date(device.last_seen).toLocaleString() : '—'}</div>
        <div><span className="font-medium text-gray-700">latitude:</span> {device.latitude || '—'}</div>
        <div><span className="font-medium text-gray-700">longitude:</span> {device.longitude || '—'}</div>
      </div>

      <div className="bg-white rounded-xl border border-gray-200 p-6 space-y-4">
        <h2 className="text-lg font-bold text-gray-900">Basic Actions</h2>
        <div className="flex flex-wrap items-end gap-3">
          <button
            type="button"
            onClick={handleHeartbeat}
            disabled={busy}
            className="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 transition"
          >
            <HeartPulse size={16} />
            <span>Send Heartbeat</span>
          </button>
          <div>
            <label className="block text-xs text-gray-600 mb-1">latitude</label>
            <input
              type="text"
              value={latitude}
              onChange={(e) => setLatitude(e.target.value)}
              className="px-3 py-2 border border-gray-200 rounded-lg"
            />
          </div>
          <div>
            <label className="block text-xs text-gray-600 mb-1">longitude</label>
            <input
              type="text"
              value={longitude}
              onChange={(e) => setLongitude(e.target.value)}
              className="px-3 py-2 border border-gray-200 rounded-lg"
            />
          </div>
          <button
            type="button"
            onClick={handleLocation}
            disabled={busy}
            className="inline-flex items-center gap-2 px-4 py-2 border border-gray-200 text-gray-700 rounded-lg hover:bg-gray-50 disabled:opacity-50 transition"
          >
            <MapPin size={16} />
            <span>Update Location</span>
          </button>
        </div>
      </div>
    </div>
  );
};

export default DeviceDetail;
