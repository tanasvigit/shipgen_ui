
import React, { useState, useEffect, useRef } from 'react';
import { Truck, AlertCircle, Navigation } from 'lucide-react';
import { apiClient } from '../services/apiClient';
import { initializeSocket, disconnectSocket, onVehicleLocationUpdate, offVehicleLocationUpdate } from '../services/socket';

interface Vehicle {
  id: string;
  plateNumber: string;
  lastKnownLatitude?: number;
  lastKnownLongitude?: number;
  lastKnownLocationAt?: string;
  latestTelemetry?: {
    latitude: number;
    longitude: number;
    speed: number;
    fuelLevel?: number;
    recordedAt: string;
  };
}

const LiveOperations: React.FC = () => {
  const [vehicles, setVehicles] = useState<Vehicle[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [mapCenter, setMapCenter] = useState<[number, number]>([19.0760, 72.8777]); // Mumbai default
  const mapRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    fetchData();
    initializeSocketConnection();

    return () => {
      disconnectSocket();
    };
  }, []);

  const initializeSocketConnection = () => {
    try {
      initializeSocket();

      const handleVehicleUpdate = (data: any) => {
        setVehicles(prev => prev.map(v => 
          v.id === data.vehicleId 
            ? { ...v, latestTelemetry: { ...data, recordedAt: data.timestamp } }
            : v
        ));
      };

      onVehicleLocationUpdate(handleVehicleUpdate);

      return () => {
        offVehicleLocationUpdate(handleVehicleUpdate);
      };
    } catch (err) {
      console.error('Failed to initialize socket:', err);
    }
  };

  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);

      const vehiclesRes = await apiClient.get<{ data: Vehicle[] }>('/tracking/vehicles');
      setVehicles(vehiclesRes.data || []);

      // Set map center to first vehicle or default
      if (vehiclesRes.data && vehiclesRes.data.length > 0) {
        const firstVehicle = vehiclesRes.data[0];
        const lat = firstVehicle.latestTelemetry?.latitude || firstVehicle.lastKnownLatitude;
        const lng = firstVehicle.latestTelemetry?.longitude || firstVehicle.lastKnownLongitude;
        if (lat && lng) {
          setMapCenter([lat, lng]);
        }
      }
    } catch (err: any) {
      setError(err.message || 'Failed to load data');
    } finally {
      setLoading(false);
    }
  };

  if (loading && vehicles.length === 0) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-500">Loading live operations...</div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Live Operations</h1>
          <p className="text-sm text-gray-500">Real-time vehicle tracking</p>
        </div>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
          {error}
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Map View */}
        <div className="lg:col-span-2 bg-white rounded-xl border border-gray-100 shadow-sm overflow-hidden">
          <div className="p-4 border-b border-gray-100 bg-gray-50/30">
            <h3 className="font-semibold text-gray-800 flex items-center">
              <Navigation size={18} className="mr-2" />
              Live Map View
            </h3>
          </div>
          <div ref={mapRef} className="h-[500px] bg-gray-100 relative">
            {/* Simple map placeholder - can be replaced with Leaflet/MapLibre */}
            <iframe
              width="100%"
              height="100%"
              frameBorder="0"
              scrolling="no"
              marginHeight={0}
              marginWidth={0}
              src={`https://www.openstreetmap.org/export/embed.html?bbox=${mapCenter[1] - 0.1},${mapCenter[0] - 0.1},${mapCenter[1] + 0.1},${mapCenter[0] + 0.1}&layer=mapnik&marker=${mapCenter[0]},${mapCenter[1]}`}
              style={{ border: 0 }}
            />
            
            {/* Vehicle markers overlay */}
            <div className="absolute top-4 left-4 bg-white p-2 rounded-lg shadow-md">
              <div className="text-xs font-semibold text-gray-700 mb-1">Active Vehicles</div>
              {vehicles.filter(v => v.latestTelemetry || (v.lastKnownLatitude && v.lastKnownLongitude)).map(vehicle => (
                <div key={vehicle.id} className="flex items-center text-xs text-gray-600 mb-1">
                  <Truck size={12} className="mr-1 text-blue-600" />
                  {vehicle.plateNumber || vehicle.id}
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Vehicles List */}
        <div className="bg-white rounded-xl border border-gray-100 shadow-sm overflow-hidden">
          <div className="p-4 border-b border-gray-100 bg-gray-50/30">
            <h3 className="font-semibold text-gray-800 flex items-center">
              <Truck size={18} className="mr-2" />
              Vehicles
            </h3>
          </div>
          <div className="overflow-y-auto max-h-[500px]">
            {vehicles.length === 0 ? (
              <div className="p-8 text-center text-gray-500 text-sm">
                No vehicles found
              </div>
            ) : (
              <div className="divide-y divide-gray-50">
                {vehicles.map(vehicle => (
                  <div
                    key={vehicle.id}
                    className="p-4 hover:bg-gray-50 transition-colors"
                  >
                    <div className="flex items-start justify-between mb-2">
                      <div className="flex-1">
                        <div className="text-sm font-medium text-gray-900">{vehicle.plateNumber || vehicle.id}</div>
                        <div className="text-xs text-gray-500 mt-1">{vehicle.id.substring(0, 8)}</div>
                      </div>
                      {vehicle.latestTelemetry?.speed !== undefined ? (
                        <span className="px-2 py-0.5 rounded-full text-[10px] font-bold uppercase bg-blue-50 text-blue-700">
                          {Math.round(vehicle.latestTelemetry.speed)} km/h
                        </span>
                      ) : null}
                    </div>
                    {vehicle.latestTelemetry ? (
                      <div className="text-xs text-gray-500 mt-2">
                        Last update: {new Date(vehicle.latestTelemetry.recordedAt).toLocaleString()}
                      </div>
                    ) : null}
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default LiveOperations;
