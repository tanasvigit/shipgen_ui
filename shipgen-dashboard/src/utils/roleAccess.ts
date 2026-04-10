import { normalizeUserRole, UserRole } from '../types';

/**
 * Role-based access control configuration
 * Defines which roles can access which sections of the application
 */

export type SectionId =
  | 'dashboard'
  | 'logistics'
  | 'warehouse'
  | 'fleet'
  | 'billing'
  | 'analytics'
  | 'ai-assistant';

export type AccessLevel = 'full' | 'read-only' | 'limited' | 'none';

interface SectionAccess {
  sectionId: SectionId;
  roles: Record<UserRole, AccessLevel>;
}

export const SECTION_ACCESS: SectionAccess[] = [
  {
    sectionId: 'dashboard',
    roles: {
      [UserRole.ADMIN]: 'full',
      [UserRole.OPERATIONS_MANAGER]: 'full',
      [UserRole.DISPATCHER]: 'full',
      [UserRole.DRIVER]: 'none',
      [UserRole.VIEWER]: 'read-only', // VIEWER can access Dashboard
    },
  },
  {
    sectionId: 'logistics',
    roles: {
      [UserRole.ADMIN]: 'full',
      [UserRole.OPERATIONS_MANAGER]: 'full',
      [UserRole.DISPATCHER]: 'full',
      [UserRole.DRIVER]: 'limited',
      [UserRole.VIEWER]: 'read-only', // VIEWER can access Orders & Customers
    },
  },
  {
    sectionId: 'warehouse',
    roles: {
      [UserRole.ADMIN]: 'full',
      [UserRole.OPERATIONS_MANAGER]: 'full',
      [UserRole.DISPATCHER]: 'none',
      [UserRole.DRIVER]: 'none',
      [UserRole.VIEWER]: 'none', // VIEWER cannot access Warehouse
    },
  },
  {
    sectionId: 'fleet',
    roles: {
      [UserRole.ADMIN]: 'full',
      [UserRole.OPERATIONS_MANAGER]: 'full',
      [UserRole.DISPATCHER]: 'read-only',
      [UserRole.DRIVER]: 'none',
      [UserRole.VIEWER]: 'read-only', // VIEWER can access Drivers, Vehicles, Fleet Dashboard
    },
  },
  {
    sectionId: 'billing',
    roles: {
      [UserRole.ADMIN]: 'full',
      [UserRole.OPERATIONS_MANAGER]: 'read-only',
      [UserRole.DISPATCHER]: 'none',
      [UserRole.DRIVER]: 'none',
      [UserRole.VIEWER]: 'none', // VIEWER: hidden for now, will add later
    },
  },
  {
    sectionId: 'analytics',
    roles: {
      [UserRole.ADMIN]: 'full',
      [UserRole.OPERATIONS_MANAGER]: 'full',
      [UserRole.DISPATCHER]: 'read-only',
      [UserRole.DRIVER]: 'none',
      [UserRole.VIEWER]: 'none', // VIEWER: hidden for now, will add later
    },
  },
  {
    sectionId: 'ai-assistant',
    roles: {
      [UserRole.ADMIN]: 'full',
      [UserRole.OPERATIONS_MANAGER]: 'full',
      [UserRole.DISPATCHER]: 'full',
      [UserRole.DRIVER]: 'none',
      [UserRole.VIEWER]: 'none', // VIEWER cannot access AI Assistant
    },
  },
];

export function canAccess(role: UserRole, sectionId: SectionId): AccessLevel {
  const section = SECTION_ACCESS.find((s) => s.sectionId === sectionId);
  if (!section) return 'none';
  return section.roles[role] || 'none';
}

export function hasAccess(role: UserRole, sectionId: SectionId): boolean {
  return canAccess(role, sectionId) !== 'none';
}

export function hasFullAccess(role: UserRole, sectionId: SectionId): boolean {
  return canAccess(role, sectionId) === 'full';
}

export function hasReadOnlyAccess(role: UserRole, sectionId: SectionId): boolean {
  const access = canAccess(role, sectionId);
  return access === 'read-only' || access === 'limited';
}

export function getAccessibleSections(role: UserRole): SectionId[] {
  return SECTION_ACCESS.filter((section) => hasAccess(role, section.sectionId)).map(
    (section) => section.sectionId
  );
}

/** Read normalized role from localStorage `user` (set at login). */
export function getStoredUserRole(): UserRole | null {
  if (typeof localStorage === 'undefined') return null;
  const raw = localStorage.getItem('user');
  if (!raw) return null;
  try {
    const u = JSON.parse(raw) as { role?: string };
    return normalizeUserRole(u.role);
  } catch {
    return null;
  }
}

