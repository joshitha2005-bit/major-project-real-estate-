import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { 
  Building2, MapPin, Bed, Maximize2, Phone, Sparkles, 
  Eye, Compass, CheckCircle2, User, MessageSquare, X, Navigation 
} from 'lucide-react';
import { resolvePropertyDisplay, navigateToProperty } from '../utils/propertyLocationUtils';

const getCleanFallbackImage = (id, ptype = "") => {
  const ptype_lower = (ptype || "").toLowerCase();
  let cat = "apartments";
  let count = 20;
  if (ptype_lower.includes("villa")) {
    cat = "villas";
    count = 15;
  } else if (ptype_lower.includes("house") || ptype_lower.includes("independent")) {
    cat = "houses";
    count = 15;
  } else if (ptype_lower.includes("penthouse")) {
    cat = "penthouses";
    count = 10;
  } else if (ptype_lower.includes("plot") || ptype_lower.includes("land")) {
    cat = "plots";
    count = 9;
  }
  const idx = String(((id || 0) % count) + 1).padStart(2, '0');
  return `/static/property-images/${cat}/${cat}_${idx}.jpg`;
};

// Module-level tracking for displayed images in the current render pass.
// Resets automatically after the batch rendering completes.
let displayedImageUrls = new Set();
let resetTimeout = null;

const checkDuplicate = (url) => {
  if (!url) return false;
  if (displayedImageUrls.has(url)) {
    return true; // Duplicate detected!
  }
  displayedImageUrls.add(url);
  
  if (resetTimeout) clearTimeout(resetTimeout);
  resetTimeout = setTimeout(() => {
    displayedImageUrls.clear();
  }, 150);
  
  return false;
};

