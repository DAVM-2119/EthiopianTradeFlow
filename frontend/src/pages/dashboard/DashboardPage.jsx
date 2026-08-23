import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { useAuth } from '../../contexts/AuthContext';
import { PageHeader } from '../../components/common/PageHeader';
import { LoadingSpinner } from '../../components/common/LoadingSpinner';
import { ErrorMessage } from '../../components/common/ErrorMessage';
import apiClient from '../../api/axios';
import { API_ENDPOINTS } from '../../api/endpoints';

import { ShipperDashboard } from './ShipperDashboard';
import { TransporterDashboard } from './TransporterDashboard';
import { DriverDashboard } from './DriverDashboard';
import { FreightForwarderDashboard } from './FreightForwarderDashboard';
import { CustomsStaffDashboard } from './CustomsStaffDashboard';
import { AdminDashboard } from './AdminDashboard';

export const DashboardPage = () => {
  const { user } = useAuth();
  const role = user?.role || 'SHIPPER';

  const { data: summary, isLoading, error, refetch } = useQuery({
    queryKey: ['dashboard-summary', role],
    queryFn: async () => {
      const res = await apiClient.get(API_ENDPOINTS.DASHBOARD_SUMMARY);
      return res.data?.data || res.data;
    },
    staleTime: 60 * 1000,
  });

  if (isLoading) return <LoadingSpinner label="Loading TradeFlow operational dashboard metrics..." />;
  if (error) return <ErrorMessage title="Dashboard API Error" message={error.message} onRetry={refetch} />;

  const renderDashboardByRole = () => {
    switch (role) {
      case 'TRANSPORTER':
        return <TransporterDashboard summary={summary} />;
      case 'DRIVER':
        return <DriverDashboard summary={summary} />;
      case 'FREIGHT_FORWARDER':
        return <FreightForwarderDashboard summary={summary} />;
      case 'CUSTOMS_STAFF':
        return <CustomsStaffDashboard summary={summary} />;
      case 'ADMIN':
        return <AdminDashboard summary={summary} />;
      case 'SHIPPER':
      default:
        return <ShipperDashboard summary={summary} />;
    }
  };

  return (
    <div>
      <PageHeader
        title={`${role} Control Center`}
        subtitle={`Live metrics and freight movement along the Djibouti Port ➔ Modjo Dry Port corridor.`}
      />
      {renderDashboardByRole()}
    </div>
  );
};
