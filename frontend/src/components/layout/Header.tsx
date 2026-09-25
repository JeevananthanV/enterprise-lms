import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import {
  Shield,
  Bell,
  Search,
  Menu,
  Server,
  LogOut,
  User as UserIcon,
  ChevronRight,
  Activity,
} from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import { Badge } from '../common/Badge';

export interface HeaderProps {
  onToggleSidebar: () => void;
  systemStatus?: string;
}

export const Header: React.FC<HeaderProps> = ({
  onToggleSidebar,
  systemStatus = 'healthy',
}) => {
  const { user, logout, isAuthenticated } = useAuth();
  const navigate = useNavigate();
  const [searchQuery, setSearchQuery] = useState('');
  const [showNotifications, setShowNotifications] = useState(false);
  const [showUserMenu, setShowUserMenu] = useState(false);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      navigate(`/courses?search=${encodeURIComponent(searchQuery.trim())}`);
    }
  };

  return (
    <header className="sticky top-0 z-30 flex h-16 w-full items-center justify-between border-b border-slate-200 bg-white/95 backdrop-blur-md px-4 md:px-6">
      {/* Brand & Mobile Toggle */}
      <div className="flex items-center gap-3">
        <button
          onClick={onToggleSidebar}
          className="p-2 rounded-lg text-slate-500 hover:bg-slate-100 md:hidden focus:outline-none focus:ring-2 focus:ring-slate-300"
          aria-label="Toggle Sidebar"
        >
          <Menu className="w-5 h-5" />
        </button>

        <Link to="/" className="flex items-center gap-2.5 group">
          <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-tr from-sky-600 to-indigo-600 text-white font-bold shadow-sm transition-transform group-hover:scale-105">
            <Shield className="w-5 h-5" />
          </div>
          <div>
            <span className="font-bold text-slate-900 tracking-tight text-base hidden sm:inline">
              Enterprise <span className="text-sky-600">LMS</span>
            </span>
            <span className="block text-[10px] uppercase font-semibold tracking-wider text-slate-400">
              Multi-Tenant Architecture
            </span>
          </div>
        </Link>
      </div>

      {/* Global Quick Search Bar */}
      <form onSubmit={handleSearchSubmit} className="hidden md:flex items-center flex-1 max-w-md mx-6">
        <div className="relative w-full">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search courses, syllabi, certifications..."
            className="w-full pl-9 pr-4 py-1.5 text-xs bg-slate-100 border border-transparent rounded-lg focus:bg-white focus:border-sky-500 focus:outline-none focus:ring-2 focus:ring-sky-100 transition-all"
          />
        </div>
      </form>

      {/* Right Controls & User Info */}
      <div className="flex items-center gap-2.5">
        {/* System Status Pill */}
        <div
          className="hidden lg:flex items-center gap-1.5 px-2.5 py-1 bg-slate-50 border border-slate-200 rounded-full text-xs"
          title="Multi-tier: PostgreSQL + MongoDB + Redis Online"
        >
          <div className="flex items-center gap-1">
            <Server className="w-3.5 h-3.5 text-slate-500" />
            <Activity className="w-3 h-3 text-sky-500" />
          </div>
          <span className="text-slate-500 text-[11px]">System:</span>
          <span className="flex h-2 w-2 relative">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
          </span>
          <span className="font-semibold text-slate-700 text-[11px] capitalize">{systemStatus}</span>
        </div>

        {/* Notifications Dropdown Trigger */}
        <div className="relative">
          <button
            onClick={() => {
              setShowNotifications(!showNotifications);
              setShowUserMenu(false);
            }}
            className="relative p-2 rounded-lg text-slate-500 hover:bg-slate-100 focus:outline-none"
            title="Notifications"
            aria-label="View notifications"
          >
            <Bell className="w-5 h-5" />
            <span className="absolute top-1.5 right-1.5 w-2 h-2 rounded-full bg-sky-500 ring-2 ring-white"></span>
          </button>

          {/* Notifications Drawer Popover */}
          {showNotifications && (
            <div className="absolute right-0 mt-2 w-80 bg-white rounded-2xl border border-slate-200 shadow-xl p-4 z-50 animate-in fade-in slide-in-from-top-2 duration-150">
              <div className="flex items-center justify-between pb-2 border-b border-slate-100">
                <h4 className="text-xs font-bold text-slate-900 uppercase tracking-wider">
                  Notifications
                </h4>
                <span className="text-[10px] font-semibold text-sky-600 bg-sky-50 px-2 py-0.5 rounded-full">
                  2 New
                </span>
              </div>
              <div className="divide-y divide-slate-100 mt-2">
                <div className="py-2.5 text-xs">
                  <p className="font-semibold text-slate-800">Course Certificate Ready</p>
                  <p className="text-[11px] text-slate-500 mt-0.5">
                    Your certificate for PostgreSQL Architecture is available.
                  </p>
                </div>
                <div className="py-2.5 text-xs">
                  <p className="font-semibold text-slate-800">Redis Cache Sync Complete</p>
                  <p className="text-[11px] text-slate-500 mt-0.5">
                    Course catalogs and syllabi cached with sub-millisecond latency.
                  </p>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Authenticated User Menu */}
        {isAuthenticated && user ? (
          <div className="relative">
            <button
              onClick={() => {
                setShowUserMenu(!showUserMenu);
                setShowNotifications(false);
              }}
              className="flex items-center gap-2 p-1 rounded-xl hover:bg-slate-50 border border-transparent hover:border-slate-200 transition-all focus:outline-none"
            >
              <div
                className={`w-8 h-8 rounded-full text-white flex items-center justify-center font-bold text-xs shadow-xs ${
                  user.role === 'PLATFORM_ADMIN'
                    ? 'bg-rose-600'
                    : user.role === 'INSTRUCTOR'
                    ? 'bg-amber-600'
                    : 'bg-sky-600'
                }`}
              >
                {user.full_name ? user.full_name[0].toUpperCase() : 'U'}
              </div>
              <div className="hidden xl:block text-left text-xs pr-1">
                <p className="font-semibold text-slate-900 leading-tight truncate max-w-[120px]">
                  {user.full_name}
                </p>
                <span className="text-[10px] text-slate-500 capitalize">{user.role.toLowerCase()}</span>
              </div>
              <ChevronRight className="w-3.5 h-3.5 text-slate-400 rotate-90 hidden xl:block" />
            </button>

            {/* User Dropdown */}
            {showUserMenu && (
              <div className="absolute right-0 mt-2 w-56 bg-white rounded-2xl border border-slate-200 shadow-xl p-3 z-50 animate-in fade-in slide-in-from-top-2 duration-150">
                <div className="px-2 py-1.5 border-b border-slate-100">
                  <p className="text-xs font-bold text-slate-900 truncate">{user.full_name}</p>
                  <p className="text-[11px] text-slate-500 truncate">{user.email}</p>
                  <Badge
                    variant={
                      user.role === 'PLATFORM_ADMIN'
                        ? 'error'
                        : user.role === 'INSTRUCTOR'
                        ? 'warning'
                        : 'info'
                    }
                    className="text-[9px] mt-1.5"
                  >
                    {user.role}
                  </Badge>
                </div>

                <div className="py-1">
                  <button
                    onClick={() => {
                      setShowUserMenu(false);
                      if (user.role === 'PLATFORM_ADMIN') navigate('/admin/dashboard');
                      else if (user.role === 'INSTRUCTOR') navigate('/instructor/dashboard');
                      else navigate('/student/dashboard');
                    }}
                    className="w-full text-left px-2 py-1.5 text-xs text-slate-700 hover:bg-slate-50 rounded-lg transition-colors flex items-center gap-2"
                  >
                    <UserIcon className="w-3.5 h-3.5 text-slate-400" />
                    <span>My Dashboard</span>
                  </button>
                  <button
                    onClick={() => {
                      setShowUserMenu(false);
                      navigate('/courses');
                    }}
                    className="w-full text-left px-2 py-1.5 text-xs text-slate-700 hover:bg-slate-50 rounded-lg transition-colors flex items-center gap-2"
                  >
                    <Search className="w-3.5 h-3.5 text-slate-400" />
                    <span>Browse Catalog</span>
                  </button>
                </div>

                <div className="pt-1 border-t border-slate-100">
                  <button
                    onClick={() => {
                      setShowUserMenu(false);
                      logout();
                    }}
                    className="w-full text-left px-2 py-1.5 text-xs font-semibold text-rose-600 hover:bg-rose-50 rounded-lg transition-colors flex items-center gap-2"
                  >
                    <LogOut className="w-3.5 h-3.5" />
                    <span>Sign Out</span>
                  </button>
                </div>
              </div>
            )}
          </div>
        ) : (
          <div className="flex items-center gap-2">
            <Link
              to="/login"
              className="px-3 py-1.5 text-xs font-semibold text-slate-700 hover:text-slate-900 hover:bg-slate-100 rounded-lg transition-colors"
            >
              Sign In
            </Link>
            <Link
              to="/register"
              className="px-3.5 py-1.5 text-xs font-semibold bg-sky-600 hover:bg-sky-700 text-white rounded-lg shadow-sm transition-colors"
            >
              Register
            </Link>
          </div>
        )}
      </div>
    </header>
  );
};

