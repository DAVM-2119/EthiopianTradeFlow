import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { ProtectedRoute } from './ProtectedRoute';
import { RoleRoute } from './RoleRoute';
import { AuthLayout } from '../layouts/AuthLayout';
import { DashboardLayout } from '../layouts/DashboardLayout';
import { LoginPage } from '../pages/auth/LoginPage';
import { RegisterPage } from '../pages/auth/RegisterPage';
import { DashboardPage } from '../pages/dashboard/DashboardPage';
import { NotFoundPage } from '../pages/NotFoundPage';

export const AppRoutes = () => {
  return (
    <Routes>
      <Route element={<AuthLayout />}>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
      </Route>

      <Route element={<ProtectedRoute />}>
        <Route element={<DashboardLayout />}>
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
          <Route path="/dashboard" element={<DashboardPage />} />

          <Route path="/loads" element={<DashboardPage />} />
          <Route path="/bids" element={<DashboardPage />} />
          <Route path="/shipments" element={<DashboardPage />} />
          <Route path="/tracking" element={<DashboardPage />} />
          <Route path="/fleet/*" element={<DashboardPage />} />
          <Route path="/customs" element={<DashboardPage />} />
          <Route path="/customs/*" element={<DashboardPage />} />
          <Route path="/payments" element={<DashboardPage />} />
          <Route path="/risk" element={<DashboardPage />} />
          <Route path="/analytics" element={<DashboardPage />} />
          <Route path="/notifications" element={<DashboardPage />} />
          <Route path="/profile" element={<DashboardPage />} />

          <Route element={<RoleRoute allowedRoles={['ADMIN']} />}>
            <Route path="/admin/*" element={<DashboardPage />} />
          </Route>
        </Route>
      </Route>

      <Route path="*" element={<NotFoundPage />} />
    </Routes>
  );
};
