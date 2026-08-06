import React from 'react';
import { Building2, Home, IndianRupee, ShieldCheck, Sparkles, TrendingUp } from 'lucide-react';

export const LocalityStatsCard = ({ stats }) => {
  if (!stats) return null;

  return (
    <div className="glass-card p-6 rounded-3xl border border-slate-800 space-y-4">
      <div className="flex items-center justify-between border-b border-slate-800 pb-3">
        <div>
          <h3 className="text-base font-bold text-white font-outfit flex items-center gap-2">
            <TrendingUp className="w-5 h-5 text-brand-500" />
            {stats.locality} Market AI Statistics & Analytics
          </h3>
          <p className="text-xs text-slate-400">Locality market benchmark values, safety index, and amenity distribution</p>
        </div>
        <span className="text-xs font-semibold px-3 py-1 rounded-full bg-brand-500/10 text-brand-300 border border-brand-500/20">
          {stats.total_properties} Locality Listings
        </span>
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
        {/* Stat 1: Apartments */}
        <div className="p-3.5 rounded-2xl bg-slate-900/80 border border-slate-800/80 space-y-1">
          <div className="flex items-center gap-1.5 text-xs text-slate-400">
            <Building2 className="w-4 h-4 text-brand-400" />
            <span>Apartments</span>
          </div>
          <p className="text-xl font-extrabold text-white">{stats.num_apartments}</p>
        </div>

        {/* Stat 2: Villas */}
        <div className="p-3.5 rounded-2xl bg-slate-900/80 border border-slate-800/80 space-y-1">
          <div className="flex items-center gap-1.5 text-xs text-slate-400">
            <Home className="w-4 h-4 text-accent-400" />
            <span>Villas</span>
          </div>
          <p className="text-xl font-extrabold text-white">{stats.num_villas}</p>
        </div>

        {/* Stat 3: Avg Selling Price */}
        <div className="p-3.5 rounded-2xl bg-slate-900/80 border border-brand-500/30 space-y-1">
          <div className="flex items-center gap-1.5 text-xs text-slate-400">
            <IndianRupee className="w-4 h-4 text-emerald-400" />
            <span>Average Price</span>
          </div>
          <p className="text-base font-extrabold text-emerald-400">{stats.avg_price_formatted}</p>
        </div>

        {/* Stat 4: Avg Monthly Rent */}
        <div className="p-3.5 rounded-2xl bg-slate-900/80 border border-accent-500/30 space-y-1">
          <div className="flex items-center gap-1.5 text-xs text-slate-400">
            <IndianRupee className="w-4 h-4 text-accent-400" />
            <span>Average Rent</span>
          </div>
          <p className="text-base font-extrabold text-accent-400">{stats.avg_rental_formatted}</p>
        </div>

        {/* Stat 5: Safety Score */}
        <div className="p-3.5 rounded-2xl bg-slate-900/80 border border-emerald-500/30 space-y-1">
          <div className="flex items-center gap-1.5 text-xs text-slate-400">
            <ShieldCheck className="w-4 h-4 text-emerald-400" />
            <span>Safety Score</span>
          </div>
          <p className="text-xl font-extrabold text-emerald-400">{stats.safety_score} / 100</p>
        </div>

        {/* Stat 6: Amenities Score */}
        <div className="p-3.5 rounded-2xl bg-slate-900/80 border border-purple-500/30 space-y-1">
          <div className="flex items-center gap-1.5 text-xs text-slate-400">
            <Sparkles className="w-4 h-4 text-purple-400" />
            <span>Amenities Score</span>
          </div>
          <p className="text-xl font-extrabold text-purple-400">{stats.amenities_score} / 100</p>
        </div>
      </div>
    </div>
  );
};
