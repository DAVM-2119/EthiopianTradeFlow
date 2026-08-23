import React from 'react';

export const DashboardChart = ({ title, type = 'bar', data = [] }) => {
  if (!data || data.length === 0) {
    return (
      <div className="glass-panel p-6 rounded-2xl border border-slate-800 flex items-center justify-center h-56 text-xs text-slate-500">
        No chart metrics available
      </div>
    );
  }

  const maxValue = Math.max(...data.map((d) => d.value || d.amount || d.count || 1));

  return (
    <div className="glass-panel p-6 rounded-2xl border border-slate-800">
      <h3 className="text-sm font-bold text-white mb-4">{title}</h3>

      {type === 'bar' && (
        <div className="flex items-end justify-between h-40 pt-4 space-x-2 border-b border-slate-800">
          {data.map((item, idx) => {
            const val = item.value || item.amount || item.count || 0;
            const heightPct = Math.max(15, Math.round((val / maxValue) * 100));
            return (
              <div key={idx} className="flex-1 flex flex-col items-center group">
                <div className="text-[10px] text-cyan-300 font-semibold mb-1 opacity-0 group-hover:opacity-100 transition">
                  {val >= 1000 ? `${(val / 1000).toFixed(0)}k` : val}
                </div>
                <div
                  style={{ height: `${heightPct}%` }}
                  className="w-full max-w-[28px] bg-gradient-to-t from-cyan-600 to-blue-500 rounded-t-lg group-hover:from-cyan-400 group-hover:to-blue-400 transition"
                />
                <span className="text-[10px] text-slate-400 mt-2 font-medium">
                  {item.label || item.month || item.role || item.status}
                </span>
              </div>
            );
          })}
        </div>
      )}

      {type === 'list' && (
        <div className="space-y-3">
          {data.map((item, idx) => {
            const val = item.value || item.count || 0;
            const pct = Math.round((val / maxValue) * 100);
            return (
              <div key={idx} className="space-y-1">
                <div className="flex justify-between text-xs font-semibold">
                  <span className="text-slate-300">{item.status || item.role || item.label}</span>
                  <span className="text-cyan-400">{val}</span>
                </div>
                <div className="w-full h-2 bg-slate-900 rounded-full overflow-hidden">
                  <div
                    style={{ width: `${pct}%` }}
                    className="h-full bg-gradient-to-r from-cyan-500 to-blue-600 rounded-full"
                  />
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};
