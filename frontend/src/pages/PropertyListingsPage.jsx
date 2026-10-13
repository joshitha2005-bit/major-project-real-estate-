import React, { useEffect, useState } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { propertyService } from '../services/propertyService';
import { Navbar } from '../components/Navbar';
import { Footer } from '../components/Footer';
import { PropertyCard } from '../components/PropertyCard';
import { 
  Building2, MapPin, Search, Plus, Filter, 
  ArrowRight, Loader2, IndianRupee, Layers, CheckCircle2,
  ShieldCheck, ExternalLink, Landmark
} from 'lucide-react';

const PROPERTY_TYPES = ["All", "Apartment", "Villa", "Independent House", "Penthouse", "Plot"];

export const PropertyListingsPage = () => {
  const [searchParams, setSearchParams] = useSearchParams();

  const [properties, setProperties] = useState([]);
  const [districtsList, setDistrictsList] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState(searchParams.get('q') || '');
  const [selectedDistrict, setSelectedDistrict] = useState(searchParams.get('district') || 'All');
  const [selectedType, setSelectedType] = useState('All');
  const [selectedBhk, setSelectedBhk] = useState(null);
  
  // RERA Registered Projects State (kept strictly separate from individual listings)
  const [activeCatalogTab, setActiveCatalogTab] = useState('individual'); // 'individual' | 'rera'
  const [reraProjects, setReraProjects] = useState([]);
  const [reraLoading, setReraLoading] = useState(false);

  // Additional listing filter states
  const [selectedListingType, setSelectedListingType] = useState('All');
  const [minPrice, setMinPrice] = useState('');
  const [maxPrice, setMaxPrice] = useState('');
  const [minArea, setMinArea] = useState('');
  const [maxArea, setMaxArea] = useState('');
  const [selectedFurnishing, setSelectedFurnishing] = useState('All');
  const [selectedParking, setSelectedParking] = useState('All');

  // Load districts on mount
  useEffect(() => {
    const fetchDistricts = async () => {
      try {
        const res = await propertyService.getDistricts();
        if (res && res.districts) {
          setDistrictsList(res.districts);
        }
      } catch (e) {
        console.error("Failed to load districts:", e);
      }
    };
    fetchDistricts();
  }, []);

  // Fetch K-RERA Projects whenever selectedDistrict changes
  useEffect(() => {
    fetchReraProjects();
  }, [selectedDistrict]);

  const fetchReraProjects = async () => {
    setReraLoading(true);
    try {
      const data = await propertyService.getReraProjects(selectedDistrict);
      setReraProjects(data.projects || []);
    } catch (e) {
      console.error("Failed to load RERA projects:", e);
    } finally {
      setReraLoading(false);
    }
  };

  // Update selectedDistrict if URL query param changes
  useEffect(() => {
    const distParam = searchParams.get('district');
    if (distParam && distParam !== selectedDistrict) {
      setSelectedDistrict(distParam);
    }
  }, [searchParams]);

  useEffect(() => {
    fetchProperties();
  }, [
    selectedDistrict, selectedType, selectedBhk, selectedListingType, 
    minPrice, maxPrice, minArea, maxArea, 
    selectedFurnishing, selectedParking
  ]);

  const fetchProperties = async () => {
    setLoading(true);
    try {
      const params = {};
      if (searchQuery.trim()) params.query = searchQuery.trim();
      if (selectedDistrict && selectedDistrict !== 'All') params.district = selectedDistrict;
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

  const handleDistrictChange = (dist) => {
    setSelectedDistrict(dist);
    const newParams = {};
    if (searchQuery.trim()) newParams.q = searchQuery.trim();
    if (dist !== 'All') newParams.district = dist;
    setSearchParams(newParams);
  };

  return (
    <div className="min-h-screen flex flex-col bg-dark-950 text-slate-100">
      <Navbar />

      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
        {/* Banner Header */}
        <div className="glass-card p-8 rounded-3xl border border-slate-800 flex flex-col md:flex-row items-start md:items-center justify-between gap-6 relative overflow-hidden bg-gradient-to-r from-slate-950 via-slate-900 to-slate-950">
          <div className="space-y-2 z-10">
            <div className="flex items-center gap-2">
              <span className="text-xs uppercase font-extrabold tracking-widest text-brand-400">Government Verified Records</span>
              <span className="text-slate-600">•</span>
              <span className="text-xs font-semibold text-emerald-400 flex items-center gap-1">
                <CheckCircle2 className="w-3.5 h-3.5" /> 31 Districts Supported
              </span>
            </div>
            <h1 className="text-3xl font-extrabold font-outfit text-white">Karnataka Real Estate Catalog</h1>
            <p className="text-xs sm:text-sm text-slate-400 max-w-2xl">
              Authentic property listings across all 31 Karnataka administrative districts with multimodal AI valuation, Geoapify GIS spatial analysis, and explainable intelligence.
            </p>
          </div>
        </div>

        {/* State & District Selector Bar */}
        <div className="bg-slate-900/60 p-4 sm:p-5 rounded-2xl border border-slate-800 space-y-4">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div className="flex items-center gap-2.5">
              <span className="text-xs uppercase font-extrabold tracking-wider text-slate-400">State:</span>
              <span className="px-3 py-1 rounded-xl bg-brand-500/10 border border-brand-500/30 text-brand-300 font-bold text-xs flex items-center gap-1.5">
                <MapPin className="w-3.5 h-3.5 text-brand-400" />
                Karnataka
              </span>
            </div>

            <div className="flex items-center gap-2.5 w-full sm:w-auto">
              <label htmlFor="district-select" className="text-xs uppercase font-extrabold tracking-wider text-slate-400 whitespace-nowrap">
                District:
              </label>
              <select
                id="district-select"
                value={selectedDistrict}
                onChange={(e) => handleDistrictChange(e.target.value)}
                className="w-full sm:w-72 bg-slate-950 border border-slate-700 hover:border-brand-500 px-3.5 py-2 rounded-xl text-xs sm:text-sm font-semibold text-white focus:outline-none focus:border-brand-500 transition-colors shadow-inner"
              >
                <option value="All">All Karnataka Districts (2,400+)</option>
                {districtsList.map((d) => (
                  <option key={d.district} value={d.district}>
                    {d.district} ({d.verified_properties} verified)
                  </option>
                ))}
              </select>
            </div>
          </div>

          {/* Quick-select District Pills */}
          <div className="flex items-center gap-1.5 overflow-x-auto pb-1 scrollbar-none text-xs">
            <button
              onClick={() => handleDistrictChange('All')}
              className={`px-3 py-1.5 rounded-xl font-medium whitespace-nowrap transition-all border ${
                selectedDistrict === 'All'
                  ? 'bg-brand-600 text-white border-brand-500 shadow-md shadow-brand-500/20'
                  : 'bg-slate-950 text-slate-400 border-slate-800 hover:text-white'
              }`}
            >
              All Districts
            </button>
            {['Bengaluru Urban', 'Mysuru', 'Belagavi', 'Dakshina Kannada', 'Dharwad', 'Kalaburagi', 'Tumakuru', 'Shivamogga', 'Ballari', 'Vijayapura', 'Hassan', 'Mandya', 'Udupi'].map((dist) => (
              <button
                key={dist}
                onClick={() => handleDistrictChange(dist)}
                className={`px-3 py-1.5 rounded-xl font-medium whitespace-nowrap transition-all border ${
                  selectedDistrict === dist
                    ? 'bg-brand-600 text-white border-brand-500 shadow-md shadow-brand-500/20'
                    : 'bg-slate-950 text-slate-400 border-slate-800 hover:text-white'
                }`}
              >
                {dist}
              </button>
            ))}
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
                placeholder="Search properties by title, locality (e.g. Gokulam, Navanagar, Whitefield), or address..."
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

        {/* Category Tabs: Individual Properties vs Government K-RERA Projects */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800 pb-4">
          <div className="flex items-center gap-2">
            <button
              onClick={() => setActiveCatalogTab('individual')}
              className={`px-4 py-2 rounded-xl text-xs sm:text-sm font-bold flex items-center gap-2 transition-all border ${
                activeCatalogTab === 'individual'
                  ? 'bg-brand-600 text-white border-brand-500 shadow-md shadow-brand-500/25'
                  : 'bg-slate-900/60 text-slate-400 border-slate-800 hover:text-white'
              }`}
            >
              <Building2 className="w-4 h-4" />
              <span>Individual Properties</span>
              <span className={`px-2 py-0.5 rounded-full text-[11px] font-extrabold ${
                activeCatalogTab === 'individual' ? 'bg-white/20 text-white' : 'bg-slate-800 text-slate-400'
              }`}>
                {properties.length}
              </span>
            </button>

            <button
              onClick={() => setActiveCatalogTab('rera')}
              className={`px-4 py-2 rounded-xl text-xs sm:text-sm font-bold flex items-center gap-2 transition-all border ${
                activeCatalogTab === 'rera'
                  ? 'bg-emerald-600 text-white border-emerald-500 shadow-md shadow-emerald-500/25'
                  : 'bg-slate-900/60 text-slate-400 border-slate-800 hover:text-white'
              }`}
            >
              <ShieldCheck className="w-4 h-4 text-emerald-400" />
              <span>Government K-RERA Projects</span>
              <span className={`px-2 py-0.5 rounded-full text-[11px] font-extrabold ${
                activeCatalogTab === 'rera' ? 'bg-white/20 text-white' : 'bg-slate-800 text-slate-400'
              }`}>
                {reraProjects.length}
              </span>
            </button>
          </div>

          <div className="text-xs text-slate-400">
            {activeCatalogTab === 'individual' ? (
              <span>
                Showing <strong className="text-white">{properties.length}</strong> individual properties in <strong className="text-brand-300">{selectedDistrict === 'All' ? 'Karnataka' : selectedDistrict}</strong>
              </span>
            ) : (
              <span>
                Showing <strong className="text-emerald-300">{reraProjects.length}</strong> registered projects in <strong className="text-emerald-300">{selectedDistrict === 'All' ? 'Karnataka' : selectedDistrict}</strong>
              </span>
            )}
          </div>
        </div>

        {/* Tab 1: Individual Properties Grid */}
        {activeCatalogTab === 'individual' && (
          <>
            {loading ? (
              <div className="py-20 text-center space-y-3">
                <Loader2 className="w-10 h-10 text-brand-500 animate-spin mx-auto" />
                <p className="text-xs text-slate-400 font-medium">Loading verified Karnataka properties...</p>
              </div>
            ) : properties.length === 0 ? (
              <div className="py-16 px-6 text-center bg-slate-900/40 rounded-3xl border border-slate-800/60 space-y-5 max-w-2xl mx-auto">
                <div className="w-14 h-14 rounded-2xl bg-amber-500/10 border border-amber-500/20 flex items-center justify-center mx-auto text-amber-400">
                  <Building2 className="w-7 h-7" />
                </div>
                <div className="space-y-2">
                  <h3 className="text-lg font-bold text-white">
                    No Individual House Listings for {selectedDistrict === 'All' ? 'Karnataka' : selectedDistrict}
                  </h3>
                  <p className="text-xs sm:text-sm text-slate-400 leading-relaxed">
                    Under our zero-synthetic authenticity policy, we never generate artificial properties.
                    {reraProjects.length > 0 ? (
                      <span>
                        {' '}However, <strong className="text-emerald-400">{reraProjects.length} official Government K-RERA registered projects</strong> are verified for {selectedDistrict}.
                      </span>
                    ) : (
                      ' You can explore other districts like Bengaluru Urban, Bengaluru Rural, or Ramanagara.'
                    )}
                  </p>
                </div>
                {reraProjects.length > 0 && (
                  <button
                    onClick={() => setActiveCatalogTab('rera')}
                    className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-semibold text-xs transition-all shadow-md shadow-emerald-600/20"
                  >
                    <ShieldCheck className="w-4 h-4" />
                    <span>View {reraProjects.length} Verified K-RERA Projects</span>
                  </button>
                )}
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {properties.map((prop) => (
                  <PropertyCard key={prop.id} property={prop} />
                ))}
              </div>
            )}
          </>
        )}

        {/* Tab 2: Government K-RERA Projects Grid */}
        {activeCatalogTab === 'rera' && (
          <div className="space-y-6">
            <div className="p-4 rounded-2xl bg-emerald-950/20 border border-emerald-800/30 flex items-start gap-3">
              <ShieldCheck className="w-5 h-5 text-emerald-400 flex-shrink-0 mt-0.5" />
              <div className="text-xs text-slate-300 space-y-1">
                <p className="font-bold text-emerald-300">
                  Karnataka Real Estate Regulatory Authority (K-RERA) Official Registry
                </p>
                <p className="text-slate-400">
                  These records represent authentic approved housing and development projects registered with K-RERA. 
                  In accordance with regulatory transparency, project registrations are preserved separately from individual unit listings.
                </p>
              </div>
            </div>

            {reraLoading ? (
              <div className="py-20 text-center space-y-3">
                <Loader2 className="w-10 h-10 text-emerald-500 animate-spin mx-auto" />
                <p className="text-xs text-slate-400 font-medium">Loading verified K-RERA projects...</p>
              </div>
            ) : reraProjects.length === 0 ? (
              <div className="py-16 text-center bg-slate-900/40 rounded-3xl border border-slate-800/60 space-y-3">
                <ShieldCheck className="w-10 h-10 text-slate-600 mx-auto" />
                <h3 className="text-base font-bold text-white">No K-RERA projects found</h3>
                <p className="text-xs text-slate-400">No registered projects recorded for {selectedDistrict}.</p>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {reraProjects.map((proj) => (
                  <div
                    key={proj.project_id || proj.registration_number}
                    className="p-5 rounded-2xl bg-slate-900/80 border border-slate-800 hover:border-emerald-500/50 transition-all flex flex-col justify-between space-y-4 group"
                  >
                    <div className="space-y-3">
                      <div className="flex items-center justify-between gap-2">
                        <span className="px-2.5 py-1 rounded-lg bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 font-mono text-[11px] font-bold">
                          {proj.district || selectedDistrict}
                        </span>
                        <span className="text-[10px] uppercase font-bold tracking-wider text-slate-500 flex items-center gap-1">
                          <CheckCircle2 className="w-3 h-3 text-emerald-400" />
                          K-RERA Verified
                        </span>
                      </div>

                      <h4 className="text-base font-bold text-white group-hover:text-emerald-300 transition-colors line-clamp-2">
                        {proj.project_name}
                      </h4>

                      <div className="space-y-1.5 text-xs text-slate-400">
                        <div>
                          <span className="text-slate-500">Promoter: </span>
                          <span className="text-slate-200 font-medium">{proj.promoter_name || 'N/A'}</span>
                        </div>
                        <div>
                          <span className="text-slate-500">Reg No: </span>
                          <span className="text-emerald-400/90 font-mono text-[11px]">{proj.registration_number}</span>
                        </div>
                      </div>
                    </div>

                    <div className="pt-3 border-t border-slate-800/80 flex items-center justify-between text-xs">
                      <span className="text-[10px] text-slate-500 uppercase tracking-wider">
                        Registered Project
                      </span>
                      <a
                        href={proj.source_url || "https://rera.karnataka.gov.in/viewAllProjects"}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="inline-flex items-center gap-1 text-emerald-400 hover:text-emerald-300 font-semibold transition-colors"
                      >
                        <span>Verify Portal</span>
                        <ExternalLink className="w-3.5 h-3.5" />
                      </a>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </main>

      <Footer />
    </div>
  );
};
