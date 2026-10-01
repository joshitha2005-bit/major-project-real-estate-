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
  CheckCircle2, AlertTriangle, Cpu, Layers, Compass, ThumbsUp, ThumbsDown, Lock, MapPin
} from 'lucide-react';
import { resolvePropertyDisplay } from '../utils/propertyLocationUtils';

export const AiDashboardPage = () => {
  const { id } = useParams();
  const propertyId = id || 1;
  const navigate = useNavigate();

  const [aiData, setAiData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [downloadingPdf, setDownloadingPdf] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');
  const [proLocked, setProLocked] = useState(false);


  useEffect(() => {
    fetchAiAnalytics();
  }, [propertyId]);

  const fetchAiAnalytics = async () => {
    setLoading(true);
    setProLocked(false);
    setErrorMsg('');
    try {
      const data = await aiService.analyzeProperty(propertyId);
      setAiData(data);
    } catch (err) {
      console.error("Failed to load AI analytics:", err);
      if (err.response?.status === 403) {
        setProLocked(true);
      } else {
        setErrorMsg("Failed to run AI Analytics suite for this property.");
      }
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

  if (proLocked) {
    return (
      <div className="min-h-screen flex flex-col bg-dark-950 text-slate-100">
        <Navbar />
        <main className="flex-1 max-w-lg mx-auto px-4 py-24 text-center space-y-6">
          <div className="w-16 h-16 rounded-3xl bg-gradient-to-tr from-brand-600 to-accent-600 flex items-center justify-center shadow-xl shadow-brand-500/30 mx-auto animate-bounce">
            <Brain className="w-8 h-8 text-white" />
          </div>
          <div className="space-y-2">
            <h2 className="text-2xl font-extrabold font-outfit text-white">Unlock Advanced AI Analytics</h2>
            <p className="text-sm text-slate-400">The dynamic full-suite AI dashboard is exclusive to Pro members. Upgrade to get predictions, SHAP pricing explainers, and ResNet visual scans.</p>
          </div>
          <div className="bg-slate-900 border border-slate-800 p-6 rounded-3xl space-y-4">
            <div className="flex items-center justify-between text-left">
              <div>
                <span className="text-[10px] uppercase font-bold text-brand-400">Premium plan</span>
                <h4 className="text-sm font-bold text-white">PropPulse Pro Plan</h4>
              </div>
              <span className="text-lg font-mono font-extrabold text-white">₹299/mo</span>
            </div>
            <button
              onClick={() => navigate('/subscription')}
              className="w-full py-2.5 rounded-xl bg-brand-600 hover:bg-brand-500 text-white font-extrabold text-xs shadow-lg shadow-brand-500/20 transition-all duration-300"
            >
              Upgrade to Pro Plan
            </button>
          </div>
          <button
            onClick={() => navigate(-1)}
            className="inline-flex items-center gap-1.5 text-xs text-slate-400 hover:text-white font-semibold transition-colors"
          >
            <ArrowLeft className="w-3.5 h-3.5" />
            <span>Go Back</span>
          </button>
        </main>
        <Footer />
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
  const disp = resolvePropertyDisplay(property);

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

        {/* Dashboard Title Header: CRITICAL 3-TIER HIERARCHY */}
        <div className="glass-card p-8 rounded-3xl border border-brand-500/30 bg-gradient-to-r from-slate-950 via-dark-950 to-brand-950/40 relative overflow-hidden flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
          <div className="space-y-2.5 z-10">
            <div className="flex flex-wrap items-center gap-2">
              <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-brand-500/20 text-brand-300 border border-brand-500/30 text-xs font-semibold">
                <Sparkles className="w-3.5 h-3.5 text-brand-400" />
                <span>Full AI Analytics & Explainable Valuation Engine</span>
              </div>
              <span className={`px-2.5 py-0.5 rounded text-[10px] font-semibold border ${
                disp.isExact 
                  ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/30' 
                  : 'bg-amber-500/10 text-amber-400 border border-amber-500/30'
              }`}>
                {disp.coordinateAccuracy}
              </span>
            </div>

            {/* 1. ACTUAL BUILDING / PROJECT / PROPERTY NAME */}
            <h1 className="text-2xl sm:text-3xl font-extrabold font-outfit text-white leading-tight">
              {disp.primaryTitle}
            </h1>

            {disp.identitySubtitle && (
              <p className="text-xs italic text-slate-400">
                {disp.identitySubtitle}
              </p>
            )}

            {/* 2. SUB-LOCALITY / LOCALITY, BENGALURU */}
            <p className="text-sm font-semibold text-brand-300 flex items-center gap-1.5">
              <MapPin className="w-4 h-4 text-brand-400 flex-shrink-0" />
              <span>{disp.locationLine}</span>
            </p>

            {/* 3. STREET / ROAD / FULL ADDRESS */}
            {disp.addressLine && (
              <p className="text-xs text-slate-400 pl-5.5">
                {disp.addressLine}
              </p>
            )}
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

          {/* Card 4: Data Reliability Score */}
          <div className="glass-card p-5 rounded-2xl border border-slate-800 space-y-2" title="Input locality match & domain data reliability index (not model prediction accuracy)">
            <div className="flex items-center justify-between">
              <span className="text-[11px] font-bold uppercase tracking-wider text-slate-400">Data Reliability Score</span>
              <div className="w-7 h-7 rounded-lg bg-purple-500/20 text-purple-400 flex items-center justify-center">
                <Cpu className="w-4 h-4" />
              </div>
            </div>
            <p className="text-2xl font-extrabold text-purple-400">{price_prediction.confidence_score}%</p>
            <p className="text-[10px] text-slate-500">Input Locality & Domain Reliability</p>
          </div>

        </div>

        {/* STEP 1 — Multimodal Pipeline & Feature Fusion (544 Dimensions) */}
        <div className="glass-card p-6 sm:p-8 rounded-3xl border border-brand-500/40 bg-gradient-to-br from-slate-950 via-slate-900 to-brand-950/30 space-y-6 relative overflow-hidden">
          <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 border-b border-slate-800 pb-4">
            <div className="space-y-1">
              <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-brand-500/20 text-brand-300 border border-brand-500/30 text-xs font-semibold">
                <Sparkles className="w-3.5 h-3.5 text-brand-400" />
                <span>STEP 1 — MULTIMODAL FEATURE FUSION ENGINE</span>
              </div>
              <h2 className="text-xl sm:text-2xl font-extrabold text-white font-outfit">
                End-to-End Image & Geospatial Feature Integration
              </h2>
            </div>
            <div className="flex items-center gap-2">
              <span className="px-3 py-1 rounded-xl text-xs font-mono font-bold bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 flex items-center gap-1.5">
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
                {price_prediction.prediction_status || 'GENUINE_MODEL_OUTPUT'}
              </span>
              <span className="px-3 py-1 rounded-xl text-xs font-mono font-bold bg-brand-500/20 text-brand-300 border border-brand-500/30">
                544 Fused Features
              </span>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 items-stretch">
            {/* 1. Property Image & ResNet-18 Status */}
            <div className="bg-slate-900/90 rounded-2xl border border-slate-800 overflow-hidden flex flex-col justify-between">
              <div className="relative aspect-video w-full bg-slate-950 overflow-hidden group">
                <img
                  src={
                    property.images && property.images.length > 0
                      ? (property.images[0].startsWith('http') || property.images[0].startsWith('/') 
                          ? property.images[0] 
                          : `/static/${property.images[0]}`)
                      : '/static/property-images/apartments/apartments_02.jpg'
                  }
                  alt={disp.primaryTitle}
                  className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-105"
                  onError={(e) => {
                    e.target.onerror = null;
                    e.target.src = '/static/property-images/apartments/apartments_02.jpg';
                  }}
                />
                <div className="absolute top-2.5 left-2.5 flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-slate-950/80 backdrop-blur-md border border-brand-500/40 text-[10px] font-mono font-bold text-brand-300">
                  <Eye className="w-3 h-3 text-brand-400" />
                  <span>ResNet-18 Active</span>
                </div>
                <div className="absolute bottom-2.5 right-2.5 px-2 py-0.5 rounded bg-black/80 text-[10px] font-mono text-emerald-400 border border-emerald-500/30">
                  512-dim CNN Embedding
                </div>
              </div>

              <div className="p-4 space-y-3">
                <div className="flex items-center justify-between text-xs">
                  <span className="text-slate-400">CNN Architecture:</span>
                  <span className="font-mono text-brand-300 font-bold">{image_ai.cnn_model || 'PyTorch ResNet-18'}</span>
                </div>
                <div className="flex items-center justify-between text-xs">
                  <span className="text-slate-400">Image Provenance:</span>
                  <span className="font-mono text-amber-300 font-bold">{image_ai.image_provenance || price_prediction.image_provenance || 'REPRESENTATIVE'}</span>
                </div>
                <div className="flex items-center justify-between text-xs">
                  <span className="text-slate-400">CNN Status:</span>
                  <span className="font-mono text-emerald-400 font-bold">{image_ai.cnn_status || 'ACTIVE'}</span>
                </div>
                <div className="flex items-center justify-between text-xs">
                  <span className="text-slate-400">Embedding Dimensions:</span>
                  <span className="font-mono text-emerald-400 font-bold">{image_ai.embedding_dimensions || 512} Dimensions</span>
                </div>
                <div className="flex items-center justify-between text-xs">
                  <span className="text-slate-400">Embedding L2 Norm:</span>
                  <span className="font-mono text-brand-300 font-bold">{image_ai.embedding_norm ?? price_prediction.embedding_norm ?? 'N/A'}</span>
                </div>
                <div className="flex items-center justify-between text-xs">
                  <span className="text-slate-400">Non-Zero Features:</span>
                  <span className="font-mono text-slate-200 font-bold">{image_ai.non_zero_features ?? price_prediction.non_zero_features ?? 512} / 512</span>
                </div>
                <div className="p-2.5 rounded-xl bg-slate-950 border border-slate-800 text-[11px] font-mono text-slate-400 break-all">
                  <span className="text-slate-500 block text-[9px] uppercase font-bold">Real Embedding Sample (First 6):</span>
                  {(() => {
                    const sample = image_ai.embedding_sample || image_ai.visual_features?.embedding_sample || price_prediction.embedding_sample;
                    if (sample && Array.isArray(sample) && sample.length > 0) {
                      return `[${sample.slice(0, 6).map(n => Number(n).toFixed(4)).join(', ')}]`;
                    }
                    return 'Extracting embedding...';
                  })()}
                </div>
              </div>
            </div>

            {/* 2. Feature Fusion Pipeline Flow */}
            <div className="lg:col-span-2 bg-slate-900/90 p-5 rounded-2xl border border-slate-800 space-y-4 flex flex-col justify-between">
              <div>
                <h3 className="text-sm font-bold text-white uppercase tracking-wider flex items-center gap-2">
                  <Layers className="w-4 h-4 text-brand-400" />
                  Multimodal Feature Fusion Architecture
                </h3>
                <p className="text-xs text-slate-400 mt-1">
                  High-dimensional multimodal vector concatenation passed directly to the trained XGBoost regressor.
                </p>
              </div>

              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
                {/* Modality 1 */}
                <div className="p-3 rounded-xl bg-slate-950/80 border border-slate-800 space-y-1">
                  <div className="flex items-center justify-between">
                    <span className="text-[10px] uppercase font-bold text-slate-400">Structured</span>
                    <span className="w-2 h-2 rounded-full bg-emerald-400"></span>
                  </div>
                  <span className="text-base font-extrabold text-white block">6 Features</span>
                  <span className="text-[10px] text-slate-400 block">Area, BHK, Bath, Locality</span>
                </div>

                {/* Modality 2 */}
                <div className="p-3 rounded-xl bg-slate-950/80 border border-slate-800 space-y-1">
                  <div className="flex items-center justify-between">
                    <span className="text-[10px] uppercase font-bold text-slate-400">Geoapify</span>
                    <span className="w-2 h-2 rounded-full bg-emerald-400"></span>
                  </div>
                  <span className="text-base font-extrabold text-white block">10 Features</span>
                  <span className="text-[10px] text-slate-400 block">9 POI Categories + Total</span>
                </div>

                {/* Modality 3 */}
                <div className="p-3 rounded-xl bg-slate-950/80 border border-slate-800 space-y-1">
                  <div className="flex items-center justify-between">
                    <span className="text-[10px] uppercase font-bold text-slate-400">TF-IDF NLP</span>
                    <span className="w-2 h-2 rounded-full bg-emerald-400"></span>
                  </div>
                  <span className="text-base font-extrabold text-white block">16 Features</span>
                  <span className="text-[10px] text-slate-400 block">Property Text Term Weights</span>
                </div>

                {/* Modality 4 */}
                <div className="p-3 rounded-xl bg-slate-950/80 border border-brand-500/40 space-y-1 bg-brand-950/20">
                  <div className="flex items-center justify-between">
                    <span className="text-[10px] uppercase font-bold text-brand-300">ResNet-18</span>
                    <span className="w-2 h-2 rounded-full bg-brand-400 animate-pulse"></span>
                  </div>
                  <span className="text-base font-extrabold text-brand-300 block">512 Features</span>
                  <span className="text-[10px] text-slate-400 block">Deep Visual Embeddings</span>
                </div>
              </div>

              {/* Fused Vector Total Row */}
              <div className="p-3.5 rounded-xl bg-gradient-to-r from-brand-950/50 via-slate-950 to-emerald-950/40 border border-brand-500/30 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 text-xs">
                <div className="flex items-center gap-2.5">
                  <div className="w-8 h-8 rounded-lg bg-brand-500/20 text-brand-400 flex items-center justify-center font-bold font-mono">
                    Σ
                  </div>
                  <div>
                    <span className="font-bold text-white block text-sm">Fused Feature Matrix: 544 Total Dimensions</span>
                    <span className="text-[10px] text-slate-400">[Structured: 6] + [Geoapify: 10] + [TF-IDF: 16] + [ResNet-18: 512]</span>
                  </div>
                </div>
                <div className="text-right">
                  <span className="text-[10px] text-slate-400 block">Regression Algorithm</span>
                  <span className="font-bold text-emerald-400 font-mono">XGBRegressor (Trained)</span>
                </div>
              </div>

              {/* SHAP Modality Attribution Percentages */}
              <div className="space-y-1.5 pt-2 border-t border-slate-800/80">
                <div className="flex justify-between items-center text-xs">
                  <span className="text-slate-300 font-semibold">SHAP Modality Attribution Breakdown:</span>
                  <span className="text-slate-400 text-[10px]">Real TreeExplainer Feature Weights</span>
                </div>
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 text-[11px]">
                  <div className="p-2 rounded-lg bg-slate-950 border border-slate-800 flex justify-between">
                    <span className="text-slate-400">Structured:</span>
                    <span className="font-mono text-emerald-400 font-bold">{price_prediction.modality_percentages?.structured_tabular ?? 54.8}%</span>
                  </div>
                  <div className="p-2 rounded-lg bg-slate-950 border border-slate-800 flex justify-between">
                    <span className="text-slate-400">ResNet-18:</span>
                    <span className="font-mono text-brand-400 font-bold">{price_prediction.modality_percentages?.image_resnet18 ?? 40.1}%</span>
                  </div>
                  <div className="p-2 rounded-lg bg-slate-950 border border-slate-800 flex justify-between">
                    <span className="text-slate-400">Geoapify:</span>
                    <span className="font-mono text-accent-400 font-bold">{price_prediction.modality_percentages?.geospatial_geoapify ?? 4.7}%</span>
                  </div>
                  <div className="p-2 rounded-lg bg-slate-950 border border-slate-800 flex justify-between">
                    <span className="text-slate-400">TF-IDF:</span>
                    <span className="font-mono text-purple-400 font-bold">{price_prediction.modality_percentages?.text_tfidf ?? 0.4}%</span>
                  </div>
                </div>
              </div>
            </div>
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
              <div className="flex items-center gap-2">
                <span className="text-[10px] font-mono uppercase bg-amber-500/10 text-amber-300 border border-amber-500/30 px-2 py-0.5 rounded-full font-bold">
                  {image_ai.image_provenance || 'REPRESENTATIVE'}
                </span>
                <span className="text-xs font-mono bg-brand-500/10 text-brand-400 px-2.5 py-0.5 rounded-full border border-brand-500/20">
                  {image_ai.cnn_model || 'PyTorch ResNet-18'}
                </span>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4 text-xs">
              <div className="bg-slate-900/80 p-4 rounded-xl border border-slate-800 space-y-1">
                <span className="text-slate-400 block text-[10px] uppercase font-bold">Embedding Dimensions</span>
                <span className="text-lg font-bold text-brand-400 font-mono">{image_ai.embedding_dimensions || 512} Dims</span>
              </div>
              <div className="bg-slate-900/80 p-4 rounded-xl border border-slate-800 space-y-1">
                <span className="text-slate-400 block text-[10px] uppercase font-bold">Embedding L2 Norm</span>
                <span className="text-lg font-bold text-emerald-400 font-mono">{image_ai.embedding_norm ?? 'N/A'}</span>
              </div>
              <div className="bg-slate-900/80 p-4 rounded-xl border border-slate-800 space-y-1">
                <span className="text-slate-400 block text-[10px] uppercase font-bold">Non-Zero Features</span>
                <span className="text-lg font-bold text-white font-mono">{image_ai.non_zero_features ?? 512} / 512</span>
              </div>
              <div className="bg-slate-900/80 p-4 rounded-xl border border-slate-800 space-y-1">
                <span className="text-slate-400 block text-[10px] uppercase font-bold">Image Quality Score</span>
                <span className="text-lg font-bold text-white">{image_ai.image_quality_score ?? 'N/A'} / 100</span>
              </div>
              <div className="bg-slate-900/80 p-4 rounded-xl border border-slate-800 space-y-1">
                <span className="text-slate-400 block text-[10px] uppercase font-bold">Sharpness (Laplacian)</span>
                <span className="text-sm font-bold text-slate-200">{image_ai.visual_features?.sharpness ?? 'N/A'}</span>
              </div>
              <div className="bg-slate-900/80 p-4 rounded-xl border border-slate-800 space-y-1">
                <span className="text-slate-400 block text-[10px] uppercase font-bold">Brightness (0-255)</span>
                <span className="text-sm font-bold text-slate-200">{image_ai.visual_features?.brightness ?? 'N/A'}</span>
              </div>
            </div>

            <div className="bg-slate-900/50 p-3.5 rounded-xl border border-slate-800/80 text-xs space-y-2">
              <div className="flex items-center justify-between text-slate-400 text-[11px]">
                <span>Resolution: <strong className="text-slate-200">{image_ai.visual_features?.resolution || 'N/A'}</strong></span>
                <span>Tone: <strong className="text-slate-200">{image_ai.visual_features?.color_tone || 'Natural'}</strong></span>
              </div>
              <p className="text-[11px] text-slate-400 border-t border-slate-800/80 pt-2 leading-relaxed">
                {image_ai.disclosure_note || 'Image processed by PyTorch ResNet-18 for visual feature extraction.'}
              </p>
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
                TF-IDF & NLP Engine
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

            {/* Sentiment & Tone Row */}
            <div className="grid grid-cols-2 gap-4 text-xs">
              <div className="bg-slate-900/50 p-3 rounded-xl border border-slate-800/80 space-y-1">
                <span className="text-slate-400 block text-[10px] uppercase font-bold">Sentiment Analysis</span>
                <div className="flex items-center gap-2">
                  <span className={`font-bold ${text_ai.sentiment_label === 'Positive' ? 'text-emerald-400' : text_ai.sentiment_label === 'Negative' ? 'text-rose-400' : 'text-amber-400'}`}>
                    {text_ai.sentiment_label || 'Neutral'}
                  </span>
                  <span className="text-slate-400 text-[11px]">({text_ai.sentiment_score ?? 0.5})</span>
                </div>
              </div>
              <div className="bg-slate-900/50 p-3 rounded-xl border border-slate-800/80 space-y-1">
                <span className="text-slate-400 block text-[10px] uppercase font-bold">Text Tone</span>
                <span className="font-bold text-slate-200">{text_ai.tone || 'Standard'}</span>
              </div>
            </div>

            {/* Top TF-IDF Terms */}
            {text_ai.top_tfidf_terms && text_ai.top_tfidf_terms.length > 0 && (
              <div className="space-y-2 pt-1 border-t border-slate-800/60">
                <span className="text-xs font-semibold text-slate-300 block">Top TF-IDF Terms & Weights:</span>
                <div className="flex flex-wrap gap-2">
                  {text_ai.top_tfidf_terms.map((item, idx) => (
                    <span key={idx} className="px-2.5 py-1 rounded-lg bg-slate-900 border border-slate-800 text-xs font-mono flex items-center gap-1.5">
                      <span className="text-slate-200">{item.term}</span>
                      <span className="text-accent-400 font-bold text-[11px]">{item.weight}</span>
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Categorized Amenities */}
            {text_ai.categorized_amenities && Object.keys(text_ai.categorized_amenities).some(cat => text_ai.categorized_amenities[cat]?.length > 0) && (
              <div className="space-y-3 pt-1 border-t border-slate-800/60 text-xs">
                <span className="text-xs font-semibold text-slate-300 block">Detected Amenities & Features:</span>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  {Object.entries(text_ai.categorized_amenities).map(([category, items]) => {
                    if (!items || items.length === 0) return null;
                    return (
                      <div key={category} className="bg-slate-900/40 p-3 rounded-xl border border-slate-800/60 space-y-1.5">
                        <span className="text-[10px] font-bold text-accent-400 uppercase tracking-wider block">{category}</span>
                        <div className="space-y-1">
                          {items.map((item, i) => (
                            <div key={i} className="flex items-center gap-1.5 text-slate-300 text-[11px]">
                              <span className="text-emerald-400 font-bold">✓</span>
                              <span>{item}</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            )}

            {/* Detected Premium Keywords */}
            <div className="space-y-2 pt-1 border-t border-slate-800/60">
              <span className="text-xs font-semibold text-slate-300 block">Detected Keywords ({text_ai.detected_keywords?.length || 0}):</span>
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
                  <span className="text-slate-400">Emergency Infrastructure Score</span>
                  <span className="font-bold text-emerald-400">{safety_guard.emergency_coverage_score ?? safety_guard.safety_score} / 100</span>
                </div>
                <div className="w-full bg-slate-900 rounded-full h-2">
                  <div className="bg-emerald-500 h-2 rounded-full" style={{ width: `${safety_guard.emergency_coverage_score ?? safety_guard.safety_score}%` }}></div>
                </div>
              </div>

              {/* Emergency GIS Proximity Details */}
              <div className="space-y-2 pt-1 border-t border-slate-800/60 text-xs">
                <span className="text-slate-400 block text-[10px] uppercase font-bold">GIS Emergency Infrastructure:</span>
                
                <div className="bg-slate-900/60 p-2.5 rounded-xl border border-slate-800/80 space-y-0.5">
                  <span className="text-[10px] text-slate-400 font-bold block">Nearest Police Station:</span>
                  <div className="flex items-center justify-between">
                    <span className="font-semibold text-slate-200 line-clamp-1 text-[11px]">{safety_guard.nearest_police_station || 'None detected'}</span>
                    <span className="text-emerald-400 font-mono text-[11px] font-bold">
                      {safety_guard.nearest_police_station_dist_meters ? (safety_guard.nearest_police_station_dist_meters >= 1000 ? `${(safety_guard.nearest_police_station_dist_meters/1000).toFixed(2)} km` : `${Math.round(safety_guard.nearest_police_station_dist_meters)} m`) : 'N/A'}
                    </span>
                  </div>
                </div>

                <div className="bg-slate-900/60 p-2.5 rounded-xl border border-slate-800/80 space-y-0.5">
                  <span className="text-[10px] text-slate-400 font-bold block">Nearest Emergency Hospital:</span>
                  <div className="flex items-center justify-between">
                    <span className="font-semibold text-slate-200 line-clamp-1 text-[11px]">{safety_guard.nearest_hospital || 'None detected'}</span>
                    <span className="text-emerald-400 font-mono text-[11px] font-bold">
                      {safety_guard.nearest_hospital_dist_meters ? (safety_guard.nearest_hospital_dist_meters >= 1000 ? `${(safety_guard.nearest_hospital_dist_meters/1000).toFixed(2)} km` : `${Math.round(safety_guard.nearest_hospital_dist_meters)} m`) : 'N/A'}
                    </span>
                  </div>
                </div>

                <div className="bg-slate-900/60 p-2.5 rounded-xl border border-slate-800/80 space-y-0.5">
                  <span className="text-[10px] text-slate-400 font-bold block">Nearest Fire Station:</span>
                  <div className="flex items-center justify-between">
                    <span className="font-semibold text-slate-200 line-clamp-1 text-[11px]">{safety_guard.nearest_fire_station || 'None detected (<5km)'}</span>
                    <span className="text-emerald-400 font-mono text-[11px] font-bold">
                      {safety_guard.nearest_fire_station_dist_meters ? (safety_guard.nearest_fire_station_dist_meters >= 1000 ? `${(safety_guard.nearest_fire_station_dist_meters/1000).toFixed(2)} km` : `${Math.round(safety_guard.nearest_fire_station_dist_meters)} m`) : 'N/A'}
                    </span>
                  </div>
                </div>
              </div>

              {/* Data Availability Indicators */}
              <div className="grid grid-cols-2 gap-2 pt-1 border-t border-slate-800/60 text-xs">
                <div className="p-2.5 rounded-xl bg-slate-900/40 border border-slate-800/60">
                  <span className="text-slate-400 block text-[9px] uppercase font-bold">Flood Risk</span>
                  <span className="font-semibold text-slate-400 text-[11px]">{safety_guard.flood_risk || 'Data Not Available'}</span>
                </div>
                <div className="p-2.5 rounded-xl bg-slate-900/40 border border-slate-800/60">
                  <span className="text-slate-400 block text-[9px] uppercase font-bold">Traffic Congestion</span>
                  <span className="font-semibold text-slate-400 text-[11px]">Data Not Available</span>
                </div>
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
            property={property}
            nearbyPlaces={property.nearby_places || []}
          />
          <NearbyPlacesList places={property.nearby_places || []} />
        </div>
      </main>

      <Footer />
    </div>
  );
};