export function canManageUsers(role: UserRole): boolean {
  return role === UserRole.ADMIN || role === UserRole.OPERATIONS_MANAGER;
}

export function canDeleteUsers(role: UserRole): boolean {
  return role === UserRole.ADMIN;
}

export function canDeleteOrders(role: UserRole): boolean {
  return role === UserRole.ADMIN;
}

export function canCreateOrders(role: UserRole): boolean {
  return role === UserRole.ADMIN || role === UserRole.OPERATIONS_MANAGER || role === UserRole.DISPATCHER;
}

export function canEditOrders(role: UserRole): boolean {
  return canCreateOrders(role);
}

export function canAssignOrDispatchOrders(role: UserRole): boolean {
  return role === UserRole.ADMIN || role === UserRole.OPERATIONS_MANAGER || role === UserRole.DISPATCHER;
}

/** Driver/vehicle master-data ownership is with admin + operations manager, not dispatcher. */
export function canManageDriverVehicleMasterData(role: UserRole): boolean {
  return role === UserRole.ADMIN || role === UserRole.OPERATIONS_MANAGER;
}

/** Driver/vehicle delete remains admin-only. */
export function canDeleteDriverVehicleMasterData(role: UserRole): boolean {
  return role === UserRole.ADMIN;
}

export function canAccessCustomersModule(role: UserRole): boolean {
  return role !== UserRole.DRIVER;
}

export function isViewerReadOnly(role: UserRole): boolean {
  return role === UserRole.VIEWER;
}

export function canMutateCustomers(role: UserRole): boolean {
  return role === UserRole.ADMIN || role === UserRole.OPERATIONS_MANAGER || role === UserRole.DISPATCHER;
}

export function canDeleteCustomers(role: UserRole): boolean {
  return role === UserRole.ADMIN;
}

/** Sidebar module ids for VIEWER: Dashboard, Logistics, Fleet & Operations only. */
const VIEWER_SIDEBAR_MODULE_IDS = new Set(['dashboard', 'logistics', 'fleet-operations']);
/** Sidebar module ids for DISPATCHER: core operational modules only. */
const DISPATCHER_SIDEBAR_MODULE_IDS = new Set([
  'dashboard',
  'logistics',
  'fleet-operations',
  'locations-coverage',
  'tracking',
  'business-entities',
  'operations-execution',
]);

export function isSidebarModuleVisibleForRole(role: UserRole, moduleId: string): boolean {
  if (role === UserRole.VIEWER) {
    return VIEWER_SIDEBAR_MODULE_IDS.has(moduleId);
  }
  if (role === UserRole.DISPATCHER) {
    return DISPATCHER_SIDEBAR_MODULE_IDS.has(moduleId);
  }
  return true;
}

export function isAIAssistantVisibleForRole(role: UserRole): boolean {
  return role !== UserRole.DISPATCHER && hasAccess(role, 'ai-assistant');
}

/**
 * Routes a VIEWER may open — aligned with the first three sidebar modules (plus profile).
 * Must run before section-based hasAccess (e.g. analytics/devices is allowed though SectionId analytics is "none").
 */
function isViewerAllowedNavPath(normalizedPath: string): boolean {
  if (normalizedPath === 'profile') return true;

  if (normalizedPath === 'dashboard' || normalizedPath.startsWith('dashboard/')) return true;

  if (normalizedPath === 'logistics' || normalizedPath.startsWith('logistics/')) {
    if (normalizedPath.includes('dispatch-board')) return false;
    if (normalizedPath === 'logistics' || normalizedPath.startsWith('logistics/orders')) return true;
    if (normalizedPath.startsWith('logistics/customers')) return true;
    return false;
  }

  if (normalizedPath === 'fleet' || normalizedPath.startsWith('fleet/')) {
    if (normalizedPath === 'fleet' || normalizedPath === 'fleet/dashboard' || normalizedPath.startsWith('fleet/dashboard/')) {
      return true;
    }
    if (normalizedPath === 'fleet/fleets' || normalizedPath.startsWith('fleet/fleets/')) return true;
    if (normalizedPath === 'fleet/vehicles' || normalizedPath.startsWith('fleet/vehicles/')) return true;
    if (normalizedPath === 'fleet/drivers' || normalizedPath.startsWith('fleet/drivers/')) return true;
    return false;
  }

  if (normalizedPath === 'analytics/devices' || normalizedPath.startsWith('analytics/devices/')) return true;

  return false;
}

