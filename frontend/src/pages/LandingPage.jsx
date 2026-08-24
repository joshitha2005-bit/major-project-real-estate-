import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { 
  Building2, MapPin, Search, Sparkles, ShieldCheck, 
  TrendingUp, Compass, Layers, ArrowRight, CheckCircle2 
} from 'lucide-react';
import { Navbar } from '../components/Navbar';
import { Footer } from '../components/Footer';
import { BangaloreLocationAutocomplete, BANGALORE_LOCALITIES } from '../components/BangaloreLocationAutocomplete';

export const LandingPage = () => {
  const [quickQuery, setQuickQuery] = useState('');
  const navigate = useNavigate();

  const handleQuickSearch = (e) => {
    if (e && e.preventDefault) e.preventDefault();
    if (quickQuery.trim()) {
      navigate(`/dashboard?search=${encodeURIComponent(quickQuery.trim())}`);
    } else {
      navigate('/dashboard');
    }
  };

  const featuredLocalities = [
    "Koramangala", "HSR Layout", "Electronic City", 
    "Whitefield", "Indiranagar", "Marathahalli", 
    "Bellandur", "Sarjapur Road"
  ];

  return (
    <div className="min-h-screen flex flex-col bg-dark-950 text-slate-100">
      <Navbar />

      {/* Hero Section */}
      <section className="relative pt-20 pb-32 overflow-hidden">
        {/* Glowing Background Orbs */}
        <div className="absolute top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-brand-500/15 rounded-full blur-[140px] pointer-events-none"></div>
        <div className="absolute top-1/3 right-10 w-[400px] h-[400px] bg-accent-500/15 rounded-full blur-[120px] pointer-events-none"></div>

        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10 text-center">
          {/* Badge */}
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full glass-card border-brand-500/30 text-brand-300 text-xs font-semibold uppercase tracking-wider mb-8 shadow-lg shadow-brand-500/10 animate-fade-in">
            <Sparkles className="w-4 h-4 text-brand-400" />
            <span>Bangalore Spatial GIS & Real Estate AI Engine</span>
          </div>

          {/* Heading */}
          <h1 className="text-4xl sm:text-6xl lg:text-7xl font-extrabold tracking-tight font-outfit max-w-4xl mx-auto leading-[1.15] mb-6">
            Predict Property Values with <span className="gradient-text">Precision Real Estate AI</span>
          </h1>

          {/* Subheading */}
          <p className="text-lg sm:text-xl text-slate-400 max-w-2xl mx-auto leading-relaxed mb-10">
            Search 50+ Bangalore localities or custom coordinates. Instantly query real estate valuations, nearby schools, metro lines, hospitals, and infrastructure.
          </p>

          {/* Hero Autocomplete Quick Search Box */}
          <form onSubmit={handleQuickSearch} className="max-w-2xl mx-auto mb-12 relative z-20">
            <div className="glass-card p-2 rounded-2xl flex flex-col sm:flex-row items-center gap-2 border border-slate-700/80 shadow-2xl">
              <div className="w-full">
                <BangaloreLocationAutocomplete
                  value={quickQuery}
                  onChange={(val) => setQuickQuery(val)}
                  onSelect={(val) => {
                    setQuickQuery(val);
                    navigate(`/dashboard?search=${encodeURIComponent(val)}`);
                  }}
                  placeholder="Enter locality (e.g. Koramangala, Whitefield, HSR Layout)..."
                />
              </div>
              <button
                type="submit"
                className="w-full sm:w-auto px-8 py-3.5 rounded-xl bg-gradient-to-r from-brand-600 to-accent-600 hover:from-brand-500 hover:to-accent-500 text-white font-semibold text-sm transition-all shadow-lg shadow-brand-500/25 flex items-center justify-center gap-2 flex-shrink-0"
              >
                <span>Analyze Locality</span>
                <ArrowRight className="w-4 h-4" />
              </button>
            </div>
          </form>

          {/* Featured Bangalore Badges */}
          <div className="flex flex-wrap items-center justify-center gap-2 max-w-3xl mx-auto">
            <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider mr-2">Featured Hubs:</span>
            {featuredLocalities.map((loc) => (
              <button
                key={loc}
                onClick={() => navigate(`/dashboard?search=${encodeURIComponent(loc)}`)}
                className="px-3 py-1.5 rounded-xl text-xs font-medium bg-slate-900/80 hover:bg-brand-500/20 text-slate-300 hover:text-brand-300 border border-slate-800 hover:border-brand-500/40 transition-all"
              >
                {loc}
              </button>
            ))}
          </div>
        </div>
      </section>

      {/* Feature Cards Grid */}
      <section className="py-20 bg-dark-900/50 border-t border-slate-800/80">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-3xl mx-auto mb-16 space-y-3">
            <span className="text-xs uppercase font-bold tracking-widest text-brand-500">Core Architecture</span>
            <h2 className="text-3xl sm:text-4xl font-bold font-outfit text-white">Engineered for Production GIS Workloads</h2>
            <p className="text-slate-400 text-sm">Full-stack platform built with FastAPI, PostgreSQL, Geoapify spatial APIs, and Leaflet interactive map canvases.</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {/* Feature 1 */}
            <div className="glass-card glass-card-hover p-8 rounded-2xl space-y-4">
              <div className="w-12 h-12 rounded-xl bg-brand-500/20 border border-brand-500/30 flex items-center justify-center text-brand-400">
                <Compass className="w-6 h-6" />
              </div>
              <h3 className="text-xl font-bold text-white font-outfit">Geoapify Geocoding API</h3>
              <p className="text-sm text-slate-400 leading-relaxed">
                Seamlessly convert string addresses for Koramangala, Whitefield, Electronic City, or any coordinate into precise lat/long positions and formatted location metadata.
              </p>
            </div>

            {/* Feature 2 */}
            <div className="glass-card glass-card-hover p-8 rounded-2xl space-y-4">
              <div className="w-12 h-12 rounded-xl bg-accent-500/20 border border-accent-500/30 flex items-center justify-center text-accent-400">
                <Layers className="w-6 h-6" />
              </div>
              <h3 className="text-xl font-bold text-white font-outfit">Categorized GIS Places</h3>
              <p className="text-sm text-slate-400 leading-relaxed">
                Automatically aggregate nearby schools, hospitals, metro stations, bus stops, restaurants, malls, banks, and colleges within a 5km radius.
              </p>
            </div>

            {/* Feature 3 */}
            <div className="glass-card glass-card-hover p-8 rounded-2xl space-y-4">
              <div className="w-12 h-12 rounded-xl bg-emerald-500/20 border border-emerald-500/30 flex items-center justify-center text-emerald-400">
                <TrendingUp className="w-6 h-6" />
              </div>
              <h3 className="text-xl font-bold text-white font-outfit">Real Estate Valuation</h3>
              <p className="text-sm text-slate-400 leading-relaxed">
                Compute estimated real estate price per sq.ft and locality valuation ranges based on spatial distance metrics and XGBoost ML regression models.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Tech Specifications */}
      <section className="py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="glass-card p-8 md:p-12 rounded-3xl border border-slate-800 flex flex-col lg:flex-row items-center justify-between gap-8">
            <div className="space-y-4 max-w-xl">
              <span className="text-xs uppercase font-bold tracking-widest text-emerald-400">Production Standard</span>
              <h3 className="text-2xl sm:text-3xl font-bold font-outfit text-white">Full Authentication & GIS API Integration</h3>
              <ul className="space-y-2.5 text-sm text-slate-300">
                <li className="flex items-center gap-2"><CheckCircle2 className="w-4 h-4 text-brand-400" /> JWT Bearer Authentication & Password Hashing</li>
                <li className="flex items-center gap-2"><CheckCircle2 className="w-4 h-4 text-brand-400" /> PostgreSQL & SQLAlchemy ORM Persistence</li>
                <li className="flex items-center gap-2"><CheckCircle2 className="w-4 h-4 text-brand-400" /> Leaflet & OpenStreetMap Vector Canvas</li>
                <li className="flex items-center gap-2"><CheckCircle2 className="w-4 h-4 text-brand-400" /> Automated Search History & Saved Favorites</li>
              </ul>
            </div>
            <div>
              <Link
                to="/register"
                className="px-8 py-4 rounded-2xl bg-brand-600 hover:bg-brand-500 text-white font-bold text-base shadow-xl shadow-brand-500/30 transition-all inline-flex items-center gap-3"
              >
                <span>Launch Interactive Dashboard</span>
                <ArrowRight className="w-5 h-5" />
              </Link>
            </div>
          </div>
        </div>
      </section>

      <Footer />
    </div>
  );
};
