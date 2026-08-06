import React, { useEffect, useState } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { propertyService } from '../services/propertyService';
import { Navbar } from '../components/Navbar';
import { Footer } from '../components/Footer';
import { 
  Building2, MapPin, Search, Plus, Filter, 
  ArrowRight, Loader2, IndianRupee, Layers 
} from 'lucide-react';

const PROPERTY_TYPES = ["All", "Apartment", "Villa", "Independent House", "Penthouse", "Plot"];

export const PropertyListingsPage = () => {
  const [searchParams, setSearchParams] = useSearchParams();

  const [properties, setProperties] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState(searchParams.get('q') || '');
  const [selectedType, setSelectedType] = useState('All');
  const [selectedBhk, setSelectedBhk] = useState(null);

  useEffect(() => {
    fetchProperties();
  }, [selectedType, selectedBhk]);

  const fetchProperties = async () => {
    setLoading(true);
    try {
      const params = {};
      if (searchQuery.trim()) params.query = searchQuery.trim();
      if (selectedType !== 'All') params.property_type = selectedType;
      if (selectedBhk) params.bhk = selectedBhk;

      const data = await propertyService.getProperties(params);
      setProperties(data.items || []);
    } catch (err) {
      console.error("Failed to fetch properties:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    fetchProperties();
  };

  return (
    <div className="min-h-screen flex flex-col bg-dark-950 text-slate-100">
      <Navbar />

      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
        {/* Banner Header */}
        <div className="glass-card p-8 rounded-3xl border border-slate-800 flex flex-col md:flex-row items-start md:items-center justify-between gap-6 relative overflow-hidden">
          <div className="space-y-2 z-10">
            <span className="text-xs uppercase font-bold tracking-widest text-brand-400">GIS Verified Inventory</span>
            <h1 className="text-3xl font-extrabold font-outfit text-white">Bangalore Real Estate Catalog</h1>
            <p className="text-xs sm:text-sm text-slate-400">
              Browse properties complete with spatial GIS metrics, amenity scoring, and locality analytics.
            </p>
          </div>
        </div>

        {/* Search & Filter Bar */}
        <div className="space-y-4">
          <form onSubmit={handleSearchSubmit} className="flex flex-col sm:flex-row items-center gap-3">
            <div className="relative w-full">
              <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none text-slate-500">
                <Search className="w-5 h-5" />
              </div>
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search properties by title, locality (e.g. Koramangala, Whitefield), or address..."
                className="w-full pl-12 pr-4 py-3.5 rounded-2xl bg-slate-900/90 border border-slate-800 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-brand-500 shadow-xl transition-all"
              />
            </div>
            <button
              type="submit"
              className="w-full sm:w-auto px-8 py-3.5 rounded-2xl bg-brand-600 hover:bg-brand-500 text-white font-semibold text-sm shadow-md transition-all flex items-center justify-center gap-2 flex-shrink-0"
            >
              <span>Search</span>
            </button>
          </form>

          {/* Type & BHK Filter Pills */}
          <div className="flex flex-wrap items-center justify-between gap-4 border-b border-slate-800 pb-4">
            {/* Property Types */}
            <div className="flex items-center gap-2 overflow-x-auto pb-1 scrollbar-none">
              <span className="text-xs font-bold text-slate-500 uppercase tracking-wider whitespace-nowrap mr-1">Type:</span>
              {PROPERTY_TYPES.map((type) => (
                <button
                  key={type}
                  onClick={() => setSelectedType(type)}
                  className={`px-3.5 py-1.5 rounded-xl text-xs font-semibold whitespace-nowrap transition-all border ${
                    selectedType === type
                      ? 'bg-brand-500 text-white border-brand-400 shadow-md shadow-brand-500/25'
                      : 'bg-slate-900/80 text-slate-400 border-slate-800 hover:text-white'
                  }`}
                >
                  {type}
                </button>
              ))}
            </div>

            {/* BHK Filter */}
            <div className="flex items-center gap-2">
              <span className="text-xs font-bold text-slate-500 uppercase tracking-wider">BHK:</span>
              {[1, 2, 3, 4].map((bhk) => (
                <button
                  key={bhk}
                  onClick={() => setSelectedBhk(selectedBhk === bhk ? null : bhk)}
                  className={`px-3 py-1 rounded-lg text-xs font-semibold transition-all border ${
                    selectedBhk === bhk
                      ? 'bg-accent-600 text-white border-accent-500'
                      : 'bg-slate-900 text-slate-400 border-slate-800 hover:text-white'
                  }`}
                >
                  {bhk} BHK
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Property Grid List */}
        {loading ? (
          <div className="py-20 text-center space-y-3">
            <Loader2 className="w-10 h-10 text-brand-500 animate-spin mx-auto" />
            <p className="text-xs text-slate-400 font-medium">Loading property listings...</p>
          </div>
        ) : properties.length === 0 ? (
          <div className="py-20 text-center bg-slate-900/40 rounded-3xl border border-slate-800/60 space-y-4">
            <Building2 className="w-12 h-12 text-slate-600 mx-auto" />
            <div className="space-y-1">
              <h3 className="text-lg font-bold text-white">No properties found</h3>
              <p className="text-xs text-slate-400">Try adjusting your search criteria or select another locality.</p>
            </div>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {properties.map((prop) => (
              <div
                key={prop.id}
                className="glass-card glass-card-hover rounded-2xl overflow-hidden border border-slate-800 flex flex-col justify-between group"
              >
                {/* Image & Badges */}
                <div className="relative h-52 w-full overflow-hidden bg-slate-900">
                  {prop.images && prop.images[0] ? (
                    <img
                      src={prop.images[0]}
                      alt={prop.title}
                      className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
                    />
                  ) : (
                    <div className="w-full h-full flex items-center justify-center text-slate-600">
                      <Building2 className="w-12 h-12" />
                    </div>
                  )}

                  <div className="absolute top-3 left-3 flex items-center gap-2">
                    <span className="px-2.5 py-1 rounded-lg bg-dark-950/80 backdrop-blur-md text-brand-300 text-[10px] font-bold uppercase tracking-wider border border-brand-500/30">
                      {prop.property_type}
                    </span>
                    <span className="px-2.5 py-1 rounded-lg bg-dark-950/80 backdrop-blur-md text-accent-300 text-[10px] font-bold uppercase tracking-wider border border-accent-500/30">
                      {prop.bhk} BHK
                    </span>
                  </div>

                  <div className="absolute bottom-3 right-3 px-3 py-1 rounded-xl bg-dark-950/90 backdrop-blur-md border border-emerald-500/30">
                    <span className="text-xs font-mono font-extrabold text-emerald-400">{prop.price_formatted}</span>
                  </div>
                </div>

                {/* Body Content */}
                <div className="p-5 space-y-3 flex-1 flex flex-col justify-between">
                  <div className="space-y-1.5">
                    <h3 className="text-base font-bold text-white line-clamp-1 group-hover:text-brand-300 transition-colors">
                      {prop.title}
                    </h3>
                    <p className="text-xs text-slate-400 flex items-center gap-1 line-clamp-1">
                      <MapPin className="w-3.5 h-3.5 text-brand-400 flex-shrink-0" />
                      <span>{prop.address}</span>
                    </p>
                  </div>

                  {/* Attributes Bar */}
                  <div className="pt-3 border-t border-slate-800/80 grid grid-cols-3 gap-2 text-center text-xs">
                    <div className="bg-slate-900/60 p-2 rounded-lg border border-slate-800/60">
                      <span className="text-[10px] text-slate-500 block">Area</span>
                      <span className="font-bold text-slate-200">{prop.area_sqft} sqft</span>
                    </div>
                    <div className="bg-slate-900/60 p-2 rounded-lg border border-slate-800/60">
                      <span className="text-[10px] text-slate-500 block">Baths</span>
                      <span className="font-bold text-slate-200">{prop.bathrooms}</span>
                    </div>
                    <div className="bg-slate-900/60 p-2 rounded-lg border border-slate-800/60">
                      <span className="text-[10px] text-slate-500 block">Rate</span>
                      <span className="font-bold text-emerald-400">₹{prop.price_per_sqft}</span>
                    </div>
                  </div>

                  {/* Details Action Button */}
                  <Link
                    to={`/properties/${prop.id}`}
                    className="w-full py-2.5 rounded-xl bg-slate-900 hover:bg-brand-600 text-slate-200 hover:text-white font-semibold text-xs border border-slate-800 hover:border-brand-500 transition-all flex items-center justify-center gap-1.5 mt-2"
                  >
                    <span>View Property GIS Report</span>
                    <ArrowRight className="w-3.5 h-3.5" />
                  </Link>
                </div>
              </div>
            ))}
          </div>
        )}
      </main>

      <Footer />
    </div>
  );
};
