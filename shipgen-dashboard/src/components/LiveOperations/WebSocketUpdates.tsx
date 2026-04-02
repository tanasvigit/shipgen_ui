import React, { useState, useEffect } from 'react';
import { Activity, Radio, Clock, Truck, FileText } from 'lucide-react';

interface WebSocketEvent {
  id: string;
  type: string;
  timestamp: string;
  data: any;
}

const WebSocketUpdates: React.FC = () => {
  const [events, setEvents] = useState<WebSocketEvent[]>([]);
  const [isConnected, setIsConnected] = useState(false);

  useEffect(() => {
    // In production, connect to actual WebSocket
    // const socket = io(WS_URL);
    // socket.on('connect', () => setIsConnected(true));
    // socket.on('disconnect', () => setIsConnected(false));
    // socket.on('order:status', (data) => {
    //   setEvents(prev => [{ id: Date.now().toString(), type: 'order:status', timestamp: new Date().toISOString(), data }, ...prev].slice(0, 50));
    // });
    
    // Mock connection for demo
    setIsConnected(true);
  }, []);

  const eventTypes = [
    { type: 'order:status', label: 'Order Status Update', icon: FileText, color: 'blue' },
    { type: 'vehicle:location', label: 'Vehicle Location Update', icon: Truck, color: 'green' },
    { type: 'invoice:generated', label: 'Invoice Generated', icon: FileText, color: 'purple' },
  ];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">WebSocket Updates</h1>
        <p className="text-sm text-gray-600 mt-1">Real-time event architecture and instant notifications</p>
      </div>

      {/* Connection Status */}
      <div className={`p-4 rounded-lg border-2 ${
        isConnected ? 'bg-green-50 border-green-200' : 'bg-red-50 border-red-200'
      }`}>
        <div className="flex items-center space-x-3">
          <Radio className={isConnected ? 'text-green-600' : 'text-red-600'} size={24} />
          <div>
            <div className="font-semibold text-gray-900">
              {isConnected ? 'Connected' : 'Disconnected'}
            </div>
            <div className="text-sm text-gray-600">
              {isConnected ? 'Receiving real-time updates' : 'WebSocket connection lost'}
            </div>
          </div>
        </div>
      </div>

      {/* Event Types */}
      <div className="grid md:grid-cols-3 gap-4">
        {eventTypes.map((eventType) => (
          <div key={eventType.type} className="bg-white rounded-xl border border-gray-200 p-6">
            <div className={`w-12 h-12 rounded-lg bg-${eventType.color}-100 flex items-center justify-center mb-4`}>
              <eventType.icon className={`text-${eventType.color}-600`} size={24} />
            </div>
            <h3 className="font-semibold text-gray-900 mb-2">{eventType.label}</h3>
            <p className="text-sm text-gray-600">
              Instant notifications when {eventType.type.replace(':', ' ')} events occur
            </p>
          </div>
        ))}
      </div>

      {/* Architecture Explanation */}
      <div className="bg-white rounded-xl border border-gray-200 p-6">
        <h2 className="text-lg font-bold text-gray-900 mb-4">Real-Time Architecture</h2>
        <div className="space-y-4">
          <div className="flex items-start space-x-4">
            <div className="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center flex-shrink-0">
              <span className="text-blue-600 font-bold text-sm">1</span>
            </div>
            <div>
              <h3 className="font-semibold text-gray-900">WebSocket Server</h3>
              <p className="text-sm text-gray-600">
                Socket.IO server maintains persistent connections with all clients for instant bidirectional communication
              </p>
            </div>
          </div>
          <div className="flex items-start space-x-4">
            <div className="w-8 h-8 rounded-full bg-green-100 flex items-center justify-center flex-shrink-0">
              <span className="text-green-600 font-bold text-sm">2</span>
            </div>
            <div>
              <h3 className="font-semibold text-gray-900">Event Broadcasting</h3>
              <p className="text-sm text-gray-600">
                When status changes occur (order updates, vehicle locations, invoice generation), events are broadcast to all connected clients
              </p>
            </div>
          </div>
          <div className="flex items-start space-x-4">
            <div className="w-8 h-8 rounded-full bg-purple-100 flex items-center justify-center flex-shrink-0">
              <span className="text-purple-600 font-bold text-sm">3</span>
            </div>
            <div>
              <h3 className="font-semibold text-gray-900">Client Updates</h3>
              <p className="text-sm text-gray-600">
                Frontend receives events instantly and updates UI without page refresh, ensuring real-time visibility
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Recent Events (Read-only) */}
      <div className="bg-white rounded-xl border border-gray-200 p-6">
        <h2 className="text-lg font-bold text-gray-900 mb-4">Recent Events (Last 24 Hours)</h2>
        {events.length === 0 ? (
          <div className="text-center py-8">
            <Activity size={48} className="mx-auto text-gray-300 mb-4" />
            <p className="text-gray-600">No events in the last 24 hours</p>
            <p className="text-sm text-gray-500 mt-2">Events will appear here when they occur</p>
          </div>
        ) : (
          <div className="space-y-2">
            {events.map((event) => (
              <div key={event.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div className="flex items-center space-x-3">
                  <Activity size={16} className="text-blue-600" />
                  <span className="text-sm font-medium text-gray-900">{event.type}</span>
                </div>
                <span className="text-xs text-gray-500">
                  {new Date(event.timestamp).toLocaleTimeString()}
                </span>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default WebSocketUpdates;
