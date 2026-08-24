import React, { useEffect, useState } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { propertyService } from '../services/propertyService';
import { Navbar } from '../components/Navbar';
import { Footer } from '../components/Footer';
import { PropertyCard } from '../components/PropertyCard';
import { 
  Building2, MapPin, Search, Plus, Filter, 
  ArrowRight, Loader2, IndianRupee, Layers 
} from 'lucide-react';

const localFallbackImage = "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='800' height='600' viewBox='0 0 800 600'><rect width='800' height='600' fill='%230f172a'/><g transform='translate(400, 300)'><path d='M-60,40 L-60,-20 L0,-70 L60,-20 L60,40 Z' fill='none' stroke='%2338bdf8' stroke-width='6' stroke-linejoin='round'/><path d='M-20,40 L-20,0 L20,0 L20,40' fill='none' stroke='%2338bdf8' stroke-width='6' stroke-linejoin='round'/></g><text x='400' y='420' fill='%2364748b' font-family='sans-serif' font-size='20' font-weight='bold' text-anchor='middle'>Property Photo Unavailable</text></svg>";

const PROPERTY_TYPES = ["All", "Apartment", "Villa", "Independent House", "Penthouse", "Plot"];

export const PropertyListingsPage = () => {
  const [searchParams, setSearchParams] = useSearchParams();

  const [properties, setProperties] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState(searchParams.get('q') || '');
  const [selectedType, setSelectedType] = useState('All');
  const [selectedBhk, setSelectedBhk] = useState(null);
  
  // Phase 2B additional listing filter states
  const [selectedListingType, setSelectedListingType] = useState('All');
  const [minPrice, setMinPrice] = useState('');
  const [maxPrice, setMaxPrice] = useState('');
  const [minArea, setMinArea] = useState('');
  const [maxArea, setMaxArea] = useState('');
  const [selectedFurnishing, setSelectedFurnishing] = useState('All');
  const [selectedParking, setSelectedParking] = useState('All');

  useEffect(() => {
    fetchProperties();
  }, [
    selectedType, selectedBhk, selectedListingType, 
    minPrice, maxPrice, minArea, maxArea, 
    selectedFurnishing, selectedParking
  ]);

  const fetchProperties = async () => {
    setLoading(true);
    try {
      const params = {};
      if (searchQuery.trim()) params.query = searchQuery.trim();
      if (selectedType !== 'All') params.property_type = selectedType;
      if (selectedBhk) params.bhk = selectedBhk;
      if (selectedListingType !== 'All') params.listing_type = selectedListingType;
      if (minPrice) params.min_price = parseFloat(minPrice);
      if (maxPrice) params.max_price = parseFloat(maxPrice);
      if (minArea) params.min_area = parseFloat(minArea);
      if (maxArea) params.max_area = parseFloat(maxArea);
      if (selectedFurnishing !== 'All') params.furnishing = selectedFurnishing;
      if (selectedParking !== 'All') params.parking = selectedParking;

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

          {/* Advanced filters */}
          <div className="grid grid-cols-2 sm:grid-cols-5 gap-3 text-xs bg-slate-900/40 p-4 rounded-2xl border border-slate-800">
            {/* Buy / Rent */}
            <div className="space-y-1">
              <label className="text-[10px] uppercase font-bold text-slate-400">Listing Type</label>
              <select
                value={selectedListingType}
                onChange={(e) => setSelectedListingType(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 px-2.5 py-1.5 rounded-xl text-slate-200 text-xs focus:outline-none"
              >
                <option value="All">All Types</option>
                <option value="Buy">Buy</option>
                <option value="Rent">Rent</option>
              </select>
            </div>

            {/* Furnishing */}
            <div className="space-y-1">
              <label className="text-[10px] uppercase font-bold text-slate-400">Furnishing</label>
              <select
                value={selectedFurnishing}
                onChange={(e) => setSelectedFurnishing(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 px-2.5 py-1.5 rounded-xl text-slate-200 text-xs focus:outline-none"
              >
                <option value="All">All Furnishing</option>
                <option value="Fully Furnished">Fully Furnished</option>
                <option value="Semi-Furnished">Semi-Furnished</option>
                <option value="Unfurnished">Unfurnished</option>
              </select>
            </div>

            {/* Parking */}
            <div className="space-y-1">
              <label className="text-[10px] uppercase font-bold text-slate-400">Parking</label>
              <select
                value={selectedParking}
                onChange={(e) => setSelectedParking(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 px-2.5 py-1.5 rounded-xl text-slate-200 text-xs focus:outline-none"
              >
                <option value="All">All Parking</option>
                <option value="Covered">Covered</option>
                <option value="Open">Open</option>
                <option value="None">None</option>
              </select>
            </div>

            {/* Price Inputs */}
            <div className="space-y-1">
              <label className="text-[10px] uppercase font-bold text-slate-400">Price Range (INR)</label>
              <div className="flex items-center gap-1">
                <input
                  type="number"
                  placeholder="Min"
                  value={minPrice}
                  onChange={(e) => setMinPrice(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 px-2 py-1.5 rounded-lg text-slate-200 text-xs focus:outline-none"
                />
                <span className="text-slate-500">-</span>
                <input
                  type="number"
                  placeholder="Max"
                  value={maxPrice}
                  onChange={(e) => setMaxPrice(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 px-2 py-1.5 rounded-lg text-slate-200 text-xs focus:outline-none"
                />
              </div>
            </div>

            {/* Area Inputs */}
            <div className="space-y-1">
              <label className="text-[10px] uppercase font-bold text-slate-400">Area (Sqft)</label>
              <div className="flex items-center gap-1">
                <input
                  type="number"
                  placeholder="Min"
                  value={minArea}
                  onChange={(e) => setMinArea(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 px-2 py-1.5 rounded-lg text-slate-200 text-xs focus:outline-none"
                />
                <span className="text-slate-500">-</span>
                <input
                  type="number"
                  placeholder="Max"
                  value={maxArea}
                  onChange={(e) => setMaxArea(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 px-2 py-1.5 rounded-lg text-slate-200 text-xs focus:outline-none"
                />
              </div>
            </div>
          </div>

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
              <PropertyCard key={prop.id} property={prop} />
            ))}
          </div>
        )}
      </main>

      <Footer />
    </div>
  );
};
