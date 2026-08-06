import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { 
  Building2, MapPin, Bed, Maximize2, Phone, Sparkles, 
  Eye, Compass, CheckCircle2, User, MessageSquare, X 
} from 'lucide-react';

export const PropertyCard = ({ property, onSelectOnMap }) => {
  const [showContactModal, setShowContactModal] = useState(false);
  const [messageSent, setMessageSent] = useState(false);

  const defaultImage = "https://images.unsplash.com/photo-1545324418-cc1a3fa10c00?auto=format&fit=crop&w=800&q=80";
  const mainImage = (property.images && property.images.length > 0) ? property.images[0] : defaultImage;

  const nearbyCount = property.nearby_places ? property.nearby_places.length : 0;

  return (
    <>
      <div className="glass-card glass-card-hover rounded-3xl overflow-hidden border border-slate-800 flex flex-col justify-between group">
        <div>
          {/* Image Canvas */}
          <div className="relative aspect-[16/10] overflow-hidden bg-slate-900">
            <img 
              src={mainImage} 
              alt={property.title} 
              className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500" 
            />
            <div className="absolute inset-0 bg-gradient-to-t from-dark-950 via-transparent to-transparent opacity-80"></div>
            
            {/* Property Type Badge */}
            <div className="absolute top-3 left-3 flex items-center gap-1.5 px-3 py-1 rounded-full bg-dark-950/80 backdrop-blur-md border border-slate-700/80 text-xs font-bold text-brand-300">
              <Building2 className="w-3.5 h-3.5 text-brand-400" />
              <span>{property.property_type}</span>
            </div>

            {/* Price Badge */}
            <div className="absolute bottom-3 left-3 right-3 flex items-center justify-between">
              <div className="bg-slate-900/90 backdrop-blur-md px-3.5 py-1.5 rounded-2xl border border-brand-500/40 text-emerald-400 font-extrabold text-base">
                {property.price_formatted}
              </div>
              <span className="text-[10px] bg-slate-950/80 text-slate-300 px-2 py-1 rounded-lg border border-slate-800 font-mono">
                ₹{property.price_per_sqft} / sq.ft
              </span>
            </div>
          </div>

          {/* Details Body */}
          <div className="p-5 space-y-3">
            <h3 className="text-base font-bold text-white line-clamp-1 group-hover:text-brand-300 transition-colors font-outfit">
              {property.title}
            </h3>

            <p className="text-xs text-slate-400 flex items-center gap-1.5 line-clamp-1">
              <MapPin className="w-3.5 h-3.5 text-brand-400 flex-shrink-0" />
              <span>{property.address}</span>
            </p>

            {/* Spec Icons Grid */}
            <div className="grid grid-cols-3 gap-2 pt-2 border-t border-slate-800/60 text-xs text-slate-300">
              <div className="flex items-center gap-1.5 bg-slate-900/60 px-2.5 py-1.5 rounded-xl border border-slate-800">
                <Bed className="w-3.5 h-3.5 text-brand-400" />
                <span>{property.bhk} BHK</span>
              </div>
              <div className="flex items-center gap-1.5 bg-slate-900/60 px-2.5 py-1.5 rounded-xl border border-slate-800">
                <Maximize2 className="w-3.5 h-3.5 text-accent-400" />
                <span>{property.area_sqft} sq.ft</span>
              </div>
              <div className="flex items-center gap-1.5 bg-slate-900/60 px-2.5 py-1.5 rounded-xl border border-slate-800">
                <Sparkles className="w-3.5 h-3.5 text-emerald-400" />
                <span>{nearbyCount} Places</span>
              </div>
            </div>

            {/* Owner Info */}
            <div className="flex items-center justify-between text-xs text-slate-400 pt-1">
              <span className="flex items-center gap-1 text-slate-300">
                <User className="w-3.5 h-3.5 text-brand-400" />
                <strong className="font-semibold text-slate-200">{property.owner_name}</strong>
              </span>
              <a 
                href={`tel:${property.owner_phone}`} 
                className="text-emerald-400 font-mono hover:underline flex items-center gap-1"
              >
                <Phone className="w-3 h-3" />
                <span>{property.owner_phone}</span>
              </a>
            </div>
          </div>
        </div>

        {/* Card Actions Footer */}
        <div className="p-4 border-t border-slate-800/80 bg-slate-900/40 grid grid-cols-2 gap-2 text-xs">
          <Link
            to={`/properties/${property.id}`}
            className="px-3 py-2 rounded-xl bg-brand-600 hover:bg-brand-500 text-white font-semibold text-center flex items-center justify-center gap-1.5 transition-all shadow-md shadow-brand-500/20"
          >
            <Eye className="w-3.5 h-3.5" />
            <span>View Details</span>
          </Link>

          <a
            href={`tel:${property.owner_phone}`}
            className="px-3 py-2 rounded-xl bg-emerald-500/10 hover:bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 font-semibold text-center flex items-center justify-center gap-1.5 transition-all"
          >
            <Phone className="w-3.5 h-3.5" />
            <span>Call Owner</span>
          </a>

          <button
            onClick={() => setShowContactModal(true)}
            className="px-3 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 font-semibold text-center flex items-center justify-center gap-1.5 transition-all"
          >
            <MessageSquare className="w-3.5 h-3.5 text-brand-400" />
            <span>Contact Owner</span>
          </button>

          {onSelectOnMap ? (
            <button
              onClick={() => onSelectOnMap(property)}
              className="px-3 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 font-semibold text-center flex items-center justify-center gap-1.5 transition-all"
            >
              <Compass className="w-3.5 h-3.5 text-accent-400" />
              <span>View on Map</span>
            </button>
          ) : (
            <Link
              to={`/analytics/${property.id}`}
              className="px-3 py-2 rounded-xl bg-accent-500/10 hover:bg-accent-500/20 text-accent-300 border border-accent-500/30 font-semibold text-center flex items-center justify-center gap-1.5 transition-all"
            >
              <Sparkles className="w-3.5 h-3.5" />
              <span>AI Dashboard</span>
            </Link>
          )}
        </div>
      </div>

      {/* Owner Contact Modal */}
      {showContactModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-dark-950/80 backdrop-blur-md">
          <div className="glass-card w-full max-w-md p-6 rounded-3xl border border-slate-800 space-y-4 relative shadow-2xl">
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
              <p className="text-xs text-slate-400">Directly inquiry for: <strong className="text-slate-200">{property.title}</strong></p>
            </div>

            <div className="p-3 rounded-2xl bg-slate-900 border border-slate-800 space-y-1 text-xs">
              <p className="font-semibold text-white">Owner: {property.owner_name}</p>
              <p className="text-emerald-400 font-mono">Phone: {property.owner_phone}</p>
              <p className="text-slate-400">Location: {property.address}</p>
            </div>

            {messageSent ? (
              <div className="p-4 rounded-2xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-xs flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 flex-shrink-0" />
                <span>Your contact request has been sent to {property.owner_name}. They will call back shortly!</span>
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
                  <input required type="text" placeholder="Enter your full name" className="w-full px-3 py-2 rounded-xl bg-slate-900 border border-slate-800 text-xs text-white" />
                </div>
                <div>
                  <label className="text-xs font-semibold text-slate-300 block mb-1">Your Phone Number</label>
                  <input required type="tel" placeholder="+91 98765 43210" className="w-full px-3 py-2 rounded-xl bg-slate-900 border border-slate-800 text-xs text-white" />
                </div>
                <div>
                  <label className="text-xs font-semibold text-slate-300 block mb-1">Inquiry Message</label>
                  <textarea rows={3} defaultValue={`Hi ${property.owner_name}, I am interested in viewing your property '${property.title}'. Please share availability.`} className="w-full px-3 py-2 rounded-xl bg-slate-900 border border-slate-800 text-xs text-white" />
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
