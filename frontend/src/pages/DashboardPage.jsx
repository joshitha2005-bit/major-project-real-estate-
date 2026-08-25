import React, { useState, useEffect } from 'react';
import { useSearchParams, useNavigate, useLocation, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { locationService } from '../services/locationService';
import { propertyService } from '../services/propertyService';
import { Navbar } from '../components/Navbar';
import { Footer } from '../components/Footer';
import { MapView } from '../components/MapView';
import { NearbyPlacesList } from '../components/NearbyPlacesList';
import { PropertyCard } from '../components/PropertyCard';
import { LocalityStatsCard } from '../components/LocalityStatsCard';
import { BangaloreLocationAutocomplete } from '../components/BangaloreLocationAutocomplete';
import { 
  Search, Navigation, Clock, Bookmark, Sparkles, 
  MapPin, Loader2, IndianRupee, History, Compass, Check, Building2,
  Plus, X, CheckCircle2, Crown, Shield, Activity, ChevronRight, Lock, Map, LayoutGrid, Heart, User as UserIcon, ListChecks, CheckCircle
} from 'lucide-react';



export const DashboardPage = () => {
  const { user } = useAuth();
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const location = useLocation();

  const [activeTab, setActiveTab] = useState('portal'); // 'portal' or 'gis'
  const [allProperties, setAllProperties] = useState([]);
  const [verifyingId, setVerifyingId] = useState(null);
  const [dashboardStats, setDashboardStats] = useState(null);
  const [datasetStats, setDatasetStats] = useState(null);


  const [searchInput, setSearchInput] = useState('');

  const [activeSearchResult, setActiveSearchResult] = useState(null);
  const [localityStats, setLocalityStats] = useState(null);
  const [localityProperties, setLocalityProperties] = useState([]);
  const [currentLocation, setCurrentLocation] = useState(null);
  const [nearbyPlaces, setNearbyPlaces] = useState([]);
  const [searchHistory, setSearchHistory] = useState([]);
  const [savedLocations, setSavedLocations] = useState([]);

  const [loadingSearch, setLoadingSearch] = useState(false);
  const [loadingGeo, setLoadingGeo] = useState(false);
  const [loadingPlaces, setLoadingPlaces] = useState(false);
  const [loadingProps, setLoadingProps] = useState(false);
  const [isSaved, setIsSaved] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');

  // Post Property modal states
  const [showPostModal, setShowPostModal] = useState(false);
  const [postSuccess, setPostSuccess] = useState(false);
  const [postLoading, setPostLoading] = useState(false);
  const [postError, setPostError] = useState('');

  // Form states
  const [formListingType, setFormListingType] = useState('Buy');
  const [formPropType, setFormPropType] = useState('Apartment');
  const [formBhk, setFormBhk] = useState(2);
  const [formArea, setFormArea] = useState(1200);
  const [formPrice, setFormPrice] = useState(7500000);
  const [formLocality, setFormLocality] = useState('');
  const [formAddress, setFormAddress] = useState('');
  const [formBaths, setFormBaths] = useState(2);
  const [formBalconies, setFormBalconies] = useState(1);
  const [formFloor, setFormFloor] = useState(1);
  const [formTotalFloors, setFormTotalFloors] = useState(10);
  const [formAge, setFormAge] = useState('New');
  const [formFacing, setFormFacing] = useState('East');
  const [formParking, setFormParking] = useState('Covered');
  const [formFurnishing, setFormFurnishing] = useState('Semi-Furnished');
  const [formAmenities, setFormAmenities] = useState('Security, Power Backup, Water Supply, Lift');
  const [formDescription, setFormDescription] = useState('');
  const [formUploadFiles, setFormUploadFiles] = useState([]);
  const [formOwnerName, setFormOwnerName] = useState('');
  const [formOwnerPhone, setFormOwnerPhone] = useState('');

  // Phase 2B filter states
  const [filterListingType, setFilterListingType] = useState('All');
  const [filterPropType, setFilterPropType] = useState('All');
  const [filterBhk, setFilterBhk] = useState('All');
  const [filterMinPrice, setFilterMinPrice] = useState('');
  const [filterMaxPrice, setFilterMaxPrice] = useState('');
  const [filterMinArea, setFilterMinArea] = useState('');
  const [filterMaxArea, setFilterMaxArea] = useState('');
  const [filterFurnishing, setFilterFurnishing] = useState('All');
  const [filterParking, setFilterParking] = useState('All');
  const [nearbyRadius, setNearbyRadius] = useState(5000); // 1000 for 1 KM, 5000 for 5 KM

  useEffect(() => {
    fetchHistoryAndSaved();
    
    const queryParam = searchParams.get('search');
    if (queryParam || location.pathname === '/gis' || location.pathname === '/search') {
      setActiveTab('gis');
      if (queryParam) {
        setSearchInput(queryParam);
        handleSearch(queryParam);
      } else {
        setSearchInput("Koramangala");
        handleSearch("Koramangala");
      }
    } else {
      setActiveTab('portal');
      setSearchInput("Koramangala");
      handleSearch("Koramangala");
    }
  }, [location.pathname, searchParams]);


  // 1. Fetch nearby places whenever activeSearchResult or radius changes, with a stale-response guard
  useEffect(() => {
    if (!activeSearchResult) return;

    let isCurrent = true;
    const fetchPlaces = async () => {
      setLoadingPlaces(true);
      try {
        const places = await locationService.getNearbyPlaces(
          activeSearchResult.latitude,
          activeSearchResult.longitude,
          nearbyRadius
        );
        if (isCurrent) {
          setNearbyPlaces(places || []);
        }
      } catch (err) {
        console.error("Error fetching nearby places:", err);
        if (isCurrent) {
          setNearbyPlaces([]);
        }
      } finally {
        if (isCurrent) {
          setLoadingPlaces(false);
        }
      }
    };

    fetchPlaces();

    return () => {
      isCurrent = false;
    };
  }, [activeSearchResult, nearbyRadius]);

  // 2. Fetch locality statistics & property listings with filters and a stale-response guard
  useEffect(() => {
    if (!activeSearchResult) return;

    let isCurrent = true;
    const cleanLoc = (activeSearchResult.query || activeSearchResult.formatted_address || "").split(',')[0].trim();
    
    const fetchProps = async () => {
      setLoadingProps(true);
      // Clear old results immediately on search changes to prevent rendering stale properties
      setLocalityProperties([]);
      setLocalityStats(null);
      try {
        const params = {
          query: cleanLoc,
          limit: 20,
          lat: activeSearchResult.latitude,
          lon: activeSearchResult.longitude
        };
        if (filterListingType !== 'All') params.listing_type = filterListingType;
        if (filterPropType !== 'All') params.property_type = filterPropType;
        if (filterBhk !== 'All') params.bhk = parseInt(filterBhk);
        if (filterMinPrice) params.min_price = parseFloat(filterMinPrice);
        if (filterMaxPrice) params.max_price = parseFloat(filterMaxPrice);
        if (filterMinArea) params.min_area = parseFloat(filterMinArea);
        if (filterMaxArea) params.max_area = parseFloat(filterMaxArea);
        if (filterFurnishing !== 'All') params.furnishing = filterFurnishing;
        if (filterParking !== 'All') params.parking = filterParking;

        const [statsData, propsData] = await Promise.all([
          locationService.getLocalityStats(cleanLoc, activeSearchResult.latitude, activeSearchResult.longitude),
          propertyService.getProperties(params)
        ]);

        if (isCurrent) {
          // Verify returned properties match locality strictly
          const matchedItems = (propsData?.items || []).filter(item => {
            const queryClean = cleanLoc.toLowerCase().trim();
            const itemLoc = (item.locality || "").toLowerCase().trim();
            return itemLoc.includes(queryClean) || queryClean.includes(itemLoc);
          });
          setLocalityStats(statsData);
          setLocalityProperties(matchedItems);
        }
      } catch (err) {
        console.error("Error fetching stats/props:", err);
      } finally {
        if (isCurrent) {
          setLoadingProps(false);
        }
      }
    };

    fetchProps();

    return () => {
      isCurrent = false;
    };
  }, [
    activeSearchResult,
    filterListingType, filterPropType, filterBhk, 
    filterMinPrice, filterMaxPrice, filterMinArea, 
    filterMaxArea, filterFurnishing, filterParking
  ]);

  const fetchHistoryAndSaved = async () => {
    try {
      const [histData, savedData, propsData, dbStats] = await Promise.all([
        locationService.getSearchHistory(8),
        locationService.getSavedLocations(),
        propertyService.getProperties({ limit: 10 }),
        propertyService.getDashboardStats()
      ]);
      setSearchHistory(histData || []);
      setSavedLocations(savedData || []);
      setAllProperties(propsData?.items || []);
      setDashboardStats(dbStats || null);

      if (user?.role === 'ADMIN') {
        const dStats = await propertyService.getDatasetStats();
        setDatasetStats(dStats || null);
      }
    } catch (err) {
      console.error("Error fetching user history/saved:", err);
    }
  };



  const handleSearch = async (queryToSearch) => {
    const query = (queryToSearch || searchInput).trim();
    if (!query) return;

    setLoadingSearch(true);
    setErrorMsg('');
    setIsSaved(false);

    // Clear old data immediately to prevent stale states displaying
    setNearbyPlaces([]);
    setLocalityProperties([]);
    setLocalityStats(null);

    // Reset filters to defaults on location change
    setFilterListingType('All');
    setFilterPropType('All');
    setFilterBhk('All');
    setFilterMinPrice('');
    setFilterMaxPrice('');
    setFilterMinArea('');
    setFilterMaxArea('');
    setFilterFurnishing('All');
    setFilterParking('All');

    try {
      // Geocode via Geoapify
      const res = await locationService.searchLocation(query);
      if (!res) {
        throw new Error(`Location "${query}" could not be geocoded by Geoapify API.`);
      }

      setActiveSearchResult(res);

      const alreadySaved = savedLocations.some(
        s => Math.abs(s.latitude - res.latitude) < 0.001 && Math.abs(s.longitude - res.longitude) < 0.001
      );
      setIsSaved(alreadySaved);
      
      fetchHistoryAndSaved();
    } catch (err) {
      console.error(err);
      setErrorMsg(err.response?.data?.detail || err.message || `Unable to find locality "${query}". Please select a valid Bangalore location.`);
    } finally {
      setLoadingSearch(false);
    }
  };

  const handlePostPropertySubmit = async (e) => {
    e.preventDefault();
    setPostLoading(true);
    setPostError('');
    
    const amenitiesArr = formAmenities
      .split(',')
      .map(s => s.trim())
      .filter(s => s.length > 0);

    const payload = {
      title: `${formListingType === 'Rent' ? 'Rental' : 'Premium'} ${formBhk}BHK ${formPropType} in ${formLocality}`,
      property_type: formPropType,
      listing_type: formListingType,
      bhk: parseInt(formBhk),
      area_sqft: parseFloat(formArea),
      price: parseFloat(formPrice),
      address: formAddress,
      locality: formLocality,
      bathrooms: parseInt(formBaths),
      balconies: parseInt(formBalconies),
      floor: parseInt(formFloor),
      total_floors: parseInt(formTotalFloors),
      property_age: formAge,
      facing: formFacing,
      parking: formParking,
      furnishing: formFurnishing,
      amenities: amenitiesArr,
      description: formDescription,
      images: [],
      owner_name: formOwnerName,
      owner_phone: formOwnerPhone,
      seller_type: 'Owner',
      seller_name: formOwnerName,
      phone: formOwnerPhone
    };

    try {
      const created = await propertyService.createProperty(payload);
      
      if (formUploadFiles && formUploadFiles.length > 0) {
        await propertyService.uploadPropertyImages(created.id, formUploadFiles);
      }
      
      setPostSuccess(true);
      
      // Auto-refresh properties if viewing the same locality
      if (activeSearchResult) {
        const cleanLoc = (activeSearchResult.query || '').split(',')[0].trim().toLowerCase();
        if (cleanLoc === formLocality.trim().toLowerCase()) {
          setActiveSearchResult({ ...activeSearchResult });
        }
      }
    } catch (err) {
      console.error(err);
      setPostError(err.response?.data?.detail || err.message || "Failed to submit property listing.");
    } finally {
      setPostLoading(false);
    }
  };

  const handleAdminVerify = async (propId) => {
    setVerifyingId(propId);
    try {
      await propertyService.verifyProperty(propId, 'Verified');
      // Update local states
      setAllProperties(prev => prev.map(p => p.id === propId ? { ...p, verification_status: 'Verified' } : p));
      if (localityProperties.some(p => p.id === propId)) {
        setLocalityProperties(prev => prev.map(p => p.id === propId ? { ...p, verification_status: 'Verified' } : p));
      }
      alert(`Property ID ${propId} verified successfully!`);
    } catch (err) {
      console.error(err);
      alert("Failed to verify property.");
    } finally {
      setVerifyingId(null);
    }
  };




  const handleRadiusChange = (newRadius) => {
    setNearbyRadius(newRadius);
  };

  const handleCurrentLocationClick = () => {
    if (!navigator.geolocation) {
      setErrorMsg("Geolocation is not supported by your browser.");
      return;
    }

    setLoadingGeo(true);
    setErrorMsg('');

    // Clear old data
    setNearbyPlaces([]);
    setLocalityProperties([]);
    setLocalityStats(null);

    // Reset filters
    setFilterListingType('All');
    setFilterPropType('All');
    setFilterBhk('All');
    setFilterMinPrice('');
    setFilterMaxPrice('');
    setFilterMinArea('');
    setFilterMaxArea('');
    setFilterFurnishing('All');
    setFilterParking('All');

    navigator.geolocation.getCurrentPosition(
      async (position) => {
        const { latitude, longitude } = position.coords;
        try {
          const res = await locationService.getCurrentLocation(latitude, longitude);
          setCurrentLocation(res);
          setActiveSearchResult(res);
        } catch (err) {
          console.error(err);
          handleSearch("Koramangala");
        } finally {
          setLoadingGeo(false);
        }
      },
      (error) => {
        console.error("Geolocation error:", error);
        setErrorMsg("Unable to retrieve device location. Showing Koramangala default.");
        setLoadingGeo(false);
        handleSearch("Koramangala");
      },
      { timeout: 10000, enableHighAccuracy: true }
    );
  };


  const handleSaveLocation = async () => {
    if (!activeSearchResult || isSaved) return;
    try {
      const payload = {
        title: activeSearchResult.query || activeSearchResult.formatted_address,
        address: activeSearchResult.formatted_address,
        latitude: activeSearchResult.latitude,
        longitude: activeSearchResult.longitude
      };
      await locationService.saveLocation(payload);
      setIsSaved(true);
      fetchHistoryAndSaved();
    } catch (err) {
      console.error("Save location failed:", err);
    }
  };

  const topPresets = ["Koramangala", "Electronic City", "Whitefield", "HSR Layout", "Chandapura", "JP Nagar", "Indiranagar", "Bellandur"];

  return (
    <div className="min-h-screen flex flex-col bg-dark-950 text-slate-100">
      <Navbar />

      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
        {/* Navigation Tabs Header */}
        <div className="flex border-b border-slate-800 pb-px">
          <button
            onClick={() => setActiveTab('portal')}
            className={`px-6 py-3 text-sm font-bold border-b-2 transition-all flex items-center gap-2 ${
              activeTab === 'portal'
                ? 'border-brand-500 text-brand-400 font-extrabold'
                : 'border-transparent text-slate-400 hover:text-slate-200'
            }`}
          >
            <LayoutGrid className="w-4 h-4" />
            <span>Executive Dashboard</span>
          </button>
          <button
            onClick={() => setActiveTab('gis')}
            className={`px-6 py-3 text-sm font-bold border-b-2 transition-all flex items-center gap-2 ${
              activeTab === 'gis'
                ? 'border-brand-500 text-brand-400 font-extrabold'
                : 'border-transparent text-slate-400 hover:text-slate-200'
            }`}
          >
            <Compass className="w-4 h-4 text-emerald-400" />
            <span>GIS & Locality Map Search</span>
          </button>
        </div>

        {activeTab === 'portal' ? (
          <div className="space-y-8 animate-fadeIn">
            {/* Row 1: Welcome Banner & Quick Profile Info */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              <div className="lg:col-span-2 glass-card p-6 md:p-8 rounded-3xl border border-slate-800 flex flex-col justify-between gap-6 relative overflow-hidden bg-gradient-to-r from-slate-900/80 to-brand-950/20">
                <div className="absolute top-0 right-0 w-80 h-80 bg-brand-500/10 rounded-full blur-[90px] pointer-events-none"></div>
                <div className="space-y-2 z-10">
                  <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-brand-500/10 border border-brand-500/20 text-brand-300 text-xs font-semibold">
                    <Sparkles className="w-3.5 h-3.5 text-brand-400 animate-pulse" />
                    <span>Real-Estate Spatial & Valuation Engine</span>
                  </div>
                  <h1 className="text-2xl sm:text-3xl font-extrabold font-outfit text-white">
                    Welcome back, <span className="gradient-text">{user?.full_name || 'Valued User'}</span>
                  </h1>
                  <p className="text-xs text-slate-400 leading-relaxed max-w-lg">
                    Access Bengaluru's first academically defensive valuation system integrating ResNet-18 Computer Vision scans, TF-IDF descriptions, and GIS locality safety indices.
                  </p>
                </div>
                <div className="flex flex-wrap items-center gap-4 z-10 pt-4">
                  <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-slate-950/80 border border-slate-850 text-xs">
                    <Shield className="w-4 h-4 text-brand-400" />
                    <span className="text-slate-400">Role: <strong className="text-slate-200">{user?.role}</strong></span>
                  </div>
                  <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-slate-950/80 border border-slate-850 text-xs">
                    <Crown className={`w-4 h-4 ${user?.subscription_status === 'ACTIVE' ? 'text-amber-400' : 'text-slate-500'}`} />
                    <span className="text-slate-400">Status: <strong className="text-slate-200">{user?.subscription_status === 'ACTIVE' ? 'PRO' : 'FREE'}</strong></span>
                  </div>
                </div>
              </div>

              {/* Profile Card & Counters */}
              <div className="glass-card p-6 rounded-3xl border border-slate-800 bg-slate-900/10 flex flex-col justify-between space-y-4">
                <div className="border-b border-slate-850 pb-2">
                  <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400">Profile Summary</h4>
                  <p className="text-sm font-semibold text-white mt-1">{user?.email}</p>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div className="p-3.5 rounded-2xl bg-slate-900 border border-slate-800 text-center">
                    <Building2 className="w-5 h-5 text-brand-400 mx-auto mb-1" />
                    <span className="text-[10px] uppercase font-bold text-slate-500">Available Properties</span>
                    <p className="text-xl font-extrabold text-white mt-0.5">{allProperties.length || 109}</p>
                  </div>
                  <div className="p-3.5 rounded-2xl bg-slate-900 border border-slate-800 text-center">
                    <Bookmark className="w-5 h-5 text-emerald-400 mx-auto mb-1" />
                    <span className="text-[10px] uppercase font-bold text-slate-500">Saved Places</span>
                    <p className="text-xl font-extrabold text-white mt-0.5">{savedLocations.length}</p>
                  </div>
                </div>
              </div>
            </div>

            {/* Live Market Index Statistics Panel */}
            {dashboardStats && (
              <div className="glass-card p-6 md:p-8 rounded-3xl border border-slate-850 space-y-6 bg-slate-900/10">
                <div className="flex flex-wrap items-center justify-between gap-4 border-b border-slate-850 pb-4">
                  <div>
                    <h3 className="text-base font-bold font-outfit text-white">Live Bengaluru Market Index Statistics</h3>
                    <p className="text-xs text-slate-400 mt-1">Real-time indicators calculated directly from active SQLite catalog listings.</p>
                  </div>
                  <div className="text-right">
                    <span className="text-[10px] uppercase font-bold text-slate-500 block">Database Provenance</span>
                    <span className="text-xs font-bold text-brand-300">Dataset ({dashboardStats.dataset_listings}) | Direct ({dashboardStats.verified_direct + allProperties.filter(p => p.verification_status === 'Pending Verification').length})</span>
                  </div>
                </div>

                <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-4">
                  <div className="p-4 rounded-2xl bg-slate-950/60 border border-slate-850 space-y-1">
                    <span className="text-[10px] uppercase font-bold text-slate-500">Total Listings</span>
                    <p className="text-2xl font-black text-white">{dashboardStats.total_properties}</p>
                  </div>
                  <div className="p-4 rounded-2xl bg-slate-950/60 border border-slate-850 space-y-1">
                    <span className="text-[10px] uppercase font-bold text-slate-500">Buy Listings</span>
                    <p className="text-2xl font-black text-emerald-400">{dashboardStats.buy_properties}</p>
                  </div>
                  <div className="p-4 rounded-2xl bg-slate-950/60 border border-slate-850 space-y-1">
                    <span className="text-[10px] uppercase font-bold text-slate-500">Rent Listings</span>
                    <p className="text-2xl font-black text-accent-400">{dashboardStats.rent_properties}</p>
                  </div>
                  <div className="p-4 rounded-2xl bg-slate-950/60 border border-slate-850 space-y-1">
                    <span className="text-[10px] uppercase font-bold text-slate-500">Apartments</span>
                    <p className="text-2xl font-black text-blue-400">{dashboardStats.apartments}</p>
                  </div>
                  <div className="p-4 rounded-2xl bg-slate-950/60 border border-slate-850 space-y-1">
                    <span className="text-[10px] uppercase font-bold text-slate-500">Villas & Houses</span>
                    <p className="text-2xl font-black text-purple-400">{dashboardStats.villas + dashboardStats.independent_houses}</p>
                  </div>
                  <div className="p-4 rounded-2xl bg-slate-950/60 border border-slate-850 space-y-1">
                    <span className="text-[10px] uppercase font-bold text-slate-500">Localities</span>
                    <p className="text-2xl font-black text-amber-400">{dashboardStats.localities_covered}</p>
                  </div>
                </div>

                <div className="space-y-3 pt-2">
                  <span className="text-[10px] uppercase font-bold text-slate-500 tracking-wider block">Top Market Densities by Locality</span>
                  <div className="flex flex-wrap gap-2">
                    {dashboardStats.top_localities.slice(0, 8).map((item, idx) => (
                      <button
                        key={idx}
                        onClick={() => {
                          setSearchInput(item.name);
                          handleSearch(item.name);
                          setActiveTab('gis');
                        }}
                        className="px-3 py-1.5 rounded-xl bg-slate-900 hover:bg-brand-500/10 border border-slate-850 hover:border-brand-500/30 text-xs font-semibold text-slate-300 transition-all flex items-center gap-2 group"
                      >
                        <span className="text-slate-500 group-hover:text-brand-400 font-bold">{idx + 1}.</span>
                        <span className="text-slate-200 group-hover:text-white">{item.name}</span>
                        <span className="px-2 py-0.5 rounded-md bg-slate-955 text-[10px] font-black text-brand-400 group-hover:bg-brand-500/20">{item.count}</span>
                      </button>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {/* Quick Gating CTAs Row */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {/* Upgrade to Pro Card */}
              {user?.subscription_status !== 'ACTIVE' ? (
                <div className="glass-card p-6 rounded-3xl border border-brand-500/25 bg-gradient-to-r from-slate-900/90 to-brand-950/20 space-y-4 flex flex-col justify-between">
                  <div className="space-y-1.5">
                    <div className="flex items-center gap-1.5">
                      <Crown className="w-4 h-4 text-amber-400" />
                      <h4 className="text-xs uppercase font-extrabold tracking-wider text-white">Upgrade to Pro – ₹299/mo</h4>
                    </div>
                    <p className="text-[11px] text-slate-400 leading-relaxed">Get complete XGBoost predictions, local SHAP attributions, Image CV parameters, and ReportLab PDF downloads.</p>
                  </div>
                  <button
                    onClick={() => navigate('/subscription')}
                    className="w-full py-2.5 rounded-xl bg-brand-600 hover:bg-brand-500 text-white text-xs font-bold transition-all shadow-md shadow-brand-500/10 flex items-center justify-center gap-1.5"
                  >
                    <span>Upgrade Now</span>
                    <ChevronRight className="w-3.5 h-3.5" />
                  </button>
                </div>
              ) : (
                <div className="glass-card p-6 rounded-3xl border border-slate-800 space-y-4 flex flex-col justify-between">
                  <div className="space-y-1.5">
                    <div className="flex items-center gap-1.5">
                      <Crown className="w-4 h-4 text-emerald-400" />
                      <h4 className="text-xs uppercase font-extrabold tracking-wider text-white">Pro Plan Unlocked</h4>
                    </div>
                    <p className="text-[11px] text-slate-400 leading-relaxed">You have full access to all deep spatial intelligence valuation estimates, visual features scoring, and PDF reporting.</p>
                  </div>
                  <button
                    disabled
                    className="w-full py-2.5 rounded-xl bg-slate-850 border border-slate-800 text-slate-400 text-xs font-bold flex items-center justify-center gap-1.5 cursor-not-allowed"
                  >
                    <Check className="w-3.5 h-3.5 text-emerald-400" />
                    <span>Premium Subscription Active</span>
                  </button>
                </div>
              )}



              {/* Admin verifications CTA */}
              {user?.role === 'ADMIN' && (
                <div className="glass-card p-6 rounded-3xl border border-slate-850 bg-slate-900/10 space-y-4 flex flex-col justify-between md:col-span-2">
                  <div className="space-y-1">
                    <div className="flex items-center gap-1.5">
                      <ListChecks className="w-4 h-4 text-emerald-400" />
                      <h4 className="text-xs uppercase font-extrabold tracking-wider text-white">Pending Listings Verification Queue</h4>
                    </div>
                    <p className="text-[11px] text-slate-400">Admin access verified. Audit submitted property requests below to publish them live to catalog search.</p>
                  </div>
                  <div className="space-y-2 max-h-[140px] overflow-y-auto pr-1">
                    {allProperties.filter(p => p.verification_status !== 'Verified').length === 0 ? (
                      <p className="text-xs text-slate-500 italic py-2">No properties pending verification.</p>
                    ) : (
                      allProperties.filter(p => p.verification_status !== 'Verified').map(p => (
                        <div key={p.id} className="p-2.5 rounded-xl bg-slate-950 border border-slate-850 flex items-center justify-between text-xs gap-4">
                          <div className="truncate">
                            <p className="font-bold text-slate-200 truncate">{p.title}</p>
                            <p className="text-[10px] text-slate-500 truncate">{p.address} | Price: ₹{p.price.toLocaleString()}</p>
                          </div>
                          <button
                            onClick={() => handleAdminVerify(p.id)}
                            disabled={verifyingId === p.id}
                            className="px-3 py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-[10px] transition-all whitespace-nowrap flex items-center gap-1"
                          >
                            {verifyingId === p.id ? <Loader2 className="w-3 h-3 animate-spin" /> : <CheckCircle className="w-3 h-3" />}
                            <span>Verify</span>
                          </button>
                        </div>
                      ))
                    )}
                  </div>
                </div>
              )}

              {/* Admin Data Quality Audit Panel */}
              {user?.role === 'ADMIN' && datasetStats && (
                <div className="glass-card p-6 rounded-3xl border border-slate-850 bg-slate-900/10 space-y-4 md:col-span-3">
                  <div className="flex items-center justify-between border-b border-slate-850 pb-3">
                    <div className="flex items-center gap-2">
                      <Shield className="w-5 h-5 text-brand-400" />
                      <div>
                        <h4 className="text-xs uppercase font-extrabold tracking-wider text-white">Database Health & Data Quality Audit Panel</h4>
                        <p className="text-[10px] text-slate-500 mt-0.5">Admin-only statistics monitoring data completeness & provenance.</p>
                      </div>
                    </div>
                    <span className="px-2 py-0.5 rounded-full bg-slate-950 border border-slate-850 text-[10px] text-slate-400 font-mono">Role: ADMIN</span>
                  </div>

                  <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
                    <div className="p-3.5 rounded-2xl bg-slate-950/60 border border-slate-850">
                      <span className="text-[9px] uppercase font-bold text-slate-500 block">Dataset Listings</span>
                      <span className="text-base font-extrabold text-white">{datasetStats.dataset_listings}</span>
                    </div>
                    <div className="p-3.5 rounded-2xl bg-slate-950/60 border border-slate-850">
                      <span className="text-[9px] uppercase font-bold text-slate-500 block">Direct Postings</span>
                      <span className="text-base font-extrabold text-white">{datasetStats.direct_listings}</span>
                    </div>
                    <div className="p-3.5 rounded-2xl bg-slate-950/60 border border-slate-850">
                      <span className="text-[9px] uppercase font-bold text-slate-500 block">Unmapped Geocoding</span>
                      <span className="text-base font-extrabold text-amber-500">{datasetStats.missing_coordinates}</span>
                    </div>
                    <div className="p-3.5 rounded-2xl bg-slate-950/60 border border-slate-850">
                      <span className="text-[9px] uppercase font-bold text-slate-500 block">No Image Listings</span>
                      <span className="text-base font-extrabold text-slate-450">{datasetStats.missing_images}</span>
                    </div>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6 pt-2">
                    <div className="space-y-2">
                      <span className="text-[10px] uppercase font-bold text-slate-500 block">Listings Source Distribution</span>
                      <div className="space-y-1.5 max-h-[120px] overflow-y-auto pr-1">
                        {datasetStats.source_distribution.map((src, idx) => (
                          <div key={idx} className="flex items-center justify-between text-xs py-1.5 px-2.5 rounded-xl bg-slate-950 border border-slate-850">
                            <span className="text-slate-300 font-medium">{src.source}</span>
                            <span className="font-extrabold text-brand-400">{src.count}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                    <div className="space-y-2">
                      <span className="text-[10px] uppercase font-bold text-slate-500 block">Localities Data Distribution</span>
                      <div className="space-y-1.5 max-h-[120px] overflow-y-auto pr-1">
                        {datasetStats.locality_distribution.slice(0, 10).map((loc, idx) => (
                          <div key={idx} className="flex items-center justify-between text-xs py-1.5 px-2.5 rounded-xl bg-slate-950 border border-slate-850">
                            <span className="text-slate-300 font-medium">{loc.locality}</span>
                            <span className="font-extrabold text-brand-400">{loc.count}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>

            {/* Quick Locality Search and Preset Categories Highlight */}
            <div className="glass-card p-6 md:p-8 rounded-3xl border border-slate-800 space-y-6">
              <div className="space-y-1.5">
                <h3 className="text-base font-bold font-outfit text-white">Quick Property Locality Search</h3>
                <p className="text-xs text-slate-400">Search any major Bangalore locality to immediately view maps, coordinates, nearby amenities, and pricing listings.</p>
              </div>

              <form
                onSubmit={(e) => {
                  e.preventDefault();
                  if (searchInput.trim()) {
                    handleSearch(searchInput);
                    setActiveTab('gis');
                  }
                }}
                className="flex items-center gap-3 bg-slate-950 border border-slate-800 p-1.5 rounded-2xl"
              >
                <Search className="w-5 h-5 text-slate-500 ml-3" />
                <input
                  type="text"
                  value={searchInput}
                  onChange={(e) => setSearchInput(e.target.value)}
                  placeholder="Type locality (e.g. Whitefield, Indiranagar, HSR Layout, Electronic City)..."
                  className="w-full bg-transparent text-sm text-slate-200 placeholder-slate-500 focus:outline-none py-2"
                />
                <button
                  type="submit"
                  className="px-5 py-2.5 rounded-xl bg-gradient-to-r from-brand-600 to-accent-600 hover:from-brand-500 hover:to-accent-500 text-white font-semibold text-xs shadow-md transition-all whitespace-nowrap"
                >
                  Find Locality
                </button>
              </form>

              <div className="space-y-2">
                <span className="text-[10px] uppercase font-bold text-slate-500 tracking-wider block">Bengaluru Key Locality Highlights</span>
                <div className="grid grid-cols-2 sm:grid-cols-5 gap-4">
                  {[
                    { name: "Koramangala", rate: "₹9,800/sqft" },
                    { name: "Whitefield", rate: "₹7,500/sqft" },
                    { name: "Indiranagar", rate: "₹11,200/sqft" },
                    { name: "Electronic City", rate: "₹5,500/sqft" },
                    { name: "HSR Layout", rate: "₹8,200/sqft" }
                  ].map((loc) => (
                    <button
                      key={loc.name}
                      onClick={() => {
                        setSearchInput(loc.name);
                        handleSearch(loc.name);
                        setActiveTab('gis');
                      }}
                      className="p-3.5 rounded-2xl bg-slate-900/60 hover:bg-brand-500/10 border border-slate-800 hover:border-brand-500/30 text-left transition-all space-y-1 group"
                    >
                      <p className="text-xs font-bold text-slate-200 group-hover:text-brand-300">{loc.name}</p>
                      <p className="text-[10px] text-slate-500">Benchmark: {loc.rate}</p>
                    </button>
                  ))}
                </div>
              </div>
            </div>

            {/* Quick Portal Navigation Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* GIS Map Shortcut */}
              <button
                onClick={() => setActiveTab('gis')}
                className="glass-card p-6 rounded-3xl border border-slate-800 hover:border-brand-500/30 text-left transition-all space-y-3 relative overflow-hidden bg-gradient-to-br from-slate-900/40 to-emerald-950/5 group"
              >
                <div className="w-10 h-10 rounded-xl bg-emerald-500/10 text-emerald-400 flex items-center justify-center">
                  <Map className="w-5 h-5" />
                </div>
                <div>
                  <h4 className="text-sm font-bold text-white group-hover:text-emerald-400">Interactive GIS Map Canvas</h4>
                  <p className="text-xs text-slate-400 mt-1">Explore OpenStreetMap geocoding integration and local 1KM/5KM amenities indexes.</p>
                </div>
              </button>

              {/* AI Analytics Shortcut */}
              <button
                onClick={() => navigate(`/analytics/${allProperties[0]?.id || 1}`)}
                className="glass-card p-6 rounded-3xl border border-slate-800 hover:border-brand-500/30 text-left transition-all space-y-3 relative overflow-hidden bg-gradient-to-br from-slate-900/40 to-brand-950/5 group"
              >
                <div className="w-10 h-10 rounded-xl bg-brand-500/10 text-brand-400 flex items-center justify-center">
                  <Sparkles className="w-5 h-5" />
                </div>
                <div>
                  <h4 className="text-sm font-bold text-white group-hover:text-brand-400">AI Valuation Dashboard</h4>
                  <p className="text-xs text-slate-400 mt-1">Unlock machine learning predictions, SHAP explanatory maps, and description quality sentiments.</p>
                </div>
              </button>
            </div>

            {/* Recommended Properties & Recently Viewed */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
              {/* Recommended Listings (Verified) */}
              <div className="lg:col-span-2 space-y-4">
                <div className="flex items-center justify-between border-b border-slate-850 pb-2">
                  <h3 className="text-sm font-bold uppercase tracking-wider text-slate-200">Recommended Properties</h3>
                  <span className="text-[10px] text-brand-400 font-bold">Bangalore Top Pick listings</span>
                </div>

                {allProperties.filter(p => p.verification_status === 'Verified').length === 0 ? (
                  <div className="p-8 text-center text-slate-500 italic text-xs glass-card border border-slate-800 rounded-2xl">
                    No recommended verified listings found. Showing all listings.
                  </div>
                ) : (
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    {allProperties
                      .filter(p => p.verification_status === 'Verified')
                      .slice(0, 2)
                      .map(p => (
                        <PropertyCard key={p.id} property={p} />
                      ))}
                  </div>
                )}
              </div>

              {/* Stored Recently Viewed List */}
              <div className="space-y-4">
                <div className="flex items-center justify-between border-b border-slate-850 pb-2">
                  <h3 className="text-sm font-bold uppercase tracking-wider text-slate-200">Recently Viewed</h3>
                  <Clock className="w-4 h-4 text-slate-500" />
                </div>
                <div className="space-y-2.5">
                  {allProperties.slice(0, 3).map(p => (
                    <Link
                      key={p.id}
                      to={`/properties/${p.id}`}
                      className="block p-3 rounded-2xl bg-slate-900 border border-slate-800 hover:border-slate-700 transition-all"
                    >
                      <span className="text-[9px] uppercase font-bold text-slate-500 block">{p.property_type} in {p.locality}</span>
                      <span className="text-xs font-bold text-slate-200 block truncate mt-0.5 hover:text-brand-300">{p.title}</span>
                      <span className="text-xs text-brand-400 font-semibold block mt-1">₹{p.price.toLocaleString()}</span>
                    </Link>
                  ))}
                </div>
              </div>
            </div>

            {/* Profile Detail Summary & Recent Activity timeline */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8 border-t border-slate-850 pt-8">
              <div className="glass-card p-6 rounded-3xl border border-slate-800 space-y-4">
                <h4 className="text-xs font-extrabold uppercase tracking-wider text-white">Verification Activity Logs</h4>
                <div className="space-y-3.5 text-xs text-slate-400">
                  <div className="flex gap-3">
                    <Activity className="w-4 h-4 text-emerald-400 flex-shrink-0 mt-0.5" />
                    <div>
                      <p className="font-semibold text-slate-300">Database Connection Active</p>
                      <p className="text-[10px] text-slate-500">Real estate listings synchronized successfully.</p>
                    </div>
                  </div>
                  <div className="flex gap-3">
                    <Activity className="w-4 h-4 text-brand-400 flex-shrink-0 mt-0.5" />
                    <div>
                      <p className="font-semibold text-slate-300">Security Gate Status</p>
                      <p className="text-[10px] text-slate-500">JWT Token verification and session limits validated.</p>
                    </div>
                  </div>
                </div>
              </div>

              <div className="glass-card p-6 rounded-3xl border border-slate-800 space-y-4">
                <h4 className="text-xs font-extrabold uppercase tracking-wider text-white">Local System Summary</h4>
                <ul className="text-xs text-slate-400 space-y-2">
                  <li className="flex justify-between"><span>Coordinate precision:</span> <strong className="text-slate-300">WGS 84 Spherical</strong></li>
                  <li className="flex justify-between"><span>XGBoost ML Pipeline:</span> <strong className="text-slate-300">Active (5 inputs mapped)</strong></li>
                  <li className="flex justify-between"><span>ResNet-18 Layers:</span> <strong className="text-slate-300">Pretrained Feature Scan</strong></li>
                </ul>
              </div>
            </div>
          </div>
        ) : (
          <div className="space-y-8 animate-fadeIn">
            {/* Locality Autocomplete Search Form */}
            <div className="space-y-4">
              <form
                onSubmit={(e) => {
                  e.preventDefault();
                  handleSearch();
                }}
                className="flex flex-col sm:flex-row items-center gap-3"
              >
                <div className="w-full">
                  <BangaloreLocationAutocomplete
                    value={searchInput}
                    onChange={(val) => setSearchInput(val)}
                    onSelect={(val) => {
                      setSearchInput(val);
                      handleSearch(val);
                    }}
                    placeholder="Search Koramangala, Whitefield, Electronic City, HSR Layout, Chandapura, JP Nagar..."
                  />
                </div>

                <button
                  type="submit"
                  disabled={loadingSearch}
                  className="w-full sm:w-auto px-8 py-3.5 rounded-2xl bg-gradient-to-r from-brand-600 to-accent-600 hover:from-brand-500 hover:to-accent-500 text-white font-semibold text-sm shadow-lg shadow-brand-500/25 transition-all flex items-center justify-center gap-2 disabled:opacity-50 flex-shrink-0"
                >
                  {loadingSearch ? (
                    <>
                      <Loader2 className="w-4 h-4 animate-spin" />
                      <span>Geocoding...</span>
                    </>
                  ) : (
                    <>
                      <span>Search GIS</span>
                    </>
                  )}
                </button>
              </form>

              {/* Preset Locality Pills */}
              <div className="flex items-center gap-2 overflow-x-auto pb-1 scrollbar-none">
                <span className="text-[11px] font-bold text-slate-500 uppercase tracking-wider whitespace-nowrap">Key Hubs:</span>
                {topPresets.map((preset) => (
                  <button
                    key={preset}
                    type="button"
                    onClick={() => {
                      setSearchInput(preset);
                      handleSearch(preset);
                    }}
                    className="px-3 py-1.5 rounded-xl text-xs font-medium bg-slate-900/80 hover:bg-brand-500/20 text-slate-300 hover:text-brand-300 border border-slate-800 hover:border-brand-500/40 transition-all whitespace-nowrap"
                  >
                    {preset}
                  </button>
                ))}
              </div>

              {errorMsg && (
                <div className="p-3 rounded-xl bg-red-500/10 border border-red-500/20 text-red-400 text-xs font-medium">
                  {errorMsg}
                </div>
              )}
            </div>

            {/* Active Search Result Report Card */}
            {activeSearchResult && (
              <div className="glass-card p-6 rounded-2xl border border-brand-500/30 bg-gradient-to-r from-slate-900/90 to-brand-950/40 flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
                <div className="space-y-1.5">
                  <div className="flex items-center gap-2">
                    <MapPin className="w-4 h-4 text-brand-400" />
                    <span className="text-xs uppercase font-bold text-brand-400 tracking-wider">Locality GIS Report</span>
                  </div>
                  <h2 className="text-xl font-bold text-white">{activeSearchResult.formatted_address}</h2>
                  <div className="flex flex-wrap items-center gap-4 text-xs text-slate-400 pt-1">
                    <span>City: <strong className="text-slate-200">{activeSearchResult.city}</strong></span>
                    <span>State: <strong className="text-slate-200">{activeSearchResult.state}</strong></span>
                    <span>Coordinates: <strong className="text-slate-200 font-mono">{activeSearchResult.latitude.toFixed(4)}, {activeSearchResult.longitude.toFixed(4)}</strong></span>
                  </div>
                </div>

                <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-4 w-full md:w-auto">
                  {activeSearchResult.estimated_price_sqft && (
                    <div className="bg-slate-900/90 px-5 py-3 rounded-2xl border border-slate-800 space-y-0.5">
                      <div className="flex items-center gap-1 text-[11px] text-slate-400">
                        <IndianRupee className="w-3 h-3 text-emerald-400" />
                        <span>Est. Benchmark</span>
                      </div>
                      <p className="text-lg font-extrabold text-emerald-400">{activeSearchResult.price_range}</p>
                      <p className="text-[10px] text-slate-500">Avg: ₹{activeSearchResult.estimated_price_sqft.toLocaleString()} / sq.ft</p>
                    </div>
                  )}

                  <button
                    onClick={handleSaveLocation}
                    disabled={isSaved}
                    className={`px-4 py-3 rounded-2xl text-xs font-semibold border transition-all flex items-center justify-center gap-2 ${
                      isSaved
                        ? 'bg-slate-800 text-slate-400 border-slate-700'
                        : 'bg-brand-500/20 text-brand-300 border-brand-500/40 hover:bg-brand-500/30'
                    }`}
                  >
                    {isSaved ? <Check className="w-4 h-4 text-emerald-400" /> : <Bookmark className="w-4 h-4" />}
                    <span>{isSaved ? 'Saved' : 'Save Location'}</span>
                  </button>
                </div>
              </div>
            )}

            {/* Locality Market Statistics Card */}
            {localityStats && <LocalityStatsCard stats={localityStats} />}

            {/* Map & Recent Searches */}
            <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
              <div className="lg:col-span-3 space-y-3">
                <div className="flex items-center justify-between">
                  <h3 className="text-sm font-bold uppercase tracking-wider text-slate-300 flex items-center gap-2">
                    <Compass className="w-4 h-4 text-brand-500" />
                    Interactive OpenStreetMap & Geoapify Canvas
                  </h3>
                  <span className="text-[11px] text-slate-500 font-mono">Live GIS Layer</span>
                </div>
                <MapView
                  searchResult={activeSearchResult}
                  currentLocation={currentLocation}
                  nearbyPlaces={nearbyPlaces}
                />
              </div>

              <div className="glass-card p-5 rounded-2xl border border-slate-800 space-y-4 flex flex-col justify-between">
                <div className="space-y-4">
                  <div className="flex items-center justify-between border-b border-slate-800 pb-3">
                    <h4 className="text-xs font-bold uppercase tracking-wider text-slate-200 flex items-center gap-2">
                      <History className="w-4 h-4 text-brand-400" />
                      Recent Searches
                    </h4>
                    <span className="text-[10px] bg-slate-800 text-slate-400 px-2 py-0.5 rounded font-mono">
                      {searchHistory.length}
                    </span>
                  </div>

                  {searchHistory.length === 0 ? (
                    <p className="text-xs text-slate-500 py-6 text-center">No search history recorded yet.</p>
                  ) : (
                    <div className="space-y-2 max-h-[380px] overflow-y-auto pr-1">
                      {searchHistory.map((item) => (
                        <button
                          key={item.id}
                          onClick={() => {
                            setSearchInput(item.query);
                            handleSearch(item.query);
                          }}
                          className="w-full text-left p-3 rounded-xl bg-slate-900/60 hover:bg-slate-800/80 border border-slate-800/60 hover:border-brand-500/30 transition-all group"
                        >
                          <p className="text-xs font-bold text-slate-200 group-hover:text-brand-300 line-clamp-1">{item.query}</p>
                          <p className="text-[10px] text-slate-500 line-clamp-1 mt-0.5">{item.formatted_address}</p>
                        </button>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            </div>

            {/* Nearby Places Component */}
            <NearbyPlacesList 
              places={nearbyPlaces} 
              loading={loadingPlaces} 
              radius={nearbyRadius}
              onRadiusChange={handleRadiusChange}
            />

            {/* Locality Properties Section */}
            <div className="space-y-4 pt-4 border-t border-slate-800/80">
              <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div>
                  <h3 className="text-xl font-bold font-outfit text-white flex items-center gap-2">
                    <Building2 className="w-5 h-5 text-brand-500" />
                    {(activeSearchResult?.query || searchInput || 'Locality').split(',')[0].trim()} Properties
                  </h3>
                  <p className="text-xs text-slate-400">
                    Found <strong className="text-emerald-450">{localityProperties.length}</strong> properties in this locality • {
                      (() => {
                        const counts = {};
                        localityProperties.forEach(p => {
                          if (p.bhk) counts[`${p.bhk} BHK`] = (counts[`${p.bhk} BHK`] || 0) + 1;
                        });
                        return Object.entries(counts)
                          .sort((a, b) => a[0].localeCompare(b[0]))
                          .map(([bhkLabel, count]) => `${count} x ${bhkLabel}`)
                          .join(", ") || "No distribution data";
                      })()
                    }
                  </p>
                </div>
              </div>

              {/* Filters Bar */}
              <div className="glass-card p-4 rounded-2xl border border-slate-800 space-y-3 bg-slate-900/40">
                <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-6 gap-3 text-xs">
                  {/* Listing Type */}
                  <div className="space-y-1">
                    <label className="text-[10px] uppercase font-bold text-slate-400">Listing Type</label>
                    <select 
                      value={filterListingType}
                      onChange={(e) => setFilterListingType(e.target.value)}
                      className="w-full bg-slate-950 border border-slate-800 px-2.5 py-1.5 rounded-xl text-slate-200 text-xs focus:outline-none focus:border-brand-500"
                    >
                      <option value="All">All Types</option>
                      <option value="Buy">Buy</option>
                      <option value="Rent">Rent</option>
                    </select>
                  </div>

                  {/* Property Type */}
                  <div className="space-y-1">
                    <label className="text-[10px] uppercase font-bold text-slate-400">Property Type</label>
                    <select
                      value={filterPropType}
                      onChange={(e) => setFilterPropType(e.target.value)}
                      className="w-full bg-slate-950 border border-slate-800 px-2.5 py-1.5 rounded-xl text-slate-200 text-xs focus:outline-none focus:border-brand-500"
                    >
                      <option value="All">All</option>
                      <option value="Apartment">Apartment</option>
                      <option value="Villa">Villa</option>
                      <option value="Independent House">Independent House</option>
                      <option value="Plot">Plot</option>
                    </select>
                  </div>

                  {/* BHK */}
                  <div className="space-y-1">
                    <label className="text-[10px] uppercase font-bold text-slate-400">BHK</label>
                    <select
                      value={filterBhk}
                      onChange={(e) => setFilterBhk(e.target.value)}
                      className="w-full bg-slate-950 border border-slate-800 px-2.5 py-1.5 rounded-xl text-slate-200 text-xs focus:outline-none focus:border-brand-500"
                    >
                      <option value="All">All</option>
                      <option value="1">1 BHK</option>
                      <option value="2">2 BHK</option>
                      <option value="3">3 BHK</option>
                      <option value="4">4 BHK</option>
                    </select>
                  </div>

                  {/* Furnishing */}
                  <div className="space-y-1">
                    <label className="text-[10px] uppercase font-bold text-slate-400">Furnishing</label>
                    <select
                      value={filterFurnishing}
                      onChange={(e) => setFilterFurnishing(e.target.value)}
                      className="w-full bg-slate-950 border border-slate-800 px-2.5 py-1.5 rounded-xl text-slate-200 text-xs focus:outline-none focus:border-brand-500"
                    >
                      <option value="All">All</option>
                      <option value="Fully Furnished">Fully Furnished</option>
                      <option value="Semi-Furnished">Semi-Furnished</option>
                      <option value="Unfurnished">Unfurnished</option>
                    </select>
                  </div>

                  {/* Min Price */}
                  <div className="space-y-1">
                    <label className="text-[10px] uppercase font-bold text-slate-400">Min Price (INR)</label>
                    <input
                      type="number"
                      placeholder="e.g. 5000000"
                      value={filterMinPrice}
                      onChange={(e) => setFilterMinPrice(e.target.value)}
                      className="w-full bg-slate-950 border border-slate-800 px-2.5 py-1.5 rounded-xl text-slate-200 text-xs focus:outline-none focus:border-brand-500"
                    />
                  </div>

                  {/* Max Price */}
                  <div className="space-y-1">
                    <label className="text-[10px] uppercase font-bold text-slate-400">Max Price (INR)</label>
                    <input
                      type="number"
                      placeholder="e.g. 20000000"
                      value={filterMaxPrice}
                      onChange={(e) => setFilterMaxPrice(e.target.value)}
                      className="w-full bg-slate-950 border border-slate-800 px-2.5 py-1.5 rounded-xl text-slate-200 text-xs focus:outline-none focus:border-brand-500"
                    />
                  </div>
                </div>

                {/* Sub Filters Row */}
                <div className="flex flex-wrap items-center gap-4 text-xs pt-1">
                  <div className="flex items-center gap-2">
                    <span className="text-[10px] uppercase font-bold text-slate-400">Area (Sqft):</span>
                    <input
                      type="number"
                      placeholder="Min"
                      value={filterMinArea}
                      onChange={(e) => setFilterMinArea(e.target.value)}
                      className="w-20 bg-slate-950 border border-slate-800 px-2 py-1 rounded-lg text-slate-200 text-xs focus:outline-none focus:border-brand-500"
                    />
                    <span className="text-slate-500">-</span>
                    <input
                      type="number"
                      placeholder="Max"
                      value={filterMaxArea}
                      onChange={(e) => setFilterMaxArea(e.target.value)}
                      className="w-20 bg-slate-950 border border-slate-800 px-2 py-1 rounded-lg text-slate-200 text-xs focus:outline-none focus:border-brand-500"
                    />
                  </div>

                  <div className="flex items-center gap-2">
                    <span className="text-[10px] uppercase font-bold text-slate-400">Parking:</span>
                    <select
                      value={filterParking}
                      onChange={(e) => setFilterParking(e.target.value)}
                      className="bg-slate-950 border border-slate-800 px-2 py-1 rounded-lg text-slate-200 text-xs focus:outline-none focus:border-brand-500"
                    >
                      <option value="All">All</option>
                      <option value="Covered">Covered</option>
                      <option value="Open">Open</option>
                      <option value="None">None</option>
                    </select>
                  </div>

                  {/* Clear button */}
                  <button
                    type="button"
                    onClick={() => {
                      setFilterListingType('All');
                      setFilterPropType('All');
                      setFilterBhk('All');
                      setFilterMinPrice('');
                      setFilterMaxPrice('');
                      setFilterMinArea('');
                      setFilterMaxArea('');
                      setFilterFurnishing('All');
                      setFilterParking('All');
                    }}
                    className="ml-auto text-slate-400 hover:text-white transition-colors underline font-medium"
                  >
                    Reset Filters
                  </button>
                </div>
              </div>

              {loadingProps ? (
                <div className="p-12 text-center text-slate-400 flex flex-col items-center justify-center gap-2">
                  <Loader2 className="w-6 h-6 animate-spin text-brand-500" />
                  <p className="text-xs">Loading locality properties...</p>
                </div>
              ) : localityProperties.length === 0 ? (
                <div className="p-12 glass-card rounded-3xl text-center text-slate-400 space-y-2 border border-slate-800">
                  <Building2 className="w-8 h-8 text-slate-600 mx-auto" />
                  <p className="text-sm font-bold text-white">
                    No properties currently available for {activeSearchResult?.query || searchInput}.
                  </p>
                  <p className="text-xs text-slate-400">
                    Try another Bangalore locality or adjust your filters.
                  </p>
                </div>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                  {localityProperties.map((prop) => (
                    <PropertyCard key={prop.id} property={prop} />
                  ))}
                </div>
              )}
            </div>
          </div>
        )}
      </main>


      {/* Post Property Modal */}
      {showPostModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/85 backdrop-blur-md overflow-y-auto">
          <div className="glass-card w-full max-w-4xl p-6 md:p-8 rounded-3xl border border-slate-800 space-y-6 relative my-8 shadow-2xl max-h-[90vh] overflow-y-auto">
            <button
              onClick={() => {
                setShowPostModal(false);
                setPostSuccess(false);
              }}
              className="absolute top-6 right-6 text-slate-400 hover:text-white transition-colors"
            >
              <X className="w-6 h-6" />
            </button>

            <div className="space-y-1">
              <h3 className="text-2xl font-bold text-white font-outfit flex items-center gap-2">
                <Sparkles className="w-6 h-6 text-brand-400" />
                Post Direct Property Listing
              </h3>
              <p className="text-xs text-slate-400">Direct owner-submitted listings are subject to verification before public search exposure.</p>
            </div>

            {postSuccess ? (
              <div className="p-8 rounded-3xl bg-emerald-500/10 border border-emerald-500/20 text-center space-y-4 max-w-lg mx-auto py-12">
                <CheckCircle2 className="w-16 h-16 text-emerald-400 mx-auto animate-pulse" />
                <h4 className="text-lg font-bold text-white font-outfit">Submission Successful!</h4>
                <p className="text-xs text-slate-300 leading-relaxed font-semibold">
                  Your property has been submitted and is <strong className="text-emerald-400 animate-pulse">Pending Verification</strong>. Our administrators will review the details shortly.
                </p>
                <button
                  onClick={() => {
                    setShowPostModal(false);
                    setPostSuccess(false);
                  }}
                  className="px-6 py-2 rounded-xl bg-brand-600 hover:bg-brand-500 text-white font-semibold text-xs transition-all"
                >
                  Close Window
                </button>
              </div>
            ) : (
              <form onSubmit={handlePostPropertySubmit} className="space-y-6 text-slate-200">
                {postError && (
                  <div className="p-4 rounded-xl bg-red-500/10 border border-red-500/20 text-red-400 text-xs">
                    {postError}
                  </div>
                )}

                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  {/* Basic Info Column */}
                  <div className="space-y-4">
                    <h4 className="text-[10px] uppercase font-bold text-slate-400 tracking-wider border-b border-slate-800 pb-1.5">1. Basic Specifications</h4>
                    
                    <div className="space-y-1">
                      <label className="text-[10px] uppercase text-slate-500 font-bold">Listing Type</label>
                      <select required value={formListingType} onChange={e => setFormListingType(e.target.value)} className="w-full bg-slate-950 border border-slate-800 px-3 py-2 rounded-xl text-slate-200 text-xs focus:outline-none focus:border-brand-500">
                        <option value="Buy">For Sale (Buy)</option>
                        <option value="Rent">For Rent (Rent)</option>
                      </select>
                    </div>

                    <div className="space-y-1">
                      <label className="text-[10px] uppercase text-slate-500 font-bold">Property Type</label>
                      <select required value={formPropType} onChange={e => setFormPropType(e.target.value)} className="w-full bg-slate-950 border border-slate-800 px-3 py-2 rounded-xl text-slate-200 text-xs focus:outline-none focus:border-brand-500">
                        <option value="Apartment">Apartment</option>
                        <option value="Independent House">Independent House</option>
                        <option value="Villa">Villa</option>
                        <option value="Plot">Plot</option>
                      </select>
                    </div>

                    <div className="grid grid-cols-2 gap-4">
                      <div className="space-y-1">
                        <label className="text-[10px] uppercase text-slate-500 font-bold">BHK config</label>
                        <input required type="number" min={0} value={formBhk} onChange={e => setFormBhk(e.target.value)} className="w-full bg-slate-950 border border-slate-800 px-3 py-2 rounded-xl text-slate-200 text-xs focus:outline-none" />
                      </div>
                      <div className="space-y-1">
                        <label className="text-[10px] uppercase text-slate-500 font-bold">Area (Sqft)</label>
                        <input required type="number" min={1} value={formArea} onChange={e => setFormArea(e.target.value)} className="w-full bg-slate-950 border border-slate-800 px-3 py-2 rounded-xl text-slate-200 text-xs focus:outline-none" />
                      </div>
                    </div>

                    <div className="space-y-1">
                      <label className="text-[10px] uppercase text-slate-500 font-bold">Price (INR)</label>
                      <input required type="number" min={1} value={formPrice} onChange={e => setFormPrice(e.target.value)} className="w-full bg-slate-950 border border-slate-800 px-3 py-2 rounded-xl text-slate-200 text-xs focus:outline-none focus:border-brand-500 font-mono" />
                    </div>
                  </div>

                  {/* Location Column */}
                  <div className="space-y-4">
                    <h4 className="text-[10px] uppercase font-bold text-slate-400 tracking-wider border-b border-slate-800 pb-1.5">2. Location Details</h4>

                    <div className="space-y-1">
                      <label className="text-[10px] uppercase text-slate-500 font-bold">Bengaluru Locality</label>
                      <input required type="text" placeholder="e.g. Koramangala" value={formLocality} onChange={e => setFormLocality(e.target.value)} className="w-full bg-slate-950 border border-slate-800 px-3 py-2 rounded-xl text-slate-200 text-xs focus:outline-none focus:border-brand-500" />
                    </div>

                    <div className="space-y-1">
                      <label className="text-[10px] uppercase text-slate-500 font-bold">Complete Address</label>
                      <textarea required rows={3} placeholder="Complete physical address of the listing" value={formAddress} onChange={e => setFormAddress(e.target.value)} className="w-full bg-slate-950 border border-slate-800 px-3 py-2 rounded-xl text-slate-200 text-xs focus:outline-none focus:border-brand-500" />
                    </div>

                    <div className="space-y-1">
                      <label className="text-[10px] uppercase text-slate-500 font-bold">Property Photos Upload</label>
                      <input 
                        type="file" 
                        multiple 
                        accept="image/*" 
                        onChange={e => setFormUploadFiles(Array.from(e.target.files))} 
                        className="w-full bg-slate-950 border border-slate-800 px-3 py-2 rounded-xl text-slate-400 text-xs focus:outline-none focus:border-brand-500" 
                      />
                      <span className="text-[9px] text-slate-500 mt-1 block">
                        {formUploadFiles.length} photos selected
                      </span>
                    </div>

                  </div>

                  {/* Specs & Owner Column */}
                  <div className="space-y-4">
                    <h4 className="text-[10px] uppercase font-bold text-slate-400 tracking-wider border-b border-slate-800 pb-1.5">3. Additional Metadata</h4>

                    <div className="grid grid-cols-2 gap-4">
                      <div className="space-y-1">
                        <label className="text-[10px] uppercase text-slate-500 font-bold">Bathrooms</label>
                        <input required type="number" min={1} value={formBaths} onChange={e => setFormBaths(e.target.value)} className="w-full bg-slate-950 border border-slate-800 px-3 py-2 rounded-xl text-slate-200 text-xs focus:outline-none" />
                      </div>
                      <div className="space-y-1">
                        <label className="text-[10px] uppercase text-slate-500 font-bold">Balconies</label>
                        <input required type="number" min={0} value={formBalconies} onChange={e => setFormBalconies(e.target.value)} className="w-full bg-slate-950 border border-slate-800 px-3 py-2 rounded-xl text-slate-200 text-xs focus:outline-none" />
                      </div>
                    </div>

                    <div className="grid grid-cols-3 gap-2">
                      <div className="space-y-1">
                        <label className="text-[9px] uppercase text-slate-500 font-bold">Floor</label>
                        <input required type="number" value={formFloor} onChange={e => setFormFloor(e.target.value)} className="w-full bg-slate-950 border border-slate-800 px-2 py-2 rounded-xl text-slate-200 text-xs focus:outline-none" />
                      </div>
                      <div className="space-y-1">
                        <label className="text-[9px] uppercase text-slate-500 font-bold">Total Floors</label>
                        <input required type="number" value={formTotalFloors} onChange={e => setFormTotalFloors(e.target.value)} className="w-full bg-slate-950 border border-slate-800 px-2 py-2 rounded-xl text-slate-200 text-xs focus:outline-none" />
                      </div>
                      <div className="space-y-1">
                        <label className="text-[9px] uppercase text-slate-500 font-bold">Age</label>
                        <select required value={formAge} onChange={e => setFormAge(e.target.value)} className="w-full bg-slate-950 border border-slate-800 px-1 py-2 rounded-xl text-slate-200 text-[10px] focus:outline-none">
                          <option value="New">New</option>
                          <option value="1-5 yrs">1-5 yrs</option>
                          <option value="5-10 yrs">5-10 yrs</option>
                          <option value="10+ yrs">10+ yrs</option>
                        </select>
                      </div>
                    </div>

                    <div className="grid grid-cols-2 gap-4">
                      <div className="space-y-1">
                        <label className="text-[10px] uppercase text-slate-500 font-bold">Parking</label>
                        <select required value={formParking} onChange={e => setFormParking(e.target.value)} className="w-full bg-slate-950 border border-slate-800 px-2 py-2 rounded-xl text-slate-200 text-xs focus:outline-none">
                          <option value="Covered">Covered</option>
                          <option value="Open">Open</option>
                          <option value="None">None</option>
                        </select>
                      </div>
                      <div className="space-y-1">
                        <label className="text-[10px] uppercase text-slate-500 font-bold">Furnishing</label>
                        <select required value={formFurnishing} onChange={e => setFormFurnishing(e.target.value)} className="w-full bg-slate-950 border border-slate-800 px-2 py-2 rounded-xl text-slate-200 text-xs focus:outline-none">
                          <option value="Fully Furnished">Fully</option>
                          <option value="Semi-Furnished">Semi</option>
                          <option value="Unfurnished">Unfurnished</option>
                        </select>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Lower fields (Description + Contact info) */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6 pt-2 border-t border-slate-800/80">
                  <div className="space-y-3">
                    <div className="space-y-1">
                      <label className="text-[10px] uppercase text-slate-500 font-bold">Property Description</label>
                      <textarea required rows={4} placeholder="Describe main advantages, amenities, and layout features..." value={formDescription} onChange={e => setFormDescription(e.target.value)} className="w-full bg-slate-950 border border-slate-800 px-3 py-2 rounded-xl text-slate-200 text-xs focus:outline-none focus:border-brand-500" />
                    </div>
                  </div>

                  <div className="space-y-3">
                    <h4 className="text-[10px] uppercase font-bold text-slate-400 tracking-wider">4. Contact Information</h4>
                    <div className="grid grid-cols-2 gap-4">
                      <div className="space-y-1">
                        <label className="text-[10px] uppercase text-slate-500 font-bold">Owner Name</label>
                        <input required type="text" placeholder="e.g. Suresh Kumar" value={formOwnerName} onChange={e => setFormOwnerName(e.target.value)} className="w-full bg-slate-950 border border-slate-800 px-3 py-2 rounded-xl text-slate-200 text-xs focus:outline-none" />
                      </div>
                      <div className="space-y-1">
                        <label className="text-[10px] uppercase text-slate-500 font-bold">Phone Number</label>
                        <input required type="tel" placeholder="e.g. +91 98860 12345" value={formOwnerPhone} onChange={e => setFormOwnerPhone(e.target.value)} className="w-full bg-slate-950 border border-slate-800 px-3 py-2 rounded-xl text-slate-200 text-xs focus:outline-none font-mono" />
                      </div>
                    </div>

                    <div className="pt-2">
                      <button
                        type="submit"
                        disabled={postLoading}
                        className="w-full py-3.5 rounded-xl bg-brand-600 hover:bg-brand-500 text-white font-bold text-xs shadow-lg shadow-brand-500/20 disabled:opacity-50 flex items-center justify-center gap-2"
                      >
                        {postLoading ? (
                          <>
                            <Loader2 className="w-4 h-4 animate-spin" />
                            Submitting Listing for Verification...
                          </>
                        ) : (
                          "Submit Direct Listing for Verification"
                        )}
                      </button>
                    </div>
                  </div>
                </div>

              </form>
            )}
          </div>
        </div>
      )}

      <Footer />
    </div>
  );
};
