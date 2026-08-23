import React from 'react';
import { Navigate, Outlet } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

export const RoleRoute = ({ allowedRoles = [] }) => {
  const { user } = useAuth();
  const role = user?.role || 'SHIPPER';

  if (!allowedRoles.includes(role)) {
    return <Navigate to="/dashboard" replace />;
  }

  return <Outlet />;
};
