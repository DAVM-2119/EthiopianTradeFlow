import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { useForm } from 'react-hook-form';
import { z } from 'zod';
import { zodResolver } from '@hookform/resolvers/zod';
import { PageHeader } from '../../components/common/PageHeader';
import { LoadingSpinner } from '../../components/common/LoadingSpinner';
import { ErrorMessage } from '../../components/common/ErrorMessage';
import apiClient from '../../api/axios';
import { API_ENDPOINTS } from '../../api/endpoints';
import { ArrowLeft, Package, Calendar, MapPin, AlertCircle, CheckCircle2 } from 'lucide-react';

const loadSchema = z.object({
  title: z.string().min(3, 'Load title must be at least 3 characters'),
  origin_city: z.string().min(2, 'Origin city is required'),
  origin_address: z.string().optional(),
  destination_city: z.string().min(2, 'Destination city is required'),
  destination_address: z.string().optional(),
  cargo_type: z.string().min(1, 'Cargo type is required'),
  weight: z.coerce.number().positive('Weight must be greater than 0'),
  volume: z.coerce.number().optional().or(z.literal('')),
  pickup_window_start: z.string().min(1, 'Pickup window start date is required'),
  pickup_window_end: z.string().min(1, 'Pickup window end date is required'),
  special_requirements: z.string().optional(),
});

