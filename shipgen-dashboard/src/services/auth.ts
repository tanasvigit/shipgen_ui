import { apiClient } from './apiClient';

type LoginResponse = {
  token?: string;
  user?: {
    id?: string;
    email?: string;
    name?: string;
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

export function logout() {
  localStorage.removeItem('token');
  localStorage.removeItem('accessToken');
  localStorage.removeItem('refreshToken');
  localStorage.removeItem('user');
  window.location.href = '/#/login';
}
