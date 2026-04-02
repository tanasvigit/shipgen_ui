import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { UserRole } from '../types';
import { canAccessRoute } from '../utils/roleAccess';
import { APP_MODE } from '../config/appMode';

interface RoleGuardProps {
  children: React.ReactElement;
  userRole: UserRole | null;
  requiredRole?: UserRole[];
  fallbackPath?: string;
}

/**
 * Route guard component that checks if user has access to a route
 * Redirects to fallback path or dashboard if access is denied
 */
const RoleGuard: React.FC<RoleGuardProps> = ({
  children,
  userRole,
  requiredRole,
  fallbackPath,
}) => {
  if (APP_MODE.disableAuth) {
    return children;
  }

  const location = useLocation();

  // If no user role, redirect to login
  if (!userRole) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  // If specific roles are required, check them
  if (requiredRole && !requiredRole.includes(userRole)) {
    return <Navigate to={fallbackPath || '/dashboard'} replace />;
  }

  // Check route access using roleAccess utility
  if (!canAccessRoute(userRole, location.pathname)) {
    return <Navigate to={fallbackPath || '/dashboard'} replace />;
  }

  return children;
};

export default RoleGuard;
