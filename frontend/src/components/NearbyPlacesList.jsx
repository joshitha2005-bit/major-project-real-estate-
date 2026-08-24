import React, { useState } from 'react';
import { 
  GraduationCap, Hospital, Train, Utensils, 
  ShoppingBag, Landmark, Trees, Bus, MapPin, Filter, AlertTriangle 
} from 'lucide-react';

const CATEGORY_MAP = {
  "All":            { icon: Filter,         color: "text-slate-300",  bg: "bg-slate-800" },
  "Schools":        { icon: GraduationCap,  color: "text-blue-400",   bg: "bg-blue-500/10 border-blue-500/20" },
  "Colleges":       { icon: GraduationCap,  color: "text-indigo-400", bg: "bg-indigo-500/10 border-indigo-500/20" },
  "Hospitals":      { icon: Hospital,       color: "text-red-400",    bg: "bg-red-500/10 border-red-500/20" },
  "Metro Stations": { icon: Train,          color: "text-amber-400",  bg: "bg-amber-500/10 border-amber-500/20" },
  "Bus Stops":      { icon: Bus,            color: "text-yellow-400", bg: "bg-yellow-500/10 border-yellow-500/20" },
  "Restaurants":    { icon: Utensils,       color: "text-orange-400", bg: "bg-orange-500/10 border-orange-500/20" },
  "Shopping Malls": { icon: ShoppingBag,    color: "text-purple-400", bg: "bg-purple-500/10 border-purple-500/20" },
  "Banks":          { icon: Landmark,       color: "text-emerald-400",bg: "bg-emerald-500/10 border-emerald-500/20" },
};

const CATEGORIES_LIST = [
  "All", "Schools", "Hospitals", "Metro Stations", "Restaurants",
  "Shopping Malls", "Banks", "Colleges", "Bus Stops"
];

const GENERIC_NAMES = new Set([
  'point of interest', 'unnamed', 'unnamed road', 'unknown',
  'building', 'structure', 'place', 'area', 'zone', 'road',
]);

function isGenericName(name) {
  const lower = (name || '').toLowerCase().trim();
  if (lower.length < 3) return true;
  if (GENERIC_NAMES.has(lower)) return true;
  if (/^[0-9]+$/.test(lower)) return true;
  return false;
}

