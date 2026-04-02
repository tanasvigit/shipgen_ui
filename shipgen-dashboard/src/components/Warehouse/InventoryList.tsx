import React, { useState, useEffect } from 'react';
import { Package, Search, Plus, Eye, AlertCircle } from 'lucide-react';
import { apiClient, ApiResponse } from '../../services/apiClient';
import { Link } from 'react-router-dom';

interface Inventory {
  id: string;
  sku: string;
  name: string;
  quantity: number;
  unit: string;
  binId: string;
  bin: {
    name: string;
    rack: {
      name: string;
      zone: {
        name: string;
        warehouse: { name: string };
      };
    };
  };
}

const InventoryList: React.FC = () => {
  const [inventory, setInventory] = useState<Inventory[]>([]);
  const [warehouses, setWarehouses] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [warehouseFilter, setWarehouseFilter] = useState<string>('all');
  const [searchTerm, setSearchTerm] = useState('');
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);

  useEffect(() => {
    loadWarehouses();
    loadInventory();
  }, [page, warehouseFilter]);

  const loadWarehouses = async () => {
    try {
      const response = await apiClient.get('/warehouses', { page: 1, pageSize: 100 });
      setWarehouses(response.data || []);
    } catch (err) {
      // Ignore
    }
  };

  const loadInventory = async () => {
    try {
      setLoading(true);
      setError(null);
      const params: any = { page, pageSize: 20 };
      if (warehouseFilter !== 'all') {
        params.warehouseId = warehouseFilter;
      }
      const response = await apiClient.get<ApiResponse<Inventory[]>>('/inventory', params);
      setInventory(response.data);
      setTotalPages(Math.ceil((response.pagination?.total || 0) / 20));
      setLoading(false);
    } catch (err: any) {
      setError(err.message || 'Failed to load inventory');
      setLoading(false);
    }
  };

  const filteredInventory = inventory.filter(inv =>
    inv.sku.toLowerCase().includes(searchTerm.toLowerCase()) ||
    inv.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    inv.bin.name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Inventory</h1>
          <p className="text-sm text-gray-600 mt-1">Bin-level inventory tracking</p>
        </div>
        <Link
          to="/warehouse/inventory/grn"
          className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
        >
          <Plus size={18} />
          <span>Process GRN</span>
        </Link>
      </div>

      <div className="flex flex-col sm:flex-row gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={18} />
          <input
            type="text"
            placeholder="Search SKU, name, bin..."
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
        <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
          {filteredInventory.length === 0 ? (
            <div className="p-12 text-center">
              <Package size={48} className="mx-auto text-gray-300 mb-4" />
              <p className="text-gray-600">No inventory found</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50 border-b border-gray-200">
                  <tr>
                    <th className="text-left py-3 px-4 text-xs font-semibold text-gray-600 uppercase">SKU</th>
                    <th className="text-left py-3 px-4 text-xs font-semibold text-gray-600 uppercase">Name</th>
                    <th className="text-left py-3 px-4 text-xs font-semibold text-gray-600 uppercase">Location</th>
                    <th className="text-right py-3 px-4 text-xs font-semibold text-gray-600 uppercase">Quantity</th>
                    <th className="text-left py-3 px-4 text-xs font-semibold text-gray-600 uppercase">Unit</th>
                    <th className="text-right py-3 px-4 text-xs font-semibold text-gray-600 uppercase">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-100">
                  {filteredInventory.map((inv) => (
                    <tr key={inv.id} className="hover:bg-gray-50">
                      <td className="py-3 px-4">
                        <span className="text-sm font-medium text-gray-900">{inv.sku}</span>
                      </td>
                      <td className="py-3 px-4">
                        <span className="text-sm text-gray-700">{inv.name}</span>
                      </td>
                      <td className="py-3 px-4">
                        <div className="text-xs text-gray-600">
                          {inv.bin.zone.warehouse.name} → {inv.bin.zone.name} → {inv.bin.rack.name} → {inv.bin.name}
                        </div>
                      </td>
                      <td className="py-3 px-4 text-right">
                        <span className="text-sm font-semibold text-gray-900">{inv.quantity}</span>
                      </td>
                      <td className="py-3 px-4">
                        <span className="text-xs text-gray-600">{inv.unit}</span>
                      </td>
                      <td className="py-3 px-4">
                        <div className="flex items-center justify-end">
                          <Link
                            to={`/warehouse/inventory/${inv.id}`}
                            className="p-2 text-gray-600 hover:bg-gray-100 rounded-lg transition"
                          >
                            <Eye size={16} />
                          </Link>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      {totalPages > 1 && (
        <div className="flex items-center justify-center space-x-2">
          <button
            onClick={() => setPage(p => Math.max(1, p - 1))}
            disabled={page === 1}
            className="px-4 py-2 border border-gray-200 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
          >
            Previous
          </button>
          <span className="px-4 py-2 text-sm text-gray-600">
            Page {page} of {totalPages}
          </span>
          <button
            onClick={() => setPage(p => Math.min(totalPages, p + 1))}
            disabled={page === totalPages}
            className="px-4 py-2 border border-gray-200 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
          >
            Next
          </button>
        </div>
      )}
    </div>
  );
};

export default InventoryList;
