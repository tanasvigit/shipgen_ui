import React, { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { ArrowLeft, Save, AlertCircle, Package, Warehouse } from 'lucide-react';
import { apiClient } from '../../services/apiClient';

const GRNProcess: React.FC = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [warehouses, setWarehouses] = useState<any[]>([]);
  const [zones, setZones] = useState<any[]>([]);
  const [racks, setRacks] = useState<any[]>([]);
  const [bins, setBins] = useState<any[]>([]);
  const [formData, setFormData] = useState({
    warehouseId: '',
    zoneId: '',
    rackId: '',
    binId: '',
    sku: '',
    name: '',
    quantity: '',
    unit: 'pcs',
    vendorId: '',
    notes: ''
  });

  useEffect(() => {
    loadWarehouses();
  }, []);

  useEffect(() => {
    if (formData.warehouseId) {
      loadZones();
    }
  }, [formData.warehouseId]);

  useEffect(() => {
    if (formData.zoneId) {
      loadRacks();
    }
  }, [formData.zoneId]);

  useEffect(() => {
    if (formData.rackId) {
      loadBins();
    }
  }, [formData.rackId]);

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
      const response = await apiClient.get('/zones', { warehouseId: formData.warehouseId, page: 1, pageSize: 100 });
      setZones(response.data || []);
    } catch (err) {
      setZones([]);
    }
  };

  const loadRacks = async () => {
    try {
      const response = await apiClient.get('/racks', { zoneId: formData.zoneId, page: 1, pageSize: 100 });
      setRacks(response.data || []);
    } catch (err) {
      setRacks([]);
    }
  };

  const loadBins = async () => {
    try {
      const response = await apiClient.get('/bins', { rackId: formData.rackId, page: 1, pageSize: 100 });
      setBins(response.data || []);
    } catch (err) {
      setBins([]);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      setLoading(true);
      setError(null);
      const response = await apiClient.post('/wms/grn', {
        warehouseId: formData.warehouseId,
        binId: formData.binId,
        sku: formData.sku,
        name: formData.name || formData.sku,
        quantity: parseInt(formData.quantity),
        unit: formData.unit,
        vendorId: formData.vendorId || undefined,
        notes: formData.notes || undefined
      });
      navigate('/warehouse/inventory');
    } catch (err: any) {
      setError(err.message || 'Failed to process GRN');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center space-x-4">
        <Link
          to="/warehouse/inventory"
          className="p-2 hover:bg-gray-100 rounded-lg transition"
        >
          <ArrowLeft size={20} />
        </Link>
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Process GRN (Goods Receipt Note)</h1>
          <p className="text-sm text-gray-600 mt-1">Record incoming inventory</p>
        </div>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg flex items-center space-x-2">
          <AlertCircle size={20} />
          <span>{error}</span>
        </div>
      )}

      <form onSubmit={handleSubmit} className="bg-white rounded-xl border border-gray-200 p-6">
        <div className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2 flex items-center space-x-2">
                <Warehouse size={16} className="text-purple-500" />
                <span>Warehouse <span className="text-red-500">*</span></span>
              </label>
              <select
                required
                className="w-full px-4 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
                value={formData.warehouseId}
                onChange={(e) => setFormData({ ...formData, warehouseId: e.target.value, zoneId: '', rackId: '', binId: '' })}
              >
                <option value="">Select Warehouse</option>
                {warehouses.map((wh) => (
                  <option key={wh.id} value={wh.id}>{wh.name}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Zone <span className="text-red-500">*</span></label>
              <select
                required
                disabled={!formData.warehouseId}
                className="w-full px-4 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none disabled:bg-gray-100"
                value={formData.zoneId}
                onChange={(e) => setFormData({ ...formData, zoneId: e.target.value, rackId: '', binId: '' })}
              >
                <option value="">Select Zone</option>
                {zones.map((zone) => (
                  <option key={zone.id} value={zone.id}>{zone.name}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Rack <span className="text-red-500">*</span></label>
              <select
                required
                disabled={!formData.zoneId}
                className="w-full px-4 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none disabled:bg-gray-100"
                value={formData.rackId}
                onChange={(e) => setFormData({ ...formData, rackId: e.target.value, binId: '' })}
              >
                <option value="">Select Rack</option>
                {racks.map((rack) => (
                  <option key={rack.id} value={rack.id}>{rack.name}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Bin <span className="text-red-500">*</span></label>
              <select
                required
                disabled={!formData.rackId}
                className="w-full px-4 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none disabled:bg-gray-100"
                value={formData.binId}
                onChange={(e) => setFormData({ ...formData, binId: e.target.value })}
              >
                <option value="">Select Bin</option>
                {bins.map((bin) => (
                  <option key={bin.id} value={bin.id}>{bin.name}</option>
                ))}
              </select>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">SKU <span className="text-red-500">*</span></label>
              <input
                type="text"
                required
                className="w-full px-4 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
                value={formData.sku}
                onChange={(e) => setFormData({ ...formData, sku: e.target.value })}
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Product Name</label>
              <input
                type="text"
                className="w-full px-4 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Quantity <span className="text-red-500">*</span></label>
              <input
                type="number"
                required
                min="1"
                className="w-full px-4 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
                value={formData.quantity}
                onChange={(e) => setFormData({ ...formData, quantity: e.target.value })}
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Unit</label>
              <select
                className="w-full px-4 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
                value={formData.unit}
                onChange={(e) => setFormData({ ...formData, unit: e.target.value })}
              >
                <option value="pcs">Pieces</option>
                <option value="kg">Kilograms</option>
                <option value="ltr">Liters</option>
                <option value="box">Boxes</option>
              </select>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Notes</label>
            <textarea
              rows={3}
              className="w-full px-4 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
              value={formData.notes}
              onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
            />
          </div>

          <div className="flex items-center justify-end space-x-4 pt-4 border-t border-gray-200">
            <Link
              to="/warehouse/inventory"
              className="px-6 py-2 border border-gray-200 text-gray-700 rounded-lg hover:bg-gray-50 transition"
            >
              Cancel
            </Link>
            <button
              type="submit"
              disabled={loading}
              className="flex items-center space-x-2 px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition disabled:opacity-50"
            >
              <Save size={18} />
              <span>{loading ? 'Processing...' : 'Process GRN'}</span>
            </button>
          </div>
        </div>
      </form>
    </div>
  );
};

export default GRNProcess;
