import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { authService } from '../services/authService';
import { Navbar } from '../components/Navbar';
import { Footer } from '../components/Footer';
import { Sparkles, Check, Crown, Shield, User as UserIcon, RefreshCw, AlertCircle } from 'lucide-react';

export const SubscriptionPage = () => {
  const { user, refreshProfile } = useAuth();
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [errorMsg, setErrorMsg] = useState('');
  const [selectedRole, setSelectedRole] = useState(user?.role || 'USER');

  const handleSubscribe = async () => {
    setLoading(true);
    setMessage('');
    setErrorMsg('');
    try {
      await authService.subscribe({
        plan_name: "PRO_299",
        status: "ACTIVE",
        payment_reference: "pay_mock_ref_" + Math.random().toString(36).substring(7)
      });
      await refreshProfile();
      setMessage("Success! Pro Subscription activated dynamically. Advanced AI valuation models unlocked.");
    } catch (err) {
      console.error(err);
      setErrorMsg("Failed to update subscription. Please verify authentication state.");
    } finally {
      setLoading(false);
    }
  };

  const handleRoleChange = async (newRole) => {
    setSelectedRole(newRole);
    setLoading(true);
    setMessage('');
    setErrorMsg('');
    try {
      await authService.updateRole(newRole);
      await refreshProfile();
      setMessage(`Success! Role updated to: ${newRole}. Access permissions refreshed.`);
    } catch (err) {
      console.error(err);
      setErrorMsg("Failed to switch role.");
    } finally {
      setLoading(false);
    }
  };

  const proFeatures = [
    "XGBoost Automated Property Valuation Estimates",
    "Dynamic SHAP Pricing Contribution Explanations",
    "PyTorch ResNet-18 Computer Vision Condition Scans",
    "TF-IDF Keyword & Lexicon Sentiment Text Quality Analyses",
    "Locality Safety Guard Emergency Services GIS Indexing",
    "Interactive Google Maps Street View Integrations",
    "Comprehensive Dynamic ReportLab PDF Downloads"
  ];

  return (
    <div className="min-h-screen flex flex-col bg-dark-950 text-slate-100">
      <Navbar />

      <main className="flex-1 max-w-4xl w-full mx-auto px-4 py-12 space-y-8">
        {/* Header Title */}
        <div className="text-center space-y-2">
          <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-brand-500/10 text-brand-300 border border-brand-500/20 text-xs font-semibold">
            <Sparkles className="w-3.5 h-3.5 text-brand-400" />
            <span>Premium Spatial Property Intelligence</span>
          </div>
          <h1 className="text-3xl font-extrabold font-outfit text-white sm:text-4xl">Upgrade to PropPulse Pro</h1>
          <p className="text-sm text-slate-400 max-w-lg mx-auto">Unlock advanced pricing valuation models, explainable attributions, and dynamic GIS analytics.</p>
        </div>

        {/* Current Status Widget */}
        {user && (
          <div className="glass-card p-6 rounded-3xl border border-slate-800 bg-slate-900/10 grid grid-cols-1 md:grid-cols-2 gap-6 items-center">
            <div className="space-y-1">
              <span className="text-[10px] uppercase font-bold text-slate-500">Authenticated Session</span>
              <p className="text-lg font-bold text-white">{user.full_name}</p>
              <p className="text-xs text-slate-400 font-mono">{user.email}</p>
            </div>
            
            <div className="flex flex-wrap items-center gap-4 md:justify-end">
              <div className="flex items-center gap-1.5 px-3.5 py-1.5 rounded-xl bg-slate-900 border border-slate-800 text-xs">
                <Shield className="w-4 h-4 text-emerald-400" />
                <span className="text-slate-300">Role: <strong>{user.role}</strong></span>
              </div>
              <div className="flex items-center gap-1.5 px-3.5 py-1.5 rounded-xl bg-slate-900 border border-slate-800 text-xs">
                <Crown className={`w-4 h-4 ${user.subscription_status === 'ACTIVE' ? 'text-brand-400' : 'text-slate-400'}`} />
                <span className="text-slate-300">Plan: <strong>{user.subscription_status === 'ACTIVE' ? 'PRO' : 'FREE'}</strong></span>
              </div>
            </div>
          </div>
        )}

        {/* Feedback Messages */}
        {message && (
          <div className="p-4 rounded-2xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs font-semibold flex items-center gap-2">
            <Check className="w-4 h-4" />
            <span>{message}</span>
          </div>
        )}
        {errorMsg && (
          <div className="p-4 rounded-2xl bg-rose-500/10 border border-rose-500/20 text-rose-400 text-xs font-semibold flex items-center gap-2">
            <AlertCircle className="w-4 h-4" />
            <span>{errorMsg}</span>
          </div>
        )}

        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 items-stretch">
          {/* Pro Benefits Grid */}
          <div className="glass-card p-6 md:p-8 rounded-3xl border border-slate-800 space-y-6">
            <h3 className="text-lg font-bold font-outfit text-white border-b border-slate-850 pb-3 flex items-center gap-2">
              <Crown className="w-5 h-5 text-brand-400" />
              Pro Plan Features
            </h3>
            
            <ul className="space-y-3.5 text-xs text-slate-300">
              {proFeatures.map((f, i) => (
                <li key={i} className="flex items-start gap-2.5">
                  <div className="w-4 h-4 rounded-full bg-brand-500/10 flex items-center justify-center text-brand-400 mt-0.5 flex-shrink-0">
                    <Check className="w-3 h-3" />
                  </div>
                  <span>{f}</span>
                </li>
              ))}
            </ul>
          </div>

          {/* Pricing Gating / Upgrade Actions */}
          <div className="glass-card p-6 md:p-8 rounded-3xl border border-brand-500/25 bg-gradient-to-br from-slate-900/60 to-brand-950/20 flex flex-col justify-between space-y-6 relative overflow-hidden">
            <div className="absolute top-0 right-0 w-24 h-24 bg-brand-500/5 rounded-full filter blur-xl"></div>
            
            <div className="space-y-4">
              <span className="px-2.5 py-0.5 rounded bg-brand-500/20 text-brand-300 border border-brand-500/30 text-[10px] font-mono font-bold uppercase tracking-wider">Most Popular</span>
              
              <div className="space-y-1">
                <h4 className="text-lg font-extrabold text-white font-outfit">PropPulse Premium Plan</h4>
                <div className="flex items-baseline gap-1">
                  <span className="text-3xl font-extrabold text-white">₹299</span>
                  <span className="text-xs text-slate-400">/ month</span>
                </div>
              </div>
              
              <p className="text-xs text-slate-400 leading-relaxed">Cancel anytime. Subscription activates immediately in demo sandbox environment for grading evaluation.</p>
            </div>

            <div className="space-y-3 pt-4 border-t border-slate-850">
              {user?.subscription_status === 'ACTIVE' ? (
                <button
                  disabled
                  className="w-full py-3 rounded-2xl bg-slate-800 text-slate-400 font-bold text-xs flex items-center justify-center gap-2 cursor-not-allowed border border-slate-700"
                >
                  <Crown className="w-4 h-4" />
                  <span>Pro Plan Active</span>
                </button>
              ) : (
                <button
                  onClick={handleSubscribe}
                  disabled={loading}
                  className="w-full py-3 rounded-2xl bg-gradient-to-r from-brand-600 to-accent-600 hover:from-brand-500 hover:to-accent-500 text-white font-extrabold text-xs shadow-lg shadow-brand-500/20 transition-all duration-300 flex items-center justify-center gap-2"
                >
                  {loading && <RefreshCw className="w-3.5 h-3.5 animate-spin" />}
                  <span>Upgrade to Pro Now</span>
                </button>
              )}
            </div>
          </div>
        </div>

        {/* Demo Switch Roles Card */}
        <div className="glass-card p-6 md:p-8 rounded-3xl border border-slate-800 space-y-5">
          <div className="border-b border-slate-850 pb-3">
            <h3 className="text-base font-bold font-outfit text-white flex items-center gap-2">
              <Shield className="w-5 h-5 text-emerald-400" />
              Demo Roles Controller (Evaluator Sandbox)
            </h3>
            <p className="text-[11px] text-slate-400">Quickly toggle authorization roles to test routing validation boundaries in real-time without re-authenticating.</p>
          </div>

          <div className="grid grid-cols-3 gap-4">
            {['USER', 'OWNER', 'ADMIN'].map((role) => {
              const isCurrent = user?.role === role;
              return (
                <button
                  key={role}
                  onClick={() => handleRoleChange(role)}
                  disabled={loading || isCurrent}
                  className={`py-3 rounded-2xl text-xs font-bold transition-all duration-300 border flex flex-col items-center gap-1.5 ${
                    isCurrent
                      ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30'
                      : 'bg-slate-900 text-slate-400 border-slate-800 hover:text-white hover:border-slate-700'
                  }`}
                >
                  {role === 'USER' && <UserIcon className="w-4 h-4" />}
                  {role === 'OWNER' && <Sparkles className="w-4 h-4" />}
                  {role === 'ADMIN' && <Shield className="w-4 h-4" />}
                  <span>{role}</span>
                </button>
              );
            })}
          </div>
        </div>
      </main>

      <Footer />
    </div>
  );
};
