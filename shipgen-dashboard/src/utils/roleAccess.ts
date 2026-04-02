import { UserRole } from '../types';

/**
 * Role-based access control configuration
 * Defines which roles can access which sections of the application
 */

export type SectionId = 
  | 'dashboard'
  | 'logistics'
  | 'warehouse'
  | 'fleet'
  | 'live-operations'
  | 'billing'
  | 'analytics'
  | 'master-data'
  | 'ai-assistant';

export type AccessLevel = 'full' | 'read-only' | 'limited' | 'none';

interface SectionAccess {
  sectionId: SectionId;
  roles: Record<UserRole, AccessLevel>;
}

/**
 * Role-to-section access matrix
 * Based on enterprise logistics SaaS requirements
 */
export const SECTION_ACCESS: SectionAccess[] = [
  {
    sectionId: 'dashboard',
    roles: {
      [UserRole.SUPER_ADMIN]: 'full',
      [UserRole.COMPANY_ADMIN]: 'full',
      [UserRole.OPERATIONS_MANAGER]: 'full',
      [UserRole.WAREHOUSE_MANAGER]: 'full',
      [UserRole.FINANCE]: 'full',
      [UserRole.DRIVER]: 'none',
      [UserRole.CUSTOMER]: 'none',
    },
  },
  {
    sectionId: 'logistics',
    roles: {
      [UserRole.SUPER_ADMIN]: 'full',
      [UserRole.COMPANY_ADMIN]: 'full',
      [UserRole.OPERATIONS_MANAGER]: 'full',
      [UserRole.WAREHOUSE_MANAGER]: 'none',
      [UserRole.FINANCE]: 'none',
      [UserRole.DRIVER]: 'limited', // Can view assigned orders only
      [UserRole.CUSTOMER]: 'read-only', // Tracking only
    },
  },
  {
    sectionId: 'warehouse',
    roles: {
      [UserRole.SUPER_ADMIN]: 'full',
      [UserRole.COMPANY_ADMIN]: 'full',
      [UserRole.OPERATIONS_MANAGER]: 'full',
      [UserRole.WAREHOUSE_MANAGER]: 'full',
      [UserRole.FINANCE]: 'none',
      [UserRole.DRIVER]: 'none',
      [UserRole.CUSTOMER]: 'none',
    },
  },
  {
    sectionId: 'fleet',
    roles: {
      [UserRole.SUPER_ADMIN]: 'full',
      [UserRole.COMPANY_ADMIN]: 'full',
      [UserRole.OPERATIONS_MANAGER]: 'full',
      [UserRole.WAREHOUSE_MANAGER]: 'none',
      [UserRole.FINANCE]: 'none',
      [UserRole.DRIVER]: 'read-only', // Own vehicle & orders
      [UserRole.CUSTOMER]: 'none',
    },
  },
  {
    sectionId: 'live-operations',
    roles: {
      [UserRole.SUPER_ADMIN]: 'full',
      [UserRole.COMPANY_ADMIN]: 'full',
      [UserRole.OPERATIONS_MANAGER]: 'full',
      [UserRole.WAREHOUSE_MANAGER]: 'full',
      [UserRole.FINANCE]: 'none',
      [UserRole.DRIVER]: 'limited', // Own tracking only
      [UserRole.CUSTOMER]: 'none',
    },
  },
  {
    sectionId: 'billing',
    roles: {
      [UserRole.SUPER_ADMIN]: 'full',
      [UserRole.COMPANY_ADMIN]: 'full',
      [UserRole.OPERATIONS_MANAGER]: 'read-only',
      [UserRole.WAREHOUSE_MANAGER]: 'none',
      [UserRole.FINANCE]: 'full',
      [UserRole.DRIVER]: 'none',
      [UserRole.CUSTOMER]: 'none',
    },
  },
  {
    sectionId: 'analytics',
    roles: {
      [UserRole.SUPER_ADMIN]: 'full',
      [UserRole.COMPANY_ADMIN]: 'full',
      [UserRole.OPERATIONS_MANAGER]: 'full',
      [UserRole.WAREHOUSE_MANAGER]: 'none',
      [UserRole.FINANCE]: 'full',
      [UserRole.DRIVER]: 'none',
      [UserRole.CUSTOMER]: 'none',
    },
  },
  {
    sectionId: 'master-data',
    roles: {
      [UserRole.SUPER_ADMIN]: 'full',
      [UserRole.COMPANY_ADMIN]: 'full',
      [UserRole.OPERATIONS_MANAGER]: 'none',
      [UserRole.WAREHOUSE_MANAGER]: 'none',
      [UserRole.FINANCE]: 'none',
      [UserRole.DRIVER]: 'none',
      [UserRole.CUSTOMER]: 'none',
    },
  },
  {
    sectionId: 'ai-assistant',
    roles: {
      [UserRole.SUPER_ADMIN]: 'full',
      [UserRole.COMPANY_ADMIN]: 'full',
      [UserRole.OPERATIONS_MANAGER]: 'full',
      [UserRole.WAREHOUSE_MANAGER]: 'full',
      [UserRole.FINANCE]: 'full',
      [UserRole.DRIVER]: 'full',
      [UserRole.CUSTOMER]: 'none',
    },
  },
];

