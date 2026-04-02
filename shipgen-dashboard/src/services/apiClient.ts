import { API_BASE_URL } from './api';
import { APP_MODE } from '../config/appMode';
import axios from 'axios';
import { getApiErrorMessage } from './apiErrors';

/** Prefer `PaginatedResponse<T>` from `src/types/api` for new list endpoints. */
export interface ApiResponse<T> {
  data: T;
  pagination?: {
    total: number;
    page: number;
    pageSize: number;
  };
}

export interface ApiError {
  message: string;
  code?: string;
}

class ApiClient {
  private readonly useMock = APP_MODE.useMockApi;
  private readonly http = axios.create({
    baseURL: API_BASE_URL,
    headers: { 'Content-Type': 'application/json' },
  });

  constructor() {
    this.http.interceptors.request.use((config) => {
      const token = localStorage.getItem('token');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    });

    this.http.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error?.response?.status === 401) {
          localStorage.removeItem('token');
          localStorage.removeItem('accessToken');
          localStorage.removeItem('refreshToken');
          localStorage.removeItem('user');
          window.location.href = '/#/login';
          return Promise.reject(new Error(getApiErrorMessage(error)));
        }
        return Promise.reject(new Error(getApiErrorMessage(error)));
      },
    );
  }

  private isAuthEndpoint(endpoint: string): boolean {
    return endpoint.startsWith('/int/v1/auth/');
  }

  private isAlwaysRealEndpoint(endpoint: string): boolean {
    // Orders must always come from backend to stay consistent with dashboard/analytics.
    return endpoint.startsWith('/fleetops/v1/orders');
  }

  private shouldUseMock(endpoint: string): boolean {
    if (!this.useMock) return false;
    if (this.isAuthEndpoint(endpoint)) return false;
    if (this.isAlwaysRealEndpoint(endpoint)) return false;
    return true;
  }

  private async getMockApi() {
    // Lazy-load mocks so they don't appear in Network tab unless used.
    const mod = await import('../mocks/mockApi');
    return mod.mockApi;
  }

  async get<T>(endpoint: string, params?: Record<string, any>): Promise<T> {
    if (this.shouldUseMock(endpoint)) {
      const mockApi = await this.getMockApi();
      return mockApi.get(endpoint, params) as Promise<T>;
    }
    const response = await this.http.get<T>(endpoint, { params });
    return response.data;
  }

  async post<T>(endpoint: string, data?: any): Promise<T> {
    if (this.shouldUseMock(endpoint)) {
      const mockApi = await this.getMockApi();
      return mockApi.post(endpoint, data) as Promise<T>;
    }
    const response = await this.http.post<T>(endpoint, data);
    return response.data;
  }

  async patch<T>(endpoint: string, data?: any): Promise<T> {
    if (this.shouldUseMock(endpoint)) {
      const mockApi = await this.getMockApi();
      return mockApi.patch(endpoint, data) as Promise<T>;
    }
    const response = await this.http.patch<T>(endpoint, data);
    return response.data;
  }

  async put<T>(endpoint: string, data?: any): Promise<T> {
    if (this.shouldUseMock(endpoint)) {
      const mockApi = await this.getMockApi();
      return mockApi.put(endpoint, data) as Promise<T>;
    }
    const response = await this.http.put<T>(endpoint, data);
    return response.data;
  }

  async delete<T>(endpoint: string): Promise<T> {
    if (this.shouldUseMock(endpoint)) {
      const mockApi = await this.getMockApi();
      return mockApi.delete(endpoint) as Promise<T>;
    }
    const response = await this.http.delete<T>(endpoint);
    return response.data;
  }
}

export const apiClient = new ApiClient();
