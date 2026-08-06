import React, { useEffect, useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { locationService } from '../services/locationService';
import { Navbar } from '../components/Navbar';
import { Footer } from '../components/Footer';
import { useNavigate } from 'react-router-dom';
import { 
  User, Mail, Calendar, Search, Bookmark, 
  MapPin, Shield, CheckCircle2, ArrowRight, Trash2 
} from 'lucide-react';

export const ProfilePage = () => {
  const { user, refreshProfile } = useAuth();
  const navigate = useNavigate();

  const [savedLocations, setSavedLocations] = useState([]);
  const [searchHistory, setSearchHistory] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      try {
        await refreshProfile();
        const [saved, history] = await Promise.all([
          locationService.getSavedLocations(),
          locationService.getSearchHistory(20)
        ]);
        setSavedLocations(saved || []);
        setSearchHistory(history || []);
      } catch (err) {
        console.error("Failed to load profile data:", err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  const formatDate = (dateStr) => {
    if (!dateStr) return 'N/A';
    return new Date(dateStr).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  return (
    <div className="min-h-screen flex flex-col bg-dark-950 text-slate-100">
      <Navbar />

      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
        {/* Profile Banner */}
        <div className="glass-card p-8 rounded-3xl border border-slate-800 flex flex-col md:flex-row items-start md:items-center justify-between gap-6 relative overflow-hidden">
          <div className="flex items-center gap-5">
            <div className="w-16 h-16 rounded-2xl bg-gradient-to-tr from-brand-600 to-accent-600 flex items-center justify-center text-2xl font-extrabold text-white shadow-xl shadow-brand-500/20">
              {user?.full_name?.charAt(0).toUpperCase() || 'U'}
            </div>
            <div className="space-y-1">
              <div className="flex items-center gap-2">
                <h1 className="text-2xl font-bold font-outfit text-white">{user?.full_name}</h1>
                <span className="px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 text-[10px] font-bold uppercase tracking-wider">
                  Active Account
                </span>
              </div>
              <p className="text-xs text-slate-400 flex items-center gap-2">
                <Mail className="w-3.5 h-3.5 text-brand-400" />
                {user?.email}
              </p>
              <p className="text-xs text-slate-500 flex items-center gap-2">
                <Calendar className="w-3.5 h-3.5 text-slate-400" />
                Member since {formatDate(user?.created_at)}
              </p>
            </div>
          </div>

          <div className="flex items-center gap-4 w-full md:w-auto">
            <div className="bg-slate-900/90 px-5 py-3 rounded-2xl border border-slate-800 flex-1 md:flex-initial text-center">
              <span className="text-[10px] uppercase font-bold text-slate-400">Total GIS Searches</span>
              <p className="text-xl font-extrabold text-brand-400">{user?.total_searches || searchHistory.length}</p>
            </div>
            <div className="bg-slate-900/90 px-5 py-3 rounded-2xl border border-slate-800 flex-1 md:flex-initial text-center">
              <span className="text-[10px] uppercase font-bold text-slate-400">Saved Locations</span>
              <p className="text-xl font-extrabold text-accent-400">{user?.total_saved || savedLocations.length}</p>
            </div>
          </div>
        </div>

        {/* Saved Locations & Full History Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Saved Locations Panel */}
          <div className="glass-card p-6 rounded-2xl border border-slate-800 space-y-4">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <h3 className="text-sm font-bold uppercase tracking-wider text-slate-200 flex items-center gap-2">
                <Bookmark className="w-4 h-4 text-accent-400" />
                Saved Locality Favorites
              </h3>
              <span className="text-xs font-mono bg-accent-500/10 text-accent-400 px-2 py-0.5 rounded">
                {savedLocations.length} Saved
              </span>
            </div>

            {loading ? (
              <p className="text-xs text-slate-400 py-8 text-center">Loading saved locations...</p>
            ) : savedLocations.length === 0 ? (
              <div className="py-12 text-center bg-slate-900/40 rounded-xl border border-slate-800/60 space-y-2">
                <Bookmark className="w-8 h-8 text-slate-600 mx-auto" />
                <p className="text-xs text-slate-400 font-medium">No saved locations yet</p>
                <p className="text-[11px] text-slate-500">Search for a locality in the Dashboard and click "Save Location".</p>
              </div>
            ) : (
              <div className="space-y-3 max-h-[450px] overflow-y-auto pr-1">
                {savedLocations.map((item) => (
                  <div
                    key={item.id}
                    className="p-4 rounded-xl bg-slate-900/80 border border-slate-800 hover:border-slate-700 transition-all flex items-center justify-between gap-4 group"
                  >
                    <div className="space-y-1">
                      <h4 className="text-sm font-bold text-white group-hover:text-brand-300 transition-colors">{item.title}</h4>
                      <p className="text-xs text-slate-400">{item.address}</p>
                      <p className="text-[10px] text-slate-500 font-mono">
                        Lat: {item.latitude.toFixed(4)}, Lon: {item.longitude.toFixed(4)}
                      </p>
                    </div>
                    <button
                      onClick={() => navigate(`/dashboard?search=${encodeURIComponent(item.title)}`)}
                      className="px-3 py-2 rounded-lg bg-brand-500/10 text-brand-300 hover:bg-brand-500/20 text-xs font-semibold flex items-center gap-1 flex-shrink-0"
                    >
                      <span>View</span>
                      <ArrowRight className="w-3.5 h-3.5" />
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Complete Search History Panel */}
          <div className="glass-card p-6 rounded-2xl border border-slate-800 space-y-4">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <h3 className="text-sm font-bold uppercase tracking-wider text-slate-200 flex items-center gap-2">
                <Search className="w-4 h-4 text-brand-400" />
                Historical Spatial Queries
              </h3>
              <span className="text-xs font-mono bg-brand-500/10 text-brand-400 px-2 py-0.5 rounded">
                {searchHistory.length} Logged
              </span>
            </div>

            {loading ? (
              <p className="text-xs text-slate-400 py-8 text-center">Loading search history...</p>
            ) : searchHistory.length === 0 ? (
              <div className="py-12 text-center bg-slate-900/40 rounded-xl border border-slate-800/60 space-y-2">
                <Search className="w-8 h-8 text-slate-600 mx-auto" />
                <p className="text-xs text-slate-400 font-medium">No search history recorded</p>
              </div>
            ) : (
              <div className="space-y-3 max-h-[450px] overflow-y-auto pr-1">
                {searchHistory.map((item) => (
                  <div
                    key={item.id}
                    className="p-3.5 rounded-xl bg-slate-900/80 border border-slate-800 flex items-center justify-between gap-4"
                  >
                    <div className="space-y-0.5">
                      <p className="text-xs font-bold text-slate-200">{item.query}</p>
                      <p className="text-[11px] text-slate-400 line-clamp-1">{item.formatted_address}</p>
                      <p className="text-[10px] text-slate-500">{formatDate(item.created_at)}</p>
                    </div>
                    <button
                      onClick={() => navigate(`/dashboard?search=${encodeURIComponent(item.query)}`)}
                      className="px-2.5 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-medium flex items-center gap-1 flex-shrink-0"
                    >
                      <ArrowRight className="w-3.5 h-3.5" />
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </main>

      <Footer />
    </div>
  );
};
