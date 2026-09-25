import { apiClient } from './apiClient';
import { TokenResponse, User, UserRole } from '../types';

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface RegisterCredentials {
  email: string;
  password: string;
  full_name: string;
  role: UserRole;
}

export const authService = {
  async login(credentials: LoginCredentials): Promise<TokenResponse> {
    const response = await apiClient.post<TokenResponse>('/api/v1/auth/login', credentials);
    return response.data;
  },

  async register(credentials: RegisterCredentials): Promise<TokenResponse> {
    const response = await apiClient.post<TokenResponse>('/api/v1/auth/register', credentials);
    return response.data;
  },

  async getCurrentUser(): Promise<User> {
    const response = await apiClient.get<User>('/api/v1/auth/me');
    return response.data;
  },

  async refreshToken(refreshToken: string): Promise<TokenResponse> {
    const response = await apiClient.post<TokenResponse>('/api/v1/auth/refresh', {
      refresh_token: refreshToken,
    });
    return response.data;
  },

  async logout(refreshToken?: string | null): Promise<void> {
    try {
      await apiClient.post('/api/v1/auth/logout', {
        refresh_token: refreshToken || undefined,
      });
    } catch (e) {
      // Ignore network errors on logout
      console.warn('Logout notification to backend failed:', e);
    }
  },
};
