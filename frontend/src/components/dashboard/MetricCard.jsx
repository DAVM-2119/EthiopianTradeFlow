import React from 'react';

export const MetricCard = ({ title, value, icon: Icon, color = 'cyan', subtext }) => {
  const colorMap = {
    cyan: { text: 'text-cyan-400', bg: 'bg-cyan-500/10', border: 'border-cyan-500/20' },
    amber: { text: 'text-amber-400', bg: 'bg-amber-500/10', border: 'border-amber-500/20' },
    emerald: { text: 'text-emerald-400', bg: 'bg-emerald-500/10', border: 'border-emerald-500/20' },
    purple: { text: 'text-purple-400', bg: 'bg-purple-500/10', border: 'border-purple-500/20' },
    rose: { text: 'text-rose-400', bg: 'bg-rose-500/10', border: 'border-rose-500/20' },
  };

  const theme = colorMap[color] || colorMap.cyan;

  return (
    <div className={`glass-card p-5 rounded-2xl border border-slate-800 hover:${theme.border} transition`}>
      <div className="flex items-center justify-between">
        <div>
          <p className="text-xs font-semibold text-slate-400">{title}</p>
          <p className="text-2xl font-black text-white mt-1">{value}</p>
          {subtext && <p className="text-[10px] text-slate-400 mt-1">{subtext}</p>}
        </div>
        <div className={`w-12 h-12 rounded-2xl ${theme.bg} ${theme.text} flex items-center justify-center shrink-0`}>
          <Icon className="w-6 h-6" />
        </div>
      </div>
    </div>
  );
};