export const PropertyCard = ({ property, onSelectOnMap }) => {
  const [showContactModal, setShowContactModal] = useState(false);
  const [messageSent, setMessageSent] = useState(false);

  const isHistorical = property && (
    property.source_type === 'historical_dataset' ||
    property.source_type === 'HISTORICAL_MARKET_DATA' ||
    property.source === 'Bengaluru_House_Data.csv' ||
    property.source === 'Real Estate Data V21.csv' ||
    property.source === 'Kaggle Research Dataset' ||
    property.listing_status === 'HISTORICAL' ||
    property.listing_status === 'HISTORICAL MARKET DATA'
  );
  const isDirect = property && (
    property.source === 'PropPulse Direct' ||
    property.source_type === 'owner_listing' ||
    property.source_type === 'PROPPULSE_DIRECT'
  ) && !isHistorical;
  const isCurrentSource = property && (
    property.listing_status === 'CURRENT' ||
    property.listing_status === 'CURRENT_SOURCE_LISTING' ||
    property.is_main_ai_ready === true ||
    property.dataset_category === 'MAIN_AI_READY'
  );
  
  // Extract primary / first image if available
  let primaryImage = null;
  if (property.uploaded_images && property.uploaded_images.length > 0) {
    const primaryObj = property.uploaded_images.find(img => img.is_primary) || property.uploaded_images[0];
    primaryImage = primaryObj.image_path;
  } else if (property.images && property.images.length > 0) {
    primaryImage = property.images[0];
  }

  const [imgError, setImgError] = useState(false);
  const prov = (property.image_provenance || property.gallery?.image_provenance || '').toUpperCase();
  const hasImage = !imgError && primaryImage && primaryImage.trim() !== '';
  const isActualPropertyPhoto = hasImage && (
    prov === 'PROPERTY_SPECIFIC' || 
    prov === 'USER_UPLOADED' || 
    prov === 'OWNER_UPLOADED' ||
    (property.has_genuine_image && prov !== 'REPRESENTATIVE' && prov !== 'AI_GENERATED')
  );
  const isAiGenerated = hasImage && prov === 'AI_GENERATED';
  const isRepresentative = hasImage && !isActualPropertyPhoto && !isAiGenerated;
  const hasVerifiedImage = hasImage;

  // Phone contact privacy: ONLY allowed for genuine owner listings
  const isOwnerListing = property.source_type === 'owner_listing';
  const displayPhone = (property.owner_phone && property.owner_phone !== 'Contact information unavailable' && property.owner_phone.trim() !== '')
    ? property.owner_phone
    : null;

  const disp = resolvePropertyDisplay(property);
  const displayName = disp.buildingName;

  return (
    <>
      <div className="glass-card glass-card-hover rounded-3xl overflow-hidden border border-slate-800 flex flex-col justify-between group bg-slate-950/40">
        <div>
          {/* Image Canvas */}
          <div className="relative aspect-[16/10] overflow-hidden bg-slate-900">
            {hasVerifiedImage ? (
              <img 
                src={primaryImage} 
                onError={() => setImgError(true)}
                alt={displayName} 
                className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500" 
              />
            ) : (
              <div className="w-full h-full flex flex-col items-center justify-center bg-slate-900/90 text-slate-500 gap-2 p-4">
                <Building2 className="w-10 h-10 text-slate-700" />
                <span className="text-xs font-semibold text-slate-400">PROPERTY IMAGE UNAVAILABLE</span>
              </div>
            )}
            <div className="absolute inset-0 bg-gradient-to-t from-dark-950 via-transparent to-transparent opacity-80"></div>
            
            {/* Property Type Badge */}
            <div className="absolute top-3 left-3 flex items-center gap-1.5 px-3 py-1 rounded-full bg-dark-950/80 backdrop-blur-md border border-slate-700/80 text-xs font-bold text-brand-300">
              <Building2 className="w-3.5 h-3.5 text-brand-400" />
              <span>{property.property_type && property.property_type !== 'Not specified' ? property.property_type : 'Property'}</span>
            </div>

            {/* Listing Status & Source Badges */}
            <div className="absolute top-3 right-3 flex flex-col items-end gap-1.5">
              <span className={`px-2.5 py-1 rounded-full backdrop-blur-md border text-[10px] font-extrabold uppercase tracking-wider ${
                isDirect
                  ? 'bg-emerald-500/25 border-emerald-500/50 text-emerald-300'
                  : isCurrentSource
                    ? 'bg-cyan-500/25 border-cyan-500/50 text-cyan-300'
                    : (property.source_type === 'authorized_provider' || property.listing_status === 'AUTHORIZED')
                      ? 'bg-blue-500/25 border-blue-500/50 text-blue-300'
                      : property.listing_status === 'REFERENCE'
                        ? 'bg-sky-500/25 border-sky-500/50 text-sky-300'
                        : 'bg-amber-500/25 border-amber-500/50 text-amber-300'
              }`}>
                {isDirect
                  ? 'PROPPULSE DIRECT'
                  : isCurrentSource
                    ? 'CURRENT SOURCE LISTING'
                    : (property.source_type === 'authorized_provider' || property.listing_status === 'AUTHORIZED')
                      ? 'AUTHORIZED PROVIDER'
                      : property.listing_status === 'REFERENCE'
                        ? 'MARKET REFERENCE'
                        : 'HISTORICAL MARKET DATA'}
              </span>
              {isActualPropertyPhoto ? (
                <span className="px-2 py-0.5 rounded-full backdrop-blur-md border text-[9px] font-bold bg-emerald-950/90 border-emerald-500/50 text-emerald-300">
                  ACTUAL PROPERTY IMAGE
                </span>
              ) : isRepresentative ? (
                <span className="px-2 py-0.5 rounded-full backdrop-blur-md border text-[9px] font-bold bg-amber-950/90 border-amber-500/40 text-amber-300" title="Representative image — not the actual property">
                  REPRESENTATIVE IMAGE — NOT ACTUAL PROPERTY
                </span>
              ) : isAiGenerated ? (
                <span className="px-2 py-0.5 rounded-full backdrop-blur-md border text-[9px] font-bold bg-purple-950/90 border-purple-500/40 text-purple-300">
                  AI-GENERATED REFERENCE — NOT PROPERTY EVIDENCE
                </span>
              ) : (
                <span className="px-2 py-0.5 rounded-full backdrop-blur-md border text-[9px] font-bold bg-slate-900/90 border-slate-700 text-slate-400">
                  PROPERTY IMAGE UNAVAILABLE
                </span>
              )}
            </div>

            {/* Price Badge */}
            <div className="absolute bottom-3 left-3 right-3 flex items-center justify-between">
              <div className="bg-slate-900/90 backdrop-blur-md px-3.5 py-1.5 rounded-2xl border border-brand-500/40 text-emerald-400 font-extrabold text-base">
                {property.price_formatted}
              </div>
              <span className="text-[10px] bg-slate-950/80 text-slate-350 px-2 py-1 rounded-lg border border-slate-800 font-mono">
                {disp.pricePerSqftText}
              </span>
            </div>
          </div>

          {/* Details Body — CRITICAL 3-TIER HIERARCHY */}
          <div className="p-5 space-y-3">
            <div className="flex items-center justify-between text-[10px] uppercase font-bold tracking-widest text-slate-500">
              <span className="text-brand-400 font-semibold">{property.locality || 'Bengaluru'}</span>
              <span className="text-slate-700">•</span>
              <span className={isHistorical ? 'text-amber-400 font-semibold' : 'text-emerald-400 font-semibold'}>
                {isDirect ? 'PropPulse Direct' : isCurrentSource ? 'Verified Market Listing' : 'Historical Dataset'}
              </span>
            </div>

            {/* 1. ACTUAL BUILDING / PROJECT / PROPERTY NAME */}
            <h3 className="text-base font-bold text-white line-clamp-1 group-hover:text-brand-300 transition-colors font-outfit">
              {disp.primaryTitle}
            </h3>

            {/* Unresolved Identity Indicator */}
            {disp.identitySubtitle && (
              <p className="text-[11px] text-slate-400 italic -mt-1 font-medium flex items-center gap-1">
                <span>{disp.identitySubtitle}</span>
              </p>
            )}

            {/* 2. SUB-LOCALITY / LOCALITY, BENGALURU */}
            <p className="text-xs text-brand-300 font-semibold flex items-center gap-1.5 line-clamp-1">
              <MapPin className="w-3.5 h-3.5 text-brand-400 flex-shrink-0" />
              <span>{disp.locationLine}</span>
            </p>

            {/* 3. STREET / ROAD / FULL ADDRESS (when available) */}
            {disp.addressLine && (
              <p className="text-[11px] text-slate-400 line-clamp-1 pl-5">
                {disp.addressLine}
              </p>
            )}

            {/* Spec Icons Grid */}
            <div className="grid grid-cols-2 gap-2 text-xs text-slate-300">
              <div className="flex items-center gap-1.5 bg-slate-900/60 px-2.5 py-1.5 rounded-xl border border-slate-800">
                <Bed className="w-3.5 h-3.5 text-brand-400" />
                <span>{property.bhk} BHK</span>
              </div>
              <div className="flex items-center gap-1.5 bg-slate-900/60 px-2.5 py-1.5 rounded-xl border border-slate-800">
                <Maximize2 className="w-3.5 h-3.5 text-accent-400" />
                <span>{property.area_sqft} sq.ft</span>
              </div>
            </div>

            {/* Location Accuracy Badge */}
            <div className="flex items-center justify-between text-[11px] pt-2 border-t border-slate-800/60">
              <span className="text-slate-400">Location Confidence:</span>
              <span className={`font-semibold px-2 py-0.5 rounded text-[10px] ${
                disp.isExact 
                  ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' 
                  : 'bg-amber-500/10 text-amber-400 border border-amber-500/20'
              }`}>
                {disp.coordinateAccuracy}
              </span>
            </div>

            {/* Historical Warning */}
            {isHistorical && (
              <div className="p-2 rounded-xl bg-amber-500/10 border border-amber-500/30 text-[10px] text-amber-300 leading-snug">
                <strong>Historical Market Data:</strong> Transaction benchmark record.
              </div>
            )}
          </div>
        </div>

        {/* Card Actions Footer: View Details, Open Map, Get Directions */}
        <div className="p-4 border-t border-slate-800/80 bg-slate-900/40 flex flex-col gap-2">
          <div className="grid grid-cols-3 gap-1.5 text-xs">
            <Link
              to={`/properties/${property.id}`}
              className="px-2 py-2 rounded-xl bg-brand-600 hover:bg-brand-500 text-white font-semibold text-center flex items-center justify-center gap-1 transition-all shadow-md shadow-brand-500/20 text-[11px]"
              title="View property details"
            >
              <Eye className="w-3.5 h-3.5" />
              <span>Details</span>
            </Link>

            <button
              onClick={() => onSelectOnMap ? onSelectOnMap(property) : window.open(`https://www.google.com/maps/search/?api=1&query=${property.latitude},${property.longitude}`, '_blank')}
              className="px-2 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 font-semibold text-center flex items-center justify-center gap-1 transition-all border border-slate-700 text-[11px]"
              title="Open property in Map"
            >
              <Compass className="w-3.5 h-3.5 text-accent-400" />
              <span>Map</span>
            </button>

            <button
              onClick={() => navigateToProperty(property)}
              className="px-2 py-2 rounded-xl bg-emerald-600/90 hover:bg-emerald-500 text-white font-semibold text-center flex items-center justify-center gap-1 transition-all shadow-md shadow-emerald-500/20 text-[11px]"
              title={disp.isExact ? "Navigate from your location to exact property" : "Get directions to locality area"}
            >
              <Navigation className="w-3.5 h-3.5" />
              <span>Directions</span>
            </button>
          </div>

          {/* Contact buttons ONLY for real verified owner listings */}
          {isOwnerListing && displayPhone ? (
            <button
              onClick={() => setShowContactModal(true)}
              className="w-full py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-semibold text-center flex items-center justify-center gap-1.5 transition-all text-xs"
            >
              <MessageSquare className="w-3.5 h-3.5" />
              <span>Contact Owner</span>
            </button>
          ) : null}
        </div>
      </div>

      {/* Owner Contact Modal */}
      {showContactModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-dark-950/80 backdrop-blur-md">
          <div className="glass-card w-full max-w-md p-6 rounded-3xl border border-slate-800 space-y-4 relative shadow-2xl bg-slate-900">
            <button
              onClick={() => {
                setShowContactModal(false);
                setMessageSent(false);
              }}
              className="absolute top-4 right-4 text-slate-400 hover:text-white"
            >
              <X className="w-5 h-5" />
            </button>

            <div className="space-y-1">
              <h4 className="text-lg font-bold text-white font-outfit">Contact Property Owner</h4>
              <p className="text-xs text-slate-400">Direct inquiry for: <strong className="text-slate-200">{displayName}</strong></p>
            </div>

            <div className="p-3 rounded-2xl bg-slate-950 border border-slate-850 space-y-1 text-xs">
              <p className="font-semibold text-white">Owner: {property.owner_name}</p>
              <p className="text-emerald-400 font-mono">Phone: {displayPhone}</p>
              <p className="text-slate-400 font-mono">Status: {property.coordinate_status === 'EXACT' ? 'Exact location coordinate' : 'Approximate coordinate location'}</p>
            </div>

            {messageSent ? (
              <div className="p-4 rounded-2xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-xs flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 flex-shrink-0" />
                <span>Your contact request has been sent. They will call back shortly!</span>
              </div>
            ) : (
              <form 
                onSubmit={(e) => {
                  e.preventDefault();
                  setMessageSent(true);
                }} 
                className="space-y-3"
              >
                <div>
                  <label className="text-xs font-semibold text-slate-300 block mb-1">Your Name</label>
                  <input required type="text" placeholder="Enter your full name" className="w-full px-3 py-2 rounded-xl bg-slate-950 border border-slate-850 text-xs text-white" />
                </div>
                <div>
                  <label className="text-xs font-semibold text-slate-300 block mb-1">Your Phone Number</label>
                  <input required type="tel" placeholder="+91 98765 43210" className="w-full px-3 py-2 rounded-xl bg-slate-950 border border-slate-850 text-xs text-white" />
                </div>
                <div>
                  <label className="text-xs font-semibold text-slate-300 block mb-1">Inquiry Message</label>
                  <textarea rows={3} defaultValue={`Hi, I am interested in viewing your property '${property.title}' in ${property.locality}. Please let me know your availability.`} className="w-full px-3 py-2 rounded-xl bg-slate-950 border border-slate-850 text-xs text-white" />
                </div>

                <button type="submit" className="w-full py-3 rounded-xl bg-brand-600 hover:bg-brand-500 text-white font-semibold text-xs shadow-lg shadow-brand-500/20">
                  Send Contact Inquiry
                </button>
              </form>
            )}
          </div>
        </div>
      )}
    </>
  );
};
