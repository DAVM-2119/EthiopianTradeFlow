import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { PageHeader } from '../../components/common/PageHeader';
import apiClient from '../../api/axios';
import { API_ENDPOINTS } from '../../api/endpoints';
import { Key, ArrowLeft, AlertCircle, Check } from 'lucide-react';

export const ChangePasswordPage = () => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    old_password: '',
    new_password: '',
    new_password_confirm: '',
  });

  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [submitting, setSubmitting] = useState(false);

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    if (formData.new_password !== formData.new_password_confirm) {
      setError('New passwords do not match. Please try again.');
      return;
    }

    if (formData.new_password === formData.old_password) {
      setError('New password must be different from your old password.');
      return;
    }

    setSubmitting(true);
    try {
      await apiClient.post(API_ENDPOINTS.PASSWORD_CHANGE, formData);
      setSuccess('Password changed successfully!');
      setFormData({ old_password: '', new_password: '', new_password_confirm: '' });
      setTimeout(() => navigate('/profile'), 1500);
    } catch (err) {
      const resp = err.response?.data;
      if (typeof resp === 'object' && resp !== null) {
        const firstKey = Object.keys(resp)[0];
        const val = resp[firstKey];
        const errorText = Array.isArray(val) ? val[0] : String(val);
        setError(`${firstKey.replace('_', ' ')}: ${errorText}`);
      } else {
        setError('Failed to update password. Please verify your current password and try again.');
      }
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="max-w-xl mx-auto">
      <PageHeader
        title="Change Password"
        subtitle="Ensure your account credentials meet security standards."
        actions={
          <button
            onClick={() => navigate('/profile')}
            className="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-xl text-xs font-semibold flex items-center space-x-1 transition"
          >
            <ArrowLeft className="w-4 h-4" />
            <span>Cancel</span>
          </button>
        }
      />

      <div className="glass-panel p-6 sm:p-8 rounded-2xl border border-slate-800">
        {error && (
          <div className="mb-4 p-3 bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs rounded-xl flex items-center space-x-2">
            <AlertCircle className="w-4 h-4 text-rose-400 shrink-0" />
            <span>{error}</span>
          </div>
        )}

        {success && (
          <div className="mb-4 p-3 bg-emerald-500/10 border border-emerald-500/30 text-emerald-300 text-xs rounded-xl flex items-center space-x-2">
            <Check className="w-4 h-4 text-emerald-400 shrink-0" />
            <span>{success}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-1">Current Password</label>
            <input
              type="password"
              name="old_password"
              required
              value={formData.old_password}
              onChange={handleChange}
              placeholder="••••••••"
              className="w-full px-3.5 py-2.5 bg-slate-900/80 border border-slate-800 rounded-xl text-sm text-white focus:outline-none focus:border-cyan-500 transition"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-1">New Password</label>
            <input
              type="password"
              name="new_password"
              required
              value={formData.new_password}
              onChange={handleChange}
              placeholder="••••••••"
              className="w-full px-3.5 py-2.5 bg-slate-900/80 border border-slate-800 rounded-xl text-sm text-white focus:outline-none focus:border-cyan-500 transition"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-1">Confirm New Password</label>
            <input
              type="password"
              name="new_password_confirm"
              required
              value={formData.new_password_confirm}
              onChange={handleChange}
              placeholder="••••••••"
              className="w-full px-3.5 py-2.5 bg-slate-900/80 border border-slate-800 rounded-xl text-sm text-white focus:outline-none focus:border-cyan-500 transition"
            />
          </div>

          <div className="pt-4 flex justify-end">
            <button
              type="submit"
              disabled={submitting}
              className="px-5 py-2.5 bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-white font-semibold text-xs rounded-xl shadow-lg shadow-cyan-500/20 transition flex items-center space-x-2"
            >
              {submitting ? (
                <span className="animate-pulse">Updating Password...</span>
              ) : (
                <>
                  <Key className="w-4 h-4" />
                  <span>Update Password</span>
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

