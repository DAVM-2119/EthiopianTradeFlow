import React, { useState, useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { z } from 'zod';
import { zodResolver } from '@hookform/resolvers/zod';
import { DollarSign, Calendar, MessageSquare, AlertCircle, CheckCircle2 } from 'lucide-react';

const bidSchema = z.object({
  amount: z.coerce.number().positive('Bid amount must be greater than 0 ETB'),
  proposed_pickup_date: z.string().optional(),
  estimated_delivery_date: z.string().optional(),
  message: z.string().optional(),
});

export const BidForm = ({ initialData, onSubmit, onCancel, submitting, serverError }) => {
  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm({
    resolver: zodResolver(bidSchema),
    defaultValues: {
      amount: initialData?.amount || '',
      proposed_pickup_date: initialData?.proposed_pickup_date
        ? new Date(initialData.proposed_pickup_date).toISOString().slice(0, 16)
        : '',
      estimated_delivery_date: initialData?.estimated_delivery_date
        ? new Date(initialData.estimated_delivery_date).toISOString().slice(0, 16)
        : '',
      message: initialData?.message || '',
    },
  });

  useEffect(() => {
    if (initialData) {
      reset({
        amount: initialData.amount || '',
        proposed_pickup_date: initialData.proposed_pickup_date
          ? new Date(initialData.proposed_pickup_date).toISOString().slice(0, 16)
          : '',
        estimated_delivery_date: initialData.estimated_delivery_date
          ? new Date(initialData.estimated_delivery_date).toISOString().slice(0, 16)
          : '',
        message: initialData.message || '',
      });
    }
  }, [initialData, reset]);

  const handleFormSubmit = (data) => {
    const payload = {
      amount: String(data.amount),
      proposed_pickup_date: data.proposed_pickup_date ? new Date(data.proposed_pickup_date).toISOString() : null,
      estimated_delivery_date: data.estimated_delivery_date ? new Date(data.estimated_delivery_date).toISOString() : null,
      message: data.message || '',
    };
    onSubmit(payload);
  };

  return (
    <form onSubmit={handleSubmit(handleFormSubmit)} className="space-y-4">
      {serverError && (
        <div className="p-3 bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs rounded-xl flex items-center space-x-2">
          <AlertCircle className="w-4 h-4 text-rose-400 shrink-0" />
          <span>{serverError}</span>
        </div>
      )}

      <div>
        <label className="block text-xs font-semibold text-slate-300 mb-1">Bid Amount (ETB)</label>
        <div className="relative">
          <DollarSign className="w-4 h-4 text-slate-500 absolute left-3.5 top-1/2 -translate-y-1/2" />
          <input
            type="number"
            step="0.01"
            {...register('amount')}
            placeholder="85000.00"
            className="w-full pl-10 pr-3.5 py-2.5 bg-slate-900 border border-slate-800 rounded-xl text-sm text-white focus:outline-none focus:border-cyan-500 transition"
          />
        </div>
        {errors.amount && <p className="text-[11px] text-rose-400 mt-1">{errors.amount.message}</p>}
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div>
          <label className="block text-xs font-semibold text-slate-300 mb-1">Proposed Pickup Date (Optional)</label>
          <input
            type="datetime-local"
            {...register('proposed_pickup_date')}
            className="w-full px-3.5 py-2.5 bg-slate-900 border border-slate-800 rounded-xl text-sm text-white focus:outline-none focus:border-cyan-500 transition"
          />
        </div>

        <div>
          <label className="block text-xs font-semibold text-slate-300 mb-1">Estimated Delivery Date (Optional)</label>
          <input
            type="datetime-local"
            {...register('estimated_delivery_date')}
            className="w-full px-3.5 py-2.5 bg-slate-900 border border-slate-800 rounded-xl text-sm text-white focus:outline-none focus:border-cyan-500 transition"
          />
        </div>
      </div>

      <div>
        <label className="block text-xs font-semibold text-slate-300 mb-1">Transporter Proposal / Notes (Optional)</label>
        <textarea
          rows={3}
          {...register('message')}
          placeholder="e.g. 40ft Flatbed trailer available at Djibouti Port yard; ready for immediate loading."
          className="w-full px-3.5 py-2.5 bg-slate-900 border border-slate-800 rounded-xl text-sm text-white focus:outline-none focus:border-cyan-500 transition"
        />
      </div>

      <div className="pt-2 flex justify-end space-x-3">
        {onCancel && (
          <button
            type="button"
            onClick={onCancel}
            className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 font-semibold text-xs rounded-xl transition"
          >
            Cancel
          </button>
        )}
        <button
          type="submit"
          disabled={submitting}
          className="px-5 py-2 bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-white font-semibold text-xs rounded-xl shadow-lg shadow-cyan-500/20 transition flex items-center space-x-2"
        >
          {submitting ? (
            <span className="animate-pulse">Submitting Bid...</span>
          ) : (
            <>
              <CheckCircle2 className="w-4 h-4" />
              <span>{initialData ? 'Update Bid' : 'Submit Rate Bid'}</span>
            </>
          )}
        </button>
      </div>
    </form>
  );
};
