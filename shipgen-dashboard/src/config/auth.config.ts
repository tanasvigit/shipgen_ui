/**
 * Authentication Configuration
 * Development credentials for superadmin access
 * 
 * IMPORTANT: In production, these should be managed by the backend API
 */

import { User, UserRole } from '../types';

export const SUPERADMIN_CREDENTIALS = {
  email: 'superadmin@ShipGen.com',
  password: 'SuperAdmin@123',
};

export const SUPERADMIN_USER: User = {
  id: 'sa-1',
  name: 'Super Administrator',
  email: SUPERADMIN_CREDENTIALS.email,
  role: UserRole.SUPER_ADMIN,
  company_id: 'system',
};

/**
 * Development mode flag
 * Set VITE_DEV_AUTH=true in .env to enable local authentication fallback.
 * Defaults to false so that the frontend always uses the real backend auth.
 */
export const DEV_MODE = import.meta.env.VITE_DEV_AUTH === 'true';

/**
 * Generate a mock access token for development
 */
export function generateMockToken(): string {
  return `dev_token_${btoa(JSON.stringify({ 
    userId: SUPERADMIN_USER.id, 
    role: SUPERADMIN_USER.role,
    exp: Date.now() + 24 * 60 * 60 * 1000 // 24 hours
  }))}`;
}
