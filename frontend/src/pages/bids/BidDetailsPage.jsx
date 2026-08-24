import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useAuth } from '../../contexts/AuthContext';
import { PageHeader } from '../../components/common/PageHeader';
import { LoadingSpinner } from '../../components/common/LoadingSpinner';
import { ErrorMessage } from '../../components/common/ErrorMessage';
import { BidStatusBadge } from '../../components/bids/BidStatusBadge';
import { BidForm } from '../../components/bids/BidForm';
import { AcceptBidModal } from '../../components/bids/AcceptBidModal';
import { WithdrawBidModal } from '../../components/bids/WithdrawBidModal';
import apiClient from '../../api/axios';
import { API_ENDPOINTS } from '../../api/endpoints';
import { ArrowLeft, UserCheck, DollarSign, Calendar, MessageSquare, Edit, RotateCcw, CheckCircle2, Package } from 'lucide-react';

export const BidDetailsPage = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { user } = useAuth();
  const queryClient = useQueryClient();

  const [isEditing, setIsEditing] = useState(false);
  const [showAcceptModal, setShowAcceptModal] = useState(false);
  const [showWithdrawModal, setShowWithdrawModal] = useState(false);

  const [actionError, setActionError] = useState('');

  const { data: bid, isLoading, error, refetch } = useQuery({
    queryKey: ['bid-detail', id],
    queryFn: async () => {
      const res = await apiClient.get(API_ENDPOINTS.BID_DETAIL(id));
      return res.data?.data || res.data;
    },
  });

  const loadId = bid?.load;
  const { data: load } = useQuery({
    queryKey: ['load-detail', loadId],
    queryFn: async () => {
      if (!loadId) return null;
      const res = await apiClient.get(`${API_ENDPOINTS.LOADS}${loadId}/`);
      return res.data?.data || res.data;
    },
    enabled: !!loadId,
  });

  const isBidOwner = bid && (bid.transporter === user?.id || bid.transporter_email === user?.email);
  const isLoadOwner = load && (load.shipper === user?.id || load.shipper_email === user?.email);

  const editMutation = useMutation({
    mutationFn: async (payload) => {
      const res = await apiClient.patch(API_ENDPOINTS.BID_DETAIL(id), payload);
      return res.data;
    },
    onSuccess: () => {
      setIsEditing(false);
      queryClient.invalidateQueries(['bid-detail', id]);
      queryClient.invalidateQueries(['my-bids']);
    },
    onError: (err) => {
      setActionError(err.response?.data?.detail || 'Failed to update bid.');
    },
  });

  const withdrawMutation = useMutation({
    mutationFn: async () => {
      const res = await apiClient.post(API_ENDPOINTS.BID_WITHDRAW(id));
      return res.data;
    },
    onSuccess: () => {
      setShowWithdrawModal(false);
      queryClient.invalidateQueries(['bid-detail', id]);
      queryClient.invalidateQueries(['my-bids']);
    },
    onError: (err) => {
      setActionError(err.response?.data?.detail || 'Failed to withdraw bid.');
    },
  });

  const acceptMutation = useMutation({
    mutationFn: async () => {
      const res = await apiClient.post(API_ENDPOINTS.BID_ACCEPT(id));
      return res.data;
    },
    onSuccess: () => {
      setShowAcceptModal(false);
      queryClient.invalidateQueries(['bid-detail', id]);
      queryClient.invalidateQueries(['load-detail', loadId]);
      queryClient.invalidateQueries(['loads']);
    },
    onError: (err) => {
      setActionError(err.response?.data?.detail || 'Failed to accept bid.');
    },
  });

  if (isLoading) return <LoadingSpinner label="Loading bid specifications..." />;
  if (error || !bid) return <ErrorMessage title="Bid Not Found" message={error?.message || 'Specified rate bid does not exist.'} onRetry={refetch} />;

  const formattedAmount = Number(bid.amount).toLocaleString('en-US', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  });

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      <PageHeader
        title={`Bid Specification`}
        subtitle={`Rate offer #${bid.id?.substring(0, 8)}`}
        actions={
          <div className="flex items-center space-x-2">
            <button
              onClick={() => navigate(-1)}
              className="px-3.5 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-xl text-xs font-semibold flex items-center space-x-1 transition"
            >
              <ArrowLeft className="w-4 h-4" />
              <span>Back</span>
            </button>

            {isBidOwner && bid.status === 'ACTIVE' && !isEditing && (
              <button
                onClick={() => setIsEditing(true)}
                className="px-3.5 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded-xl text-xs font-semibold flex items-center space-x-1.5 transition"
              >
                <Edit className="w-4 h-4" />
                <span>Edit Bid</span>
              </button>
            )}

            {isBidOwner && bid.status === 'ACTIVE' && (
              <button
                onClick={() => setShowWithdrawModal(true)}
                className="px-3.5 py-1.5 bg-rose-500/10 hover:bg-rose-500/20 text-rose-300 border border-rose-500/30 rounded-xl text-xs font-semibold flex items-center space-x-1.5 transition"
              >
                <RotateCcw className="w-4 h-4" />
                <span>Withdraw</span>
              </button>
            )}

            {isLoadOwner && bid.status === 'ACTIVE' && (
              <button
                onClick={() => setShowAcceptModal(true)}
                className="px-3.5 py-1.5 bg-emerald-600 hover:bg-emerald-500 text-white rounded-xl text-xs font-semibold flex items-center space-x-1.5 transition shadow-lg shadow-emerald-600/20"
              >
                <CheckCircle2 className="w-4 h-4" />
                <span>Accept Bid & Book</span>
              </button>
            )}
          </div>
        }
      />

      {isEditing ? (
        <div className="glass-panel p-6 sm:p-8 rounded-2xl border border-slate-800 space-y-4">
          <h3 className="text-sm font-bold text-white mb-2">Edit Transporter Rate Offer</h3>
          <BidForm
            initialData={bid}
            onSubmit={(payload) => editMutation.mutate(payload)}
            onCancel={() => setIsEditing(false)}
            submitting={editMutation.isPending}
            serverError={actionError}
          />
        </div>
      ) : (
        <div className="glass-panel p-6 sm:p-8 rounded-2xl border border-slate-800 space-y-6">
          <div className="flex items-center justify-between pb-4 border-b border-slate-800">
            <div>
              <span className="text-[10px] font-bold text-cyan-400 uppercase tracking-widest">Rate Offer ID #{bid.id?.substring(0, 8)}</span>
              <h2 className="text-2xl font-black text-emerald-400 mt-1">
                {formattedAmount} <span className="text-sm text-emerald-500">{bid.currency || 'ETB'}</span>
              </h2>
            </div>
            <BidStatusBadge status={bid.status} />
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div className="p-4 bg-slate-900/60 rounded-xl border border-slate-800 space-y-1">
              <p className="text-[10px] text-slate-500 font-semibold uppercase flex items-center space-x-1">
                <UserCheck className="w-3.5 h-3.5 text-cyan-400" />
                <span>Transporter Account</span>
              </p>
              <p className="text-sm font-bold text-white">{bid.transporter_email}</p>
            </div>

            {load && (
              <div className="p-4 bg-slate-900/60 rounded-xl border border-slate-800 space-y-1">
                <p className="text-[10px] text-slate-500 font-semibold uppercase flex items-center space-x-1">
                  <Package className="w-3.5 h-3.5 text-cyan-400" />
                  <span>Freight Load Listing</span>
                </p>
                <p className="text-sm font-bold text-white truncate">{load.title}</p>
                <p className="text-xs text-slate-400">{load.origin_city} ➔ {load.destination_city}</p>
              </div>
            )}
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-2">
            <div className="p-3 bg-slate-900/40 rounded-xl border border-slate-800">
              <p className="text-[10px] text-slate-500 font-semibold uppercase">Proposed Pickup Date</p>
              <p className="text-xs font-bold text-white mt-1">
                {bid.proposed_pickup_date ? new Date(bid.proposed_pickup_date).toLocaleString() : 'Immediate / Flexible'}
              </p>
            </div>

            <div className="p-3 bg-slate-900/40 rounded-xl border border-slate-800">
              <p className="text-[10px] text-slate-500 font-semibold uppercase">Estimated Delivery Date</p>
              <p className="text-xs font-bold text-white mt-1">
                {bid.estimated_delivery_date ? new Date(bid.estimated_delivery_date).toLocaleString() : 'Standard Delivery'}
              </p>
            </div>
          </div>

          {bid.message && (
            <div className="p-4 bg-slate-900/40 rounded-xl border border-slate-800 space-y-1">
              <p className="text-xs font-semibold text-slate-400 flex items-center space-x-1">
                <MessageSquare className="w-3.5 h-3.5 text-cyan-400" />
                <span>Transporter Proposal Message</span>
              </p>
              <p className="text-xs text-slate-200 leading-relaxed italic">"{bid.message}"</p>
            </div>
          )}
        </div>
      )}

      {showAcceptModal && (
        <AcceptBidModal
          bid={bid}
          load={load}
          onConfirm={() => acceptMutation.mutate()}
          onCancel={() => setShowAcceptModal(false)}
          submitting={acceptMutation.isPending}
          error={actionError}
        />
      )}

      {showWithdrawModal && (
        <WithdrawBidModal
          bid={bid}
          onConfirm={() => withdrawMutation.mutate()}
          onCancel={() => setShowWithdrawModal(false)}
          submitting={withdrawMutation.isPending}
          error={actionError}
        />
      )}
    </div>
  );
};

