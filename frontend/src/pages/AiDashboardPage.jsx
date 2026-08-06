import React, { useEffect, useState } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { aiService } from '../services/aiService';
import { Navbar } from '../components/Navbar';
import { Footer } from '../components/Footer';
import { MapView } from '../components/MapView';
import { NearbyPlacesList } from '../components/NearbyPlacesList';
import { 
  Sparkles, Brain, Eye, FileText, ShieldAlert, 
  TrendingUp, IndianRupee, Download, ArrowLeft, Loader2, 
  CheckCircle2, AlertTriangle, Cpu, Layers, Compass, ThumbsUp, ThumbsDown
} from 'lucide-react';

export const AiDashboardPage = () => {
  const { id } = useParams();
  const propertyId = id || 1;
  const navigate = useNavigate();

  const [aiData, setAiData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [downloadingPdf, setDownloadingPdf] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');

  useEffect(() => {
    fetchAiAnalytics();
  }, [propertyId]);

  const fetchAiAnalytics = async () => {
    setLoading(true);
    try {
      const data = await aiService.analyzeProperty(propertyId);
      setAiData(data);
    } catch (err) {
      console.error("Failed to load AI analytics:", err);
      setErrorMsg("Failed to run AI Analytics suite for this property.");
    } finally {
      setLoading(false);
    }
  };

  const handleDownloadPdf = async () => {
    setDownloadingPdf(true);
    try {
      await aiService.downloadPdfReport(propertyId);
    } catch (err) {
      console.error("PDF download failed:", err);
    } finally {
      setDownloadingPdf(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-dark-950">
        <div className="flex flex-col items-center gap-4">
          <div className="w-14 h-14 rounded-2xl bg-gradient-to-tr from-brand-600 to-accent-600 flex items-center justify-center shadow-xl shadow-brand-500/30 animate-bounce">
            <Brain className="w-7 h-7 text-white" />
          </div>
          <div className="text-center space-y-1">
            <h3 className="text-lg font-bold text-white font-outfit">Computing AI Spatial & XGBoost Models</h3>
            <p className="text-xs text-slate-400">Running Computer Vision, NLP, Safety Guard, and SHAP Explainability...</p>
          </div>
        </div>
      </div>
    );
  }

  if (errorMsg || !aiData) {
    return (
      <div className="min-h-screen flex flex-col bg-dark-950 text-slate-100">
        <Navbar />
        <main className="flex-1 max-w-4xl mx-auto px-4 py-20 text-center space-y-4">
          <Brain className="w-16 h-16 text-slate-600 mx-auto" />
          <h2 className="text-2xl font-bold text-white">{errorMsg || 'AI Analytics Unavailable'}</h2>
          <Link to="/properties" className="inline-flex items-center gap-2 px-6 py-3 rounded-xl bg-brand-600 text-white text-sm font-semibold">
            <ArrowLeft className="w-4 h-4" />
            <span>Return to Properties</span>
          </Link>
        </main>
        <Footer />
      </div>
    );
  }

  const { property, image_ai, text_ai, safety_guard, price_prediction } = aiData;
  const shap = price_prediction.shap_explanation || {};

  const mapSearchResult = {
    latitude: property.latitude,
    longitude: property.longitude,
    formatted_address: property.address,
    query: property.title,
    city: 'Bengaluru',
    estimated_price_sqft: price_prediction.price_per_sqft,
    price_range: `₹${intFormat(price_prediction.predicted_selling_price)}`
  };

  function intFormat(val) {
    return val ? Math.round(val).toLocaleString() : '0';
  }

  return (
    <div className="min-h-screen flex flex-col bg-dark-950 text-slate-100">
      <Navbar />

      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
        {/* Navigation & Action Bar */}
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          <button
            onClick={() => navigate(`/properties/${id}`)}
            className="inline-flex items-center gap-2 text-xs font-semibold text-slate-400 hover:text-white transition-colors"
          >
            <ArrowLeft className="w-4 h-4" />
            <span>Back to Property Details</span>
          </button>

          <button
            onClick={handleDownloadPdf}
            disabled={downloadingPdf}
            className="px-6 py-3 rounded-2xl bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white font-bold text-xs shadow-lg shadow-emerald-500/20 transition-all flex items-center gap-2 self-stretch sm:self-auto justify-center"
          >
            {downloadingPdf ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                <span>Generating PDF Report...</span>
              </>
            ) : (
              <>
                <Download className="w-4 h-4" />
                <span>Export PDF Intelligence Report</span>
              </>
            )}
          </button>
        </div>

        {/* Dashboard Title Header */}
        <div className="glass-card p-8 rounded-3xl border border-brand-500/30 bg-gradient-to-r from-slate-950 via-dark-950 to-brand-950/40 relative overflow-hidden flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
          <div className="space-y-2 z-10">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-brand-500/20 text-brand-300 border border-brand-500/30 text-xs font-semibold">
              <Sparkles className="w-3.5 h-3.5 text-brand-400" />
              <span>Full AI Analytics & Explainable Valuation Engine</span>
            </div>
            <h1 className="text-2xl sm:text-3xl font-extrabold font-outfit text-white">{property.title}</h1>
            <p className="text-xs text-slate-400 flex items-center gap-1">
              <span>{property.address}</span>
            </p>
          </div>
        </div>

        {/* 4 Metric Cards Banner */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {/* Card 1: XGBoost Selling Price */}
          <div className="glass-card p-5 rounded-2xl border border-slate-800 space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-[11px] font-bold uppercase tracking-wider text-slate-400">Predicted Selling Price</span>
              <div className="w-7 h-7 rounded-lg bg-emerald-500/20 text-emerald-400 flex items-center justify-center">
                <IndianRupee className="w-4 h-4" />
              </div>
            </div>
            <p className="text-2xl font-extrabold text-emerald-400">₹{intFormat(price_prediction.predicted_selling_price)}</p>
            <p className="text-[10px] text-slate-500">XGBoost ML Regressor Valuation</p>
          </div>

          {/* Card 2: Estimated Rental Price */}
          <div className="glass-card p-5 rounded-2xl border border-slate-800 space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-[11px] font-bold uppercase tracking-wider text-slate-400">Estimated Rental Price</span>
              <div className="w-7 h-7 rounded-lg bg-brand-500/20 text-brand-400 flex items-center justify-center">
                <TrendingUp className="w-4 h-4" />
              </div>
            </div>
            <p className="text-2xl font-extrabold text-brand-400">₹{intFormat(price_prediction.estimated_rental_price)} <span className="text-xs font-normal text-slate-400">/ mo</span></p>
            <p className="text-[10px] text-slate-500">3.6% Annual Rental Yield Estimate</p>
          </div>

          {/* Card 3: Rate per Sq.ft */}
          <div className="glass-card p-5 rounded-2xl border border-slate-800 space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-[11px] font-bold uppercase tracking-wider text-slate-400">Price Per Sq.ft</span>
              <div className="w-7 h-7 rounded-lg bg-accent-500/20 text-accent-400 flex items-center justify-center">
                <Layers className="w-4 h-4" />
              </div>
            </div>
            <p className="text-2xl font-extrabold text-accent-400">₹{intFormat(price_prediction.price_per_sqft)} <span className="text-xs font-normal text-slate-400">/ sqft</span></p>
            <p className="text-[10px] text-slate-500">Super Built-up Benchmark</p>
          </div>

          {/* Card 4: Confidence Score */}
          <div className="glass-card p-5 rounded-2xl border border-slate-800 space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-[11px] font-bold uppercase tracking-wider text-slate-400">Confidence Score</span>
              <div className="w-7 h-7 rounded-lg bg-purple-500/20 text-purple-400 flex items-center justify-center">
                <Cpu className="w-4 h-4" />
              </div>
            </div>
            <p className="text-2xl font-extrabold text-purple-400">{price_prediction.confidence_score}%</p>
            <p className="text-[10px] text-slate-500">GIS & CV Feature Confidence</p>
          </div>
        </div>

        {/* Computer Vision & NLP Section */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Image AI (The Eyes) */}
          <div className="glass-card p-6 rounded-3xl border border-slate-800 space-y-5">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <h3 className="text-base font-bold font-outfit text-white flex items-center gap-2">
                <Eye className="w-5 h-5 text-brand-400" />
                Image AI Analysis (The Eyes)
              </h3>
              <span className="text-xs font-mono bg-brand-500/10 text-brand-400 px-2.5 py-0.5 rounded-full border border-brand-500/20">
                OpenCV Engine
              </span>
            </div>

            <div className="grid grid-cols-2 gap-4 text-xs">
              <div className="bg-slate-900/80 p-4 rounded-xl border border-slate-800 space-y-1">
                <span className="text-slate-400 block text-[10px] uppercase font-bold">Image Quality Score</span>
                <span className="text-lg font-bold text-white">{image_ai.image_quality_score} / 100</span>
              </div>
              <div className="bg-slate-900/80 p-4 rounded-xl border border-slate-800 space-y-1">
                <span className="text-slate-400 block text-[10px] uppercase font-bold">Brightness Score</span>
                <span className="text-lg font-bold text-white">{image_ai.brightness_score} / 100</span>
              </div>
              <div className="bg-slate-900/80 p-4 rounded-xl border border-slate-800 space-y-1">
                <span className="text-slate-400 block text-[10px] uppercase font-bold">Sharpness Score</span>
                <span className="text-lg font-bold text-white">{image_ai.sharpness_score} / 100</span>
              </div>
              <div className="bg-slate-900/80 p-4 rounded-xl border border-slate-800 space-y-1">
                <span className="text-slate-400 block text-[10px] uppercase font-bold">Interior Condition</span>
                <span className="text-lg font-bold text-emerald-400">{image_ai.interior_condition_score} / 100</span>
              </div>
              <div className="bg-slate-900/80 p-4 rounded-xl border border-slate-800 space-y-1">
                <span className="text-slate-400 block text-[10px] uppercase font-bold">Exterior Condition</span>
                <span className="text-lg font-bold text-emerald-400">{image_ai.exterior_condition_score} / 100</span>
              </div>
              <div className="bg-slate-900/80 p-4 rounded-xl border border-slate-800 space-y-1">
                <span className="text-slate-400 block text-[10px] uppercase font-bold">Overall Property Condition</span>
                <span className="text-sm font-bold text-brand-300">{image_ai.overall_condition}</span>
              </div>
            </div>
          </div>

          {/* Text AI (The Ears) */}
          <div className="glass-card p-6 rounded-3xl border border-slate-800 space-y-5">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <h3 className="text-base font-bold font-outfit text-white flex items-center gap-2">
                <FileText className="w-5 h-5 text-accent-400" />
                Text AI Analysis (The Ears)
              </h3>
              <span className="text-xs font-mono bg-accent-500/10 text-accent-400 px-2.5 py-0.5 rounded-full border border-accent-500/20">
                TF-IDF & NLTK
              </span>
            </div>

            <div className="grid grid-cols-2 gap-4 text-xs">
              <div className="bg-slate-900/80 p-4 rounded-xl border border-slate-800 space-y-1">
                <span className="text-slate-400 block text-[10px] uppercase font-bold">Text Quality Score</span>
                <span className="text-lg font-bold text-white">{text_ai.text_quality_score} / 100</span>
              </div>
              <div className="bg-slate-900/80 p-4 rounded-xl border border-slate-800 space-y-1">
                <span className="text-slate-400 block text-[10px] uppercase font-bold">Premium Listing Score</span>
                <span className="text-lg font-bold text-accent-400">{text_ai.premium_listing_score} / 100</span>
              </div>
            </div>

            <div className="space-y-2 pt-2">
              <span className="text-xs font-semibold text-slate-300 block">Detected Premium Keywords ({text_ai.detected_keywords?.length || 0}):</span>
              {text_ai.detected_keywords && text_ai.detected_keywords.length > 0 ? (
                <div className="flex flex-wrap gap-2">
                  {text_ai.detected_keywords.map((kw, idx) => (
                    <span key={idx} className="px-3 py-1 rounded-lg bg-accent-500/15 text-accent-300 border border-accent-500/30 text-xs font-medium">
                      {kw}
                    </span>
                  ))}
                </div>
              ) : (
                <p className="text-xs text-slate-500">Standard description text.</p>
              )}
            </div>
          </div>
        </div>

        {/* Safety Guard & SHAP Explainability Section */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Locality Safety Guard (1 Col) */}
          <div className="glass-card p-6 rounded-3xl border border-slate-800 space-y-5">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <h3 className="text-base font-bold font-outfit text-white flex items-center gap-2">
                <ShieldAlert className="w-5 h-5 text-emerald-400" />
                Locality Safety Guard
              </h3>
              <span className="text-xs font-mono font-extrabold bg-emerald-500/20 text-emerald-400 px-2.5 py-0.5 rounded-md">
                Grade {safety_guard.overall_rating}
              </span>
            </div>

            <div className="space-y-4">
              <div className="space-y-1.5">
                <div className="flex justify-between text-xs">
                  <span className="text-slate-400">Safety Index</span>
                  <span className="font-bold text-emerald-400">{safety_guard.safety_score} / 100</span>
                </div>
                <div className="w-full bg-slate-900 rounded-full h-2">
                  <div className="bg-emerald-500 h-2 rounded-full" style={{ width: `${safety_guard.safety_score}%` }}></div>
                </div>
              </div>

              <div className="space-y-1.5">
                <div className="flex justify-between text-xs">
                  <span className="text-slate-400">Crime Score (Lower is Safer)</span>
                  <span className="font-bold text-slate-200">{safety_guard.crime_score} / 100</span>
                </div>
                <div className="w-full bg-slate-900 rounded-full h-2">
                  <div className="bg-blue-500 h-2 rounded-full" style={{ width: `${safety_guard.crime_score * 2.5}%` }}></div>
                </div>
              </div>

              <div className="space-y-1.5">
                <div className="flex justify-between text-xs">
                  <span className="text-slate-400">Traffic Congestion Score</span>
                  <span className="font-bold text-amber-400">{safety_guard.traffic_score} / 100</span>
                </div>
                <div className="w-full bg-slate-900 rounded-full h-2">
                  <div className="bg-amber-500 h-2 rounded-full" style={{ width: `${safety_guard.traffic_score}%` }}></div>
                </div>
              </div>

              <div className="p-3.5 rounded-xl bg-slate-900/80 border border-slate-800 text-xs text-slate-300">
                <span className="text-slate-400 block text-[10px] uppercase font-bold">Flood Risk Level</span>
                <span className="font-bold text-emerald-400">{safety_guard.flood_risk}</span>
              </div>
            </div>
          </div>

          {/* SHAP Explainability (2 Cols) */}
          <div className="lg:col-span-2 glass-card p-6 rounded-3xl border border-slate-800 space-y-6">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <h3 className="text-base font-bold font-outfit text-white flex items-center gap-2">
                <Brain className="w-5 h-5 text-purple-400" />
                SHAP Explainable AI (Valuation Drivers)
              </h3>
              <span className="text-xs font-mono bg-purple-500/10 text-purple-400 px-2.5 py-0.5 rounded-full border border-purple-500/20">
                Feature Attribution
              </span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Positive Factors */}
              <div className="space-y-3">
                <h4 className="text-xs uppercase font-bold tracking-wider text-emerald-400 flex items-center gap-1.5">
                  <ThumbsUp className="w-3.5 h-3.5" />
                  Top Positive Price Factors
                </h4>
                {shap.top_positive_factors && shap.top_positive_factors.map((f, idx) => (
                  <div key={idx} className="p-3 rounded-xl bg-emerald-500/10 border border-emerald-500/20 space-y-1">
                    <div className="flex justify-between items-center text-xs">
                      <span className="font-bold text-white">{f.factor}</span>
                      <span className="font-bold text-emerald-400">{f.impact_amount}</span>
                    </div>
                    <p className="text-[11px] text-slate-400">{f.description}</p>
                  </div>
                ))}
              </div>

              {/* Negative Factors */}
              <div className="space-y-3">
                <h4 className="text-xs uppercase font-bold tracking-wider text-red-400 flex items-center gap-1.5">
                  <ThumbsDown className="w-3.5 h-3.5" />
                  Price Adjustments / Penalties
                </h4>
                {shap.top_negative_factors && shap.top_negative_factors.length > 0 ? (
                  shap.top_negative_factors.map((f, idx) => (
                    <div key={idx} className="p-3 rounded-xl bg-red-500/10 border border-red-500/20 space-y-1">
                      <div className="flex justify-between items-center text-xs">
                        <span className="font-bold text-white">{f.factor}</span>
                        <span className="font-bold text-red-400">{f.impact_amount}</span>
                      </div>
                      <p className="text-[11px] text-slate-400">{f.description}</p>
                    </div>
                  ))
                ) : (
                  <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 text-xs text-slate-400">
                    No major negative penalties detected for this property.
                  </div>
                )}
              </div>
            </div>

            {/* Feature Importance Contribution Chart */}
            <div className="pt-4 border-t border-slate-800/80 space-y-3">
              <h4 className="text-xs uppercase font-bold tracking-wider text-slate-300">Feature Weight Attribution Breakdown</h4>
              <div className="space-y-2">
                {shap.feature_importance && shap.feature_importance.map((item, idx) => (
                  <div key={idx} className="space-y-1">
                    <div className="flex justify-between text-xs">
                      <span className="text-slate-400">{item.feature}</span>
                      <span className="font-mono text-purple-300 font-bold">{item.importance}%</span>
                    </div>
                    <div className="w-full bg-slate-900 rounded-full h-1.5">
                      <div className="bg-gradient-to-r from-brand-500 to-purple-500 h-1.5 rounded-full" style={{ width: `${item.importance}%` }}></div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* Map & Nearby Facilities */}
        <div className="space-y-6">
          <h3 className="text-lg font-bold font-outfit text-white flex items-center gap-2">
            <Compass className="w-5 h-5 text-brand-500" />
            GIS Locality Map & Amenity Spatial Query
          </h3>
          <MapView
            searchResult={mapSearchResult}
            nearbyPlaces={property.nearby_places || []}
          />
          <NearbyPlacesList places={property.nearby_places || []} />
        </div>
      </main>

      <Footer />
    </div>
  );
};
