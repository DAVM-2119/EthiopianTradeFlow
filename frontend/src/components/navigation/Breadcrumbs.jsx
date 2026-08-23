import React from 'react';
import { Link } from 'react-router-dom';
import { ChevronRight, Home } from 'lucide-react';

export const Breadcrumbs = ({ items = [] }) => {
  if (!items || items.length === 0) return null;

  return (
    <nav className="flex items-center space-x-1.5 text-xs text-slate-400 mb-1" aria-label="Breadcrumb">
      {items.map((item, idx) => {
        const isLast = idx === items.length - 1;
        return (
          <React.Fragment key={idx}>
            {idx > 0 && <ChevronRight className="w-3.5 h-3.5 text-slate-600 shrink-0" />}
            {isLast || !item.path ? (
              <span className="font-semibold text-cyan-400 truncate">{item.name}</span>
            ) : (
              <Link
                to={item.path}
                className="hover:text-slate-200 transition flex items-center space-x-1"
              >
                {idx === 0 && <Home className="w-3 h-3 text-slate-500 mr-1" />}
                <span>{item.name}</span>
              </Link>
            )}
          </React.Fragment>
        );
      })}
    </nav>
  );
};
