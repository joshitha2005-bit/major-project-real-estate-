import React, { useEffect, useState, useRef } from 'react';
import { MapContainer, TileLayer, Marker, Popup, useMap } from 'react-leaflet';
import L from 'leaflet';
import { Eye, ArrowLeft, ExternalLink, Loader2, MapPin } from 'lucide-react';

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

// Thread-safe dynamic Google Maps script loader
const loadGoogleMapsScript = (apiKey) => {
  return new Promise((resolve, reject) => {
    if (window.google && window.google.maps) {
      resolve(window.google);
      return;
    }
    const existingScript = document.getElementById('google-maps-script');
    if (existingScript) {
      const interval = setInterval(() => {
        if (window.google && window.google.maps) {
          clearInterval(interval);
          resolve(window.google);
        }
      }, 100);
      return;
    }
    const script = document.createElement('script');
    script.id = 'google-maps-script';
    script.src = `https://maps.googleapis.com/maps/api/js?key=${apiKey}&v=weekly`;
    script.async = true;
    script.defer = true;
    script.onload = () => resolve(window.google);
    script.onerror = (err) => reject(err);
    document.head.appendChild(script);
  });
};

export const MapView = ({ searchResult, currentLocation, nearbyPlaces = [] }) => {
  const [showStreetView, setShowStreetView] = useState(false);
  const [streetViewStatus, setStreetViewStatus] = useState('idle'); // 'idle' | 'loading' | 'available' | 'unavailable' | 'error'
  const [imageryDate, setImageryDate] = useState('');
  const [nearestLocation, setNearestLocation] = useState(null);

  const panoramaRef = useRef(null);
  const panoramaInstance = useRef(null);

  const defaultCenter = searchResult 
    ? [searchResult.latitude, searchResult.longitude]
    : (currentLocation ? [currentLocation.latitude, currentLocation.longitude] : [12.9352, 77.6245]); // Koramangala default

  const lat = searchResult?.latitude || currentLocation?.latitude;
  const lon = searchResult?.longitude || currentLocation?.longitude;

  const handleViewStreetView = async () => {
    if (!lat || !lon) {
      setStreetViewStatus('unavailable');
      setShowStreetView(true);
      return;
    }

    setShowStreetView(true);
    setStreetViewStatus('loading');

    const apiKey = import.meta.env.VITE_GOOGLE_MAPS_API_KEY || '';
    if (!apiKey || apiKey.includes('DummyKey') || apiKey.includes('YOUR_GOOGLE')) {
      console.warn("Street View: Dummy/missing VITE_GOOGLE_MAPS_API_KEY. Using fallback.");
      setStreetViewStatus('unavailable');
      return;
    }

    // Suppress Google Maps API alerts for dummy/restricted keys
    const originalAlert = window.alert;
    window.alert = (msg) => {
      if (msg && (msg.includes('Google Maps') || msg.includes('ApiNotActivatedMapError'))) {
        console.warn('Google Maps API warning:', msg);
        return;
      }
      originalAlert(msg);
    };

    try {
      const google = await loadGoogleMapsScript(apiKey);
      const service = new google.maps.StreetViewService();
      
      service.getPanorama({
        location: { lat, lng: lon },
        radius: 200,
        preference: google.maps.StreetViewPreference.NEAREST
      }, (data, status) => {
        window.alert = originalAlert;

        if (status === google.maps.StreetViewStatus.OK && data && data.location) {
          setStreetViewStatus('available');
          setImageryDate(data.imageDate || 'Unknown Date');
          
          setNearestLocation({
            lat: data.location.latLng.lat(),
            lon: data.location.latLng.lng()
          });

          // Mount panorama on next tick once DOM is ready
          setTimeout(() => {
            if (panoramaRef.current) {
              panoramaInstance.current = new google.maps.StreetViewPanorama(panoramaRef.current, {
                position: data.location.latLng,
                pov: { heading: 165, pitch: 0 },
                zoom: 1,
                addressControl: false,
                linksControl: true,
                panControl: true,
                enableCloseButton: false
              });
            }
          }, 50);
        } else {
          setStreetViewStatus('unavailable');
        }
      });
    } catch (err) {
      window.alert = originalAlert;
      console.error("Failed to load Google Maps SDK:", err);
      setStreetViewStatus('error');
    }
  };

  const handleBackToMap = () => {
    setShowStreetView(false);
    setStreetViewStatus('idle');
    setImageryDate('');
    setNearestLocation(null);
    if (panoramaInstance.current) {
      panoramaInstance.current = null;
    }
  };

  return (
    <div className="relative w-full h-[520px] rounded-2xl overflow-hidden border border-slate-800 shadow-2xl glass-card">
      {/* View Street View Button overlay */}
      {!showStreetView && searchResult && (
        <button
          onClick={handleViewStreetView}
          className="absolute top-4 right-4 z-[1000] px-4 py-2 bg-slate-900/90 hover:bg-slate-800 text-white text-xs font-bold rounded-xl border border-slate-800 shadow-lg flex items-center gap-1.5 transition-all hover:scale-105"
        >
          <Eye className="w-4 h-4 text-brand-400" />
          <span>View Street View</span>
        </button>
      )}

      {/* Leaflet Map (Hidden/Inactive when Street View panel overlays it) */}
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

      {/* Street View Panel Overlay */}
      {showStreetView && (
        <div className="absolute inset-0 z-[2000] bg-slate-950 flex flex-col">
          {/* Header Panel */}
          <div className="bg-slate-900 border-b border-slate-800 p-4 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <button
                onClick={handleBackToMap}
                className="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold rounded-lg flex items-center gap-1.5 transition-all"
              >
                <ArrowLeft className="w-3.5 h-3.5" />
                <span>Back to Map</span>
              </button>
              <span className="text-sm font-bold text-white font-outfit">Street View Surroundings</span>
            </div>

            <div className="text-right">
              {streetViewStatus === 'available' && (
                <div className="text-xs text-slate-400">
                  <span className="text-brand-400 font-semibold">Nearest available Street View</span>
                  {imageryDate && ` | Date: ${imageryDate}`}
                </div>
              )}
            </div>
          </div>

          {/* Viewer / Status Area */}
          <div className="flex-1 relative bg-slate-900 flex items-center justify-center">
            {streetViewStatus === 'loading' && (
              <div className="flex flex-col items-center gap-3 text-center">
                <Loader2 className="w-8 h-8 text-brand-500 animate-spin" />
                <p className="text-xs text-slate-400 font-medium">Checking Street View metadata & availability...</p>
              </div>
            )}

            {streetViewStatus === 'available' && (
              <div className="w-full h-full relative">
                {/* Panorama Target Container */}
                <div ref={panoramaRef} className="w-full h-full" />
                
                {/* Float Action: Open in Google Maps */}
                {lat && lon && (
                  <a
                    href={`https://www.google.com/maps/@?api=1&map_action=pano&viewpoint=${lat},${lon}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="absolute bottom-4 right-4 z-[2010] px-3.5 py-2 bg-slate-900/90 hover:bg-slate-800 text-white text-xs font-bold rounded-xl border border-slate-800 shadow-lg flex items-center gap-1.5 transition-all"
                  >
                    <ExternalLink className="w-3.5 h-3.5 text-emerald-400" />
                    <span>Open in Google Maps Street View</span>
                  </a>
                )}
              </div>
            )}

            {(streetViewStatus === 'unavailable' || streetViewStatus === 'error') && (
              <div className="p-6 text-center space-y-4 max-w-sm">
                <div className="w-12 h-12 bg-slate-800 rounded-full flex items-center justify-center mx-auto border border-slate-700">
                  <MapPin className="w-6 h-6 text-slate-500" />
                </div>
                <div className="space-y-1.5">
                  <h4 className="text-sm font-bold text-white">Street View Unavailable</h4>
                  <p className="text-xs text-slate-400 leading-relaxed">
                    Street View imagery is not available near this property.
                  </p>
                </div>
                {lat && lon && (
                  <div className="pt-2">
                    <a
                      href={`https://www.google.com/maps/search/?api=1&query=${lat},${lon}`}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center gap-1.5 px-4 py-2 bg-brand-500/10 hover:bg-brand-500/20 text-brand-400 border border-brand-500/20 text-xs font-semibold rounded-xl transition-all"
                    >
                      <ExternalLink className="w-3.5 h-3.5" />
                      <span>Open Location in Google Maps</span>
                    </a>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};
