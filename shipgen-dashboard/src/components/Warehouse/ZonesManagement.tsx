import React, { useState, useEffect } from 'react';
import { Plus, Layers, Search, Warehouse, AlertCircle } from 'lucide-react';
import { apiClient, ApiResponse } from '../../services/apiClient';
import { Link } from 'react-router-dom';

interface Zone {
  id: string;
  warehouseId: string;
  name: string;
  type: string;
  capacity: number;
  occupied: number;
  warehouse: { name: string };
}

const ZonesManagement: React.FC = () => {
  const [zones, setZones] = useState<Zone[]>([]);
  const [warehouses, setWarehouses] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [warehouseFilter, setWarehouseFilter] = useState<string>('all');
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    loadWarehouses();
    loadZones();
  }, [warehouseFilter]);

  const loadWarehouses = async () => {
    try {
      const response = await apiClient.get('/warehouses', { page: 1, pageSize: 100 });
      setWarehouses(response.data || []);
    } catch (err) {
      // Ignore
    }
  };

  const loadZones = async () => {
    try {
      setLoading(true);
      setError(null);
      const params: any = { page: 1, pageSize: 100 };
      if (warehouseFilter !== 'all') {
        params.warehouseId = warehouseFilter;
      }
      const response = await apiClient.get<ApiResponse<Zone[]>>('/zones', params);
      setZones(response.data);
      setLoading(false);
    } catch (err: any) {
      setError(err.message || 'Failed to load zones');
      setLoading(false);
    }
  };

  const filteredZones = zones.filter(z =>
    z.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    z.type.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Zones Management</h1>
          <p className="text-sm text-gray-600 mt-1">Manage warehouse zones</p>
        </div>
        <button className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition">
          <Plus size={18} />
          <span>New Zone</span>
        </button>
      </div>

      <div className="flex flex-col sm:flex-row gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={18} />
          <input
            type="text"
            placeholder="Search zones..."
            className="w-full pl-10 pr-4 py-2 bg-white border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>
        <select
          value={warehouseFilter}
          onChange={(e) => setWarehouseFilter(e.target.value)}
          className="px-4 py-2 bg-white border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
        >
          <option value="all">All Warehouses</option>
          {warehouses.map((wh) => (
            <option key={wh.id} value={wh.id}>{wh.name}</option>
          ))}
        </select>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg flex items-center space-x-2">
          <AlertCircle size={20} />
          <span>{error}</span>
        </div>
      )}

      {loading ? (
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredZones.length === 0 ? (
            <div className="col-span-full text-center py-12">
              <Layers size={48} className="mx-auto text-gray-300 mb-4" />
              <p className="text-gray-600">No zones found</p>
            </div>
          ) : (
            filteredZones.map((zone) => (
              <div key={zone.id} className="bg-white rounded-xl border border-gray-200 p-6">
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center space-x-2">
                    <Layers size={20} className="text-purple-600" />
                    <h3 className="font-semibold text-gray-900">{zone.name}</h3>
                  </div>
                  <span className="px-2 py-1 bg-purple-100 text-purple-700 rounded-full text-xs font-medium">
                    {zone.type}
                  </span>
                </div>
                <div className="mb-2">
                  <p className="text-xs text-gray-600 mb-1">Warehouse</p>
                  <p className="text-sm font-medium text-gray-900">{zone.warehouse.name}</p>
                </div>
                <div className="mt-4">
                  <div className="flex items-center justify-between text-xs text-gray-600 mb-1">
                    <span>Utilization</span>
                    <span>{zone.occupied} / {zone.capacity}</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className={`h-2 rounded-full ${
                        (zone.occupied / zone.capacity) * 100 >= 90 ? 'bg-red-500' :
                        (zone.occupied / zone.capacity) * 100 >= 70 ? 'bg-orange-500' : 'bg-green-500'
                      }`}
                      style={{ width: `${Math.min(100, (zone.occupied / zone.capacity) * 100)}%` }}
                    />
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      )}
    </div>
  );
};

export default ZonesManagement;
