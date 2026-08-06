import React, { useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Popup, useMap } from 'react-leaflet';
import L from 'leaflet';

// Fix Leaflet default icon paths in React Vite environment
delete L.Icon.Default.prototype._getIconUrl;

const searchLocationIcon = L.divIcon({
  className: 'custom-pin-search',
  html: `<div class="w-8 h-8 rounded-full bg-brand-500 border-2 border-white shadow-lg flex items-center justify-center text-white animate-bounce">
          <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0Z"/><circle cx="12" cy="10" r="3"/></svg>
         </div>`,
  iconSize: [32, 32],
  iconAnchor: [16, 32],
  popupAnchor: [0, -32]
});

const currentLocationIcon = L.divIcon({
  className: 'custom-pin-current',
  html: `<div class="w-7 h-7 rounded-full bg-emerald-500 border-2 border-white shadow-lg flex items-center justify-center text-white pulse">
          <div class="w-2.5 h-2.5 rounded-full bg-white animate-ping"></div>
         </div>`,
  iconSize: [28, 28],
  iconAnchor: [14, 14],
  popupAnchor: [0, -14]
});

const placeCategoryIcons = {
  "Schools": "🎓",
  "Colleges": "🏫",
  "Hospitals": "🏥",
  "Metro Stations": "🚇",
  "Bus Stops": "🚌",
  "Restaurants": "🍽️",
  "Shopping Malls": "🛍️",
  "Banks": "🏦",
  "Parks": "🌳",
  "Amenity": "📍"
};

const getPlaceIcon = (category) => {
  const emoji = placeCategoryIcons[category] || "📍";
  return L.divIcon({
    className: 'custom-pin-place',
    html: `<div class="w-6 h-6 rounded-full bg-slate-900 border border-slate-700 shadow-md flex items-center justify-center text-xs">
            ${emoji}
           </div>`,
    iconSize: [24, 24],
    iconAnchor: [12, 12],
    popupAnchor: [0, -12]
  });
};

// Component to dynamically adjust map center when search target changes
function ChangeView({ center, zoom }) {
  const map = useMap();
  useEffect(() => {
    if (center && center[0] && center[1]) {
      map.flyTo(center, zoom, {
        duration: 1.5,
        easeLinearity: 0.25
      });
    }
  }, [center, zoom, map]);
  return null;
}

export const MapView = ({ searchResult, currentLocation, nearbyPlaces = [] }) => {
  const defaultCenter = searchResult 
    ? [searchResult.latitude, searchResult.longitude]
    : (currentLocation ? [currentLocation.latitude, currentLocation.longitude] : [12.9352, 77.6245]); // Koramangala default

  return (
    <div className="relative w-full h-[520px] rounded-2xl overflow-hidden border border-slate-800 shadow-2xl glass-card">
      <MapContainer
        center={defaultCenter}
        zoom={14}
        scrollWheelZoom={true}
        className="w-full h-full"
      >
        <ChangeView center={defaultCenter} zoom={14} />
        
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />

        {/* Target Search Location Marker */}
        {searchResult && (
          <Marker 
            position={[searchResult.latitude, searchResult.longitude]} 
            icon={searchLocationIcon}
          >
            <Popup>
              <div className="p-1 space-y-2 min-w-[220px]">
                <div className="flex items-center justify-between border-b border-slate-800 pb-1">
                  <span className="text-xs uppercase tracking-wider font-bold text-brand-400">Search Target</span>
                  <span className="text-[10px] bg-brand-500/20 text-brand-300 px-1.5 py-0.5 rounded font-mono">GIS Active</span>
                </div>
                <h4 className="text-sm font-bold text-slate-100">{searchResult.formatted_address}</h4>
                {searchResult.estimated_price_sqft && (
                  <div className="bg-slate-900/90 p-2 rounded-lg border border-slate-800">
                    <p className="text-[11px] text-slate-400">Est. Real Estate Value:</p>
                    <p className="text-sm font-extrabold text-emerald-400">{searchResult.price_range}</p>
                    <p className="text-[10px] text-slate-400 mt-0.5">Avg: ₹{searchResult.estimated_price_sqft.toLocaleString()} / sq.ft</p>
                  </div>
                )}
                <p className="text-[10px] text-slate-400 font-mono">
                  Lat: {searchResult.latitude.toFixed(4)}, Lon: {searchResult.longitude.toFixed(4)}
                </p>
              </div>
            </Popup>
          </Marker>
        )}

        {/* User Current Location Marker */}
        {currentLocation && (
          <Marker 
            position={[currentLocation.latitude, currentLocation.longitude]} 
            icon={currentLocationIcon}
          >
            <Popup>
              <div className="p-1">
                <p className="text-xs font-bold text-emerald-400 mb-1">Your Current Location</p>
                <p className="text-xs text-slate-200">{currentLocation.formatted_address}</p>
              </div>
            </Popup>
          </Marker>
        )}

        {/* Nearby Amenities Markers */}
        {nearbyPlaces.map((place, idx) => (
          <Marker
            key={`${place.name}-${idx}`}
            position={[place.latitude, place.longitude]}
            icon={getPlaceIcon(place.category)}
          >
            <Popup>
              <div className="p-1 space-y-1">
                <span className="text-[10px] uppercase font-bold text-slate-400">{place.category}</span>
                <h5 className="text-xs font-bold text-slate-100">{place.name}</h5>
                <p className="text-[11px] text-brand-400 font-semibold">{place.distance_meters} meters away</p>
                {place.address && <p className="text-[10px] text-slate-400">{place.address}</p>}
              </div>
            </Popup>
          </Marker>
        ))}
      </MapContainer>
    </div>
  );
};
