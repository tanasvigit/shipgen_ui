import React, { useState, useEffect } from 'react';
import { Activity, Truck, TrendingUp, AlertCircle } from 'lucide-react';
import { apiClient, ApiResponse } from '../../services/apiClient';

const OperationalDashboard: React.FC = () => {
  const [stats, setStats] = useState({
    vehiclesOnRoad: 0,
    pendingInvoices: 0,
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadStats();
    const interval = setInterval(loadStats, 30000); // Refresh every 30 seconds
    return () => clearInterval(interval);
  }, []);

  const loadStats = async () => {
    try {
      // Load vehicles
      const vehiclesRes = await apiClient.get<ApiResponse<any[]>>('/vehicles', {
        page: 1,
        pageSize: 100
      });
      const activeVehicles = vehiclesRes.data?.filter((v: any) => v.status === 'IN_USE').length || 0;

      // Load outstanding invoices
      const invoicesRes = await apiClient.get<ApiResponse<any[]>>('/invoices', {
        status: 'GENERATED',
        page: 1,
        pageSize: 1
      });

      setStats({
        vehiclesOnRoad: activeVehicles,
        pendingInvoices: invoicesRes.pagination?.total || 0,
      });
      setLoading(false);
    } catch (err) {
      setLoading(false);
    }
  };

  const kpis = [
    {
      label: 'Vehicles on Road',
      value: stats.vehiclesOnRoad,
      icon: Truck,
      color: 'green',
      change: '+5%'
    },
    {
      label: 'Pending Invoices',
      value: stats.pendingInvoices,
      icon: AlertCircle,
      color: 'orange',
      change: '-3%'
    },
  ];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Operational Dashboard</h1>
        <p className="text-sm text-gray-600 mt-1">Live metrics and KPIs for your logistics operations</p>
      </div>

      {/* KPIs */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {kpis.map((kpi) => (
          <div key={kpi.label} className="bg-white rounded-xl border border-gray-200 p-6">
            <div className="flex items-center justify-between mb-4">
              <div className={`w-12 h-12 rounded-lg bg-${kpi.color}-100 flex items-center justify-center`}>
                <kpi.icon className={`text-${kpi.color}-600`} size={24} />
              </div>
              <span className={`text-sm font-semibold ${
                kpi.change.startsWith('+') ? 'text-green-600' : 'text-red-600'
              }`}>
                {kpi.change}
              </span>
            </div>
            <div className="text-2xl font-bold text-gray-900 mb-1">{kpi.value}</div>
            <div className="text-sm text-gray-600">{kpi.label}</div>
          </div>
        ))}
      </div>

      {/* Charts Placeholder */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-xl border border-gray-200 p-6">
          <h2 className="text-lg font-bold text-gray-900 mb-4">Order Volume (Last 7 Days)</h2>
          <div className="h-64 flex items-center justify-center bg-gray-50 rounded-lg">
            <div className="text-center">
              <TrendingUp size={48} className="mx-auto text-gray-300 mb-4" />
              <p className="text-gray-600">Chart visualization</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl border border-gray-200 p-6">
          <h2 className="text-lg font-bold text-gray-900 mb-4">Throughput trend</h2>
          <div className="h-64 flex items-center justify-center bg-gray-50 rounded-lg">
            <div className="text-center">
              <Activity size={48} className="mx-auto text-gray-300 mb-4" />
              <p className="text-gray-600">Chart visualization</p>
            </div>
          </div>
        </div>
      </div>

      {/* Alerts */}
      <div className="bg-white rounded-xl border border-gray-200 p-6">
        <h2 className="text-lg font-bold text-gray-900 mb-4">Recent Alerts</h2>
        <div className="space-y-3">
          <div className="flex items-center space-x-3 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
            <AlertCircle size={20} className="text-yellow-600" />
            <div className="flex-1">
              <p className="text-sm font-medium text-gray-900">High warehouse utilization</p>
              <p className="text-xs text-gray-600">Warehouse A is at 92% capacity</p>
            </div>
          </div>
          <div className="flex items-center space-x-3 p-3 bg-blue-50 border border-blue-200 rounded-lg">
            <Activity size={20} className="text-blue-600" />
            <div className="flex-1">
              <p className="text-sm font-medium text-gray-900">New order created</p>
              <p className="text-xs text-gray-600">Order #12345 assigned to vehicle</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default OperationalDashboard;
