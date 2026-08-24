import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { ProtectedRoute } from './ProtectedRoute';
import { RoleRoute } from './RoleRoute';
import { AuthLayout } from '../layouts/AuthLayout';
import { DashboardLayout } from '../layouts/DashboardLayout';
import { LoginPage } from '../pages/auth/LoginPage';
import { RegisterPage } from '../pages/auth/RegisterPage';
import { DashboardPage } from '../pages/dashboard/DashboardPage';
import { ProfilePage } from '../pages/profile/ProfilePage';
import { EditProfilePage } from '../pages/profile/EditProfilePage';
import { ChangePasswordPage } from '../pages/profile/ChangePasswordPage';

// Marketplace & Loads & Bids Pages
import { LoadsPage } from '../pages/loads/LoadsPage';
import { CreateLoadPage } from '../pages/loads/CreateLoadPage';
import { LoadDetailsPage } from '../pages/loads/LoadDetailsPage';
import { EditLoadPage } from '../pages/loads/EditLoadPage';
import { MyBidsPage } from '../pages/bids/MyBidsPage';
import { BidDetailsPage } from '../pages/bids/BidDetailsPage';

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

          {/* User Profile Sub-routes */}
          <Route path="/profile" element={<ProfilePage />} />
          <Route path="/profile/edit" element={<EditProfilePage />} />
          <Route path="/profile/change-password" element={<ChangePasswordPage />} />

          {/* Phase 23.5 Marketplace & Loads Sub-routes */}
          <Route path="/loads" element={<LoadsPage />} />
          <Route path="/marketplace" element={<LoadsPage />} />
          <Route path="/loads/create" element={<CreateLoadPage />} />
          <Route path="/loads/:id" element={<LoadDetailsPage />} />
          <Route path="/loads/:id/edit" element={<EditLoadPage />} />

          {/* Phase 23.6 Bidding & Booking Sub-routes */}
          <Route path="/bids" element={<MyBidsPage />} />
          <Route path="/bids/:id" element={<BidDetailsPage />} />

          {/* Future Sub-phase Domain Shell Placeholders */}
          <Route path="/shipments" element={<DashboardPage />} />

          <Route path="/tracking" element={<DashboardPage />} />
          <Route path="/fleet/*" element={<DashboardPage />} />
          <Route path="/customs" element={<DashboardPage />} />
          <Route path="/customs/*" element={<DashboardPage />} />
          <Route path="/payments" element={<DashboardPage />} />
          <Route path="/risk" element={<DashboardPage />} />
          <Route path="/analytics" element={<DashboardPage />} />
          <Route path="/notifications" element={<DashboardPage />} />

          <Route element={<RoleRoute allowedRoles={['ADMIN']} />}>
            <Route path="/admin/*" element={<DashboardPage />} />
          </Route>
        </Route>
      </Route>

      <Route path="*" element={<NotFoundPage />} />
    </Routes>
  );
};
