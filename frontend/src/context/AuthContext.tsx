import React, { createContext, useContext, useState, useEffect } from 'react';
import { User, UserRole, TokenResponse } from '../types';
import { authService, LoginCredentials, RegisterCredentials } from '../services/authService';

interface AuthContextType {
  user: User | null;
  accessToken: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (credentials: LoginCredentials) => Promise<TokenResponse>;
  register: (credentials: RegisterCredentials) => Promise<TokenResponse>;
  logout: () => Promise<void>;
  hasRole: (role: UserRole) => boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(() => {
    const saved = localStorage.getItem('lms_user');
    return saved ? JSON.parse(saved) : null;
  });
  const [accessToken, setAccessToken] = useState<string | null>(() => {
    return localStorage.getItem('lms_access_token');
  });
  const [isLoading, setIsLoading] = useState<boolean>(true);

  useEffect(() => {
    // Validate current token session on initial mount
    const checkActiveSession = async () => {
      const token = localStorage.getItem('lms_access_token');
      if (token) {
        try {
          const activeUser = await authService.getCurrentUser();
          setUser(activeUser);
          localStorage.setItem('lms_user', JSON.stringify(activeUser));
        } catch {
          // Token expired or invalid
          setUser(null);
          setAccessToken(null);
          localStorage.removeItem('lms_access_token');
          localStorage.removeItem('lms_refresh_token');
          localStorage.removeItem('lms_user');
        }
      }
      setIsLoading(false);
    };

    checkActiveSession();
  }, []);

  const login = async (credentials: LoginCredentials): Promise<TokenResponse> => {
    setIsLoading(true);
    try {
      const data = await authService.login(credentials);
      setUser(data.user);
      setAccessToken(data.access_token);
      localStorage.setItem('lms_access_token', data.access_token);
      localStorage.setItem('lms_refresh_token', data.refresh_token);
      localStorage.setItem('lms_user', JSON.stringify(data.user));
      return data;
    } finally {
      setIsLoading(false);
    }
  };

  const register = async (credentials: RegisterCredentials): Promise<TokenResponse> => {
    setIsLoading(true);
    try {
      const data = await authService.register(credentials);
      setUser(data.user);
      setAccessToken(data.access_token);
      localStorage.setItem('lms_access_token', data.access_token);
      localStorage.setItem('lms_refresh_token', data.refresh_token);
      localStorage.setItem('lms_user', JSON.stringify(data.user));
      return data;
    } finally {
      setIsLoading(false);
    }
  };

  const logout = async (): Promise<void> => {
    const refreshToken = localStorage.getItem('lms_refresh_token');
    await authService.logout(refreshToken);
    setUser(null);
    setAccessToken(null);
    localStorage.removeItem('lms_access_token');
    localStorage.removeItem('lms_refresh_token');
    localStorage.removeItem('lms_user');
  };

  const hasRole = (role: UserRole): boolean => {
    if (!user) return false;
    if (user.role === 'PLATFORM_ADMIN') return true;
    return user.role === role;
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        accessToken,
        isAuthenticated: !!user && !!accessToken,
        isLoading,
        login,
        register,
        logout,
        hasRole,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
