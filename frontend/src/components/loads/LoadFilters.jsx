import React from 'react';
import { Filter, RotateCcw } from 'lucide-react';

export const LoadFilters = ({ filters, onChange, onReset }) => {
  const cargoOptions = [
    { value: '', label: 'All Cargo Types' },
    { value: 'GENERAL_CARGO', label: 'General Cargo' },
    { value: 'DRY_BULK', label: 'Dry Bulk' },
    { value: 'LIQUID_BULK', label: 'Liquid Bulk' },
    { value: 'CONTAINERIZED', label: 'Containerized' },
    { value: 'REFRIGERATED', label: 'Refrigerated' },
    { value: 'HAZARDOUS', label: 'Hazardous' },
    { value: 'HEAVY_MACHINERY', label: 'Heavy Machinery' },
  ];

  const statusOptions = [
    { value: '', label: 'All Statuses' },
    { value: 'DRAFT', label: 'Draft' },
    { value: 'POSTED', label: 'Posted' },
    { value: 'BOOKED', label: 'Booked' },
    { value: 'CANCELLED', label: 'Cancelled' },
  ];

  return (
    <div className="glass-panel p-3 sm:p-4 rounded-xl border border-slate-800 flex flex-wrap items-center gap-3 text-xs">
      <div className="flex items-center space-x-1.5 text-slate-400 font-semibold shrink-0">
        <Filter className="w-4 h-4 text-cyan-400" />
        <span>Filters</span>
      </div>

      <input
        type="text"
        placeholder="Origin City"
        value={filters.origin_city || ''}
        onChange={(e) => onChange('origin_city', e.target.value)}
        className="px-3 py-1.5 bg-slate-900 border border-slate-800 rounded-lg text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500 min-w-[120px]"
      />

      <input
        type="text"
        placeholder="Destination City"
        value={filters.destination_city || ''}
        onChange={(e) => onChange('destination_city', e.target.value)}
        className="px-3 py-1.5 bg-slate-900 border border-slate-800 rounded-lg text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500 min-w-[120px]"
      />

      <select
        value={filters.cargo_type || ''}
        onChange={(e) => onChange('cargo_type', e.target.value)}
        className="px-3 py-1.5 bg-slate-900 border border-slate-800 rounded-lg text-slate-200 focus:outline-none focus:border-cyan-500"
      >
        {cargoOptions.map((opt) => (
          <option key={opt.value} value={opt.value}>
            {opt.label}
          </option>
        ))}
      </select>

      <select
        value={filters.status || ''}
        onChange={(e) => onChange('status', e.target.value)}
        className="px-3 py-1.5 bg-slate-900 border border-slate-800 rounded-lg text-slate-200 focus:outline-none focus:border-cyan-500"
      >
        {statusOptions.map((opt) => (
          <option key={opt.value} value={opt.value}>
            {opt.label}
          </option>
        ))}
      </select>

      <button
        onClick={onReset}
        className="px-2.5 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-400 hover:text-white rounded-lg flex items-center space-x-1 transition ml-auto"
      >
        <RotateCcw className="w-3.5 h-3.5" />
        <span>Reset</span>
      </button>
    </div>
  );
};
