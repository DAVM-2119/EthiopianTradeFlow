import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useAuth } from '../../contexts/AuthContext';
import { PageHeader } from '../../components/common/PageHeader';
import { LoadingSpinner } from '../../components/common/LoadingSpinner';
import { ErrorMessage } from '../../components/common/ErrorMessage';
import { LoadSummary } from '../../components/loads/LoadSummary';
import { BidCard } from '../../components/bids/BidCard';
import { BidComparison } from '../../components/bids/BidComparison';
import { BidForm } from '../../components/bids/BidForm';
import { AcceptBidModal } from '../../components/bids/AcceptBidModal';
import { WithdrawBidModal } from '../../components/bids/WithdrawBidModal';
import apiClient from '../../api/axios';
import { API_ENDPOINTS } from '../../api/endpoints';
import { ArrowLeft, Edit, Globe, XCircle, DollarSign, AlertCircle, Plus, CheckCircle2 } from 'lucide-react';

export const LoadDetailsPage = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { user } = useAuth();
  const queryClient = useQueryClient();

  const [showBidForm, setShowBidForm] = useState(false);
  const [selectedBidForAccept, setSelectedBidForAccept] = useState(null);
  const [selectedBidForWithdraw, setSelectedBidForWithdraw] = useState(null);
  const [actionError, setActionError] = useState('');

  const { data: load, isLoading, error, refetch } = useQuery({
    queryKey: ['load-detail', id],
    queryFn: async () => {
      const res = await apiClient.get(`${API_ENDPOINTS.LOADS}${id}/`);
      return res.data?.data || res.data;
    },
  });

  const { data: bidsData } = useQuery({
    queryKey: ['load-bids', id],
    queryFn: async () => {
      const res = await apiClient.get(API_ENDPOINTS.LOAD_BIDS(id));
      return res.data?.data || res.data;
    },
    enabled: !!load,
  });

  const bidsList = Array.isArray(bidsData) ? bidsData : bidsData?.results || [];

  const isOwner = load && (load.shipper === user?.id || load.shipper_email === user?.email);
  const isTransporter = user?.role === 'TRANSPORTER';

  // Check if transporter already submitted an active bid for this load
  const myActiveBid = isTransporter ? bidsList.find((b) => b.status === 'ACTIVE') : null;

  const postMutation = useMutation({
    mutationFn: async () => {
      const res = await apiClient.post(`${API_ENDPOINTS.LOADS}${id}/post/`);
      return res.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries(['load-detail', id]);
      queryClient.invalidateQueries(['loads']);
    },
    onError: (err) => {
      setActionError(err.response?.data?.detail || 'Failed to post load.');
    },
  });

  const cancelMutation = useMutation({
    mutationFn: async () => {
      const res = await apiClient.post(`${API_ENDPOINTS.LOADS}${id}/cancel/`);
      return res.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries(['load-detail', id]);
      queryClient.invalidateQueries(['loads']);
    },
    onError: (err) => {
      setActionError(err.response?.data?.detail || 'Failed to cancel load.');
    },
  });

  const submitBidMutation = useMutation({
    mutationFn: async (payload) => {
      const res = await apiClient.post(API_ENDPOINTS.LOAD_BIDS(id), payload);
      return res.data;
    },
    onSuccess: () => {
      setShowBidForm(false);
      queryClient.invalidateQueries(['load-bids', id]);
      queryClient.invalidateQueries(['my-bids']);
    },
    onError: (err) => {
      const resp = err.response?.data;
      if (typeof resp === 'object' && resp !== null) {
        const firstKey = Object.keys(resp)[0];
        const val = resp[firstKey];
        const text = Array.isArray(val) ? val[0] : String(val);
        setActionError(`${firstKey.replace('_', ' ')}: ${text}`);
      } else {
        setActionError('Failed to submit rate bid.');
      }
    },
  });

  const acceptBidMutation = useMutation({
    mutationFn: async (bidId) => {
      const res = await apiClient.post(API_ENDPOINTS.BID_ACCEPT(bidId));
      return res.data;
    },
    onSuccess: () => {
      setSelectedBidForAccept(null);
      queryClient.invalidateQueries(['load-detail', id]);
      queryClient.invalidateQueries(['load-bids', id]);
      queryClient.invalidateQueries(['loads']);
    },
    onError: (err) => {
      setActionError(err.response?.data?.detail || 'Failed to accept bid.');
    },
  });

  const withdrawBidMutation = useMutation({
    mutationFn: async (bidId) => {
      const res = await apiClient.post(API_ENDPOINTS.BID_WITHDRAW(bidId));
      return res.data;
    },
    onSuccess: () => {
      setSelectedBidForWithdraw(null);
      queryClient.invalidateQueries(['load-bids', id]);
      queryClient.invalidateQueries(['my-bids']);
    },
    onError: (err) => {
      setActionError(err.response?.data?.detail || 'Failed to withdraw bid.');
    },
  });

  if (isLoading) return <LoadingSpinner label="Loading load specifications..." />;
  if (error || !load) return <ErrorMessage title="Load Not Found" message={error?.message || 'Specified load listing does not exist.'} onRetry={refetch} />;

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <PageHeader
        title={`Freight Load Details`}
        subtitle={`Listing #${load.id?.substring(0, 8)}`}
        actions={
          <div className="flex items-center space-x-2">
            <button
              onClick={() => navigate('/loads')}
              className="px-3.5 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-xl text-xs font-semibold flex items-center space-x-1 transition"
            >
              <ArrowLeft className="w-4 h-4" />
              <span>Back to Loads</span>
            </button>

            {isOwner && load.status === 'DRAFT' && (
              <button
                onClick={() => postMutation.mutate()}
                disabled={postMutation.isPending}
                className="px-3.5 py-1.5 bg-cyan-600 hover:bg-cyan-500 text-white rounded-xl text-xs font-semibold flex items-center space-x-1.5 transition shadow-lg shadow-cyan-500/20"
              >
                <Globe className="w-4 h-4" />
                <span>Publish to Marketplace</span>
              </button>
            )}

            {isOwner && ['DRAFT', 'POSTED'].includes(load.status) && (
              <button
                onClick={() => navigate(`/loads/${id}/edit`)}
                className="px-3.5 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded-xl text-xs font-semibold flex items-center space-x-1.5 transition"
              >
                <Edit className="w-4 h-4" />
                <span>Edit Load</span>
              </button>
            )}

            {isOwner && ['DRAFT', 'POSTED'].includes(load.status) && (
              <button
                onClick={() => cancelMutation.mutate()}
                disabled={cancelMutation.isPending}
                className="px-3.5 py-1.5 bg-rose-500/10 hover:bg-rose-500/20 text-rose-300 border border-rose-500/30 rounded-xl text-xs font-semibold flex items-center space-x-1.5 transition"
              >
                <XCircle className="w-4 h-4" />
                <span>Cancel Load</span>
              </button>
            )}
          </div>
        }
      />

      {actionError && (
        <div className="p-3 bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs rounded-xl flex items-center space-x-2">
          <AlertCircle className="w-4 h-4 text-rose-400 shrink-0" />
          <span>{actionError}</span>
        </div>
      )}

      <LoadSummary load={load} />

      {/* Shipper Bids Matrix */}
      {isOwner && bidsList.length > 0 && (
        <div className="space-y-6">
          <BidComparison bids={bidsList} onAcceptBid={(b) => setSelectedBidForAccept(b)} />

          <div className="space-y-3">
            <h3 className="text-sm font-bold text-white flex items-center space-x-2">
              <DollarSign className="w-4 h-4 text-cyan-400" />
              <span>All Received Rate Offers ({bidsList.length})</span>
            </h3>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              {bidsList.map((bid) => (
                <BidCard
                  key={bid.id}
                  bid={bid}
                  isShipper={true}
                  onAccept={(b) => setSelectedBidForAccept(b)}
                />
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Transporter Bidding Portal */}
      {isTransporter && load.status === 'POSTED' && (
        <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h4 className="text-sm font-bold text-white flex items-center space-x-2">
                <DollarSign className="w-4 h-4 text-cyan-400" />
                <span>Transporter Rate Bidding Portal</span>
              </h4>
              <p className="text-xs text-slate-400 mt-0.5">
                Submit a competitive rate offer for transporting this cargo along the Djibouti ➔ Modjo corridor.
              </p>
            </div>

            {!myActiveBid && !showBidForm && (
              <button
                onClick={() => setShowBidForm(true)}
                className="px-4 py-2 bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-white rounded-xl text-xs font-semibold flex items-center space-x-1.5 shadow-lg shadow-cyan-500/20 transition"
              >
                <Plus className="w-4 h-4" />
                <span>Place Rate Bid</span>
              </button>
            )}
          </div>

          {myActiveBid && (
            <div className="p-4 bg-slate-900/80 rounded-xl border border-cyan-500/30 flex items-center justify-between">
              <div>
                <span className="text-[10px] font-bold text-cyan-400 uppercase">Your Active Rate Offer</span>
                <p className="text-lg font-black text-emerald-400 mt-0.5">
                  {Number(myActiveBid.amount).toLocaleString()} ETB
                </p>
                <p className="text-[11px] text-slate-400 mt-0.5">
                  Status: <strong className="text-cyan-300">ACTIVE</strong> — Awaiting shipper review
                </p>
              </div>

              <div className="flex items-center space-x-2">
                <button
                  onClick={() => navigate(`/bids/${myActiveBid.id}`)}
                  className="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded-xl text-xs font-semibold transition"
                >
                  Manage Bid
                </button>
                <button
                  onClick={() => setSelectedBidForWithdraw(myActiveBid)}
                  className="px-3 py-1.5 bg-rose-500/10 hover:bg-rose-500/20 text-rose-300 border border-rose-500/30 rounded-xl text-xs font-semibold transition"
                >
                  Withdraw
                </button>
              </div>
            </div>
          )}

          {showBidForm && !myActiveBid && (
            <div className="pt-2 border-t border-slate-800">
              <BidForm
                onSubmit={(payload) => submitBidMutation.mutate(payload)}
                onCancel={() => setShowBidForm(false)}
                submitting={submitBidMutation.isPending}
                serverError={actionError}
              />
            </div>
          )}
        </div>
      )}

      {selectedBidForAccept && (
        <AcceptBidModal
          bid={selectedBidForAccept}
          load={load}
          onConfirm={() => acceptBidMutation.mutate(selectedBidForAccept.id)}
          onCancel={() => setSelectedBidForAccept(null)}
          submitting={acceptBidMutation.isPending}
          error={actionError}
        />
      )}

      {selectedBidForWithdraw && (
        <WithdrawBidModal
          bid={selectedBidForWithdraw}
          onConfirm={() => withdrawBidMutation.mutate(selectedBidForWithdraw.id)}
          onCancel={() => setSelectedBidForWithdraw(null)}
          submitting={withdrawBidMutation.isPending}
          error={actionError}
        />
      )}
    </div>
  );
};
