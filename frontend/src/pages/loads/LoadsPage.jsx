import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import { PageHeader } from '../../components/common/PageHeader';
import { LoadingSpinner } from '../../components/common/LoadingSpinner';
import { ErrorMessage } from '../../components/common/ErrorMessage';
import { LoadCard } from '../../components/loads/LoadCard';
import { LoadSearchBar } from '../../components/loads/LoadSearchBar';
import { LoadFilters } from '../../components/loads/LoadFilters';
import { EmptyLoadsState } from '../../components/loads/EmptyLoadsState';
import apiClient from '../../api/axios';
import { API_ENDPOINTS } from '../../api/endpoints';
import { Plus, Globe, PackageCheck, ChevronLeft, ChevronRight } from 'lucide-react';

export const LoadsPage = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [searchParams] = useSearchParams();

  const isShipperOrForwarder = ['SHIPPER', 'FREIGHT_FORWARDER'].includes(user?.role);
  const [tab, setTab] = useState(searchParams.get('my_loads') === 'true' ? 'my_loads' : 'marketplace');

  const [search, setSearch] = useState('');
  const [page, setPage] = useState(1);
  const [filters, setFilters] = useState({
    origin_city: '',
    destination_city: '',
    cargo_type: '',
    status: '',
  });

  const handleFilterChange = (key, val) => {
    setFilters((prev) => ({ ...prev, [key]: val }));
    setPage(1);
  };

  const handleResetFilters = () => {
    setFilters({ origin_city: '', destination_city: '', cargo_type: '', status: '' });
    setSearch('');
    setPage(1);
  };

  const queryParams = {
    page,
    search: search || undefined,
    origin_city: filters.origin_city || undefined,
    destination_city: filters.destination_city || undefined,
    cargo_type: filters.cargo_type || undefined,
    status: filters.status || undefined,
    my_loads: tab === 'my_loads' ? 'true' : undefined,
  };

  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ['loads', tab, page, search, filters],
    queryFn: async () => {
      const res = await apiClient.get(API_ENDPOINTS.LOADS, { params: queryParams });
      return res.data;
    },
    staleTime: 30 * 1000,
  });

  const loadsList = Array.isArray(data) ? data : data?.results || [];
  const totalCount = data?.count || loadsList.length;
  const totalPages = Math.ceil(totalCount / 10) || 1;

  return (
    <div className="space-y-6">
      <PageHeader
        title={tab === 'my_loads' ? 'My Freight Listings' : 'Freight Marketplace'}
        subtitle="Browse and manage freight loads moving across the Djibouti ➔ Modjo Dry Port corridor."
        actions={
          isShipperOrForwarder && (
            <button
              onClick={() => navigate('/loads/create')}
              className="px-4 py-2 bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-white font-semibold text-xs rounded-xl shadow-lg shadow-cyan-500/20 flex items-center space-x-1.5 transition"
            >
              <Plus className="w-4 h-4" />
              <span>Post New Load</span>
            </button>
          )
        }
      />

      {isShipperOrForwarder && (
        <div className="flex border-b border-slate-800">
          <button
            onClick={() => {
              setTab('marketplace');
              setPage(1);
            }}
            className={`px-4 py-2.5 text-xs font-semibold flex items-center space-x-2 border-b-2 transition ${
              tab === 'marketplace'
                ? 'border-cyan-500 text-cyan-400'
                : 'border-transparent text-slate-400 hover:text-slate-200'
            }`}
          >
            <Globe className="w-4 h-4" />
            <span>Available Marketplace Loads</span>
          </button>
          <button
            onClick={() => {
              setTab('my_loads');
              setPage(1);
            }}
            className={`px-4 py-2.5 text-xs font-semibold flex items-center space-x-2 border-b-2 transition ${
              tab === 'my_loads'
                ? 'border-cyan-500 text-cyan-400'
                : 'border-transparent text-slate-400 hover:text-slate-200'
            }`}
          >
            <PackageCheck className="w-4 h-4" />
            <span>My Posted Loads</span>
          </button>
        </div>
      )}

      <div className="space-y-3">
        <div className="flex flex-col sm:flex-row gap-3">
          <LoadSearchBar value={search} onChange={(val) => { setSearch(val); setPage(1); }} onClear={() => setSearch('')} />
        </div>
        <LoadFilters filters={filters} onChange={handleFilterChange} onReset={handleResetFilters} />
      </div>

      {isLoading ? (
        <LoadingSpinner label="Fetching TradeFlow marketplace loads..." />
      ) : error ? (
        <ErrorMessage title="Marketplace API Error" message={error.message} onRetry={refetch} />
      ) : loadsList.length === 0 ? (
        <EmptyLoadsState isShipper={isShipperOrForwarder} onResetFilters={handleResetFilters} />
      ) : (
        <>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
            {loadsList.map((load) => (
              <LoadCard key={load.id} load={load} />
            ))}
          </div>

          {totalPages > 1 && (
            <div className="flex items-center justify-between pt-4 border-t border-slate-800 text-xs">
              <span className="text-slate-400">
                Page <strong className="text-white">{page}</strong> of <strong className="text-white">{totalPages}</strong> ({totalCount} total loads)
              </span>
              <div className="flex items-center space-x-2">
                <button
                  disabled={page === 1}
                  onClick={() => setPage((p) => Math.max(1, p - 1))}
                  className="px-3 py-1.5 bg-slate-900 border border-slate-800 text-slate-300 rounded-lg disabled:opacity-40 disabled:cursor-not-allowed hover:bg-slate-800 transition flex items-center space-x-1"
                >
                  <ChevronLeft className="w-4 h-4" />
                  <span>Prev</span>
                </button>
                <button
                  disabled={page >= totalPages}
                  onClick={() => setPage((p) => p + 1)}
                  className="px-3 py-1.5 bg-slate-900 border border-slate-800 text-slate-300 rounded-lg disabled:opacity-40 disabled:cursor-not-allowed hover:bg-slate-800 transition flex items-center space-x-1"
                >
                  <span>Next</span>
                  <ChevronRight className="w-4 h-4" />
                </button>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
};

