import { apiClient } from './apiClient';
import { UserRole, normalizeUserRole } from '../types';
import { driversService } from './driversService';

type LoginResponse = {
  token?: string;
  user?: {
    id?: string;
    email?: string;
    name?: string;
    role?: string;
  };
  type?: string;
  twoFaSession?: string;
  isEnabled?: boolean;
};

export async function login(identity: string, password: string): Promise<LoginResponse> {
  return apiClient.post<LoginResponse>('/int/v1/auth/login', {
    identity,
    email: identity,
    password,
  });
}

export async function logout() {
  // If current user is a DRIVER, set them as offline before logging out
  try {
    const userStr = localStorage.getItem('user');
    if (userStr) {
      const user = JSON.parse(userStr);
      if (user && normalizeUserRole(user.role) === UserRole.DRIVER) {
        // Account switching should not deactivate the driver profile; only mark session offline.
        await driversService.setOnline(false);
      }
    }
  } catch (err) {
    // Log error but don't block logout
    console.error('Failed to set driver offline status:', err);
  }
  
  localStorage.removeItem('token');
  localStorage.removeItem('accessToken');
  localStorage.removeItem('refreshToken');
  localStorage.removeItem('user');
  window.location.href = '/#/login';
}