/**
 * Check if a role can access a section
 * @param role - User role
 * @param sectionId - Section identifier
 * @returns Access level or 'none' if not found
 */
export function canAccess(role: UserRole, sectionId: SectionId): AccessLevel {
  const section = SECTION_ACCESS.find((s) => s.sectionId === sectionId);
  if (!section) return 'none';
  return section.roles[role] || 'none';
}

/**
 * Check if a role has any access to a section (not 'none')
 * @param role - User role
 * @param sectionId - Section identifier
 * @returns true if user can access the section
 */
export function hasAccess(role: UserRole, sectionId: SectionId): boolean {
  return canAccess(role, sectionId) !== 'none';
}

/**
 * Check if a role has full access to a section
 * @param role - User role
 * @param sectionId - Section identifier
 * @returns true if user has full access
 */
export function hasFullAccess(role: UserRole, sectionId: SectionId): boolean {
  return canAccess(role, sectionId) === 'full';
}

/**
 * Check if a role has read-only access to a section
 * @param role - User role
 * @param sectionId - Section identifier
 * @returns true if user has read-only access
 */
export function hasReadOnlyAccess(role: UserRole, sectionId: SectionId): boolean {
  const access = canAccess(role, sectionId);
  return access === 'read-only' || access === 'limited';
}

/**
 * Get all sections accessible by a role
 * @param role - User role
 * @returns Array of section IDs the role can access
 */
export function getAccessibleSections(role: UserRole): SectionId[] {
  return SECTION_ACCESS.filter((section) => hasAccess(role, section.sectionId)).map(
    (section) => section.sectionId
  );
}

/**
 * Check if a route path is accessible by a role
 * @param role - User role
 * @param path - Route path (e.g., '/dashboard', '/logistics/orders')
 * @returns true if route is accessible
 */
export function canAccessRoute(role: UserRole, path: string): boolean {
  // Normalize path
  const normalizedPath = path.startsWith('/') ? path.substring(1) : path;
  const pathParts = normalizedPath.split('/');
  const sectionId = pathParts[0] as SectionId;

  // Check section access
  if (!hasAccess(role, sectionId)) {
    return false;
  }

  // Special handling for limited/read-only access
  const accessLevel = canAccess(role, sectionId);

  // DRIVER limited access to logistics (only assigned orders)
  if (role === UserRole.DRIVER && sectionId === 'logistics') {
    // Allow viewing but restrict create/edit
    if (pathParts.includes('create') || pathParts.includes('edit') || pathParts.includes('assign')) {
      return false;
    }
  }

  // DRIVER limited access to fleet (read-only own vehicle)
  if (role === UserRole.DRIVER && sectionId === 'fleet') {
    // Allow viewing but restrict create/edit
    if (pathParts.includes('create') || pathParts.includes('edit')) {
      return false;
    }
  }

  // OPERATIONS_MANAGER read-only access to billing
  if (role === UserRole.OPERATIONS_MANAGER && sectionId === 'billing') {
    // Allow viewing but restrict create/edit
    if (pathParts.includes('generate') || pathParts.includes('record')) {
      return false;
    }
  }

  return true;
}