export const NearbyPlacesList = ({
  places = [],
  loading = false,
  radius = 5000,
  onRadiusChange = null,
  coordinateStatus = "EXACT",
  apiError = false,
}) => {
  const [selectedCategory, setSelectedCategory] = useState("All");

  const cleanPlaces = places.filter(p => !isGenericName(p.name));
  const radiusCapped = cleanPlaces.filter(p => p.distance_meters <= radius);
  const filteredPlaces = selectedCategory === "All"
    ? radiusCapped
    : radiusCapped.filter(p => p.category === selectedCategory);

  const sortedPlaces = [...filteredPlaces].sort(
    (a, b) => a.distance_meters - b.distance_meters
  );

  const categoryCounts = {};
  radiusCapped.forEach(p => {
    categoryCounts[p.category] = (categoryCounts[p.category] || 0) + 1;
  });

  return (
    <div className="glass-card p-6 rounded-2xl border border-slate-800 space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-800 pb-4">
        <div>
          <h3 className="text-lg font-bold text-white font-outfit flex items-center gap-2">
            <MapPin className="w-5 h-5 text-brand-500" />
            Nearby Amenities &amp; GIS Places
          </h3>
          <p className="text-xs text-slate-400 mt-1">
            Real-time nearby infrastructure queried via Geoapify GIS engine
          </p>
        </div>

        <div className="flex items-center gap-3 flex-shrink-0">
          {onRadiusChange && (
            <div className="flex items-center gap-1 bg-slate-900 border border-slate-800 rounded-xl p-1">
              {[
                { label: '1 KM',  value: 1000 },
                { label: '5 KM',  value: 5000 },
              ].map(({ label, value }) => (
                <button
                  key={value}
                  onClick={() => onRadiusChange(value)}
                  className={`px-3 py-1 text-xs font-semibold rounded-lg transition-all ${
                    radius === value
                      ? 'bg-brand-500 text-white shadow shadow-brand-500/30'
                      : 'text-slate-400 hover:text-white'
                  }`}
                >
                  {label}
                </button>
              ))}
            </div>
          )}

          <div className="text-xs text-slate-400 bg-slate-900 px-3 py-1.5 rounded-lg border border-slate-800 whitespace-nowrap">
            Found <span className="font-bold text-brand-400">{sortedPlaces.length}</span> places
          </div>
        </div>
      </div>

      {/* Coordinate status disclaimer badge */}
      {coordinateStatus === "LOCALITY_APPROXIMATE" && (
        <div className="p-3 rounded-xl bg-amber-500/10 border border-amber-500/25 text-amber-300 text-xs flex items-center gap-2 font-medium">
          <MapPin className="w-4 h-4 text-amber-400 flex-shrink-0" />
          <span>Amenities calculated around approximate locality</span>
        </div>
      )}

      {/* Quick stat chips */}
      {!loading && !apiError && radiusCapped.length > 0 && (
        <div className="flex flex-wrap gap-2">
          {Object.entries(categoryCounts).map(([cat, count]) => {
            const info = CATEGORY_MAP[cat] || CATEGORY_MAP["All"];
            const Icon = info.icon;
            return (
              <span
                key={cat}
                className={`inline-flex items-center gap-1 text-[11px] font-semibold px-2.5 py-1 rounded-lg border ${info.bg} ${info.color}`}
              >
                <Icon className="w-3 h-3" />
                {count} {cat}
              </span>
            );
          })}
        </div>
      )}

      {/* Category Pills Filter */}
      <div className="flex items-center gap-2 overflow-x-auto pb-2 scrollbar-thin">
        {CATEGORIES_LIST.map((cat) => {
          const catInfo = CATEGORY_MAP[cat] || CATEGORY_MAP["All"];
          const Icon = catInfo.icon;
          const isActive = selectedCategory === cat;
          const count = cat === "All" ? radiusCapped.length : (categoryCounts[cat] || 0);
          return (
            <button
              key={cat}
              onClick={() => setSelectedCategory(cat)}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-semibold whitespace-nowrap transition-all border ${
                isActive
                  ? 'bg-brand-500 text-white border-brand-400 shadow-md shadow-brand-500/25'
                  : 'bg-slate-900/80 text-slate-400 border-slate-800 hover:text-white hover:bg-slate-800'
              }`}
            >
              <Icon className="w-3.5 h-3.5" />
              {cat}
              {count > 0 && (
                <span className={`text-[10px] px-1.5 py-0.5 rounded-full font-bold ${
                  isActive ? 'bg-white/20 text-white' : 'bg-slate-800 text-slate-300'
                }`}>
                  {count}
                </span>
              )}
            </button>
          );
        })}
      </div>

      {/* Places Grid */}
      {loading ? (
        <div className="py-12 text-center space-y-3">
          <div className="w-8 h-8 mx-auto border-2 border-brand-500 border-t-transparent rounded-full animate-spin" />
          <p className="text-xs text-slate-400">
            Searching within {radius >= 1000 ? `${radius / 1000} km` : `${radius} m`}...
          </p>
        </div>
      ) : apiError ? (
        <div className="py-12 text-center bg-slate-900/40 rounded-xl border border-slate-800/60 space-y-2">
          <div className="w-12 h-12 bg-rose-950/20 rounded-full flex items-center justify-center mx-auto border border-rose-500/20">
            <AlertTriangle className="w-6 h-6 text-rose-400" />
          </div>
          <p className="text-sm font-bold text-white">
            Amenities temporarily unavailable
          </p>
          <p className="text-xs text-slate-400 font-medium">
            Failed to connect to Geoapify GIS service. Please try again later.
          </p>
        </div>
      ) : sortedPlaces.length === 0 ? (
        <div className="py-12 text-center bg-slate-900/40 rounded-xl border border-slate-800/60 space-y-2">
          <div className="w-12 h-12 bg-slate-800/40 rounded-full flex items-center justify-center mx-auto border border-slate-800">
            <MapPin className="w-6 h-6 text-slate-500" />
          </div>
          <p className="text-sm font-bold text-white">
            {selectedCategory === "All"
              ? `No amenities found within ${radius >= 1000 ? `${radius / 1000} km` : `${radius} m`}`
              : `No ${selectedCategory} found within ${radius >= 1000 ? `${radius / 1000} km` : `${radius} m`}`}
          </p>
          <p className="text-xs text-slate-400 font-medium">
            No matching POIs returned by the current data provider.
          </p>
          <p className="text-[11px] text-slate-500">
            {selectedCategory !== "All"
              ? 'Try selecting "All" or switching to a larger radius.'
              : 'Try switching to a 5 KM radius to expand the search.'}
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 max-h-[520px] overflow-y-auto pr-1">
          {sortedPlaces.map((place, idx) => {
            const catInfo = CATEGORY_MAP[place.category] || CATEGORY_MAP["All"];
            const Icon = catInfo.icon;
            const distFormatted = place.distance_meters >= 1000
              ? `${(place.distance_meters / 1000).toFixed(2)} km`
              : `${Math.round(place.distance_meters)} m`;

            return (
              <div
                key={`${place.name}-${idx}`}
                className="p-4 rounded-xl bg-slate-900/70 border border-slate-800/80 hover:border-slate-700 transition-all hover:translate-y-[-2px] space-y-3 flex flex-col justify-between"
              >
                <div className="space-y-1.5">
                  <div className="flex items-center justify-between">
                    <span className={`inline-flex items-center gap-1 text-[11px] font-semibold px-2 py-0.5 rounded-md border ${catInfo.bg} ${catInfo.color}`}>
                      <Icon className="w-3 h-3" />
                      {place.category}
                    </span>
                    <span className="text-xs font-mono font-semibold text-brand-400 bg-brand-500/10 px-2 py-0.5 rounded">
                      {distFormatted}
                    </span>
                  </div>
                  <h4 className="text-sm font-bold text-white line-clamp-1 mt-1">{place.name}</h4>
                  {place.address && (
                    <p className="text-xs text-slate-400 line-clamp-1">{place.address}</p>
                  )}
                </div>

                <div className="pt-2 border-t border-slate-800/60 flex items-center justify-between text-[11px] text-slate-500 font-mono">
                  <span>Lat: {place.latitude.toFixed(4)}</span>
                  <span>Lon: {place.longitude.toFixed(4)}</span>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};