export const EditLoadPage = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [serverError, setServerError] = useState('');
  const [submitting, setSubmitting] = useState(false);

  const { data: load, isLoading, error } = useQuery({
    queryKey: ['load-detail', id],
    queryFn: async () => {
      const res = await apiClient.get(`${API_ENDPOINTS.LOADS}${id}/`);
      return res.data?.data || res.data;
    },
  });

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm({
    resolver: zodResolver(loadSchema),
  });

  useEffect(() => {
    if (load) {
      reset({
        title: load.title || '',
        origin_city: load.origin_city || '',
        origin_address: load.origin_address || '',
        destination_city: load.destination_city || '',
        destination_address: load.destination_address || '',
        cargo_type: load.cargo_type || 'GENERAL_CARGO',
        weight: load.weight || 10,
        volume: load.volume || '',
        pickup_window_start: load.pickup_window_start ? new Date(load.pickup_window_start).toISOString().slice(0, 16) : '',
        pickup_window_end: load.pickup_window_end ? new Date(load.pickup_window_end).toISOString().slice(0, 16) : '',
        special_requirements: load.special_requirements || '',
      });
    }
  }, [load, reset]);

  const onSubmit = async (data) => {
    setServerError('');
    setSubmitting(true);

    const payload = {
      ...data,
      weight: String(data.weight),
      volume: data.volume ? String(data.volume) : null,
      pickup_window_start: new Date(data.pickup_window_start).toISOString(),
      pickup_window_end: new Date(data.pickup_window_end).toISOString(),
    };

    try {
      await apiClient.patch(`${API_ENDPOINTS.LOADS}${id}/`, payload);
      navigate(`/loads/${id}`);
    } catch (err) {
      const resp = err.response?.data;
      if (typeof resp === 'object' && resp !== null) {
        const firstKey = Object.keys(resp)[0];
        const val = resp[firstKey];
        const text = Array.isArray(val) ? val[0] : String(val);
        setServerError(`${firstKey.replace('_', ' ')}: ${text}`);
      } else {
        setServerError('Failed to update load. Please try again.');
      }
    } finally {
      setSubmitting(false);
    }
  };

  if (isLoading) return <LoadingSpinner label="Loading load details..." />;
  if (error || !load) return <ErrorMessage title="Load Not Found" message="Specified load listing does not exist." />;

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      <PageHeader
        title="Edit Load Specifications"
        subtitle={`Update details for Load Listing #${load.id?.substring(0, 8)}`}
        actions={
          <button
            onClick={() => navigate(`/loads/${id}`)}
            className="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-xl text-xs font-semibold flex items-center space-x-1 transition"
          >
            <ArrowLeft className="w-4 h-4" />
            <span>Cancel</span>
          </button>
        }
      />

      <div className="glass-panel p-6 sm:p-8 rounded-2xl border border-slate-800 space-y-6">
        {serverError && (
          <div className="p-3 bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs rounded-xl flex items-center space-x-2">
            <AlertCircle className="w-4 h-4 text-rose-400 shrink-0" />
            <span>{serverError}</span>
          </div>
        )}

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
          <div className="space-y-4">
            <h3 className="text-xs font-bold text-cyan-400 uppercase tracking-wider flex items-center space-x-1.5">
              <Package className="w-4 h-4" />
              <span>1. Basic Information</span>
            </h3>

            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1">Load Title</label>
              <input
                type="text"
                {...register('title')}
                className="w-full px-3.5 py-2.5 bg-slate-900 border border-slate-800 rounded-xl text-sm text-white focus:outline-none focus:border-cyan-500 transition"
              />
              {errors.title && <p className="text-[11px] text-rose-400 mt-1">{errors.title.message}</p>}
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">Cargo Type</label>
                <select
                  {...register('cargo_type')}
                  className="w-full px-3.5 py-2.5 bg-slate-900 border border-slate-800 rounded-xl text-sm text-slate-200 focus:outline-none focus:border-cyan-500 transition"
                >
                  <option value="GENERAL_CARGO">General Cargo</option>
                  <option value="DRY_BULK">Dry Bulk</option>
                  <option value="LIQUID_BULK">Liquid Bulk</option>
                  <option value="CONTAINERIZED">Containerized</option>
                  <option value="REFRIGERATED">Refrigerated</option>
                  <option value="HAZARDOUS">Hazardous</option>
                  <option value="HEAVY_MACHINERY">Heavy Machinery</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">Weight (Tons)</label>
                <input
                  type="number"
                  step="0.01"
                  {...register('weight')}
                  className="w-full px-3.5 py-2.5 bg-slate-900 border border-slate-800 rounded-xl text-sm text-white focus:outline-none focus:border-cyan-500 transition"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">Volume (m³)</label>
                <input
                  type="number"
                  step="0.01"
                  {...register('volume')}
                  className="w-full px-3.5 py-2.5 bg-slate-900 border border-slate-800 rounded-xl text-sm text-white focus:outline-none focus:border-cyan-500 transition"
                />
              </div>
            </div>
          </div>

          <div className="space-y-4 pt-4 border-t border-slate-800">
            <h3 className="text-xs font-bold text-cyan-400 uppercase tracking-wider flex items-center space-x-1.5">
              <MapPin className="w-4 h-4" />
              <span>2. Route Origin & Destination</span>
            </h3>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">Origin City</label>
                <input
                  type="text"
                  {...register('origin_city')}
                  className="w-full px-3.5 py-2.5 bg-slate-900 border border-slate-800 rounded-xl text-sm text-white focus:outline-none focus:border-cyan-500 transition"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">Destination City</label>
                <input
                  type="text"
                  {...register('destination_city')}
                  className="w-full px-3.5 py-2.5 bg-slate-900 border border-slate-800 rounded-xl text-sm text-white focus:outline-none focus:border-cyan-500 transition"
                />
              </div>
            </div>
          </div>

          <div className="space-y-4 pt-4 border-t border-slate-800">
            <h3 className="text-xs font-bold text-cyan-400 uppercase tracking-wider flex items-center space-x-1.5">
              <Calendar className="w-4 h-4" />
              <span>3. Pickup Window</span>
            </h3>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">Pickup Start Date & Time</label>
                <input
                  type="datetime-local"
                  {...register('pickup_window_start')}
                  className="w-full px-3.5 py-2.5 bg-slate-900 border border-slate-800 rounded-xl text-sm text-white focus:outline-none focus:border-cyan-500 transition"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">Pickup End Date & Time</label>
                <input
                  type="datetime-local"
                  {...register('pickup_window_end')}
                  className="w-full px-3.5 py-2.5 bg-slate-900 border border-slate-800 rounded-xl text-sm text-white focus:outline-none focus:border-cyan-500 transition"
                />
              </div>
            </div>
          </div>

          <div className="pt-4 border-t border-slate-800">
            <label className="block text-xs font-semibold text-slate-300 mb-1">Special Requirements</label>
            <textarea
              rows={3}
              {...register('special_requirements')}
              className="w-full px-3.5 py-2.5 bg-slate-900 border border-slate-800 rounded-xl text-sm text-white focus:outline-none focus:border-cyan-500 transition"
            />
          </div>

          <div className="pt-4 flex justify-end space-x-3">
            <button
              type="button"
              onClick={() => navigate(`/loads/${id}`)}
              className="px-4 py-2.5 bg-slate-800 hover:bg-slate-700 text-slate-300 font-semibold text-xs rounded-xl transition"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={submitting}
              className="px-6 py-2.5 bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-white font-semibold text-xs rounded-xl shadow-lg shadow-cyan-500/20 transition flex items-center space-x-2"
            >
              {submitting ? (
                <span className="animate-pulse">Saving Changes...</span>
              ) : (
                <>
                  <CheckCircle2 className="w-4 h-4" />
                  <span>Update Load</span>
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

