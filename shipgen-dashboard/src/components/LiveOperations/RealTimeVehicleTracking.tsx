import React, { useState, useEffect } from 'react';
import { Truck, MapPin, Activity, Clock, RefreshCw, Navigation } from 'lucide-react';
import { apiClient, ApiResponse } from '../../services/apiClient';

interface VehicleTracking {
  vehicleId: string;
  plateNumber: string;
  latitude: number;
  longitude: number;
  speed: number;
  heading: number;
  timestamp: string;
  status: string;
}

const RealTimeVehicleTracking: React.FC = () => {
  const [vehicles, setVehicles] = useState<VehicleTracking[]>([]);
  const [loading, setLoading] = useState(true);
  const [autoRefresh, setAutoRefresh] = useState(true);

  useEffect(() => {
    loadVehicles();
    
    if (autoRefresh) {
      const interval = setInterval(loadVehicles, 5000);
      return () => clearInterval(interval);
    }
  }, [autoRefresh]);

  const loadVehicles = async () => {
    try {
      const response = await apiClient.get<ApiResponse<VehicleTracking[]>>('/tracking/vehicles');
      setVehicles(response.data || []);
      setLoading(false);
    } catch (err) {
      setLoading(false);
    }
  };

  const activeVehicles = vehicles.filter(v => v.status === 'IN_USE' || v.status === 'AVAILABLE');

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Real-Time Vehicle Tracking</h1>
          <p className="text-sm text-gray-600 mt-1">GPS-enabled location updates for all vehicles</p>
        </div>
        <div className="flex items-center space-x-3">
          <button
            onClick={() => setAutoRefresh(!autoRefresh)}
            className={`px-4 py-2 rounded-lg border transition ${
              autoRefresh ? 'bg-green-50 border-green-200 text-green-700' : 'bg-gray-50 border-gray-200'
            }`}
          >
            {autoRefresh ? 'Auto-refresh ON' : 'Auto-refresh OFF'}
          </button>
          <button onClick={loadVehicles} className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
            <RefreshCw size={18} />
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <div className="bg-white rounded-xl border border-gray-200 p-6">
            <div className="h-[500px] bg-gradient-to-br from-blue-50 to-indigo-50 rounded-lg flex items-center justify-center">
              <div className="text-center">
                <Navigation size={64} className="mx-auto text-blue-400 mb-4" />
                <p className="text-gray-600 font-medium">Live Map View</p>
                <p className="text-sm text-gray-500 mt-2">{activeVehicles.length} vehicles active</p>
              </div>
            </div>
          </div>
        </div>

        <div className="space-y-4">
          <div className="bg-white rounded-xl border border-gray-200 p-4">
            <h3 className="font-semibold mb-4">Active Vehicles ({activeVehicles.length})</h3>
            <div className="space-y-3 max-h-96 overflow-y-auto">
              {activeVehicles.map((vehicle) => (
                <div key={vehicle.vehicleId} className="p-3 border border-gray-200 rounded-lg">
                  <div className="flex items-center justify-between mb-2">
                    <span className="font-semibold">{vehicle.plateNumber}</span>
                    <span className="px-2 py-1 bg-green-100 text-green-700 rounded-full text-xs">
                      {vehicle.status}
                    </span>
                  </div>
                  <div className="text-xs text-gray-600 space-y-1">
                    <div className="flex items-center space-x-1">
                      <MapPin size={12} />
                      <span>{vehicle.latitude.toFixed(4)}, {vehicle.longitude.toFixed(4)}</span>
                    </div>
                    <div className="flex items-center space-x-1">
                      <Activity size={12} />
                      <span>{vehicle.speed} km/h</span>
                    </div>
                    <div className="flex items-center space-x-1">
                      <Clock size={12} />
                      <span>{new Date(vehicle.timestamp).toLocaleTimeString()}</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default RealTimeVehicleTracking;
