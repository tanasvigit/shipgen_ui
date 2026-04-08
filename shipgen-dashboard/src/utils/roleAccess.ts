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
      [UserRole.VIEWER]: 'read-only',
    },
  },
  {
    sectionId: 'logistics',
    roles: {
      [UserRole.ADMIN]: 'full',
      [UserRole.OPERATIONS_MANAGER]: 'full',
      [UserRole.DISPATCHER]: 'full',
      [UserRole.DRIVER]: 'limited',
      [UserRole.VIEWER]: 'read-only',
    },
  },
  {
    sectionId: 'warehouse',
    roles: {
      [UserRole.ADMIN]: 'full',
      [UserRole.OPERATIONS_MANAGER]: 'full',
      [UserRole.DISPATCHER]: 'none',
      [UserRole.DRIVER]: 'none',
      [UserRole.VIEWER]: 'read-only',
    },
  },
  {
    sectionId: 'fleet',
    roles: {
      [UserRole.ADMIN]: 'full',
      [UserRole.OPERATIONS_MANAGER]: 'full',
      [UserRole.DISPATCHER]: 'read-only',
      [UserRole.DRIVER]: 'none',
      [UserRole.VIEWER]: 'read-only',
    },
  },
  {
    sectionId: 'billing',
    roles: {
      [UserRole.ADMIN]: 'full',
      [UserRole.OPERATIONS_MANAGER]: 'read-only',
      [UserRole.DISPATCHER]: 'none',
      [UserRole.DRIVER]: 'none',
      [UserRole.VIEWER]: 'read-only',
    },
  },
  {
    sectionId: 'analytics',
    roles: {
      [UserRole.ADMIN]: 'full',
      [UserRole.OPERATIONS_MANAGER]: 'full',
      [UserRole.DISPATCHER]: 'read-only',
      [UserRole.DRIVER]: 'none',
      [UserRole.VIEWER]: 'read-only',
    },
  },
  {
    sectionId: 'ai-assistant',
    roles: {
      [UserRole.ADMIN]: 'full',
      [UserRole.OPERATIONS_MANAGER]: 'full',
      [UserRole.DISPATCHER]: 'full',
      [UserRole.DRIVER]: 'none',
      [UserRole.VIEWER]: 'read-only',
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

export function canAccessRoute(role: UserRole, path: string): boolean {
  const normalizedPath = path.startsWith('/') ? path.substring(1) : path;

  if (role === UserRole.DRIVER) {
    // Driver UI is intentionally minimal: assigned orders + profile only.
    if (normalizedPath === 'profile') return true;
    if (normalizedPath === 'logistics/orders' || normalizedPath.startsWith('logistics/orders/')) return true;
    if (normalizedPath === 'logistics') return true;
    return false;
  }

  if (normalizedPath === 'analytics/users' || normalizedPath.startsWith('analytics/users/')) {
    return role === UserRole.ADMIN;
  }

  if (normalizedPath === 'logistics/customers' || normalizedPath.startsWith('logistics/customers/')) {
    if (role === UserRole.DRIVER) return false;
  }

  if (
    normalizedPath === 'logistics/orders/dispatch-board' ||
    normalizedPath.startsWith('logistics/orders/dispatch-board')
  ) {
    if (role === UserRole.DRIVER || role === UserRole.VIEWER) return false;
  }

  if (normalizedPath.includes('/orders/create') || normalizedPath.endsWith('orders/create')) {
    if (role === UserRole.VIEWER || role === UserRole.DRIVER) return false;
  }

  const pathParts = normalizedPath.split('/');
  const sectionId = pathParts[0] as SectionId;

  if (!hasAccess(role, sectionId)) {
    return false;
  }

  const accessLevel = canAccess(role, sectionId);

  if (role === UserRole.DRIVER && sectionId === 'logistics') {
    if (pathParts.includes('create') || pathParts.includes('edit') || pathParts.includes('assign')) {
      return false;
    }
  }

  if (role === UserRole.DRIVER && sectionId === 'fleet') {
    if (pathParts.includes('create') || pathParts.includes('edit')) {
      return false;
    }
  }

  if (role === UserRole.OPERATIONS_MANAGER && sectionId === 'billing') {
    if (pathParts.includes('generate') || pathParts.includes('record')) {
      return false;
    }
  }

  if (role === UserRole.VIEWER && accessLevel === 'read-only') {
    if (pathParts.includes('create') || pathParts.includes('edit') || pathParts.includes('new')) {
      return false;
    }
  }

  return true;
}
