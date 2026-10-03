import React, { useState } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Building2, User, LogOut, Menu, X, Home, Brain, Compass, Search as SearchIcon, Sparkles } from 'lucide-react';

export const Navbar = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const isActive = (path) => location.pathname === path;

  return (
    <nav className="sticky top-0 z-50 glass-card border-b border-slate-800/80 bg-dark-950/80 backdrop-blur-xl">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link to="/" className="flex items-center gap-3 group">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-brand-600 to-accent-500 flex items-center justify-center shadow-lg shadow-brand-500/20 group-hover:scale-105 transition-transform">
              <Building2 className="w-5 h-5 text-white" />
            </div>
            <div>
              <span className="text-xl font-extrabold tracking-tight text-white font-outfit">
                Real Estate <span className="gradient-text">AI</span>
              </span>
              <span className="block text-[10px] uppercase font-bold tracking-widest text-brand-500">
                GIS Intelligence
              </span>
            </div>
          </Link>

          {/* Desktop Navigation Links */}
          <div className="hidden md:flex items-center gap-5">
            <Link
              to="/"
              className={`flex items-center gap-1.5 text-sm font-medium transition-colors hover:text-brand-500 ${
                isActive('/') ? 'text-brand-500 font-semibold' : 'text-slate-300'
              }`}
            >
              <Home className="w-4 h-4" />
              Home
            </Link>

            <Link
              to="/properties"
              className={`flex items-center gap-1.5 text-sm font-medium transition-colors hover:text-brand-500 ${
                isActive('/properties') ? 'text-brand-500 font-semibold' : 'text-slate-300'
              }`}
            >
              <Building2 className="w-4 h-4" />
              Properties
            </Link>



            <Link
              to="/gis"
              className={`flex items-center gap-1.5 text-sm font-medium transition-colors hover:text-brand-500 ${
                isActive('/gis') || isActive('/dashboard') ? 'text-brand-500 font-semibold' : 'text-slate-300'
              }`}
            >
              <Compass className="w-4 h-4 text-emerald-400" />
              GIS Intelligence
            </Link>

            <Link
              to="/search"
              className={`flex items-center gap-1.5 text-sm font-medium transition-colors hover:text-brand-500 ${
                isActive('/search') ? 'text-brand-500 font-semibold' : 'text-slate-300'
              }`}
            >
              <SearchIcon className="w-4 h-4 text-brand-400" />
              Search
            </Link>

            <Link
              to="/subscription"
              className={`flex items-center gap-1.5 text-sm font-medium transition-colors hover:text-brand-500 ${
                isActive('/subscription') ? 'text-brand-500 font-semibold' : 'text-slate-300'
              }`}
            >
              <Sparkles className="w-4 h-4 text-amber-400" />
              PropPulse Pro
            </Link>

            <Link
              to="/profile"
              className={`flex items-center gap-1.5 text-sm font-medium transition-colors hover:text-brand-500 ${
                isActive('/profile') ? 'text-brand-500 font-semibold' : 'text-slate-300'
              }`}
            >
              <User className="w-4 h-4" />
              Profile
            </Link>

            <Link
              to="/list-property"
              className={`flex items-center gap-1.5 text-sm font-semibold px-3.5 py-1.5 rounded-xl transition-all shadow-md ${
                isActive('/list-property')
                  ? 'bg-emerald-500 text-white shadow-emerald-500/30'
                  : 'bg-emerald-500/15 text-emerald-400 hover:bg-emerald-500/25 border border-emerald-500/30'
              }`}
            >
              <Building2 className="w-4 h-4 text-emerald-400 group-hover:text-white" />
              List Your Property
            </Link>
          </div>


          {/* Action Buttons */}
          <div className="hidden md:flex items-center gap-4">
            {user ? (
              <div className="flex items-center gap-4">
                <div className="flex items-center gap-2 bg-slate-900/80 px-3 py-1.5 rounded-full border border-slate-800">
                  <div className="w-6 h-6 rounded-full bg-brand-500 flex items-center justify-center text-xs font-bold text-white">
                    {user.full_name?.charAt(0).toUpperCase() || 'U'}
                  </div>
                  <span className="text-xs font-semibold text-slate-200">{user.full_name}</span>
                </div>
                <button
                  onClick={handleLogout}
                  className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold bg-red-500/10 text-red-400 hover:bg-red-500/20 border border-red-500/20 transition-all"
                >
                  <LogOut className="w-3.5 h-3.5" />
                  Logout
                </button>
              </div>
            ) : (
              <div className="flex items-center gap-3">
                <Link
                  to="/login"
                  className="px-4 py-2 text-sm font-semibold text-slate-200 hover:text-white transition-colors"
                >
                  Sign In
                </Link>
                <Link
                  to="/register"
                  className="px-4 py-2 rounded-xl text-sm font-semibold text-white bg-gradient-to-r from-brand-600 to-accent-600 hover:from-brand-500 hover:to-accent-500 shadow-md shadow-brand-500/25 transition-all transform hover:-translate-y-0.5"
                >
                  Get Started
                </Link>
              </div>
            )}
          </div>

          {/* Mobile Menu Toggle */}
          <div className="md:hidden flex items-center">
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="p-2 text-slate-300 hover:text-white focus:outline-none"
            >
              {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile Drawer */}
      {mobileMenuOpen && (
        <div className="md:hidden bg-dark-900/95 border-b border-slate-800 px-4 pt-2 pb-6 space-y-3">
          <Link
            to="/"
            onClick={() => setMobileMenuOpen(false)}
            className="block px-3 py-2 rounded-md text-base font-medium text-slate-200 hover:bg-slate-800"
          >
            Home
          </Link>
          <Link
            to="/properties"
            onClick={() => setMobileMenuOpen(false)}
            className="block px-3 py-2 rounded-md text-base font-medium text-slate-200 hover:bg-slate-800"
          >
            Properties
          </Link>

          <Link
            to="/gis"
            onClick={() => setMobileMenuOpen(false)}
            className="block px-3 py-2 rounded-md text-base font-medium text-slate-200 hover:bg-slate-800"
          >
            GIS Intelligence
          </Link>
          <Link
            to="/search"
            onClick={() => setMobileMenuOpen(false)}
            className="block px-3 py-2 rounded-md text-base font-medium text-slate-200 hover:bg-slate-800"
          >
            Search
          </Link>
          <Link
            to="/subscription"
            onClick={() => setMobileMenuOpen(false)}
            className="block px-3 py-2 rounded-md text-base font-medium text-slate-200 hover:bg-slate-800"
          >
            PropPulse Pro
          </Link>
          <Link
            to="/profile"
            onClick={() => setMobileMenuOpen(false)}
            className="block px-3 py-2 rounded-md text-base font-medium text-slate-200 hover:bg-slate-800"
          >
            Profile
          </Link>

          {user ? (
            <button
              onClick={() => {
                setMobileMenuOpen(false);
                handleLogout();
              }}
              className="w-full text-left px-3 py-2 rounded-md text-base font-medium text-red-400 hover:bg-red-500/10"
            >
              Logout
            </button>
          ) : (
            <div className="pt-2 flex flex-col gap-2">
              <Link
                to="/login"
                onClick={() => setMobileMenuOpen(false)}
                className="w-full text-center px-4 py-2 rounded-lg text-slate-200 bg-slate-800 hover:bg-slate-700 font-medium"
              >
                Sign In
              </Link>
              <Link
                to="/register"
                onClick={() => setMobileMenuOpen(false)}
                className="w-full text-center px-4 py-2 rounded-lg text-white bg-brand-600 hover:bg-brand-500 font-medium"
              >
                Get Started
              </Link>
            </div>
          )}
        </div>
      )}
    </nav>
  );
};
