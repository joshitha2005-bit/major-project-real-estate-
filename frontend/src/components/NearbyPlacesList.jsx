import React, { useState } from 'react';
import { 
  GraduationCap, Hospital, Train, Utensils, 
  ShoppingBag, Landmark, Trees, Bus, MapPin, Search, Filter 
} from 'lucide-react';

const CATEGORY_MAP = {
  "All": { icon: Filter, color: "text-slate-300", bg: "bg-slate-800" },
  "Schools": { icon: GraduationCap, color: "text-blue-400", bg: "bg-blue-500/10 border-blue-500/20" },
  "Colleges": { icon: GraduationCap, color: "text-indigo-400", bg: "bg-indigo-500/10 border-indigo-500/20" },
  "Hospitals": { icon: Hospital, color: "text-red-400", bg: "bg-red-500/10 border-red-500/20" },
  "Metro Stations": { icon: Train, color: "text-amber-400", bg: "bg-amber-500/10 border-amber-500/20" },
  "Bus Stops": { icon: Bus, color: "text-yellow-400", bg: "bg-yellow-500/10 border-yellow-500/20" },
  "Restaurants": { icon: Utensils, color: "text-orange-400", bg: "bg-orange-500/10 border-orange-500/20" },
  "Shopping Malls": { icon: ShoppingBag, color: "text-purple-400", bg: "bg-purple-500/10 border-purple-500/20" },
  "Banks": { icon: Landmark, color: "text-emerald-400", bg: "bg-emerald-500/10 border-emerald-500/20" },
  "Parks": { icon: Trees, color: "text-green-400", bg: "bg-green-500/10 border-green-500/20" },
};

export const NearbyPlacesList = ({ places = [], loading = false }) => {
  const [selectedCategory, setSelectedCategory] = useState("All");

  const categoriesList = ["All", "Schools", "Hospitals", "Metro Stations", "Restaurants", "Shopping Malls", "Banks", "Parks", "Colleges", "Bus Stops"];

  const filteredPlaces = selectedCategory === "All"
    ? places
    : places.filter(p => p.category === selectedCategory);

  return (
    <div className="glass-card p-6 rounded-2xl border border-slate-800 space-y-6">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-800 pb-4">
        <div>
          <h3 className="text-lg font-bold text-white font-outfit flex items-center gap-2">
            <MapPin className="w-5 h-5 text-brand-500" />
            Nearby Amenities & GIS Places
          </h3>
          <p className="text-xs text-slate-400 mt-1">
            Real-time nearby infrastructure queried via Geoapify GIS engine
          </p>
        </div>
        <div className="text-xs text-slate-400 bg-slate-900 px-3 py-1.5 rounded-lg border border-slate-800 self-start md:self-auto">
          Found <span className="font-bold text-brand-400">{filteredPlaces.length}</span> places
        </div>
      </div>

      {/* Category Pills Filter */}
      <div className="flex items-center gap-2 overflow-x-auto pb-2 scrollbar-thin">
        {categoriesList.map((cat) => {
          const catInfo = CATEGORY_MAP[cat] || CATEGORY_MAP["All"];
          const Icon = catInfo.icon;
          const isActive = selectedCategory === cat;
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
            </button>
          );
        })}
      </div>

      {/* Places Grid List */}
      {loading ? (
        <div className="py-12 text-center space-y-3">
          <div className="w-8 h-8 mx-auto border-2 border-brand-500 border-t-transparent rounded-full animate-spin"></div>
          <p className="text-xs text-slate-400">Fetching nearby GIS points of interest...</p>
        </div>
      ) : filteredPlaces.length === 0 ? (
        <div className="py-12 text-center bg-slate-900/40 rounded-xl border border-slate-800/60">
          <p className="text-sm font-semibold text-slate-400">No places found in this category</p>
          <p className="text-xs text-slate-500 mt-1">Try selecting "All" or searching another locality.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 max-h-[480px] overflow-y-auto pr-1">
          {filteredPlaces.map((place, idx) => {
            const catInfo = CATEGORY_MAP[place.category] || CATEGORY_MAP["All"];
            const Icon = catInfo.icon;
            const distFormatted = place.distance_meters > 1000 
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
