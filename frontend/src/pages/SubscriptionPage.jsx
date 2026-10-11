import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { authService } from '../services/authService';
import { subscriptionService } from '../services/subscriptionService';
import { Navbar } from '../components/Navbar';
import { Footer } from '../components/Footer';
import { 
  Sparkles, Check, Crown, Shield, User as UserIcon, RefreshCw, 
  AlertCircle, Calendar, CreditCard, CheckCircle2, XCircle, ExternalLink 
} from 'lucide-react';

export const SubscriptionPage = () => {
  const { user, refreshProfile } = useAuth();
  const [loading, setLoading] = useState(false);
  const [cancelling, setCancelling] = useState(false);
  const [message, setMessage] = useState('');
  const [errorMsg, setErrorMsg] = useState('');
  const [config, setConfig] = useState(null);
  const [subData, setSubData] = useState(null);

  // Load gateway config and current user's live subscription details
  const fetchSubscriptionDetails = async () => {
    try {
      const cfg = await subscriptionService.getConfig();
      setConfig(cfg);
    } catch (e) {
      console.warn("Failed to load subscription config:", e);
    }

    if (user) {
      try {
        const sub = await subscriptionService.getMySubscription();
        setSubData(sub);
      } catch (e) {
        console.warn("Failed to load subscription details:", e);
      }
    }
  };

  useEffect(() => {
    fetchSubscriptionDetails();
  }, [user]);

  // Dynamically load Razorpay script
  const loadRazorpayScript = () => {
    return new Promise((resolve) => {
      if (window.Razorpay) {
        resolve(true);
        return;
      }
      const script = document.createElement('script');
      script.src = 'https://checkout.razorpay.com/v1/checkout.js';
      script.onload = () => resolve(true);
      script.onerror = () => resolve(false);
      document.body.appendChild(script);
    });
  };

  const handleSubscribe = async () => {
    setLoading(true);
    setMessage('');
    setErrorMsg('');

    // Check gateway configuration requirement (Rule 13)
    if (!config?.gateway_configured) {
      setErrorMsg("Payment gateway not configured. Normal FREE functionality remains active.");
      setLoading(false);
      return;
    }

    try {
      const scriptLoaded = await loadRazorpayScript();
      if (!scriptLoaded) {
        setErrorMsg("Failed to load Razorpay checkout SDK. Please verify internet connectivity.");
        setLoading(false);
        return;
      }

      // 1. Create order on server (server enforces ₹299 = 29900 paise)
      const order = await subscriptionService.createOrder();

      // 2. Open Razorpay Checkout modal
      const options = {
        key: order.razorpay_key_id,
        amount: order.amount,
        currency: order.currency,
        name: "Cloud-Based Real Estate Analysis",
        description: "PropPulse Pro Monthly Subscription",
        order_id: order.razorpay_order_id,
        prefill: {
          name: user?.full_name || "",
          email: user?.email || "",
          contact: user?.phone || ""
        },
        theme: {
          color: "#4f46e5"
        },
        handler: async (response) => {
          try {
            setLoading(true);
            setMessage("Verifying payment signature securely with server...");
            
            // 3. Server-side signature verification (Rule 4: Never trust client success)
            const verifyRes = await subscriptionService.verifyPayment({
              razorpay_order_id: response.razorpay_order_id,
              razorpay_payment_id: response.razorpay_payment_id,
              razorpay_signature: response.razorpay_signature
            });

            if (verifyRes.status === "ACTIVE" || verifyRes.plan === "PRO") {
              setMessage("Payment verified successfully! PropPulse Pro is now active.");
              await refreshProfile();
              await fetchSubscriptionDetails();
            } else {
              setErrorMsg("Payment verification completed with unexpected status.");
            }
          } catch (err) {
            console.error("Verification error:", err);
            setErrorMsg(err.response?.data?.detail || "Payment verification failed. Please contact support.");
          } finally {
            setLoading(false);
          }
        },
        modal: {
          ondismiss: () => {
            setLoading(false);
          }
        }
      };

      const razorpayInstance = new window.Razorpay(options);
      razorpayInstance.on('payment.failed', function (resp) {
        setErrorMsg(`Payment failed: ${resp.error.description || resp.error.reason}`);
        setLoading(false);
      });
      razorpayInstance.open();

    } catch (err) {
      console.error("Order creation failed:", err);
      const detail = err.response?.data?.detail;
      setErrorMsg(typeof detail === 'string' ? detail : "Failed to initiate subscription order.");
      setLoading(false);
    }
  };

  const handleCancelSubscription = async () => {
    if (!window.confirm("Are you sure you want to cancel your PropPulse Pro subscription? You will lose access to premium AI features upon expiration.")) {
      return;
    }
    setCancelling(true);
    setMessage('');
    setErrorMsg('');
    try {
      await subscriptionService.cancelSubscription();
      setMessage("Subscription has been cancelled.");
      await refreshProfile();
      await fetchSubscriptionDetails();
    } catch (err) {
      console.error(err);
      setErrorMsg(err.response?.data?.detail || "Failed to cancel subscription.");
    } finally {
      setCancelling(false);
    }
  };

  const isProActive = subData?.is_active || (user?.role === 'ADMIN');
  const currentPlan = isProActive ? 'PRO' : (subData?.plan || 'FREE');
  const subscriptionStatus = subData?.subscription_status || (user?.role === 'ADMIN' ? 'ACTIVE' : 'FREE');

  const proFeatures = [
    "544-D Multimodal XGBoost Valuation Estimates",
    "Dynamic SHAP Pricing Contribution Explanations",
    "PyTorch ResNet-18 Computer Vision Condition Scans",
    "TF-IDF Keyword & Lexicon Sentiment Text Quality Analyses",
    "Advanced Geoapify GIS / POI Spatial Metrics",
    "Interactive Home Loan & Multi-Bank Mortgage Comparison",
    "AI Voice Property Assistant / Contact Owner Telephone Callback",
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
          <h1 className="text-3xl font-extrabold font-outfit text-white sm:text-4xl">PROPULSE PRO</h1>
          <p className="text-sm text-slate-400 max-w-lg mx-auto">
            Unlock advanced 544-D multimodal valuation, SHAP explainability, AI telephone callbacks, and bank comparisons.
          </p>
        </div>

        {/* Feedback Messages */}
        {message && (
          <div className="p-4 rounded-2xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs font-semibold flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4 flex-shrink-0" />
            <span>{message}</span>
          </div>
        )}
        {errorMsg && (
          <div className="p-4 rounded-2xl bg-rose-500/10 border border-rose-500/20 text-rose-400 text-xs font-semibold flex items-center gap-2">
            <AlertCircle className="w-4 h-4 flex-shrink-0" />
            <span>{errorMsg}</span>
          </div>
        )}

        {/* Gateway Configuration Alert if not configured */}
        {config && !config.gateway_configured && (
          <div className="p-4 rounded-2xl bg-amber-500/10 border border-amber-500/20 text-amber-300 text-xs flex items-center justify-between gap-4">
            <div className="flex items-center gap-2">
              <AlertCircle className="w-4 h-4 text-amber-400 flex-shrink-0" />
              <span>Payment gateway not configured. Razorpay credentials pending in environment.</span>
            </div>
            <span className="px-2 py-0.5 rounded bg-amber-500/20 text-[10px] font-mono font-bold uppercase">FREE Mode Active</span>
          </div>
        )}

        {/* Current Subscription Status Card */}
        {user && (
          <div className="glass-card p-6 md:p-8 rounded-3xl border border-slate-800 bg-slate-900/30 space-y-6">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-800 pb-5">
              <div>
                <span className="text-[10px] uppercase font-bold text-slate-500 tracking-wider">Subscriber Profile</span>
                <p className="text-lg font-bold text-white">{user.full_name}</p>
                <p className="text-xs text-slate-400 font-mono">{user.email}</p>
              </div>

              <div className="flex flex-wrap items-center gap-3">
                <div className="flex items-center gap-1.5 px-3.5 py-1.5 rounded-xl bg-slate-900 border border-slate-800 text-xs">
                  <Shield className="w-4 h-4 text-emerald-400" />
                  <span className="text-slate-300">Role: <strong>{user.role}</strong></span>
                </div>
                <div className={`flex items-center gap-1.5 px-3.5 py-1.5 rounded-xl border text-xs font-semibold ${
                  isProActive
                    ? 'bg-brand-500/10 border-brand-500/30 text-brand-300'
                    : 'bg-slate-900 border-slate-800 text-slate-400'
                }`}>
                  <Crown className={`w-4 h-4 ${isProActive ? 'text-brand-400' : 'text-slate-400'}`} />
                  <span>Plan: <strong>{currentPlan}</strong></span>
                </div>
                <div className={`flex items-center gap-1.5 px-3.5 py-1.5 rounded-xl border text-xs font-semibold ${
                  subscriptionStatus === 'ACTIVE'
                    ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-300'
                    : 'bg-slate-900 border-slate-800 text-slate-400'
                }`}>
                  <span>Status: <strong>{subscriptionStatus}</strong></span>
                </div>
              </div>
            </div>

            {/* Subscription Period & Reference Metadata */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 text-xs">
              <div className="p-3.5 rounded-2xl bg-slate-950/60 border border-slate-800/80 space-y-1">
                <div className="flex items-center gap-1.5 text-slate-400">
                  <Calendar className="w-3.5 h-3.5 text-brand-400" />
                  <span>Activation Date</span>
                </div>
                <p className="font-semibold text-slate-200">
                  {subData?.start_date ? new Date(subData.start_date).toLocaleDateString() : 'N/A'}
                </p>
              </div>

              <div className="p-3.5 rounded-2xl bg-slate-950/60 border border-slate-800/80 space-y-1">
                <div className="flex items-center gap-1.5 text-slate-400">
                  <Calendar className="w-3.5 h-3.5 text-amber-400" />
                  <span>Expiry / Next Billing</span>
                </div>
                <p className="font-semibold text-slate-200">
                  {subData?.end_date ? new Date(subData.end_date).toLocaleDateString() : (isProActive ? 'Active Plan' : 'N/A')}
                </p>
              </div>

              <div className="p-3.5 rounded-2xl bg-slate-950/60 border border-slate-800/80 space-y-1">
                <div className="flex items-center gap-1.5 text-slate-400">
                  <CreditCard className="w-3.5 h-3.5 text-emerald-400" />
                  <span>Payment Reference</span>
                </div>
                <p className="font-mono text-[11px] text-slate-300 truncate" title={subData?.razorpay_payment_id || subData?.payment_reference || 'N/A'}>
                  {subData?.razorpay_payment_id || subData?.payment_reference || 'N/A'}
                </p>
              </div>

              <div className="p-3.5 rounded-2xl bg-slate-950/60 border border-slate-800/80 space-y-1">
                <div className="flex items-center gap-1.5 text-slate-400">
                  <Crown className="w-3.5 h-3.5 text-brand-400" />
                  <span>Entitled Rate</span>
                </div>
                <p className="font-semibold text-slate-200">
                  {config?.display_price || '₹299/month'}
                </p>
              </div>
            </div>

            {/* Manage / Cancel Action */}
            {isProActive && user?.role !== 'ADMIN' && (
              <div className="pt-2 flex justify-end">
                <button
                  onClick={handleCancelSubscription}
                  disabled={cancelling}
                  className="px-4 py-2 rounded-xl border border-rose-500/30 bg-rose-500/10 hover:bg-rose-500/20 text-rose-300 text-xs font-semibold transition-colors flex items-center gap-1.5"
                >
                  {cancelling && <RefreshCw className="w-3.5 h-3.5 animate-spin" />}
                  <span>Manage / Cancel Subscription</span>
                </button>
              </div>
            )}
          </div>
        )}

        {/* Pricing Plan & Feature Grid */}
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
              <span className="px-2.5 py-0.5 rounded bg-brand-500/20 text-brand-300 border border-brand-500/30 text-[10px] font-mono font-bold uppercase tracking-wider">
                Official Plan
              </span>
              
              <div className="space-y-1">
                <h4 className="text-xl font-extrabold text-white font-outfit">PROPULSE PRO</h4>
                <div className="flex items-baseline gap-1">
                  <span className="text-4xl font-extrabold text-white">₹299</span>
                  <span className="text-xs text-slate-400">/ month</span>
                </div>
              </div>
              
              <p className="text-xs text-slate-400 leading-relaxed">
                Full access to multimodal pricing, SHAP explainability, real outbound Twilio AI callback, and mortgage comparisons. Cancel anytime.
              </p>
            </div>

            <div className="space-y-3 pt-4 border-t border-slate-850">
              {isProActive ? (
                <div className="p-3.5 rounded-2xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 font-bold text-xs flex items-center justify-center gap-2">
                  <Crown className="w-4 h-4 text-emerald-400" />
                  <span>Pro Plan Active</span>
                </div>
              ) : (
                <button
                  onClick={handleSubscribe}
                  disabled={loading}
                  className="w-full py-3.5 rounded-2xl bg-gradient-to-r from-brand-600 to-amber-600 hover:from-brand-500 hover:to-amber-500 text-white font-extrabold text-xs shadow-lg shadow-brand-500/20 transition-all duration-300 flex items-center justify-center gap-2"
                >
                  {loading && <RefreshCw className="w-3.5 h-3.5 animate-spin" />}
                  <span>Upgrade to Pro</span>
                </button>
              )}
            </div>
          </div>
        </div>
      </main>

      <Footer />
    </div>
  );
};
