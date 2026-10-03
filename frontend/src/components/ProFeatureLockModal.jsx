import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Crown, Sparkles, X, Check, ArrowRight } from 'lucide-react';

export const ProFeatureLockModal = ({ isOpen, onClose, featureName = "Premium AI Intelligence" }) => {
  const navigate = useNavigate();

  if (!isOpen) return null;

  const handleUpgrade = () => {
    onClose && onClose();
    navigate('/subscription');
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm animate-fadeIn">
      <div className="relative w-full max-w-md bg-dark-900 border border-brand-500/30 rounded-3xl p-6 md:p-8 shadow-2xl shadow-brand-500/10 text-white space-y-6">
        {/* Close Button */}
        <button
          onClick={onClose}
          className="absolute top-5 right-5 p-2 rounded-xl text-slate-400 hover:text-white hover:bg-slate-800 transition-colors"
          aria-label="Close modal"
        >
          <X className="w-5 h-5" />
        </button>

        {/* Icon & Badges */}
        <div className="flex flex-col items-center text-center space-y-3">
          <div className="w-14 h-14 rounded-2xl bg-gradient-to-tr from-brand-600 to-amber-500 flex items-center justify-center shadow-lg shadow-brand-500/20">
            <Crown className="w-7 h-7 text-white" />
          </div>
          
          <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-brand-500/10 border border-brand-500/20 text-brand-300 text-xs font-semibold">
            <Sparkles className="w-3.5 h-3.5 text-brand-400" />
            <span>PropPulse Pro Feature</span>
          </div>

          <h2 className="text-2xl font-black font-outfit tracking-tight text-white">
            PropPulse Pro Required
          </h2>
          <p className="text-sm text-slate-400 max-w-xs">
            This feature is available with the Pro plan.
          </p>
        </div>

        {/* Feature Context */}
        <div className="p-4 rounded-2xl bg-slate-950/60 border border-slate-800/80 space-y-2.5 text-xs text-slate-300">
          <div className="font-semibold text-slate-200 flex items-center gap-1.5">
            <span className="text-brand-400">•</span> Feature: {featureName}
          </div>
          <div className="flex items-center gap-2 text-slate-400">
            <Check className="w-4 h-4 text-emerald-400 flex-shrink-0" />
            <span>544-D Multimodal Valuation, SHAP & ResNet-18</span>
          </div>
          <div className="flex items-center gap-2 text-slate-400">
            <Check className="w-4 h-4 text-emerald-400 flex-shrink-0" />
            <span>AI Voice Telephone Assistant & Instant Owner Callback</span>
          </div>
          <div className="flex items-center gap-2 text-slate-400">
            <Check className="w-4 h-4 text-emerald-400 flex-shrink-0" />
            <span>High-fidelity Bank Comparison & PDF Reports</span>
          </div>
        </div>

        {/* Pricing & CTA */}
        <div className="space-y-3 pt-2">
          <div className="flex items-baseline justify-center gap-1 text-center">
            <span className="text-3xl font-extrabold text-white">₹299</span>
            <span className="text-xs text-slate-400 font-medium">/ month</span>
          </div>

          <div className="flex gap-3">
            <button
              onClick={onClose}
              className="flex-1 py-3 rounded-2xl border border-slate-800 hover:border-slate-700 bg-slate-900/60 text-slate-300 text-xs font-bold transition-colors"
            >
              Cancel
            </button>
            <button
              onClick={handleUpgrade}
              className="flex-1 py-3 rounded-2xl bg-gradient-to-r from-brand-600 to-amber-600 hover:from-brand-500 hover:to-amber-500 text-white text-xs font-extrabold shadow-lg shadow-brand-500/20 transition-all flex items-center justify-center gap-1.5"
            >
              <span>Upgrade to Pro</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export const ProFeatureLockCard = ({ featureName = "AI Multimodal Valuation", description }) => {
  const navigate = useNavigate();

  return (
    <div className="glass-card p-6 md:p-8 rounded-3xl border border-brand-500/30 bg-gradient-to-b from-dark-900/90 to-brand-950/20 text-center space-y-5 my-4">
      <div className="w-12 h-12 mx-auto rounded-2xl bg-brand-500/10 border border-brand-500/20 flex items-center justify-center text-brand-400">
        <Crown className="w-6 h-6" />
      </div>

      <div className="space-y-1">
        <h3 className="text-xl font-black font-outfit text-white">
          PropPulse Pro Required
        </h3>
        <p className="text-xs text-slate-400 max-w-md mx-auto">
          {description || "This feature is available with the Pro plan."}
        </p>
      </div>

      <div className="flex items-baseline justify-center gap-1">
        <span className="text-2xl font-extrabold text-white">₹299</span>
        <span className="text-xs text-slate-400">/ month</span>
      </div>

      <div>
        <button
          onClick={() => navigate('/subscription')}
          className="inline-flex items-center gap-2 px-6 py-3 rounded-2xl bg-gradient-to-r from-brand-600 to-amber-600 hover:from-brand-500 hover:to-amber-500 text-white text-xs font-extrabold shadow-lg shadow-brand-500/20 transition-all"
        >
          <Crown className="w-4 h-4" />
          <span>Upgrade to Pro</span>
        </button>
      </div>
    </div>
  );
};
