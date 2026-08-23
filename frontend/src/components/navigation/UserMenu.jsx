import React, { useState, useRef, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import { User, Settings, LogOut, ChevronDown } from 'lucide-react';

export const UserMenu = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [open, setOpen] = useState(false);
  const menuRef = useRef(null);

  const role = user?.role || 'SHIPPER';

  useEffect(() => {
    const handleClickOutside = (e) => {
      if (menuRef.current && !menuRef.current.contains(e.target)) {
        setOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleLogout = async () => {
    setOpen(false);
    await logout();
    navigate('/login');
  };

  return (
    <div className="relative" ref={menuRef}>
      <button
        onClick={() => setOpen(!open)}
        className="flex items-center space-x-3 p-1.5 rounded-xl hover:bg-slate-800/60 transition border border-transparent hover:border-slate-800"
      >
        <div className="w-8 h-8 rounded-lg bg-gradient-to-tr from-cyan-500 to-blue-600 text-white flex items-center justify-center font-bold text-xs shadow-sm">
          {user?.first_name?.[0] || user?.email?.[0]?.toUpperCase() || 'U'}
        </div>
        <div className="hidden sm:block text-left">
          <p className="text-xs font-semibold text-slate-200 leading-tight">
            {user?.first_name ? `${user.first_name} ${user.last_name || ''}` : user?.email}
          </p>
          <p className="text-[10px] text-cyan-400 font-medium">{role}</p>
        </div>
        <ChevronDown className="w-4 h-4 text-slate-400" />
      </button>

      {open && (
        <div className="absolute right-0 mt-2 w-56 glass-panel rounded-2xl shadow-2xl border border-slate-800 py-2 z-50 animate-in fade-in slide-in-from-top-2 duration-150">
          <div className="px-4 py-2 border-b border-slate-800">
            <p className="text-xs font-semibold text-white truncate">{user?.email}</p>
            <div className="flex items-center space-x-1.5 mt-1">
              <span className="w-2 h-2 rounded-full bg-emerald-400" />
              <span className="text-[10px] font-semibold text-emerald-300 uppercase">{role}</span>
            </div>
          </div>

          <div className="py-1">
            <Link
              to="/profile"
              onClick={() => setOpen(false)}
              className="flex items-center space-x-2.5 px-4 py-2 text-xs font-medium text-slate-300 hover:text-white hover:bg-slate-800/60 transition"
            >
              <User className="w-4 h-4 text-slate-400" />
              <span>Profile Settings</span>
            </Link>
            <Link
              to="/profile"
              onClick={() => setOpen(false)}
              className="flex items-center space-x-2.5 px-4 py-2 text-xs font-medium text-slate-300 hover:text-white hover:bg-slate-800/60 transition"
            >
              <Settings className="w-4 h-4 text-slate-400" />
              <span>Account Credentials</span>
            </Link>
          </div>

          <div className="pt-1 border-t border-slate-800">
            <button
              onClick={handleLogout}
              className="w-full flex items-center space-x-2.5 px-4 py-2 text-xs font-semibold text-rose-400 hover:bg-rose-500/10 transition text-left"
            >
              <LogOut className="w-4 h-4 text-rose-400" />
              <span>Sign Out</span>
            </button>
          </div>
        </div>
      )}
    </div>
  );
};