/** Routes a DISPATCHER may open — focused on dispatch operations and execution only. */
function isDispatcherAllowedNavPath(normalizedPath: string): boolean {
  if (normalizedPath === 'profile') return true;

  if (normalizedPath === 'dashboard' || normalizedPath.startsWith('dashboard/')) return true;

  if (normalizedPath === 'logistics' || normalizedPath.startsWith('logistics/')) {
    if (normalizedPath === 'logistics' || normalizedPath.startsWith('logistics/orders')) return true;
    if (normalizedPath.startsWith('logistics/customers')) return true;
    return false;
  }

  if (normalizedPath === 'fleet' || normalizedPath.startsWith('fleet/')) {
    if (normalizedPath === 'fleet' || normalizedPath.startsWith('fleet/dashboard')) return true;
    if (normalizedPath.startsWith('fleet/vehicles')) return true;
    if (normalizedPath.startsWith('fleet/drivers')) return true;
    if (normalizedPath.startsWith('fleet/fleets')) return true;
    if (normalizedPath.startsWith('fleet/service-areas')) return true;
    if (normalizedPath.startsWith('fleet/zones')) return true;
    if (normalizedPath.startsWith('fleet/places')) return true;
    if (normalizedPath.startsWith('fleet/tracking-numbers')) return true;
    if (normalizedPath.startsWith('fleet/tracking-statuses')) return true;
    if (normalizedPath.startsWith('fleet/contacts')) return true;
    if (normalizedPath.startsWith('fleet/vendors')) return true;
    if (normalizedPath.startsWith('fleet/entities')) return true;
    if (normalizedPath.startsWith('fleet/payloads')) return true;
    if (normalizedPath.startsWith('fleet/issues')) return true;
    return false;
  }

  if (normalizedPath.startsWith('analytics/devices')) return true;
  if (normalizedPath.startsWith('analytics/companies')) return true;
  if (normalizedPath.startsWith('analytics/activities')) return true;
  if (normalizedPath.startsWith('analytics/transactions')) return true;
  if (normalizedPath.startsWith('analytics/comments')) return true;

  return false;
}

export function canAccessRoute(role: UserRole, path: string): boolean {
  const normalizedPath = path.startsWith('/') ? path.substring(1) : path;

  if (role === UserRole.DRIVER) {
    // Driver UI is intentionally minimal: assigned orders + profile only.
    if (normalizedPath === 'profile') return true;
    if (normalizedPath === 'logistics/orders/dispatch-board' || normalizedPath.startsWith('logistics/orders/dispatch-board/')) {
      return false;
    }
    if (normalizedPath === 'logistics/orders' || normalizedPath.startsWith('logistics/orders/')) return true;
    if (normalizedPath === 'logistics') return true;
    return false;
  }

  if (normalizedPath === 'analytics/users' || normalizedPath.startsWith('analytics/users/')) {
    return role === UserRole.ADMIN;
  }

  if (role === UserRole.VIEWER) {
    if (!isViewerAllowedNavPath(normalizedPath)) return false;
    const pathParts = normalizedPath.split('/');
    if (pathParts.includes('create') || pathParts.includes('edit') || pathParts.includes('new')) return false;
    return true;
  }

  if (role === UserRole.DISPATCHER) {
    if (!isDispatcherAllowedNavPath(normalizedPath)) return false;
    const pathParts = normalizedPath.split('/');
    if (
      (normalizedPath.startsWith('fleet/drivers') || normalizedPath.startsWith('fleet/vehicles')) &&
      (pathParts.includes('create') || pathParts.includes('edit') || pathParts.includes('new'))
    ) {
      return false;
    }
  }

  const pathParts = normalizedPath.split('/');
  const sectionId = pathParts[0] as SectionId;

  if (!hasAccess(role, sectionId)) {
    return false;
  }

  if (role === UserRole.OPERATIONS_MANAGER && sectionId === 'billing') {
    if (pathParts.includes('generate') || pathParts.includes('record')) {
      return false;
    }
  }

  return true;
}

/**
 * Get a user-friendly display label for a role.
 * VIEWER is labeled as "Viewer (Read-only)" to clarify it's an internal role, not a customer.
 */
export function getRoleDisplayLabel(role: UserRole | string): string {
  const normalized = normalizeUserRole(role);
  
  switch (normalized) {
    case UserRole.ADMIN:
      return 'Admin';
    case UserRole.OPERATIONS_MANAGER:
      return 'Operations Manager';
    case UserRole.DISPATCHER:
      return 'Dispatcher';
    case UserRole.DRIVER:
      return 'Driver';
    case UserRole.VIEWER:
      return 'Viewer (Read-only)';
    default:
      return role as string;
  }
}
