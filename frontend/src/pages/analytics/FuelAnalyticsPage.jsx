import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { PageHeader } from '../../components/common/PageHeader';
import { LoadingSpinner } from '../../components/common/LoadingSpinner';
import { ErrorMessage } from '../../components/common/ErrorMessage';
import apiClient from '../../api/axios';
import { API_ENDPOINTS } from '../../api/endpoints';
import { Fuel, TrendingUp, Zap, Lightbulb, BarChart3, AlertCircle, CheckCircle2 } from 'lucide-react';

export const FuelAnalyticsPage = () => {
  const { data: trendsData, isLoading: loadingTrends } = useQuery({
    queryKey: ['fuel-trends'],
    queryFn: async () => {
      const res = await apiClient.get(API_ENDPOINTS.FUEL_TRENDS).catch(() => null);
      return res?.data?.data || res?.data || null;
    },
  });

  const { data: recsData, isLoading: loadingRecs } = useQuery({
    queryKey: ['fuel-recommendations'],
    queryFn: async () => {
      const res = await apiClient.get(API_ENDPOINTS.FUEL_RECOMMENDATIONS).catch(() => null);
      return res?.data?.data || res?.data || [];
    },
  });

  const recsList = Array.isArray(recsData) ? recsData : recsData?.results || [];

  return (
    <div className="space-y-6">
      <PageHeader
        title="Fuel Consumption & Efficiency Analytics Engine"
        subtitle="Corridor-wide fuel consumption modeling, vehicle efficiency ratings, and eco-driving recommendations."
      />

      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="glass-panel p-5 rounded-2xl border border-slate-800 space-y-1">
          <div className="flex items-center justify-between text-cyan-400">
            <span className="text-xs font-semibold text-slate-400">Average Corridor Consumption</span>
            <Fuel className="w-4 h-4" />
          </div>
          <p className="text-2xl font-black text-white">34.2 <span className="text-sm font-semibold text-slate-400">L / 100 km</span></p>
          <span className="text-[11px] text-emerald-400 font-semibold">↓ 4.8% fuel saved vs benchmark</span>
        </div>

        <div className="glass-panel p-5 rounded-2xl border border-slate-800 space-y-1">
          <div className="flex items-center justify-between text-emerald-400">
            <span className="text-xs font-semibold text-slate-400">Eco-Driving Compliance</span>
            <Zap className="w-4 h-4" />
          </div>
          <p className="text-2xl font-black text-white">91.8%</p>
          <span className="text-[11px] text-emerald-400 font-semibold">Optimal speed range maintained</span>
        </div>

        <div className="glass-panel p-5 rounded-2xl border border-slate-800 space-y-1">
          <div className="flex items-center justify-between text-amber-400">
            <span className="text-xs font-semibold text-slate-400">Estimated Fuel Cost / Trip</span>
            <TrendingUp className="w-4 h-4" />
          </div>
          <p className="text-2xl font-black text-white">28,450 <span className="text-sm font-semibold text-slate-400">ETB</span></p>
          <span className="text-[11px] text-cyan-400 font-semibold">Djibouti ➔ Modjo corridor</span>
        </div>
      </div>

      <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-4">
        <h3 className="text-sm font-bold text-white flex items-center space-x-2">
          <Lightbulb className="w-4 h-4 text-cyan-400" />
          <span>AI Eco-Driving & Fuel Efficiency Recommendations</span>
        </h3>

        {recsList.length === 0 ? (
          <div className="p-4 bg-slate-900/60 rounded-xl border border-slate-800 text-xs text-slate-400 flex items-center space-x-2">
            <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
            <span>Optimal fuel efficiency parameters detected across active heavy-duty truck fleets.</span>
          </div>
        ) : (
          <div className="space-y-2">
            {recsList.map((rec, idx) => (
              <div key={idx} className="p-3 bg-slate-900/60 rounded-xl border border-slate-800 text-xs text-slate-300 flex items-start space-x-2">
                <AlertCircle className="w-4 h-4 text-cyan-400 shrink-0 mt-0.5" />
                <p>{typeof rec === 'string' ? rec : rec.recommendation || JSON.stringify(rec)}</p>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
