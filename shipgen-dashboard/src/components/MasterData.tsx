
import React from 'react';
import { Building2, MapPin, Users, ShieldCheck, Plus, Search, ExternalLink } from 'lucide-react';

const MasterData: React.FC = () => {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">System Master Data</h1>
          <p className="text-sm text-gray-500">Configure core organizational entities and compliance</p>
        </div>
        <button className="bg-blue-600 text-white px-4 py-2 rounded-lg text-sm font-medium flex items-center shadow-sm hover:bg-blue-700 transition">
          <Plus size={18} className="mr-2" />
          Add Entity
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {/* Company Profile Card */}
        <div className="bg-white p-6 rounded-2xl border border-gray-100 shadow-sm hover:shadow-md transition-shadow">
          <div className="flex items-center space-x-4 mb-4">
            <div className="bg-blue-100 p-3 rounded-xl text-blue-600">
              <Building2 size={24} />
            </div>
            <div>
              <h3 className="font-bold text-gray-900">ShipGen Logistics Pvt Ltd</h3>
              <p className="text-xs text-gray-500">GST: 27AAAAA0000A1Z5</p>
            </div>
          </div>
          <div className="space-y-2 border-t border-gray-50 pt-4">
            <div className="flex justify-between text-sm">
              <span className="text-gray-500">Industry</span>
              <span className="font-medium">3PL Logistics</span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-gray-500">Registered Office</span>
              <span className="font-medium">Mumbai, MH</span>
            </div>
          </div>
          <button className="w-full mt-4 py-2 text-blue-600 bg-blue-50 rounded-lg text-xs font-bold uppercase tracking-wider hover:bg-blue-100">
            Edit Profile
          </button>
        </div>

        {/* Branch Network */}
        <div className="bg-white p-6 rounded-2xl border border-gray-100 shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-bold text-gray-800 flex items-center">
              <MapPin size={18} className="mr-2 text-emerald-500" />
              Branch Network
            </h3>
            <span className="text-xs bg-emerald-100 text-emerald-700 px-2 py-0.5 rounded-full font-bold">12 Active</span>
          </div>
          <div className="space-y-3">
            {['Mumbai Hub', 'Delhi NCR', 'Bangalore Port'].map(branch => (
              <div key={branch} className="flex items-center justify-between p-2 hover:bg-gray-50 rounded-lg transition group">
                <span className="text-sm text-gray-700">{branch}</span>
                <ExternalLink size={14} className="text-gray-300 group-hover:text-blue-500" />
              </div>
            ))}
          </div>
          <button className="w-full mt-4 py-2 border border-dashed border-gray-300 rounded-lg text-xs text-gray-500 font-medium hover:border-blue-300 hover:text-blue-500">
            + Manage Branches
          </button>
        </div>

        {/* Vendor/Partner Management */}
        <div className="bg-white p-6 rounded-2xl border border-gray-100 shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-bold text-gray-800 flex items-center">
              <Users size={18} className="mr-2 text-indigo-500" />
              Vendors & Partners
            </h3>
          </div>
          <div className="space-y-3">
             <div className="p-3 bg-indigo-50/50 rounded-xl border border-indigo-100">
                <p className="text-xs font-bold text-indigo-700">Fuel Partner</p>
                <p className="text-sm font-medium">Reliance Petroleum</p>
             </div>
             <div className="p-3 bg-indigo-50/50 rounded-xl border border-indigo-100">
                <p className="text-xs font-bold text-indigo-700">Insurance</p>
                <p className="text-sm font-medium">Global Secure Ltd.</p>
             </div>
          </div>
          <button className="w-full mt-4 py-2 text-indigo-600 bg-indigo-50 rounded-lg text-xs font-bold uppercase hover:bg-indigo-100">
            Partner Portal
          </button>
        </div>
      </div>

      <div className="bg-white p-6 rounded-2xl border border-gray-100 shadow-sm">
        <h3 className="font-bold text-gray-900 mb-4 flex items-center">
          <ShieldCheck size={20} className="mr-2 text-blue-600" />
          Access Control (RBAC)
        </h3>
        <div className="overflow-x-auto">
          <table className="w-full text-left">
            <thead>
              <tr className="text-xs text-gray-400 border-b border-gray-100">
                <th className="pb-3 px-2">Role Name</th>
                <th className="pb-3 px-2">Permissions</th>
                <th className="pb-3 px-2">Users Count</th>
                <th className="pb-3 px-2">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-50">
              {[
                { name: 'Operations Manager', perm: 'Fleet, Tracking, Reports', count: 4 },
                { name: 'Warehouse Clerk', perm: 'Inventory, GRN, Putaway', count: 18 },
                { name: 'Finance Admin', perm: 'Billing, Tax, Payroll', count: 2 },
              ].map(role => (
                <tr key={role.name} className="hover:bg-gray-50">
                  <td className="py-4 px-2 text-sm font-bold text-gray-700">{role.name}</td>
                  <td className="py-4 px-2 text-xs text-gray-500">{role.perm}</td>
                  <td className="py-4 px-2 text-sm text-gray-600">{role.count}</td>
                  <td className="py-4 px-2">
                    <button className="text-blue-600 text-xs font-bold hover:underline">Manage</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default MasterData;
