import React from 'react';
import { Building2, MapPin, Globe, Shield, Heart } from 'lucide-react';

export const Footer = () => {
  return (
    <footer className="border-t border-slate-800/80 bg-dark-950 text-slate-400 py-12">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8 mb-12">
          {/* Brand Col */}
          <div className="space-y-4 md:col-span-1">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-lg bg-gradient-to-tr from-brand-600 to-accent-500 flex items-center justify-center">
                <Building2 className="w-4 h-4 text-white" />
              </div>
              <span className="text-lg font-bold text-white font-outfit">Cloud-Based Real Estate Analysis</span>
            </div>
            <p className="text-xs text-slate-400 leading-relaxed">
              Production-ready real estate price intelligence and spatial GIS analytics for Bangalore and top Indian metro localities.
            </p>
          </div>

          {/* Quick Links */}
          <div>
            <h4 className="text-xs uppercase font-bold tracking-widest text-slate-200 mb-4">Supported Hubs</h4>
            <ul className="space-y-2 text-xs">
              <li><span className="hover:text-brand-400 transition-colors">Koramangala</span></li>
              <li><span className="hover:text-brand-400 transition-colors">Indiranagar</span></li>
              <li><span className="hover:text-brand-400 transition-colors">Whitefield</span></li>
              <li><span className="hover:text-brand-400 transition-colors">HSR Layout</span></li>
              <li><span className="hover:text-brand-400 transition-colors">Electronic City</span></li>
            </ul>
          </div>

          {/* Features */}
          <div>
            <h4 className="text-xs uppercase font-bold tracking-widest text-slate-200 mb-4">GIS Intelligence</h4>
            <ul className="space-y-2 text-xs">
              <li>Geoapify Geocoding API</li>
              <li>Geoapify Categorized Places</li>
              <li>OpenStreetMap Layers</li>
              <li>Price per Sq.Ft Estimate</li>
              <li>Nearby Amenities Engine</li>
            </ul>
          </div>

          {/* Contact / Info */}
          <div>
            <h4 className="text-xs uppercase font-bold tracking-widest text-slate-200 mb-4">System Specs</h4>
            <div className="space-y-2 text-xs text-slate-400">
              <p className="flex items-center gap-2">
                <Globe className="w-3.5 h-3.5 text-brand-500" />
                <span>FastAPI + PostgreSQL Backend</span>
              </p>
              <p className="flex items-center gap-2">
                <Shield className="w-3.5 h-3.5 text-accent-500" />
                <span>JWT Authentication Security</span>
              </p>
              <p className="flex items-center gap-2">
                <MapPin className="w-3.5 h-3.5 text-emerald-500" />
                <span>React Leaflet Map Canvas</span>
              </p>
            </div>
          </div>
        </div>

        <div className="pt-8 border-t border-slate-800/60 flex flex-col sm:flex-row items-center justify-between text-xs text-slate-500 gap-4">
          <p>© 2026 Cloud-Based Real Estate Analysis. All rights reserved.</p>
          <p className="flex items-center gap-1">
            Engineered with <Heart className="w-3.5 h-3.5 text-red-500 fill-current" /> for Bangalore GIS Intelligence
          </p>
        </div>
      </div>
    </footer>
  );
};
