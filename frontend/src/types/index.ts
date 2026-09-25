export type UserRole = 'STUDENT' | 'INSTRUCTOR' | 'PLATFORM_ADMIN';

export interface User {
  id: number;
  email: string;
  full_name: string;
  role: UserRole;
  is_active: boolean;
  created_at: string;
  updated_at?: string;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
  user: User;
}

export interface SubsystemHealth {
  postgresql: string;
  mongodb: string;
  redis: string;
}

export interface HealthResponse {
  status: string;
  app_name: string;
  environment: string;
  version: string;
  timestamp: string;
  subsystems?: SubsystemHealth;
}

export interface NavItem {
  name: string;
  path: string;
  icon: string;
  badge?: string;
  description?: string;
}

export * from './content';

