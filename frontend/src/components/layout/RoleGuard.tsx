import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { UserRole } from '../../types';
import { LoadingState } from '../common/LoadingState';
import { ErrorState } from '../common/ErrorState';

export interface RoleGuardProps {
  children: React.ReactNode;
  allowedRoles?: UserRole[];
}

export const RoleGuard: React.FC<RoleGuardProps> = ({
  children,
  allowedRoles,
}) => {
  const { user, isAuthenticated, isLoading } = useAuth();
  const location = useLocation();

  if (isLoading) {
    return (
      <div className="min-h-[50vh] flex items-center justify-center">
        <LoadingState message="Verifying security credentials..." />
      </div>
    );
  }

  // If not authenticated, redirect to /login with return path
  if (!isAuthenticated || !user) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  // Check role authorization (Platform Admin has root access everywhere)
  if (
    allowedRoles &&
    allowedRoles.length > 0 &&
    user.role !== 'PLATFORM_ADMIN' &&
    !allowedRoles.includes(user.role)
  ) {
    return (
      <div className="py-12">
        <ErrorState
          title="Access Forbidden (403)"
          message={`Your current role (${user.role}) is not authorized to access this resource. Allowed roles: ${allowedRoles.join(
            ', '
          )}.`}
          onRetry={() => window.history.back()}
        />
      </div>
    );
  }

  return <>{children}</>;
};
