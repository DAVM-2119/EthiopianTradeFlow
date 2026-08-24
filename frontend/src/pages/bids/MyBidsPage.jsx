import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { PageHeader } from '../../components/common/PageHeader';
import { LoadingSpinner } from '../../components/common/LoadingSpinner';
import { ErrorMessage } from '../../components/common/ErrorMessage';
import { BidCard } from '../../components/bids/BidCard';
import { WithdrawBidModal } from '../../components/bids/WithdrawBidModal';
import { EmptyBidsState } from '../../components/bids/EmptyBidsState';
import apiClient from '../../api/axios';
import { API_ENDPOINTS } from '../../api/endpoints';
import { Filter, RotateCcw } from 'lucide-react';

export const MyBidsPage = () => {
  const queryClient = useQueryClient();
  const [statusFilter, setStatusFilter] = useState('');
  const [selectedBidForWithdraw, setSelectedBidForWithdraw] = useState(null);
  const [withdrawError, setWithdrawError] = useState('');

  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ['my-bids'],
    queryFn: async () => {
      const res = await apiClient.get(API_ENDPOINTS.MY_BIDS);
      return res.data?.data || res.data;
    },
  });

  const withdrawMutation = useMutation({
    mutationFn: async (bidId) => {
      const res = await apiClient.post(API_ENDPOINTS.BID_WITHDRAW(bidId));
      return res.data;
    },
    onSuccess: () => {
      setSelectedBidForWithdraw(null);
      queryClient.invalidateQueries(['my-bids']);
    },
    onError: (err) => {
      setWithdrawError(err.response?.data?.detail || 'Failed to withdraw bid.');
    },
  });

  const bidsList = Array.isArray(data) ? data : data?.results || [];

  const filteredBids = statusFilter
    ? bidsList.filter((b) => b.status === statusFilter)
    : bidsList;

  return (
    <div className="space-y-6">
      <PageHeader
        title="My Submitted Bids"
        subtitle="Manage and track rate bids submitted on active marketplace freight loads."
      />

      <div className="glass-panel p-3 sm:p-4 rounded-xl border border-slate-800 flex items-center justify-between gap-3 text-xs">
        <div className="flex items-center space-x-2">
          <Filter className="w-4 h-4 text-cyan-400 shrink-0" />
          <span className="text-slate-400 font-semibold hidden sm:inline">Filter Status:</span>
          <div className="flex flex-wrap gap-1.5">
            {['', 'ACTIVE', 'ACCEPTED', 'REJECTED', 'WITHDRAWN'].map((st) => (
              <button
                key={st}
                onClick={() => setStatusFilter(st)}
                className={`px-3 py-1 rounded-lg font-semibold transition ${
                  statusFilter === st
                    ? 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/30'
                    : 'bg-slate-900 text-slate-400 border border-slate-800 hover:text-white'
                }`}
              >
                {st === '' ? 'All Bids' : st}
              </button>
            ))}
          </div>
        </div>

        {statusFilter && (
          <button
            onClick={() => setStatusFilter('')}
            className="text-slate-500 hover:text-slate-300 flex items-center space-x-1"
          >
            <RotateCcw className="w-3.5 h-3.5" />
            <span className="hidden sm:inline">Reset</span>
          </button>
        )}
      </div>

      {isLoading ? (
        <LoadingSpinner label="Fetching your submitted rate bids..." />
      ) : error ? (
        <ErrorMessage title="Bids API Error" message={error.message} onRetry={refetch} />
      ) : filteredBids.length === 0 ? (
        <EmptyBidsState isTransporter={true} message="You have no rate bids matching your current filter selection." />
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
          {filteredBids.map((bid) => (
            <BidCard
              key={bid.id}
              bid={bid}
              isShipper={false}
              onWithdraw={(b) => setSelectedBidForWithdraw(b)}
            />
          ))}
        </div>
      )}

      {selectedBidForWithdraw && (
        <WithdrawBidModal
          bid={selectedBidForWithdraw}
          onConfirm={() => withdrawMutation.mutate(selectedBidForWithdraw.id)}
          onCancel={() => setSelectedBidForWithdraw(null)}
          submitting={withdrawMutation.isPending}
          error={withdrawError}
        />
      )}
    </div>
  );
};

