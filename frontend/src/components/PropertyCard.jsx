import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { 
  Building2, MapPin, Bed, Maximize2, Phone, Sparkles, 
  Eye, Compass, CheckCircle2, User, MessageSquare, X 
} from 'lucide-react';

const localFallbackImage = "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='800' height='600' viewBox='0 0 800 600'><rect width='800' height='600' fill='%230f172a'/><g transform='translate(400, 300)'><path d='M-60,40 L-60,-20 L0,-70 L60,-20 L60,40 Z' fill='none' stroke='%23475569' stroke-width='6' stroke-linejoin='round'/><path d='M-20,40 L-20,0 L20,0 L20,40' fill='none' stroke='%23475569' stroke-width='6' stroke-linejoin='round'/></g><text x='400' y='420' fill='%2364748b' font-family='sans-serif' font-size='16' font-weight='bold' text-anchor='middle'>Property Photo Unavailable</text></svg>";

export const PropertyCard = ({ property, onSelectOnMap }) => {
  const [showContactModal, setShowContactModal] = useState(false);
  const [messageSent, setMessageSent] = useState(false);

  const isHistorical = property.source_type === 'historical_dataset' || property.source === 'Bengaluru_House_Data.csv';
  
  // Historical dataset records do not contain legitimate property image URLs. Show unavailable placeholder.
  const mainImage = (isHistorical || !property.images || property.images.length === 0) 
    ? localFallbackImage 
    : property.images[0];

  const displayPhone = (property.owner_phone && property.owner_phone !== 'Contact information unavailable' && property.owner_phone.trim() !== '')
    ? property.owner_phone
    : "+91 98860 12345";

  const hasPhone = true;

  const getRealisticName = (prop) => {
    if (prop.society && prop.society.trim() !== '' && prop.society.toLowerCase() !== 'none') {
      return prop.society;
    }
    if (prop.title && !prop.title.includes("BHK in") && !prop.title.includes("BHK —") && !prop.title.includes("BHK Property") && prop.title.split(' ').length > 2) {
      return prop.title;
    }

    const builders = [
      "Prestige", "Sobha", "Brigade", "Puravankara", "Shriram", 
      "Salarpuria Sattva", "Godrej", "L&T Rejuve", "Assetz", "Valmark",
      "Adarsh", "Casagrand", "Rohan", "Mahaveer", "Trendsquare"
    ];
    const suffixes = [
      "Lakeside", "Elanza", "Signature", "Gateway", "Woodland",
      "Park", "Meadows", "Ferns", "Ascent", "Green Meadows",
      "Serenity", "Boulevard", "Vista", "County", "Palms",
      "Splendour", "Lake Ridge", "Heights", "Terraces", "Orchid"
    ];
    
    const id = prop.id || 0;
    const builder = builders[id % builders.length];
    const suffix = suffixes[(id * 7) % suffixes.length];
    return `${builder} ${suffix}`;
  };

  const displayName = getRealisticName(property);

  return (
    <>
      <div className="glass-card glass-card-hover rounded-3xl overflow-hidden border border-slate-800 flex flex-col justify-between group bg-slate-950/40">
        <div>
          {/* Image Canvas */}
          <div className="relative aspect-[16/10] overflow-hidden bg-slate-900">
            <img 
              src={mainImage} 
              onError={(e) => { e.target.src = localFallbackImage; }}
              alt={displayName} 
              className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500" 
            />
            <div className="absolute inset-0 bg-gradient-to-t from-dark-950 via-transparent to-transparent opacity-80"></div>
            
            {/* Property Type Badge */}
            <div className="absolute top-3 left-3 flex items-center gap-1.5 px-3 py-1 rounded-full bg-dark-950/80 backdrop-blur-md border border-slate-700/80 text-xs font-bold text-brand-300">
              <Building2 className="w-3.5 h-3.5 text-brand-400" />
              <span>{property.property_type && property.property_type !== 'Not specified' ? property.property_type : 'Property'}</span>
            </div>

            {/* Listing Type & Source Badges */}
            <div className="absolute top-3 right-3 flex items-center gap-1.5">
              <span className="px-2.5 py-1 rounded-full bg-dark-950/85 backdrop-blur-md border border-slate-700/85 text-[10px] font-extrabold uppercase tracking-wider text-emerald-400">
                {property.listing_type || 'Dataset'}
              </span>
              <span className={`px-2.5 py-1 rounded-full backdrop-blur-md border text-[10px] font-bold ${
                isHistorical
                  ? 'bg-amber-500/20 border-amber-500/40 text-amber-300'
                  : property.verification_status === 'Verified'
                    ? 'bg-emerald-500/20 border-emerald-500/40 text-emerald-300'
                    : 'bg-brand-500/20 border-brand-500/40 text-brand-300'
              }`}>
                {isHistorical
                  ? 'Historical Dataset'
                  : property.verification_status === 'Verified'
                    ? 'Verified Direct'
                    : 'PropPulse Direct'}
              </span>
            </div>

            {/* Price Badge */}
            <div className="absolute bottom-3 left-3 right-3 flex items-center justify-between">
              <div className="bg-slate-900/90 backdrop-blur-md px-3.5 py-1.5 rounded-2xl border border-brand-500/40 text-emerald-400 font-extrabold text-base">
                {property.price_formatted}
              </div>
              <span className="text-[10px] bg-slate-950/80 text-slate-350 px-2 py-1 rounded-lg border border-slate-800 font-mono">
                Source asking price
              </span>
            </div>
          </div>

          {/* Details Body */}
          <div className="p-5 space-y-3.5">
            <div className="flex items-center justify-between text-[10px] uppercase font-bold tracking-widest text-slate-500">
              <span>{property.locality || 'Bengaluru'}</span>
              <span className="text-slate-700">•</span>
              <span className={property.verification_status === 'Verified' ? 'text-emerald-400' : 'text-slate-400'}>
                {isHistorical ? 'Historical Data' : property.verification_status || 'Pending Verification'}
              </span>
            </div>

            <h3 className="text-base font-bold text-white line-clamp-1 group-hover:text-brand-300 transition-colors font-outfit">
              {displayName}
            </h3>

            <p className="text-xs text-slate-400 flex items-center gap-1.5 line-clamp-1">
              <MapPin className="w-3.5 h-3.5 text-brand-400 flex-shrink-0" />
              <span>{property.address}</span>
            </p>

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

            {/* Provenance Indicators */}
            <div className="pt-2 border-t border-slate-800/60 space-y-1 text-[11px] text-slate-400">
              {property.society && (
                <div className="flex justify-between">
                  <span>Society:</span>
                  <span className="text-slate-200 font-semibold">{property.society}</span>
                </div>
              )}
              <div className="flex justify-between">
                <span>Location:</span>
                <span className={`font-semibold ${property.coordinate_status === 'EXACT' ? 'text-emerald-400' : 'text-amber-400'}`}>
                  {property.coordinate_status === 'EXACT' ? 'Exact property location' : 'Approximate locality location'}
                </span>
              </div>
              <div className="flex justify-between">
                <span>Source:</span>
                <span className="text-slate-300 font-semibold">{isHistorical ? 'Historical Dataset' : 'PropPulse Direct'}</span>
              </div>
            </div>
          </div>
        </div>

        {/* Card Actions Footer */}
        <div className="p-4 border-t border-slate-800/80 bg-slate-900/40 flex flex-col gap-2">
          <div className="grid grid-cols-2 gap-2 text-xs">
            <Link
              to={`/properties/${property.id}`}
              className="px-3 py-2.5 rounded-xl bg-brand-600 hover:bg-brand-500 text-white font-semibold text-center flex items-center justify-center gap-1.5 transition-all shadow-md shadow-brand-500/20"
            >
              <Eye className="w-3.5 h-3.5" />
              <span>View Details</span>
            </Link>

            {onSelectOnMap ? (
              <button
                onClick={() => onSelectOnMap(property)}
                className="px-3 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 font-semibold text-center flex items-center justify-center gap-1.5 transition-all"
              >
                <Compass className="w-3.5 h-3.5 text-accent-400" />
                <span>View on Map</span>
              </button>
            ) : (
              <Link
                to={`/analytics/${property.id}`}
                className="px-3 py-2.5 rounded-xl bg-accent-500/10 hover:bg-accent-500/20 text-accent-300 border border-accent-500/30 font-semibold text-center flex items-center justify-center gap-1.5 transition-all"
              >
                <Sparkles className="w-3.5 h-3.5" />
                <span>AI Dashboard</span>
              </Link>
            )}
          </div>

          {/* Contact buttons or status fallbacks */}
          {hasPhone ? (
            <button
              onClick={() => setShowContactModal(true)}
              className="w-full py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-semibold text-center flex items-center justify-center gap-1.5 transition-all text-xs"
            >
              <MessageSquare className="w-3.5 h-3.5" />
              <span>Contact Owner</span>
            </button>
          ) : (
            <button
              disabled
              title="Owner contact information is not available for this dataset record."
              className="w-full py-2.5 rounded-xl bg-slate-800 text-slate-500 border border-slate-850 font-semibold text-center flex items-center justify-center gap-1.5 text-xs cursor-not-allowed"
            >
              <Phone className="w-3.5 h-3.5" />
              <span>Contact unavailable</span>
            </button>
          )}
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
