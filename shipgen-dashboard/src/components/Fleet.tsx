import React, { useState, useEffect } from 'react';
import { Truck, User, MapPin, Activity, Battery, Fuel, Search, Filter, Loader2 } from 'lucide-react';
import { apiClient, ApiResponse } from '../services/apiClient';

interface BackendVehicle {
  id: string;
  plate_number: string;
  type: string;
  status: string;
  company_uuid: string | null;
  created_at: string;
  updated_at: string;
}

interface BackendDriver {
  id: string;
  drivers_license_number: string;
  status: string;
  company_uuid: string | null;
  user_uuid: string | null;
  created_at: string;
  updated_at: string;
}

const Fleet: React.FC = () => {
  const [vehicles, setVehicles] = useState<BackendVehicle[]>([]);
  const [drivers, setDrivers] = useState<BackendDriver[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        setError(null);
        const [vehiclesRes, driversRes] = await Promise.all([
          apiClient.get<ApiResponse<BackendVehicle[]>>('/vehicles', { page: 1, pageSize: 100 }),
          apiClient.get<ApiResponse<BackendDriver[]>>('/drivers', { page: 1, pageSize: 100 })
        ]);
        setVehicles(vehiclesRes.data);
        setDrivers(driversRes.data);
      } catch (err: any) {
        setError(err.message || 'Failed to load fleet data');
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  const activeVehicles = vehicles.filter(v => v.status === 'active').length;
  const activeDrivers = drivers.filter(d => d.status === 'active').length;
  const maintenanceVehicles = vehicles.filter(v => v.status === 'maintenance').length;

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Fleet Control Tower</h1>
          <p className="text-sm text-gray-500">Live telemetry and driver assignments</p>
        </div>
        <div className="flex space-x-2">
           <button className="px-4 py-2 border border-gray-200 rounded-lg text-sm font-medium bg-white hover:bg-gray-50">Fleet Analytics</button>
           <button className="px-4 py-2 bg-primary-600 text-white rounded-lg text-sm font-medium hover:bg-primary-700">+ Add Vehicle</button>
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
        <>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-emerald-50 border border-emerald-100 p-4 rounded-xl flex items-center">
               <div className="bg-emerald-500 p-3 rounded-lg text-white mr-4 shadow-md shadow-emerald-200">
                  <Activity size={20} />
               </div>
               <div>
                  <p className="text-xs text-emerald-600 font-bold uppercase">On-Road</p>
                  <h3 className="text-2xl font-bold text-emerald-900">{activeVehicles} <small className="text-xs font-normal">/ {vehicles.length} total</small></h3>
               </div>
            </div>
            <div className="bg-primary-50 border border-primary-100 p-4 rounded-xl flex items-center">
               <div className="bg-primary-500 p-3 rounded-lg text-white mr-4 shadow-md">
                  <User size={20} />
               </div>
               <div>
                  <p className="text-xs text-primary-600 font-bold uppercase">Active Drivers</p>
                  <h3 className="text-2xl font-bold text-primary-900">{activeDrivers} <small className="text-xs font-normal">available</small></h3>
               </div>
            </div>
            <div className="bg-amber-50 border border-amber-100 p-4 rounded-xl flex items-center">
               <div className="bg-amber-500 p-3 rounded-lg text-white mr-4 shadow-md shadow-amber-200">
                  <Truck size={20} />
               </div>
               <div>
                  <p className="text-xs text-amber-600 font-bold uppercase">Under Maintenance</p>
                  <h3 className="text-2xl font-bold text-amber-900">{maintenanceVehicles} <small className="text-xs font-normal">vehicles</small></h3>
               </div>
            </div>
          </div>

          <div className="bg-white rounded-2xl border border-gray-100 shadow-sm overflow-hidden">
            <div className="p-4 border-b border-gray-100 flex items-center justify-between bg-gray-50/30">
               <div className="flex items-center bg-white border border-gray-200 rounded-lg px-3 py-1.5 w-64 shadow-sm">
                 <Search size={16} className="text-gray-400 mr-2" />
                 <input type="text" placeholder="Search fleet..." className="bg-transparent border-none text-xs w-full focus:ring-0" />
               </div>
               <button className="p-2 border border-gray-200 rounded hover:bg-white"><Filter size={16}/></button>
            </div>
            {vehicles.length === 0 ? (
              <div className="p-12 text-center text-gray-400">
                <Truck size={48} className="mx-auto mb-4 opacity-20" />
                <p>No vehicles found</p>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-3 divide-x divide-y md:divide-y-0 divide-gray-100">
                {vehicles.slice(0, 6).map((v) => {
                  const driver = drivers.find(d => d.status === 'active');
                  const statusLabel = v.status === 'active' ? 'In Transit' : v.status === 'maintenance' ? 'Maintenance' : 'Idle';
                  const statusColor = v.status === 'active' ? 'bg-primary-100 text-primary-700' :
                                    v.status === 'maintenance' ? 'bg-red-100 text-red-700' : 'bg-emerald-100 text-emerald-700';
                  return (
                    <div key={v.id} className="p-6 hover:bg-gray-50/50 transition-colors">
                      <div className="flex justify-between items-start mb-4">
                        <div>
                           <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full uppercase ${statusColor}`}>
                             {statusLabel}
                           </span>
                           <h4 className="text-lg font-bold text-gray-900 mt-1">{v.plate_number}</h4>
                           <p className="text-xs text-gray-500">Type: {v.type}</p>
                        </div>
                        <Truck size={24} className="text-gray-300" />
                      </div>
                      
                      <div className="space-y-4">
                         {driver && (
                           <div className="flex items-center text-sm">
                              <User size={14} className="mr-2 text-gray-400" />
                              <span className="text-gray-700">{driver.id}</span>
                           </div>
                         )}
                         <div className="flex items-center text-sm">
                            <MapPin size={14} className="mr-2 text-primary-500" />
                            <span className="text-gray-700">{v.status === 'active' ? 'On Route' : 'Idle'}</span>
                         </div>
                      </div>
                      
                      <button className="w-full mt-6 py-2 bg-gray-900 text-white rounded-xl text-xs font-bold hover:bg-gray-800 transition">
                        View Details
                      </button>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        </>
      )}
    </div>
  );
};

export default Fleet;
