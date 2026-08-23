import React from 'react';
import { Search, X } from 'lucide-react';

export const LoadSearchBar = ({ value, onChange, onClear, placeholder = 'Search loads by title, city, or specs...' }) => {
  return (
    <div className="relative flex-1">
      <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
      <input
        type="text"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        className="w-full pl-10 pr-9 py-2 bg-slate-900/80 border border-slate-800 rounded-xl text-xs text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500 transition"
      />
      {value && (
        <button onClick={onClear} className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-500 hover:text-slate-300">
          <X className="w-3.5 h-3.5" />
        </button>
      )}
    </div>
  );
};
