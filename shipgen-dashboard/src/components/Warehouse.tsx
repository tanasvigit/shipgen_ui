import React, { useState, useEffect } from 'react';
import { 
  Package, Layers, Database, AlertCircle, QrCode, ArrowUpRight, ArrowDownLeft, 
  Plus, History, BarChart2, MapPin, Loader2, X, ArrowRightLeft
} from 'lucide-react';
import { apiClient, ApiResponse } from '../services/apiClient';
import { Warehouse } from '../types';

interface BackendWarehouse {
  id: string;
  name: string;
  location: string;
  capacity: number;
  occupancy: number;
  companyId: string;
  createdAt: string;
  updatedAt: string;
}

interface BackendInventory {
  id: string;
  sku: string;
  name: string | null;
  quantity: number;
  unit: string;
  binId: string;
  bin: {
    code: string;
    rack: {
      name: string;
      zone: {
        name: string;
        type: string | null;
        warehouse: {
          id: string;
          name: string;
        };
      };
    };
  };
  lastUpdated: string;
}

interface Zone {
  id: string;
  name: string;
  type: string | null;
  racks: Array<{
    id: string;
    name: string;
    bins: Array<{
      id: string;
      code: string;
    }>;
  }>;
}

const WarehouseModule: React.FC = () => {
  const [warehouses, setWarehouses] = useState<Warehouse[]>([]);
  const [selectedWH, setSelectedWH] = useState<Warehouse | null>(null);
  const [inventory, setInventory] = useState<BackendInventory[]>([]);
  const [zones, setZones] = useState<Zone[]>([]);
  const [isGrnModalOpen, setIsGrnModalOpen] = useState(false);
  const [isOutwardModalOpen, setIsOutwardModalOpen] = useState(false);
  const [isTransferModalOpen, setIsTransferModalOpen] = useState(false);
  const [loading, setLoading] = useState(true);
  const [inventoryLoading, setInventoryLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedInventory, setSelectedInventory] = useState<BackendInventory | null>(null);

  useEffect(() => {
    const fetchWarehouses = async () => {
      try {
        setLoading(true);
        setError(null);
        const response = await apiClient.get<ApiResponse<BackendWarehouse[]>>('/warehouses', { page: 1, pageSize: 100 });
        const mapped: Warehouse[] = response.data.map(wh => ({
          id: wh.id,
          company_id: wh.companyId,
          name: wh.name,
          location: wh.location,
          total_capacity: wh.capacity,
          occupancy: wh.occupancy,
          zones: []
        }));
        setWarehouses(mapped);
        if (mapped.length > 0) setSelectedWH(mapped[0]);
      } catch (err: any) {
        setError(err.message || 'Failed to load warehouses');
      } finally {
        setLoading(false);
      }
    };
    fetchWarehouses();
  }, []);

  useEffect(() => {
    if (selectedWH) {
      const fetchData = async () => {
        try {
          setInventoryLoading(true);
          const [inventoryRes, zonesRes] = await Promise.all([
            apiClient.get<ApiResponse<BackendInventory[]>>('/inventory', { warehouseId: selectedWH.id, page: 1, pageSize: 100 }),
            apiClient.get<Zone[]>(`/zones/warehouse/${selectedWH.id}`)
          ]);
          setInventory(inventoryRes.data);
          setZones(zonesRes);
        } catch (err: any) {
          setError(err.message || 'Failed to load inventory');
        } finally {
          setInventoryLoading(false);
        }
      };
      fetchData();
    }
  }, [selectedWH]);

  const handleGRN = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (!selectedWH) return;
    const formData = new FormData(e.currentTarget);
    
    try {
      const bins = zones.flatMap(z => z.racks.flatMap(r => r.bins));
      const binId = bins.find(b => b.code === formData.get('binCode'))?.id;
      if (!binId) {
        setError('Bin not found');
        return;
      }

      await apiClient.post('/wms/grn', {
        warehouseId: selectedWH.id,
        binId,
        sku: formData.get('sku') as string,
        name: formData.get('name') as string,
        quantity: Number(formData.get('quantity')),
        unit: formData.get('unit') as string,
        notes: formData.get('notes') as string || undefined
      });

      // Refresh inventory
      const inventoryRes = await apiClient.get<ApiResponse<BackendInventory[]>>('/inventory', { warehouseId: selectedWH.id, page: 1, pageSize: 100 });
      setInventory(inventoryRes.data);
      setIsGrnModalOpen(false);
      setError(null);
    } catch (err: any) {
      setError(err.message || 'Failed to create GRN');
    }
  };

  const handleOutward = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (!selectedInventory) return;
    
    try {
      const formData = new FormData(e.currentTarget);
      await apiClient.post('/inventory/outward', {
        inventoryId: selectedInventory.id,
        quantity: Number(formData.get('quantity')),
        notes: formData.get('notes') as string || undefined
      });

      // Refresh inventory
      const inventoryRes = await apiClient.get<ApiResponse<BackendInventory[]>>('/inventory', { warehouseId: selectedWH!.id, page: 1, pageSize: 100 });
      setInventory(inventoryRes.data);
      setIsOutwardModalOpen(false);
      setSelectedInventory(null);
      setError(null);
    } catch (err: any) {
      setError(err.message || 'Failed to process outward');
    }
  };

  const handleTransfer = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (!selectedInventory) return;
    
    try {
      const formData = new FormData(e.currentTarget);
      const bins = zones.flatMap(z => z.racks.flatMap(r => r.bins));
      const toBinId = bins.find(b => b.code === formData.get('toBinCode'))?.id;
      if (!toBinId) {
        setError('Target bin not found');
        return;
      }

      await apiClient.post('/inventory/transfer', {
        inventoryId: selectedInventory.id,
        toBinId,
        quantity: Number(formData.get('quantity')),
        notes: formData.get('notes') as string || undefined
      });

      // Refresh inventory
      const inventoryRes = await apiClient.get<ApiResponse<BackendInventory[]>>('/inventory', { warehouseId: selectedWH!.id, page: 1, pageSize: 100 });
      setInventory(inventoryRes.data);
      setIsTransferModalOpen(false);
      setSelectedInventory(null);
      setError(null);
    } catch (err: any) {
      setError(err.message || 'Failed to transfer inventory');
    }
  };

  const bins = zones.flatMap(z => z.racks.flatMap(r => r.bins.map(b => ({ ...b, zone: z.name, rack: r.name }))));

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Warehouse Control Center</h1>
          <p className="text-sm text-gray-500">Real-time inventory and yard management</p>
        </div>
        <div className="flex items-center space-x-2">
           <button 
             onClick={() => setIsGrnModalOpen(true)}
             className="flex items-center px-4 py-2 bg-primary-600 text-white rounded-lg text-sm font-medium hover:bg-primary-700 shadow-md"
           >
             <Plus size={18} className="mr-2" />
             Inward Stock (GRN)
           </button>
        </div>
      </div>

      {loading && (
        <div className="flex items-center justify-center p-12">
          <Loader2 className="animate-spin text-primary-600" size={32} />
        </div>
      )}
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-xl">
          {error}
        </div>
      )}
      {!loading && !error && (
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Warehouse Sidebar */}
          <div className="space-y-4">
            <h3 className="text-[10px] font-bold text-gray-400 uppercase tracking-widest px-2">Facility Network</h3>
            <div className="space-y-2">
              {warehouses.map(wh => (
                <div 
                  key={wh.id} 
                  onClick={() => setSelectedWH(wh)}
                  className={`p-4 rounded-2xl cursor-pointer border transition-all ${selectedWH?.id === wh.id ? 'border-primary-600 bg-primary-600 text-white shadow-lg' : 'border-gray-100 bg-white hover:border-primary-200'}`}
                >
                  <div className="flex items-center justify-between mb-1">
                    <span className="font-bold text-sm">{wh.name}</span>
                    <Database size={14} className={selectedWH?.id === wh.id ? 'text-primary-100' : 'text-gray-300'} />
                  </div>
                  <div className={`flex items-center text-[10px] ${selectedWH?.id === wh.id ? 'text-primary-100' : 'text-gray-400'}`}>
                    <MapPin size={10} className="mr-1" />
                    <span>{wh.location}</span>
                  </div>
                  <div className="mt-3 w-full bg-black/10 rounded-full h-1">
                    <div 
                      className={`h-1 rounded-full ${selectedWH?.id === wh.id ? 'bg-white' : 'bg-primary-500'}`}
                      style={{ width: `${(wh.occupancy / wh.total_capacity) * 100}%` }}
                    ></div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Main Content Area */}
          <div className="lg:col-span-3 space-y-6">
            {selectedWH ? (
              <>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="bg-white p-6 rounded-2xl border border-gray-100 shadow-sm flex items-center">
                    <div className="p-3 bg-emerald-50 text-emerald-600 rounded-xl mr-4"><ArrowDownLeft size={24}/></div>
                    <div>
                      <p className="text-[10px] font-bold text-gray-400 uppercase">Total SKUs</p>
                      <h4 className="text-xl font-bold">{inventory.length} <small className="text-xs font-normal text-gray-500">items</small></h4>
                    </div>
                  </div>
                  <div className="bg-white p-6 rounded-2xl border border-gray-100 shadow-sm flex items-center">
                    <div className="p-3 bg-primary-50 text-primary-600 rounded-xl mr-4"><ArrowUpRight size={24}/></div>
                    <div>
                      <p className="text-[10px] font-bold text-gray-400 uppercase">Total Quantity</p>
                      <h4 className="text-xl font-bold">{inventory.reduce((sum, inv) => sum + inv.quantity, 0)} <small className="text-xs font-normal text-gray-500">units</small></h4>
                    </div>
                  </div>
                  <div className="bg-white p-6 rounded-2xl border border-gray-100 shadow-sm flex items-center">
                    <div className="p-3 bg-amber-50 text-amber-600 rounded-xl mr-4"><AlertCircle size={24}/></div>
                    <div>
                      <p className="text-[10px] font-bold text-gray-400 uppercase">Low Stock</p>
                      <h4 className="text-xl font-bold text-amber-600">{inventory.filter(inv => inv.quantity < 10).length} <small className="text-xs font-normal text-gray-500">SKUs</small></h4>
                    </div>
                  </div>
                </div>

                <div className="bg-white rounded-3xl border border-gray-100 shadow-sm overflow-hidden">
                  <div className="p-6 border-b border-gray-100 flex items-center justify-between bg-gray-50/30">
                    <div className="flex items-center space-x-2">
                      <Layers size={20} className="text-primary-600" />
                      <h3 className="font-bold text-gray-900">Live Inventory List</h3>
                    </div>
                    <div className="flex items-center space-x-2">
                      <button className="p-2 border border-gray-200 rounded-lg bg-white" aria-label="Scan inventory QR"><QrCode size={16}/></button>
                      <button className="p-2 border border-gray-200 rounded-lg bg-white" aria-label="Open inventory history"><History size={16}/></button>
                    </div>
                  </div>
                  {inventoryLoading ? (
                    <div className="flex items-center justify-center p-12">
                      <Loader2 className="animate-spin text-primary-600" size={24} />
                    </div>
                  ) : inventory.length === 0 ? (
                    <div className="p-12 text-center text-gray-400">
                      <Package size={48} className="mx-auto mb-4 opacity-20" />
                      <p>No inventory found</p>
                    </div>
                  ) : (
                    <div className="overflow-x-auto">
                      <table className="w-full text-left">
                        <thead>
                          <tr className="text-[10px] font-bold text-gray-400 uppercase tracking-wider border-b border-gray-50">
                            <th className="px-6 py-4">SKU / Item Name</th>
                            <th className="px-6 py-4">Bin Location</th>
                            <th className="px-6 py-4">Quantity</th>
                            <th className="px-6 py-4">Last Updated</th>
                            <th className="px-6 py-4">Actions</th>
                          </tr>
                        </thead>
                        <tbody className="divide-y divide-gray-50">
                          {inventory.map(item => (
                            <tr key={item.id} className="hover:bg-gray-50/50 transition-colors">
                              <td className="px-6 py-4">
                                <p className="text-sm font-bold text-gray-900">{item.name || item.sku}</p>
                                <p className="text-xs text-primary-600 font-mono uppercase">{item.sku}</p>
                              </td>
                              <td className="px-6 py-4">
                                <div className="flex flex-col">
                                  <span className="text-xs text-gray-600">{item.bin.rack.zone.name}</span>
                                  <span className="text-[10px] font-bold bg-gray-100 text-gray-600 px-2 py-0.5 rounded uppercase">
                                    {item.bin.code}
                                  </span>
                                </div>
                              </td>
                              <td className="px-6 py-4">
                                <p className="text-sm font-bold text-gray-900">{item.quantity} <small className="text-gray-400 font-normal uppercase">{item.unit}</small></p>
                              </td>
                              <td className="px-6 py-4 text-xs text-gray-500">
                                {new Date(item.lastUpdated).toLocaleDateString()}
                              </td>
                              <td className="px-6 py-4">
                                <div className="flex space-x-2">
                                  <button
                                    onClick={() => { setSelectedInventory(item); setIsOutwardModalOpen(true); }}
                                    className="px-2 py-1 text-xs bg-red-50 text-red-600 rounded hover:bg-red-100"
                                  >
                                    Outward
                                  </button>
                                  <button
                                    onClick={() => { setSelectedInventory(item); setIsTransferModalOpen(true); }}
                                    className="px-2 py-1 text-xs bg-primary-50 text-primary-600 rounded hover:bg-primary-100"
                                  >
                                    Transfer
                                  </button>
                                </div>
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  )}
                </div>
              </>
            ) : (
              <div className="h-full flex items-center justify-center bg-gray-50 rounded-3xl border-2 border-dashed border-gray-200 p-12 text-center">
                <div>
                  <Database size={48} className="mx-auto text-gray-200 mb-4" />
                  <p className="text-gray-400">Select a warehouse to view operations</p>
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* GRN Modal */}
      {isGrnModalOpen && selectedWH && (
        <div className="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-black/60 backdrop-blur-md">
          <div className="bg-white w-full max-w-lg rounded-3xl overflow-hidden shadow-2xl">
            <div className="p-6 border-b border-gray-100 flex items-center justify-between">
              <h2 className="text-xl font-bold text-gray-900">Inward Stock (GRN)</h2>
              <button onClick={() => setIsGrnModalOpen(false)} className="p-2 hover:bg-gray-100 rounded-full transition-colors" aria-label="Close GRN modal">
                <X size={24} />
              </button>
            </div>
            <form onSubmit={handleGRN} className="p-6 space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="col-span-2">
                  <label className="block text-xs font-bold text-gray-400 uppercase mb-2">Item Name</label>
                  <input name="name" required className="input-base" placeholder="e.g. Lithium Batteries" />
                </div>
                <div>
                  <label className="block text-xs font-bold text-gray-400 uppercase mb-2">SKU Code</label>
                  <input name="sku" required className="input-base font-mono" placeholder="SKU-XXX" />
                </div>
                <div>
                  <label className="block text-xs font-bold text-gray-400 uppercase mb-2">Quantity</label>
                  <input name="quantity" type="number" required min="1" className="input-base" placeholder="0" />
                </div>
                <div>
                  <label className="block text-xs font-bold text-gray-400 uppercase mb-2">Unit</label>
                  <select name="unit" className="select-base">
                    <option>pcs</option>
                    <option>kg</option>
                    <option>liters</option>
                    <option>boxes</option>
                  </select>
                </div>
                <div className="col-span-2">
                  <label className="block text-xs font-bold text-gray-400 uppercase mb-2">Bin Code</label>
                  <select name="binCode" required className="select-base">
                    <option value="">Select Bin</option>
                    {bins.map(bin => (
                      <option key={bin.id} value={bin.code}>{bin.code} ({bin.zone} - {bin.rack})</option>
                    ))}
                  </select>
                </div>
                <div className="col-span-2">
                  <label className="block text-xs font-bold text-gray-400 uppercase mb-2">Notes (Optional)</label>
                  <textarea name="notes" className="textarea-base" rows={2} />
                </div>
              </div>
              <div className="pt-4">
                <button type="submit" className="w-full py-4 bg-primary-600 text-white rounded-2xl font-bold shadow-lg hover:bg-primary-700 transition">
                  Confirm & Log Transaction
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Outward Modal */}
      {isOutwardModalOpen && selectedInventory && (
        <div className="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-black/60 backdrop-blur-md">
          <div className="bg-white w-full max-w-lg rounded-3xl overflow-hidden shadow-2xl">
            <div className="p-6 border-b border-gray-100 flex items-center justify-between">
              <h2 className="text-xl font-bold text-gray-900">Outward Movement</h2>
              <button onClick={() => { setIsOutwardModalOpen(false); setSelectedInventory(null); }} className="p-2 hover:bg-gray-100 rounded-full transition-colors" aria-label="Close outward modal">
                <X size={24} />
              </button>
            </div>
            <form onSubmit={handleOutward} className="p-6 space-y-4">
              <div className="bg-gray-50 p-4 rounded-xl">
                <p className="text-xs text-gray-500 mb-1">SKU</p>
                <p className="font-bold">{selectedInventory.sku}</p>
                <p className="text-xs text-gray-500 mt-2 mb-1">Available Quantity</p>
                <p className="font-bold text-primary-600">{selectedInventory.quantity} {selectedInventory.unit}</p>
              </div>
              <div>
                <label className="block text-xs font-bold text-gray-400 uppercase mb-2">Quantity</label>
                <input name="quantity" type="number" required min="1" max={selectedInventory.quantity} className="input-base" />
              </div>
              <div>
                <label className="block text-xs font-bold text-gray-400 uppercase mb-2">Notes (Optional)</label>
                <textarea name="notes" className="textarea-base" rows={2} />
              </div>
              <div className="pt-4">
                <button type="submit" className="w-full py-4 bg-red-600 text-white rounded-2xl font-bold shadow-lg shadow-red-200 hover:bg-red-700 transition">
                  Confirm Outward
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Transfer Modal */}
      {isTransferModalOpen && selectedInventory && (
        <div className="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-black/60 backdrop-blur-md">
          <div className="bg-white w-full max-w-lg rounded-3xl overflow-hidden shadow-2xl">
            <div className="p-6 border-b border-gray-100 flex items-center justify-between">
              <h2 className="text-xl font-bold text-gray-900">Transfer Inventory</h2>
              <button onClick={() => { setIsTransferModalOpen(false); setSelectedInventory(null); }} className="p-2 hover:bg-gray-100 rounded-full transition-colors" aria-label="Close transfer modal">
                <X size={24} />
              </button>
            </div>
            <form onSubmit={handleTransfer} className="p-6 space-y-4">
              <div className="bg-gray-50 p-4 rounded-xl">
                <p className="text-xs text-gray-500 mb-1">SKU</p>
                <p className="font-bold">{selectedInventory.sku}</p>
                <p className="text-xs text-gray-500 mt-2 mb-1">From Bin</p>
                <p className="font-bold">{selectedInventory.bin.code}</p>
                <p className="text-xs text-gray-500 mt-2 mb-1">Available Quantity</p>
                <p className="font-bold text-primary-600">{selectedInventory.quantity} {selectedInventory.unit}</p>
              </div>
              <div>
                <label className="block text-xs font-bold text-gray-400 uppercase mb-2">To Bin</label>
                <select name="toBinCode" required className="select-base">
                  <option value="">Select Target Bin</option>
                  {bins.filter(b => b.id !== selectedInventory.binId).map(bin => (
                    <option key={bin.id} value={bin.code}>{bin.code} ({bin.zone} - {bin.rack})</option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-xs font-bold text-gray-400 uppercase mb-2">Quantity</label>
                <input name="quantity" type="number" required min="1" max={selectedInventory.quantity} className="input-base" />
              </div>
              <div>
                <label className="block text-xs font-bold text-gray-400 uppercase mb-2">Notes (Optional)</label>
                <textarea name="notes" className="textarea-base" rows={2} />
              </div>
              <div className="pt-4">
                <button type="submit" className="w-full py-4 bg-primary-600 text-white rounded-2xl font-bold shadow-lg hover:bg-primary-700 transition">
                  Confirm Transfer
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default WarehouseModule;
