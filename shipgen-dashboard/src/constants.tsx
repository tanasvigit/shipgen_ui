
import React from 'react';
import { 
  LayoutDashboard, 
  Truck, 
  Warehouse, 
  Package, 
  Users, 
  FileText, 
  BarChart3, 
  Settings,
  MapPin,
  Clock,
  CheckCircle2,
  AlertCircle,
  ShieldCheck,
  HardDrive,
  Navigation
} from 'lucide-react';

export const COLORS = {
  primary: '#2563eb', // Blue 600
  secondary: '#64748b', // Slate 500
  success: '#10b981', // Emerald 500
  warning: '#f59e0b', // Amber 500
  danger: '#ef4444', // Red 500
};

export const STATUS_COLORS: Record<string, string> = {
  CREATED: 'bg-gray-100 text-gray-700',
  ASSIGNED: 'bg-blue-100 text-blue-700',
  PICKED: 'bg-indigo-100 text-indigo-700',
  IN_TRANSIT: 'bg-amber-100 text-amber-700',
  DELIVERED: 'bg-emerald-100 text-emerald-700',
  CLOSED: 'bg-slate-100 text-slate-700',
};

import { UserRole } from './types';
import { hasAccess } from './utils/roleAccess';

// Navigation items configuration
// Note: Actual visibility is controlled by roleAccess.ts
export const NAVIGATION_ITEMS = [
  { id: 'dashboard', label: 'Dashboard', icon: <LayoutDashboard size={20} /> },
  { id: 'logistics', label: 'Orders', icon: <Package size={20} /> },
  { id: 'warehouse', label: 'Warehouse Ops', icon: <Warehouse size={20} /> },
  { id: 'fleet', label: 'Fleet & Drivers', icon: <Truck size={20} /> },
  { id: 'live-operations', label: 'Live Operations', icon: <Navigation size={20} /> },
  { id: 'billing', label: 'Billing', icon: <FileText size={20} /> },
  { id: 'analytics', label: 'Reports', icon: <BarChart3 size={20} /> },
  { id: 'master-data', label: 'Master Data', icon: <HardDrive size={20} /> },
];

/**
 * Filter navigation items based on user role
 * @param role - User role
 * @returns Filtered navigation items
 */
export function getFilteredNavigationItems(role: UserRole | null) {
  if (!role) return [];
  
  return NAVIGATION_ITEMS.filter((item) => hasAccess(role, item.id as any));
}
