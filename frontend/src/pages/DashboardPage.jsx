import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
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
  MapPin, Loader2, IndianRupee, History, Compass, Check, Building2
} from 'lucide-react';

export const DashboardPage = () => {
  const { user } = useAuth();
  const [searchParams] = useSearchParams();

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

  useEffect(() => {
    fetchHistoryAndSaved();
    
    const queryParam = searchParams.get('search');
    if (queryParam) {
      setSearchInput(queryParam);
      handleSearch(queryParam);
    } else {
      setSearchInput("Koramangala");
      handleSearch("Koramangala");
    }
  }, []);

  const fetchHistoryAndSaved = async () => {
    try {
      const [histData, savedData] = await Promise.all([
        locationService.getSearchHistory(8),
        locationService.getSavedLocations()
      ]);
      setSearchHistory(histData || []);
      setSavedLocations(savedData || []);
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

    try {
      // 1. Geocode via Geoapify
      const res = await locationService.searchLocation(query);
      if (!res) {
        throw new Error(`Location "${query}" could not be geocoded by Geoapify API.`);
      }

      setActiveSearchResult(res);

      const alreadySaved = savedLocations.some(
        s => Math.abs(s.latitude - res.latitude) < 0.001 && Math.abs(s.longitude - res.longitude) < 0.001
      );
      setIsSaved(alreadySaved);

      // 2. Fetch nearby places using coordinates returned by Geocoding API
      fetchNearby(res.latitude, res.longitude);

      // 3. Fetch Locality Statistics & Locality Properties
      const cleanLocalityName = query.split(',')[0].trim();
      fetchLocalityStatsAndProps(cleanLocalityName, res.latitude, res.longitude);
      
      fetchHistoryAndSaved();
    } catch (err) {
      console.error(err);
      setErrorMsg(err.response?.data?.detail || err.message || `Unable to find locality "${query}". Please select a valid Bangalore location.`);
    } finally {
      setLoadingSearch(false);
    }
  };

  const fetchNearby = async (lat, lon) => {
    setLoadingPlaces(true);
    try {
      const places = await locationService.getNearbyPlaces(lat, lon, 5000);
      setNearbyPlaces(places || []);
    } catch (err) {
      console.error("Error fetching nearby places:", err);
      setNearbyPlaces([]);
    } finally {
      setLoadingPlaces(false);
    }
  };

  const fetchLocalityStatsAndProps = async (localityQuery, lat, lon) => {
    setLoadingProps(true);
    const cleanLoc = localityQuery.split(',')[0].trim();
    try {
      const [statsData, propsData] = await Promise.all([
        locationService.getLocalityStats(cleanLoc, lat, lon),
        propertyService.getProperties({ query: cleanLoc, limit: 20 })
      ]);

      setLocalityStats(statsData);
      setLocalityProperties(propsData?.items || []);
    } catch (err) {
      console.error("Error fetching locality stats & props:", err);
    } finally {
      setLoadingProps(false);
    }
  };

  const handleCurrentLocationClick = () => {
    if (!navigator.geolocation) {
      setErrorMsg("Geolocation is not supported by your browser.");
      return;
    }

    setLoadingGeo(true);
    setErrorMsg('');

    navigator.geolocation.getCurrentPosition(
      async (position) => {
        const { latitude, longitude } = position.coords;
        try {
          const res = await locationService.getCurrentLocation(latitude, longitude);
          setCurrentLocation(res);
          setActiveSearchResult(res);
          fetchNearby(latitude, longitude);
          fetchLocalityStatsAndProps("Bengaluru", latitude, longitude);
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
        {/* Welcome Card */}
        <div className="glass-card p-6 md:p-8 rounded-3xl border border-slate-800 flex flex-col md:flex-row items-start md:items-center justify-between gap-6 relative overflow-hidden">
          <div className="absolute top-0 right-0 w-80 h-80 bg-brand-500/10 rounded-full blur-[90px] pointer-events-none"></div>

          <div className="space-y-2 z-10">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-brand-500/10 border border-brand-500/20 text-brand-300 text-xs font-semibold">
              <Sparkles className="w-3.5 h-3.5 text-brand-400" />
              <span>Bangalore Real Estate AI Engine</span>
            </div>
            <h1 className="text-2xl sm:text-3xl font-bold font-outfit text-white">
              Welcome back, <span className="gradient-text">{user?.full_name || 'Valued User'}</span>
            </h1>
            <p className="text-xs sm:text-sm text-slate-400">
              Query 100+ Bangalore localities, view real GIS nearby amenities, and analyze locality property statistics.
            </p>
          </div>

          <button
            onClick={handleCurrentLocationClick}
            disabled={loadingGeo}
            className="z-10 px-5 py-3 rounded-2xl bg-emerald-500/10 hover:bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 font-semibold text-xs transition-all flex items-center gap-2 shadow-lg shadow-emerald-500/10"
          >
            {loadingGeo ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                <span>Locating GPS...</span>
              </>
            ) : (
              <>
                <Navigation className="w-4 h-4 fill-current" />
                <span>Use Current Location</span>
              </>
            )}
          </button>
        </div>

        {/* Autocomplete Search & Presets */}
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
        <NearbyPlacesList places={nearbyPlaces} loading={loadingPlaces} />

        {/* Locality Properties Section */}
        <div className="space-y-4 pt-4 border-t border-slate-800/80">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-xl font-bold font-outfit text-white flex items-center gap-2">
                <Building2 className="w-5 h-5 text-brand-500" />
                Property Listings in {activeSearchResult?.query || searchInput || 'Locality'}
              </h3>
              <p className="text-xs text-slate-400">Available residential apartments, villas, houses, and plots in this area</p>
            </div>
            <span className="text-xs font-semibold px-3 py-1 rounded-full bg-brand-500/10 text-brand-300 border border-brand-500/20">
              {localityProperties.length} Properties
            </span>
          </div>

          {loadingProps ? (
            <div className="p-12 text-center text-slate-400 flex flex-col items-center justify-center gap-2">
              <Loader2 className="w-6 h-6 animate-spin text-brand-500" />
              <p className="text-xs">Loading locality properties...</p>
            </div>
          ) : localityProperties.length === 0 ? (
            <div className="p-12 glass-card rounded-3xl text-center text-slate-400 space-y-2 border border-slate-800">
              <Building2 className="w-8 h-8 text-slate-600 mx-auto" />
              <p className="text-sm font-semibold text-white">No Properties Found in {searchInput}</p>
              <p className="text-xs text-slate-500">Explore GIS locality stats or search another Bangalore locality.</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {localityProperties.map((prop) => (
                <PropertyCard key={prop.id} property={prop} />
              ))}
            </div>
          )}
        </div>
      </main>

      <Footer />
    </div>
  );
};
