import React from 'react';
import { Link } from 'react-router-dom';

interface FooterProps {
  variant?: 'default' | 'dashboard';
}

const Footer: React.FC<FooterProps> = ({ variant = 'default' }) => {
  if (variant === 'dashboard') {
    return (
      <footer className="flex-shrink-0 mt-auto border-t border-gray-200 bg-white py-4">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex flex-col sm:flex-row items-center justify-between gap-3">
            <p className="text-sm text-gray-500">
              © {new Date().getFullYear()} ShipZen. All rights reserved.
            </p>
            <div className="flex flex-wrap items-center justify-center sm:justify-end gap-4 sm:gap-6">
              <Link to="/dashboard" className="text-sm text-gray-500 hover:text-gray-900 transition-colors">Dashboard</Link>
              <Link to="/logistics/orders" className="text-sm text-gray-500 hover:text-gray-900 transition-colors">Orders</Link>
              <Link to="/fleet/vehicles" className="text-sm text-gray-500 hover:text-gray-900 transition-colors">Fleet &amp; Operations</Link>
              <Link to="/analytics/reports" className="text-sm text-gray-500 hover:text-gray-900 transition-colors">Reports</Link>
            </div>
          </div>
        </div>
      </footer>
    );
  }

  return (
    <footer className="flex-shrink-0 bg-gradient-to-b from-gray-900 to-gray-800 text-gray-300 animate-fade-in">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid grid-cols-2 md:grid-cols-5 gap-8 mb-8">
          <div className="animate-fade-in-up md:col-span-2">
            <div className="flex items-center mb-4">
              <img src="/logo_logistic.png" alt="ShipZen" className="h-12 w-auto" />
            </div>
            <p className="text-sm text-gray-400 leading-relaxed">
              Enterprise logistics, warehouse, and fleet management platform.
              End-to-end visibility from order to delivery. GST-ready billing and real-time GPS tracking.
            </p>
          </div>
          <div className="animate-fade-in-up animation-delay-100">
            <h4 className="text-sm font-bold text-white uppercase tracking-wider mb-4">Core Modules</h4>
            <ul className="space-y-2">
              <li><Link to="/dashboard" className="text-sm text-gray-400 hover:text-white transition-colors duration-300">Dashboard</Link></li>
              <li><Link to="/logistics/orders" className="text-sm text-gray-400 hover:text-white transition-colors duration-300">Logistics</Link></li>
              <li><Link to="/fleet/vehicles" className="text-sm text-gray-400 hover:text-white transition-colors duration-300">Fleet &amp; Operations</Link></li>
              <li><Link to="/analytics/reports" className="text-sm text-gray-400 hover:text-white transition-colors duration-300">Reports &amp; Analytics</Link></li>
            </ul>
          </div>
          <div className="animate-fade-in-up animation-delay-150">
            <h4 className="text-sm font-bold text-white uppercase tracking-wider mb-4">Operations</h4>
            <ul className="space-y-2">
              <li><Link to="/fleet/service-areas" className="text-sm text-gray-400 hover:text-white transition-colors duration-300">Locations &amp; Coverage</Link></li>
              <li><Link to="/fleet/tracking-numbers" className="text-sm text-gray-400 hover:text-white transition-colors duration-300">Tracking</Link></li>
              <li><Link to="/fleet/payloads" className="text-sm text-gray-400 hover:text-white transition-colors duration-300">Operations &amp; Execution</Link></li>
              <li><Link to="/analytics/schedules" className="text-sm text-gray-400 hover:text-white transition-colors duration-300">Scheduling</Link></li>
            </ul>
          </div>
          <div className="animate-fade-in-up animation-delay-200">
            <h4 className="text-sm font-bold text-white uppercase tracking-wider mb-4">Configuration</h4>
            <ul className="space-y-2">
              <li><Link to="/analytics/api-credentials" className="text-sm text-gray-400 hover:text-white transition-colors duration-300">API &amp; Integrations</Link></li>
              <li><Link to="/analytics/custom-fields" className="text-sm text-gray-400 hover:text-white transition-colors duration-300">System &amp; Configuration</Link></li>
              <li><Link to="/analytics/users" className="text-sm text-gray-400 hover:text-white transition-colors duration-300">Users &amp; Access</Link></li>
            </ul>
          </div>
        </div>
        <div className="pt-8 border-t border-gray-700 flex flex-col sm:flex-row items-center justify-between animate-fade-in-up animation-delay-400">
          <p className="text-sm text-gray-400">
            © {new Date().getFullYear()} ShipZen. All rights reserved.
          </p>
          <Link
            to="/dashboard"
            className="mt-4 sm:mt-0 px-4 py-2 text-sm font-semibold text-blue-400 hover:text-blue-300 transition-colors duration-300 hover:scale-105"
          >
            Dashboard →
          </Link>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
