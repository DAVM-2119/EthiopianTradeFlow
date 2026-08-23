import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import { PageHeader } from '../../components/common/PageHeader';
import { StatusBadge } from '../../components/common/StatusBadge';
import { LoadingSpinner } from '../../components/common/LoadingSpinner';
import apiClient from '../../api/axios';
import { API_ENDPOINTS } from '../../api/endpoints';
import { Mail, Phone, Edit3, Key, Building, CheckCircle2 } from 'lucide-react';

export const ProfilePage = () => {
  const { user } = useAuth();
  const [businessProfile, setBusinessProfile] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchBusinessProfile = async () => {
      try {
        const res = await apiClient.get(API_ENDPOINTS.PROFILE);
        setBusinessProfile(res.data?.data || res.data);
      } catch (err) {
        // Business profile optional fallback
      } finally {
        setLoading(false);
      }
    };
    fetchBusinessProfile();
  }, []);

  if (loading) return <LoadingSpinner label="Loading user profile data..." />;

  const role = user?.role || 'SHIPPER';

  return (
    <div>
      <PageHeader
        title="Account & Profile Settings"
        subtitle={`Manage your identity, role attributes, and business credentials on TradeFlow Ethiopia.`}
        actions={
          <div className="flex space-x-2">
            <Link
              to="/profile/edit"
              className="px-4 py-2 bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-white font-semibold text-xs rounded-xl shadow-lg shadow-cyan-500/20 transition flex items-center space-x-1.5"
            >
              <Edit3 className="w-4 h-4" />
              <span>Edit Profile</span>
            </Link>
            <Link
              to="/profile/change-password"
              className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 font-semibold text-xs rounded-xl border border-slate-700 transition flex items-center space-x-1.5"
            >
              <Key className="w-4 h-4 text-cyan-400" />
              <span>Change Password</span>
            </Link>
          </div>
        }
      />

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-4">
          <div className="flex items-center space-x-4 pb-4 border-b border-slate-800">
            <div className="w-14 h-14 rounded-2xl bg-gradient-to-tr from-cyan-500 to-blue-600 text-white flex items-center justify-center font-black text-2xl shadow-lg shadow-cyan-500/20">
              {user?.first_name?.[0] || user?.email?.[0]?.toUpperCase() || 'U'}
            </div>
            <div>
              <h3 className="text-lg font-extrabold text-white">
                {user?.first_name} {user?.last_name}
              </h3>
              <p className="text-xs text-cyan-400 font-semibold uppercase tracking-wider">{role}</p>
            </div>
          </div>

          <div className="space-y-3 text-xs">
            <div className="flex items-center space-x-3 text-slate-300">
              <Mail className="w-4 h-4 text-cyan-400 shrink-0" />
              <span className="truncate">{user?.email}</span>
            </div>
            <div className="flex items-center space-x-3 text-slate-300">
              <Phone className="w-4 h-4 text-cyan-400 shrink-0" />
              <span>{user?.phone_number || 'Not provided'}</span>
            </div>
            <div className="flex items-center justify-between pt-2 border-t border-slate-800">
              <span className="text-slate-400">Account Status:</span>
              <StatusBadge status={user?.status || 'VERIFIED'} />
            </div>
            <div className="flex items-center justify-between">
              <span className="text-slate-400">Verification:</span>
              <StatusBadge status={user?.is_verified ? 'VERIFIED' : 'PENDING'} />
            </div>
          </div>
        </div>

        <div className="lg:col-span-2 glass-panel p-6 rounded-2xl border border-slate-800">
          <div className="flex items-center justify-between mb-4 pb-3 border-b border-slate-800">
            <h3 className="text-base font-bold text-white flex items-center space-x-2">
              <Building className="w-5 h-5 text-cyan-400" />
              <span>Role Profile Details ({role})</span>
            </h3>
            <span className="text-xs font-semibold px-2.5 py-1 rounded-full bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
              Verified Business
            </span>
          </div>

          {businessProfile ? (
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
              {Object.entries(businessProfile)
                .filter(([k]) => !['id', 'user', 'created_at', 'updated_at'].includes(k))
                .map(([key, value]) => (
                  <div key={key} className="p-3 bg-slate-900/60 rounded-xl border border-slate-800/80">
                    <p className="text-[10px] text-slate-400 uppercase font-semibold">
                      {key.replace(/_/g, ' ')}
                    </p>
                    <p className="text-sm font-semibold text-slate-100 mt-1 truncate">
                      {typeof value === 'boolean' ? (value ? 'Yes' : 'No') : String(value || 'N/A')}
                    </p>
                  </div>
                ))}
            </div>
          ) : (
            <div className="p-8 text-center bg-slate-900/40 rounded-xl border border-slate-800">
              <CheckCircle2 className="w-8 h-8 text-cyan-400 mx-auto mb-2" />
              <p className="text-xs text-slate-300 font-medium">
                Standard {role} account profile active. No additional business verification forms pending.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
