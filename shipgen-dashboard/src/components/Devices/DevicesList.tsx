import React, { useEffect, useMemo, useState } from 'react';
import { AlertCircle, Cpu, Search } from 'lucide-react';
import { devicesService, type UiDevice } from '../../services/devicesService';
import RouteDetailsModal from '../common/RouteDetailsModal';

const DevicesList: React.FC = () => {
  const [devices, setDevices] = useState<UiDevice[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [isDetailsOpen, setIsDetailsOpen] = useState(false);

  useEffect(() => {
    const load = async () => {
      try {
        setLoading(true);
        setError(null);
        const rows = await devicesService.list({ limit: 100, offset: 0 });
        setDevices(rows);
      } catch (err: unknown) {
        setError(err instanceof Error ? err.message : 'Failed to load devices');
      } finally {
        setLoading(false);
      }
    };
    load();
  }, []);

  const filtered = useMemo(() => {
    const q = searchTerm.trim().toLowerCase();
    if (!q) return devices;
    return devices.filter((d) => d.name.toLowerCase().includes(q));
  }, [devices, searchTerm]);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Devices</h1>
        <p className="text-sm text-gray-600 mt-1">Device registry from `/int/v1/devices`</p>
      </div>

      <div className="relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={18} />
        <input
          type="text"
          placeholder="Search by device name..."
          className="w-full pl-10 pr-4 py-2 bg-white border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
        />
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg flex items-center gap-2">
          <AlertCircle size={18} />
          <span>{error}</span>
        </div>
      )}

      {loading ? (
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600" />
        </div>
      ) : (
        <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
          {filtered.length === 0 ? (
            <div className="p-12 text-center">
              <Cpu size={48} className="mx-auto text-gray-300 mb-4" />
              <p className="text-gray-600">No devices found</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50 border-b border-gray-200">
                  <tr>
                    <th className="text-left py-3 px-4 text-xs font-semibold text-gray-600 uppercase">name</th>
                    <th className="text-left py-3 px-4 text-xs font-semibold text-gray-600 uppercase">status</th>
                    <th className="text-left py-3 px-4 text-xs font-semibold text-gray-600 uppercase">last_seen</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-100">
                  {filtered.map((device) => (
                    <tr
                      key={device.id}
                      className="hover:bg-gray-50 cursor-pointer"
                      onClick={() => {
                        setSelectedId(device.id);
                        setIsDetailsOpen(true);
                      }}
                    >
                      <td className="py-3 px-4 text-sm font-medium text-gray-900">{device.name || '—'}</td>
                      <td className="py-3 px-4 text-sm text-gray-700">{device.status || device.connection_status || '—'}</td>
                      <td className="py-3 px-4 text-sm text-gray-700">
                        {device.last_seen ? new Date(device.last_seen).toLocaleString() : '—'}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}
      <RouteDetailsModal
        isOpen={isDetailsOpen}
        onClose={() => setIsDetailsOpen(false)}
        title="Device Details"
        routePath={selectedId ? `/analytics/devices/${encodeURIComponent(selectedId)}` : null}
        headerTitle="Device Details"
        headerSubtitle={selectedId ?? undefined}
      />
    </div>
  );
};

export default DevicesList;
