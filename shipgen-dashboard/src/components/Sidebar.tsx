import React, { useEffect, useMemo, useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import {
  ChevronDown,
  ChevronUp,
  LogOut,
  Sparkles,
  Truck,
  MapPin,
  ScanLine,
  Boxes,
  Braces,
  CalendarRange,
  Plug,
  FolderCog,
  UserCog,
  LineChart,
} from 'lucide-react';
import { getFilteredNavigationItems } from '../constants';
import {
  canAccessRoute,
  hasAccess,
  isAIAssistantVisibleForRole,
  isSidebarModuleVisibleForRole,
} from '../utils/roleAccess';
import { UserRole } from '../types';

interface SidebarUser {
  name: string;
  role: UserRole;
}

interface SidebarProps {
  isMobileOpen: boolean;
  onCloseMobile: () => void;
  onLogout: () => void;
  currentUser: SidebarUser | null;
  isCollapsed: boolean;
}

interface NavItem {
  id: string;
  label: string;
  to: string;
}

interface ModuleItem {
  id: string;
  label: string;
  to: string;
  children?: NavItem[];
}

function pathTouchesGroup(path: string, item: ModuleItem): boolean {
  if (path === item.to || path.startsWith(`${item.to}/`)) return true;
  return Boolean(item.children?.some((c) => path === c.to || path.startsWith(`${c.to}/`)));
}

/** Sidebar modules aligned with backend; grouped for scale. Order matches product sections. */
const moduleItems: ModuleItem[] = [
  // 1. Dashboard
  { id: 'dashboard', label: 'Dashboard', to: '/dashboard' },

  // 2. Logistics
  {
    id: 'logistics',
    label: 'Logistics',
    to: '/logistics/orders',
    children: [
      { id: 'orders', label: 'Orders', to: '/logistics/orders' },
      { id: 'dispatch-board', label: 'Dispatcher Board', to: '/logistics/orders/dispatch-board' },
      { id: 'customers', label: 'Customers', to: '/logistics/customers' },
    ],
  },

  // 3. Fleet & Operations (Devices route lives under /analytics in the router)
  {
    id: 'fleet-operations',
    label: 'Fleet & Operations',
    to: '/fleet/dashboard',
    children: [
      { id: 'fleet-dashboard', label: 'Fleet dashboard', to: '/fleet/dashboard' },
      { id: 'vehicles', label: 'Vehicles', to: '/fleet/vehicles' },
      { id: 'drivers', label: 'Drivers', to: '/fleet/drivers' },
      { id: 'fleets', label: 'Fleets', to: '/fleet/fleets' },
      { id: 'devices', label: 'Devices', to: '/analytics/devices' },
    ],
  },

  // 4. Locations & Coverage
  {
    id: 'locations-coverage',
    label: 'Locations & Coverage',
    to: '/fleet/service-areas',
    children: [
      { id: 'service-areas', label: 'Service Areas', to: '/fleet/service-areas' },
      { id: 'zones', label: 'Zones', to: '/fleet/zones' },
      { id: 'places', label: 'Places', to: '/fleet/places' },
    ],
  },

  // 5. Tracking
  {
    id: 'tracking',
    label: 'Tracking',
    to: '/fleet/tracking-numbers',
    children: [
      { id: 'tracking-numbers', label: 'Tracking Numbers', to: '/fleet/tracking-numbers' },
      { id: 'tracking-statuses', label: 'Tracking Statuses', to: '/fleet/tracking-statuses' },
    ],
  },

  // 6. Business Entities
  {
    id: 'business-entities',
    label: 'Business Entities',
    to: '/analytics/companies',
    children: [
      { id: 'companies', label: 'Companies', to: '/analytics/companies' },
      { id: 'contacts', label: 'Contacts', to: '/fleet/contacts' },
      { id: 'vendors', label: 'Vendors', to: '/fleet/vendors' },
      { id: 'entities', label: 'Entities', to: '/fleet/entities' },
    ],
  },

  // 7. Operations & Execution
  {
    id: 'operations-execution',
    label: 'Operations & Execution',
    to: '/fleet/payloads',
    children: [
      { id: 'payloads', label: 'Payloads', to: '/fleet/payloads' },
      { id: 'activities', label: 'Activities', to: '/analytics/activities' },
      { id: 'transactions', label: 'Transactions', to: '/analytics/transactions' },
      { id: 'issues', label: 'Issues', to: '/fleet/issues' },
      { id: 'comments', label: 'Comments', to: '/analytics/comments' },
    ],
  },

  // 8. Scheduling
  {
    id: 'scheduling',
    label: 'Scheduling',
    to: '/analytics/schedules',
    children: [
      { id: 'schedules', label: 'Schedules', to: '/analytics/schedules' },
      { id: 'schedule-items', label: 'Schedule Items', to: '/analytics/schedule-items' },
      { id: 'schedule-templates', label: 'Schedule Templates', to: '/analytics/schedule-templates' },
      { id: 'schedule-availability', label: 'Schedule Availability', to: '/analytics/schedule-availability' },
      { id: 'schedule-constraints', label: 'Schedule Constraints', to: '/analytics/schedule-constraints' },
      { id: 'schedule-monitor', label: 'Schedule Monitor', to: '/analytics/schedule-monitor' },
    ],
  },

  // 9. API & Integrations
  {
    id: 'api-integrations',
    label: 'API & Integrations',
    to: '/analytics/api-credentials',
    children: [
      { id: 'api-credentials', label: 'API Credentials', to: '/analytics/api-credentials' },
      { id: 'api-events', label: 'API Events', to: '/analytics/api-events' },
      { id: 'api-request-logs', label: 'API Request Logs', to: '/analytics/api-request-logs' },
      { id: 'extensions', label: 'Extensions', to: '/analytics/extensions' },
    ],
  },

  // 10. System & Configuration
  {
    id: 'system-configuration',
    label: 'System & Configuration',
    to: '/analytics/custom-fields',
    children: [
      { id: 'custom-fields', label: 'Custom Fields', to: '/analytics/custom-fields' },
      { id: 'custom-field-values', label: 'Custom Field Values', to: '/analytics/custom-field-values' },
      { id: 'files', label: 'Files', to: '/analytics/files' },
      { id: 'notifications', label: 'Notifications', to: '/analytics/notifications' },
    ],
  },

  // 11. Users & Access
  {
    id: 'users-access',
    label: 'Users & Access',
    to: '/analytics/users',
    children: [
      { id: 'users', label: 'Users (Int Users)', to: '/analytics/users' },
    ],
  },

  // 12. Reports & Analytics
  {
    id: 'reports-analytics',
    label: 'Reports & Analytics',
    to: '/analytics/reports',
    children: [
      { id: 'reports', label: 'Reports', to: '/analytics/reports' },
      { id: 'fuel-reports', label: 'Fuel Reports', to: '/fleet/fuel-reports' },
    ],
  },
];

const VIEWER_HIDDEN_FLEET_OPERATIONS_CHILD_IDS = new Set(['fleets', 'devices']);

const cn = (...classes: Array<string | false | null | undefined>) => classes.filter(Boolean).join(' ');

const customModuleIcons: Record<string, React.ReactNode> = {
  logistics: <Truck size={20} />,
  'fleet-operations': <Truck size={20} />,
  'locations-coverage': <MapPin size={20} />,
  tracking: <ScanLine size={20} />,
  'business-entities': <Boxes size={20} />,
  'operations-execution': <Braces size={20} />,
  scheduling: <CalendarRange size={20} />,
  'api-integrations': <Plug size={20} />,
  'system-configuration': <FolderCog size={20} />,
  'users-access': <UserCog size={20} />,
  'reports-analytics': <LineChart size={20} />,
};

const Sidebar: React.FC<SidebarProps> = ({
  isMobileOpen,
  onCloseMobile,
  onLogout,
  currentUser,
  isCollapsed,
}) => {
  const location = useLocation();
  const currentPath = location.pathname;
  const [openGroups, setOpenGroups] = useState<Record<string, boolean>>(() => {
    const initial: Record<string, boolean> = {};
    for (const item of moduleItems) {
      if (item.children?.length) {
        initial[item.id] = false;
      }
    }
    const match = moduleItems.find((m) => m.children?.length && pathTouchesGroup(currentPath, m));
    if (match) initial[match.id] = true;
    return initial;
  });

  /** Per-child visibility via canAccessRoute (same rules as App protected routes). getFilteredNavigationItems retained for icon map. */
  const filteredItems = useMemo(() => {
    if (!currentUser) {
      return [];
    }
    const { role } = currentUser;
    const out: ModuleItem[] = [];
    for (const item of moduleItems) {
      if (!isSidebarModuleVisibleForRole(role, item.id)) {
        continue;
      }
      if (item.children?.length) {
        const children = item.children.filter((c) => {
          if (
            role === UserRole.VIEWER &&
            item.id === 'fleet-operations' &&
            VIEWER_HIDDEN_FLEET_OPERATIONS_CHILD_IDS.has(c.id)
          ) {
            return false;
          }
          return canAccessRoute(role, c.to);
        });
        if (!children.length) continue;
        out.push({ ...item, children });
        continue;
      }
      if (canAccessRoute(role, item.to)) {
        out.push(item);
      }
    }
    return out;
  }, [currentUser]);

  useEffect(() => {
    setOpenGroups(() => {
      const next: Record<string, boolean> = {};
      for (const m of moduleItems) {
        if (m.children?.length) next[m.id] = false;
      }
      const match = moduleItems.find((m) => m.children?.length && pathTouchesGroup(currentPath, m));
      if (match) next[match.id] = true;
      return next;
    });
  }, [currentPath]);

  const iconMap = useMemo(() => {
    if (!currentUser) {
      return new Map<string, React.ReactNode>();
    }
    const entries = getFilteredNavigationItems(currentUser.role).map((item) => [item.id, item.icon] as const);
    return new Map<string, React.ReactNode>(entries);
  }, [currentUser]);

  const sidebarWidthClass = isCollapsed ? 'lg:w-[78px]' : 'lg:w-[248px]';
  const itemBaseClass =
    'group flex items-center rounded-2xl px-3.5 py-2.5 text-sm font-medium transition-all duration-200 ease-out';
  const activeClass =
    'bg-gradient-to-r from-primary-50 via-primary-50 to-primary-100 text-primary-700 shadow-soft ring-1 ring-primary-100/80';
  const idleClass =
    'text-secondary-700 hover:bg-blue-500/12 hover:text-blue-700 hover:shadow-[0_8px_20px_rgba(37,99,235,0.16)] hover:ring-1 hover:ring-blue-300/45 hover:backdrop-blur-md';

  const showLabel = !isCollapsed;

  return (
    <>
      {isMobileOpen ? <div className="fixed inset-0 z-40 bg-neutral-900/30 backdrop-blur-[1px] lg:hidden" onClick={onCloseMobile} /> : null}

      <aside
        className={cn(
          'fixed inset-y-0 left-0 z-50 flex w-[248px] -translate-x-full flex-col border-r border-border bg-gradient-to-b from-white/70 via-secondary-50/65 to-white/55 px-3 py-3 backdrop-blur-xl supports-[backdrop-filter]:bg-white/45 transition-all duration-200 ease-out lg:static lg:translate-x-0',
          isMobileOpen && 'translate-x-0',
          sidebarWidthClass
        )}
      >
        <div className="mb-4 flex h-14 items-center rounded-2xl border border-white/60 bg-white/70 px-3 shadow-[0_8px_24px_rgba(15,23,42,0.08)] backdrop-blur-md">
          <Link to="/dashboard" className="flex min-w-0 items-center gap-2.5" onClick={onCloseMobile}>
            <img src="/logo_logistic.png" alt="ShipGen" className={cn('w-auto object-contain', showLabel ? 'h-10' : 'h-8')} />
          </Link>
        </div>

        <nav className="flex-1 space-y-5 overflow-y-auto pr-1">
          <section className="space-y-1.5">
            {showLabel ? <p className="px-3.5 pb-1 text-[11px] font-semibold uppercase tracking-[0.08em] text-secondary-500">Modules</p> : null}
            {filteredItems.map((item) => {
              const isGroup = Boolean(item.children?.length);
              const isActive = isGroup
                ? pathTouchesGroup(currentPath, item)
                : currentPath === item.to || currentPath.startsWith(`${item.to}/`);

              if (isGroup) {
                const isOpen = openGroups[item.id];
                return (
                  <div key={item.id} className="space-y-1">
                    <button
                      type="button"
                      onClick={() =>
                        setOpenGroups((prev) => {
                          if (prev[item.id]) {
                            return { ...prev, [item.id]: false };
                          }
                          const next: Record<string, boolean> = { ...prev };
                          for (const m of moduleItems) {
                            if (m.children?.length) {
                              next[m.id] = m.id === item.id;
                            }
                          }
                          return next;
                        })
                      }
                      className={cn(itemBaseClass, isActive ? activeClass : idleClass, 'w-full justify-between')}
                    >
                      <span className="flex items-center">
                        <span className="shrink-0 text-secondary-500 transition-transform duration-200 group-hover:scale-105">
                          {iconMap.get(item.id) ?? customModuleIcons[item.id] ?? iconMap.get('logistics')}
                        </span>
                        {showLabel ? <span className="ml-3 truncate">{item.label}</span> : null}
                      </span>
                      {showLabel ? (isOpen ? <ChevronUp size={16} /> : <ChevronDown size={16} />) : null}
                    </button>
                    {showLabel && isOpen ? (
                      <div className="ml-4 space-y-2 border-l border-white/60 pl-3">
                        {item.children?.map((child) => {
                          const isChildActive = currentPath === child.to || currentPath.startsWith(`${child.to}/`);
                          return (
                            <Link
                              key={child.id}
                              to={child.to}
                              onClick={onCloseMobile}
                              className={cn(
                                'block rounded-xl px-3 py-2 text-sm transition-all duration-200',
                                isChildActive
                                  ? 'bg-primary-50 text-primary-700 shadow-sm ring-1 ring-primary-100/80'
                                  : 'text-secondary-600 hover:bg-blue-500/12 hover:text-blue-700 hover:shadow-[0_8px_20px_rgba(37,99,235,0.14)] hover:ring-1 hover:ring-blue-300/45 hover:backdrop-blur-md'
                              )}
                            >
                              {child.label}
                            </Link>
                          );
                        })}
                      </div>
                    ) : null}
                  </div>
                );
              }

              return (
                <Link key={item.id} to={item.to} onClick={onCloseMobile} className={cn(itemBaseClass, isActive ? activeClass : idleClass)}>
                  <span className="shrink-0 text-secondary-500 transition-transform duration-200 group-hover:scale-105">
                    {iconMap.get(item.id) ?? customModuleIcons[item.id] ?? iconMap.get('logistics')}
                  </span>
                  {showLabel ? <span className="ml-3 truncate">{item.label}</span> : null}
                </Link>
              );
            })}
          </section>

          {currentUser && isAIAssistantVisibleForRole(currentUser.role) ? (
            <section>
              <Link
                to="/ai-assistant"
                onClick={onCloseMobile}
                className={cn(
                  itemBaseClass,
                  currentPath.startsWith('/ai-assistant')
                    ? 'bg-gradient-to-r from-primary-700 to-primary-600 text-white shadow-soft'
                    : 'bg-white text-primary-700 hover:bg-primary-50'
                )}
              >
                <Sparkles size={18} />
                {showLabel ? <span className="ml-3">ShipGen AI</span> : null}
              </Link>
            </section>
          ) : null}
        </nav>

        <div className="mt-3 rounded-2xl border border-white/60 bg-white/70 p-2.5 shadow-[0_10px_28px_rgba(15,23,42,0.1)] backdrop-blur-md">
          {currentUser ? (
            <div className={cn('mb-2 flex items-center rounded-xl px-2 py-2', showLabel && 'bg-secondary-50/80')}>
              <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-primary-100 font-semibold text-primary-700">
                {currentUser.name[0]}
              </div>
              {showLabel ? (
                <div className="ml-2.5 min-w-0">
                  <p className="truncate text-sm font-semibold text-neutral-900">{currentUser.name}</p>
                  <p className="truncate text-[11px] uppercase tracking-wide text-secondary-500">{currentUser.role.replace(/_/g, ' ')}</p>
                </div>
              ) : null}
            </div>
          ) : null}
          <button
            type="button"
            data-testid="logout"
            onClick={onLogout}
            className={cn(
              'flex w-full items-center justify-center rounded-xl px-3 py-2 text-sm font-medium text-danger-600 transition-all duration-200 hover:bg-danger-50',
              showLabel ? 'gap-2' : ''
            )}
            aria-label="Sign out"
          >
            <LogOut size={16} />
            {showLabel ? <span>Sign out</span> : null}
          </button>
        </div>
      </aside>
    </>
  );
};

export default Sidebar;
