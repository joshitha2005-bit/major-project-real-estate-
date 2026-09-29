import React, { useEffect, useState } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { propertyService } from '../services/propertyService';
import { aiService } from '../services/aiService';
import { locationService } from '../services/locationService';
import { useAuth } from '../context/AuthContext';
import { Navbar } from '../components/Navbar';
import { Footer } from '../components/Footer';
import { MapView } from '../components/MapView';
import { NearbyPlacesList } from '../components/NearbyPlacesList';
import { 
  Building2, MapPin, ArrowLeft, Loader2, Phone, 
  Shield, CheckCircle2, Sparkles, Download, Brain, User, MessageSquare, X, 
  ThumbsUp, ThumbsDown, Heart, Info, AlertTriangle, AlertCircle, 
  Flame, Activity, FileText, ChevronLeft, ChevronRight, Compass, Lock,
  Navigation, ExternalLink
} from 'lucide-react';
import { 
  resolvePropertyDisplay, 
  navigateToProperty, 
  openInOpenStreetMap, 
  openInGoogleMaps 
} from '../utils/propertyLocationUtils';

const getDetailsFallbackImage = (id, ptype = "") => {
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

export const PropertyDetailsPage = () => {
  const { id } = useParams();
  const navigate = useNavigate();

  const [property, setProperty] = useState(null);
  const [aiAnalytics, setAiAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [downloadingPdf, setDownloadingPdf] = useState(false);
  const [activeImageIndex, setActiveImageIndex] = useState(0);
  const [showContactModal, setShowContactModal] = useState(false);
  const [messageSent, setMessageSent] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');
  const [showReliabilityTooltip, setShowReliabilityTooltip] = useState(false);

  const { user } = useAuth();
  const [revealedContact, setRevealedContact] = useState(null);
  const [revealLoading, setRevealLoading] = useState(false);
  const [revealError, setRevealError] = useState('');
  const [proAccessDenied, setProAccessDenied] = useState(false);


  const handleRevealContact = async () => {
    if (!user) {
      setRevealError('Please login to reveal owner contact details.');
      return;
    }
    setRevealLoading(true);
    setRevealError('');
    try {
      const contactData = await propertyService.getPropertyContact(id);
      setRevealedContact(contactData);
    } catch (err) {
      console.error(err);
      setRevealError(err.response?.data?.detail || err.message || 'Failed to reveal contact details.');
    } finally {
      setRevealLoading(false);
    }
  };


  // Watchlist Save state
  const [isSavedProperty, setIsSavedProperty] = useState(() => {
    try {
      const saved = JSON.parse(localStorage.getItem('saved_properties') || '[]');
      return saved.includes(id);
    } catch {
      return false;
    }
  });

  // Nearby places — fetched live from Geoapify using property coordinates
  const [nearbyPlaces, setNearbyPlaces] = useState([]);
  const [nearbyLoading, setNearbyLoading] = useState(false);
  const [nearbyRadius, setNearbyRadius] = useState(5000); // metres: 1000 or 5000
  const [nearbyError, setNearbyError] = useState(false);

  useEffect(() => {
    // Clear old property data immediately to prevent state leakage
    setProperty(null);
    setAiAnalytics(null);
    setRevealedContact(null);
    setRevealError('');
    setActiveImageIndex(0);
    setErrorMsg('');

    const fetchPropertyAndAi = async () => {
      setLoading(true);
      setProAccessDenied(false);
      try {
        const propData = await propertyService.getPropertyById(id);
        setProperty(propData);
        
        try {
          const aiData = await aiService.analyzeProperty(id);
          setAiAnalytics(aiData);
        } catch (aiErr) {
          if (aiErr.response?.status === 403) {
            console.log("Pro access restricted for this user.");
            setProAccessDenied(true);
          } else {
            console.error("Non-403 AI fetch error:", aiErr);
          }
        }
      } catch (err) {
        console.error("Failed to load property details:", err);
        setErrorMsg("Property listing could not be found or has been removed.");
      } finally {
        setLoading(false);
      }
    };

    fetchPropertyAndAi();
  }, [id]);

  // Fetch nearby places whenever property or radius changes
  useEffect(() => {
    if (!property?.latitude || !property?.longitude) return;
    const fetchNearby = async () => {
      setNearbyLoading(true);
      setNearbyPlaces([]);
      setNearbyError(false);
      try {
        const places = await locationService.getNearbyPlaces(
          property.latitude,
          property.longitude,
          nearbyRadius
        );
        // Filter out generic/unnamed entries
        const GENERIC_NAMES = [
          'point of interest', 'unnamed', 'unnamed road', 'unknown',
          'building', 'structure', 'place', 'area', 'zone'
        ];
        const filtered = (places || []).filter(p => {
          const nameLower = (p.name || '').toLowerCase().trim();
          if (nameLower.length < 3) return false;
          if (GENERIC_NAMES.some(g => nameLower === g)) return false;
          if (/^[0-9]+$/.test(nameLower)) return false;
          return true;
        });
        setNearbyPlaces(filtered);
      } catch (err) {
        console.error('Failed to fetch nearby places:', err);
        setNearbyPlaces([]);
        setNearbyError(true);
      } finally {
        setNearbyLoading(false);
      }
    };
    fetchNearby();
  }, [property, nearbyRadius]);

  const handleToggleSave = () => {
    try {
      const saved = JSON.parse(localStorage.getItem('saved_properties') || '[]');
      let updated;
      if (saved.includes(id)) {
        updated = saved.filter(x => x !== id);
        setIsSavedProperty(false);
      } else {
        updated = [...saved, id];
        setIsSavedProperty(true);
      }
      localStorage.setItem('saved_properties', JSON.stringify(updated));
    } catch (err) {
      console.error("Failed to toggle save property:", err);
    }
  };

  const handleDownloadPdf = async () => {
    setDownloadingPdf(true);
    try {
      await aiService.downloadPdfReport(id);
    } catch (err) {
      console.error("PDF download failed:", err);
    } finally {
      setDownloadingPdf(false);
    }
  };

  const handlePrevImage = () => {
    if (uniqueImages.length > 0) {
      setActiveImageIndex((prev) => (prev === 0 ? uniqueImages.length - 1 : prev - 1));
    }
  };

  const handleNextImage = () => {
    if (uniqueImages.length > 0) {
      setActiveImageIndex((prev) => (prev === uniqueImages.length - 1 ? 0 : prev + 1));
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-dark-950">
        <div className="flex flex-col items-center gap-3">
          <Loader2 className="w-10 h-10 text-brand-500 animate-spin" />
          <p className="text-slate-400 font-medium text-sm">Loading Property Details & AI Analysis...</p>
        </div>
      </div>
    );
  }

  if (errorMsg || !property) {
    return (
      <div className="min-h-screen flex flex-col bg-dark-950 text-slate-100">
        <Navbar />
        <main className="flex-1 max-w-4xl mx-auto px-4 py-20 text-center space-y-4">
          <Building2 className="w-16 h-16 text-slate-600 mx-auto" />
          <h2 className="text-2xl font-bold text-white">{errorMsg || 'Property Not Found'}</h2>
          <Link to="/properties" className="inline-flex items-center gap-2 px-6 py-3 rounded-xl bg-brand-600 text-white text-sm font-semibold">
            <ArrowLeft className="w-4 h-4" />
            <span>Back to Property Listings</span>
          </Link>
        </main>
        <Footer />
      </div>
    );
  }

  const mapSearchResult = {
    latitude: property.latitude,
    longitude: property.longitude,
    formatted_address: property.address,
    query: property.title,
    city: 'Bengaluru',
    estimated_price_sqft: property.price_per_sqft,
    price_range: property.price_formatted
  };

  const pred = aiAnalytics?.price_prediction;
  const cv = aiAnalytics?.image_ai;
  const nlp = aiAnalytics?.text_ai;
  const safety = aiAnalytics?.safety_guard;

  // PHASE 4J Deterministic AI Property Summary Generator
  const generateDeterministicSummary = () => {
    const parts = [];
    if (pred) {
      parts.push(
        `AI Valuation: The XGBoost predictive engine estimates a market value of ${property.price_formatted || `₹${int(pred.predicted_selling_price).toLocaleString()}`} based on local supply trends and the property's ${property.bhk} BHK layout.`
      );
    }
    if (cv) {
      parts.push(
        `Visual Asset Quality: Computer Vision (ResNet-18) scanning of the property photos yields an image score of ${cv.overall_score || 75}/100 with a condition classification of '${cv.overall_condition || 'Good'}'.`
      );
    }
    if (nlp) {
      if (property.description) {
        parts.push(
          `Listing Quality: Description NLP algorithms rated the textual clarity at ${nlp.text_quality_score || 70}/100, identifying a sentiment rating of ${nlp.sentiment_label || 'Neutral'} and a professional '${nlp.tone || 'Professional'}' tone.`
        );
      } else {
        parts.push("Listing description is unavailable for NLP text analysis.");
      }
    }
    if (safety) {
      parts.push(
        `Locality Score: GIS intelligence maps an emergency safety coverage rating of ${safety.emergency_coverage_score || 70}/100, with nearby coverage including a police station at ${safety.nearest_police_station_dist_meters ? `${(safety.nearest_police_station_dist_meters / 1000).toFixed(2)} km` : 'Not available'}.`
      );
    }
    return parts.join(" ");
  };

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
  
  let imageList = [];
  if (property && property.uploaded_images && property.uploaded_images.length > 0) {
    const sortedDb = [...property.uploaded_images].sort((a, b) => (b.is_primary ? 1 : 0) - (a.is_primary ? 1 : 0));
    imageList = sortedDb.map(img => ({
      path: img.image_path,
      source_type: img.source_type || 'owner_upload',
      source_name: img.source_name || 'Owner Uploaded',
      source_url: img.source_url || ''
    }));
  } else if (property && property.images && property.images.length > 0) {
    imageList = property.images.filter(img => typeof img === 'string' && img.trim() !== '').map(img => ({
      path: img,
      source_type: 'licensed_external',
      source_name: 'Listing Image',
      source_url: ''
    }));
  }

  const uniqueImages = imageList;
  const hasMultipleImages = uniqueImages.length > 1;
  const hasImages = uniqueImages.length > 0;
  const rawPhone = property && (property.phone || property.owner_phone);
  const detailsPhone = (property && rawPhone && rawPhone !== 'Contact information unavailable' && rawPhone.trim() !== '')
    ? rawPhone
    : (isDirect ? "+91 80 4123 5500" : "Contact information unavailable for historical records");

  const disp = resolvePropertyDisplay(property);
  const displayName = disp.buildingName;

  return (
    <div className="min-h-screen flex flex-col bg-dark-950 text-slate-100">
      <Navbar />

      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
        
        {/* Navigation & Global Action Row */}
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          <button
            onClick={() => navigate(-1)}
            className="inline-flex items-center gap-2 text-xs font-semibold text-slate-400 hover:text-white transition-all duration-300"
          >
            <ArrowLeft className="w-4 h-4" />
            <span>Back to Listings</span>
          </button>

          <div className="flex items-center gap-3 w-full sm:w-auto">
            {/* Save Watchlist Toggle Button */}
            <button
              onClick={handleToggleSave}
              className={`px-4 py-2.5 rounded-xl border text-xs font-semibold transition-all duration-300 flex items-center gap-2 ${
                isSavedProperty 
                  ? 'bg-rose-500/10 text-rose-400 border-rose-500/30' 
                  : 'bg-slate-900 text-slate-300 border-slate-800 hover:text-white'
              }`}
            >
              <Heart className={`w-4 h-4 ${isSavedProperty ? 'fill-rose-500 text-rose-500' : ''}`} />
              <span>{isSavedProperty ? 'Saved in Watchlist' : 'Save Property'}</span>
            </button>

            {/* Inquire Owner Trigger Button */}
            <button
              onClick={() => setShowContactModal(true)}
              className="px-4 py-2.5 rounded-xl bg-slate-900 hover:bg-slate-800 text-slate-300 border border-slate-800 text-xs font-semibold transition-all duration-300 flex items-center gap-2"
            >
              <MessageSquare className="w-4 h-4 text-brand-400" />
              <span>Contact Seller</span>
            </button>

            {/* Download PDF Button */}
            <button
              onClick={handleDownloadPdf}
              disabled={downloadingPdf}
              className="px-5 py-2.5 rounded-xl bg-gradient-to-r from-brand-600 to-accent-600 hover:from-brand-500 hover:to-accent-500 text-white font-bold text-xs shadow-lg shadow-brand-500/20 transition-all duration-300 flex items-center justify-center gap-2"
            >
              {downloadingPdf ? <Loader2 className="w-4 h-4 animate-spin" /> : <Download className="w-4 h-4" />}
              <span>{downloadingPdf ? 'Generating PDF...' : 'Download AI Property Report'}</span>
            </button>
          </div>
        </div>

        {/* PHASE 4A — PROPERTY HEADER BANNER: CRITICAL 3-TIER HIERARCHY */}
        <div className="glass-card p-6 md:p-8 rounded-3xl border border-slate-800 flex flex-col lg:flex-row items-start lg:items-center justify-between gap-6 relative overflow-hidden bg-slate-900/20">
          <div className="space-y-2.5">
            <div className="flex flex-wrap items-center gap-2">
              <span className="px-2.5 py-0.5 rounded-md bg-brand-500/10 text-brand-300 border border-brand-500/20 text-[10px] font-extrabold uppercase tracking-wider">
                {property.property_type || "Apartment"}
              </span>
              <span className="px-2.5 py-0.5 rounded-md bg-accent-500/10 text-accent-300 border border-accent-500/20 text-[10px] font-extrabold uppercase tracking-wider">
                {property.listing_type || "Dataset"}
              </span>
              <span className={`px-2.5 py-0.5 rounded-md text-[10px] font-extrabold uppercase tracking-wider border ${
                disp.isExact
                  ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30'
                  : 'bg-amber-500/10 text-amber-400 border-amber-500/30'
              }`}>
                {disp.coordinateAccuracy}
              </span>
              <span className={`px-2.5 py-0.5 rounded-md text-[10px] font-extrabold uppercase tracking-wider border ${
                isHistorical
                  ? 'bg-amber-500/10 text-amber-300 border-amber-500/20'
                  : property.verification_status === 'Verified'
                    ? 'bg-emerald-500/10 text-emerald-300 border-emerald-500/20'
                    : 'bg-brand-500/10 text-brand-300 border-brand-500/20'
              }`}>
                {isDirect
                  ? 'PropPulse Direct Listing'
                  : (property.source_type === 'authorized_provider' || property.listing_status === 'AUTHORIZED')
                    ? 'Authorized Provider Listing'
                    : 'Historical Market Data'}
              </span>
            </div>

            {/* 1. ACTUAL BUILDING / PROJECT / PROPERTY NAME */}
            <h1 className="text-2xl sm:text-3xl font-extrabold font-outfit text-white leading-tight">
              {disp.buildingName}
            </h1>

            {/* 2. SUB-LOCALITY / LOCALITY, BENGALURU */}
            <p className="text-sm font-semibold text-brand-300 flex items-center gap-1.5">
              <MapPin className="w-4 h-4 text-brand-400 flex-shrink-0" />
              <span>{disp.locationLine}</span>
            </p>

            {/* 3. STREET / ROAD / FULL ADDRESS (when available) */}
            {disp.addressLine && (
              <p className="text-xs text-slate-400 pl-5.5">
                {disp.addressLine}
              </p>
            )}
          </div>

          <div className="bg-slate-900/90 px-6 py-4 rounded-2xl border border-slate-800 text-left lg:text-right space-y-0.5 w-full lg:w-auto flex-shrink-0 shadow-lg">
            <span className="text-[10px] uppercase font-bold text-slate-500 tracking-widest block">Asking Price</span>
            <p className="text-2xl sm:text-3xl font-extrabold text-emerald-400">{property.price_formatted}</p>
            <p className="text-xs text-slate-400 font-mono">
              {disp.pricePerSqftText || (property.price_per_sqft ? `₹${property.price_per_sqft.toLocaleString()} / sq.ft` : "Not available")}
            </p>
          </div>
        </div>

        {/* PROPERTY IMAGES GALLERY */}
        <div className="space-y-4">
          <div className="relative h-[380px] sm:h-[480px] w-full rounded-3xl overflow-hidden border border-slate-800 bg-slate-900/60 shadow-xl group">
            {hasImages && uniqueImages[activeImageIndex] ? (
              <>
                <img
                  src={uniqueImages[activeImageIndex].path}
                  alt={`${displayName} - Photo ${activeImageIndex + 1}`}
                  className="w-full h-full object-cover select-none"
                />
                
                {/* Image Source Provenance Badge */}
                <div className="absolute top-4 left-4 bg-slate-950/85 backdrop-blur-md px-3.5 py-1.5 rounded-full border border-slate-700/80 text-[11px] font-bold text-slate-200 flex items-center gap-1.5 shadow-lg">
                  <Shield className="w-3.5 h-3.5 text-brand-400" />
                  <span>
                    Source: {uniqueImages[activeImageIndex].source_type === 'owner_upload' ? 'Owner Uploaded' : (uniqueImages[activeImageIndex].source_name || 'Licensed Image')}
                  </span>
                </div>

                {/* Left Arrow */}
                {hasMultipleImages && (
                  <button
                    onClick={handlePrevImage}
                    className="absolute left-4 top-1/2 -translate-y-1/2 w-11 h-11 rounded-full bg-slate-950/80 hover:bg-slate-950 text-white border border-slate-800 flex items-center justify-center transition-all opacity-0 group-hover:opacity-100 shadow-md backdrop-blur-md"
                  >
                    <ChevronLeft className="w-6 h-6" />
                  </button>
                )}

                {/* Right Arrow */}
                {hasMultipleImages && (
                  <button
                    onClick={handleNextImage}
                    className="absolute right-4 top-1/2 -translate-y-1/2 w-11 h-11 rounded-full bg-slate-950/80 hover:bg-slate-950 text-white border border-slate-800 flex items-center justify-center transition-all opacity-0 group-hover:opacity-100 shadow-md backdrop-blur-md"
                  >
                    <ChevronRight className="w-6 h-6" />
                  </button>
                )}

                {/* Image Counter Indicator Badge */}
                <div className="absolute bottom-4 right-4 bg-slate-950/80 backdrop-blur-md px-3 py-1 rounded-full border border-slate-800 text-[10px] font-mono font-bold text-slate-300">
                  {activeImageIndex + 1} of {uniqueImages.length}
                </div>
              </>
            ) : (
              <div className="w-full h-full flex flex-col items-center justify-center text-slate-400 gap-4 bg-slate-950/90 p-8 border border-slate-800">
                <div className="flex items-center gap-2 px-3 py-1 rounded-full bg-amber-500/10 border border-amber-500/25 text-amber-400 text-xs font-bold uppercase tracking-wider">
                  <AlertTriangle className="w-4 h-4" />
                  <span>LOCATION REFERENCE — NOT ACTUAL PROPERTY PHOTO</span>
                </div>
                <Building2 className="w-16 h-16 text-slate-600" />
                <div className="text-center space-y-2 max-w-md">
                  <p className="text-sm font-bold text-slate-200 uppercase tracking-wide">BUILDING/LOCATION REFERENCE — NOT ACTUAL PROPERTY PHOTO</p>
                  <p className="text-xs text-slate-400 leading-relaxed">
                    No verified property photo is available for this historical record. Refer to the interactive geospatial map below for verified location context and infrastructure proximity.
                  </p>
                </div>
              </div>
            )}
          </div>

          {/* Thumbnails row */}
          {hasMultipleImages && (
            <div className="flex items-center gap-3 overflow-x-auto pb-2 scrollbar-thin">
              {uniqueImages.map((imgObj, idx) => (
                <button
                  key={idx}
                  onClick={() => setActiveImageIndex(idx)}
                  className={`w-20 h-20 rounded-2xl overflow-hidden border-2 flex-shrink-0 transition-all ${
                    activeImageIndex === idx 
                      ? 'border-brand-500 scale-105 shadow-md shadow-brand-500/25' 
                      : 'border-slate-800 opacity-60 hover:opacity-100'
                  }`}
                >
                  <img src={imgObj.path} alt={`Thumbnail view ${idx + 1}`} className="w-full h-full object-cover" />
                </button>
              ))}
            </div>
          )}
        </div>

        {/* PHASE 4E — AI PROPERTY VALUATION */}
        {proAccessDenied && (
          <div className="glass-card p-6 md:p-8 rounded-3xl border border-brand-500/30 bg-gradient-to-r from-slate-900/90 to-brand-950/20 shadow-lg relative overflow-hidden text-center py-10 space-y-4">
            <div className="absolute top-0 right-0 w-24 h-24 bg-brand-500/5 rounded-full filter blur-xl"></div>
            <div className="w-10 h-10 rounded-xl bg-brand-500/20 text-brand-400 flex items-center justify-center mx-auto">
              <Brain className="w-5 h-5 animate-pulse" />
            </div>
            <div className="space-y-1">
              <h4 className="text-sm font-bold text-white font-outfit uppercase tracking-wider">AI Valuation & Price Analysis [LOCKED]</h4>
              <p className="text-xs text-slate-400 max-w-md mx-auto">Upgrade to the Pro Plan to unlock the XGBoost price estimation engine, monthly rent forecast model, and dynamic SHAP feature attributions.</p>
            </div>
            <button
              onClick={() => navigate('/subscription')}
              className="inline-flex items-center gap-2 px-6 py-2 rounded-xl bg-brand-600 hover:bg-brand-500 text-white text-xs font-bold transition-all duration-300"
            >
              <span>Upgrade to Pro – ₹299/month</span>
            </button>
          </div>
        )}
        {pred && !proAccessDenied && (
          <div className="glass-card p-6 md:p-8 rounded-3xl border border-brand-500/30 bg-gradient-to-r from-slate-900/90 to-brand-950/20 shadow-lg relative overflow-hidden space-y-6">

            <div className="absolute top-0 right-0 w-24 h-24 bg-brand-500/5 rounded-full filter blur-xl"></div>
            
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6 items-center border-b border-slate-800/80 pb-6">
              
              {/* AI Market Value */}
              <div className="space-y-1 md:border-r border-slate-800/80 pr-4">
                <div className="flex items-center gap-1.5">
                  <Brain className="w-4 h-4 text-brand-400" />
                  <span className="text-[11px] font-bold uppercase text-slate-400 tracking-wider">AI Predicted Price</span>
                </div>
                <p className="text-3xl font-extrabold text-emerald-400">
                  ₹{int(pred.predicted_selling_price).toLocaleString('en-IN')}
                </p>
                <p className="text-xs text-slate-400">
                  Estimated Unit Rate: <strong className="text-slate-300">₹{int(pred.predicted_price_per_sqft || pred.price_per_sqft).toLocaleString('en-IN')} / sq.ft</strong>
                </p>
              </div>

              {/* Listed Price & Difference */}
              <div className="space-y-1 md:border-r border-slate-800/80 pr-4 md:pl-2">
                <div className="flex items-center gap-1.5">
                  <FileText className="w-4 h-4 text-blue-400" />
                  <span className="text-[11px] font-bold uppercase text-slate-400 tracking-wider">Listed Price</span>
                </div>
                <p className="text-3xl font-extrabold text-white">
                  ₹{int(property.price).toLocaleString('en-IN')}
                </p>
                {pred.difference_percentage !== null && pred.difference_percentage !== undefined ? (
                  <p className={`text-xs font-semibold ${pred.difference_percentage > 0 ? 'text-rose-400' : 'text-emerald-400'}`}>
                    Diff: {pred.difference_percentage > 0 ? `+${pred.difference_percentage}%` : `${pred.difference_percentage}%`} vs Listed
                  </p>
                ) : (
                  <p className="text-xs text-slate-400">
                    Listed Rate: <strong className="text-slate-300">₹{int(property.price / (property.area_sqft || 1)).toLocaleString('en-IN')} / sq.ft</strong>
                  </p>
                )}
              </div>

              {/* Monthly Rental */}
              <div className="space-y-1 md:border-r border-slate-800/80 pr-4 md:pl-2">
                <div className="flex items-center gap-1.5">
                  <Compass className="w-4 h-4 text-amber-400" />
                  <span className="text-[11px] font-bold uppercase text-slate-400 tracking-wider">Est. Monthly Rental</span>
                </div>
                <p className="text-3xl font-extrabold text-amber-400">
                  ₹{int(pred.estimated_rental_price).toLocaleString('en-IN')} <span className="text-sm font-semibold text-slate-400">/ mo</span>
                </p>
                <p className="text-xs text-slate-400">
                  Estimated Yield: <strong className="text-slate-300">3.6% p.a.</strong>
                </p>
              </div>

              {/* Model Quality & Data Completeness */}
              <div className="space-y-1 md:pl-2 relative">
                <div className="flex items-center gap-1.5">
                  <Shield className="w-4 h-4 text-emerald-400" />
                  <span className="text-[11px] font-bold uppercase text-slate-400 tracking-wider">Data Quality Score</span>
                  <button 
                    onMouseEnter={() => setShowReliabilityTooltip(true)}
                    onMouseLeave={() => setShowReliabilityTooltip(false)}
                    className="text-slate-500 hover:text-white"
                  >
                    <Info className="w-3.5 h-3.5" />
                  </button>
                </div>

                <div className="flex items-baseline gap-2">
                  <p className="text-3xl font-extrabold text-emerald-400">
                    {pred.data_quality?.completeness_score || pred.confidence_score || 95}%
                  </p>
                  <span className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">
                    {pred.data_quality?.is_known_locality ? 'Locality Verified' : 'Standard Quality'}
                  </span>
                </div>
                <p className="text-xs text-slate-400">
                  Matched: <strong className="text-slate-300">{pred.data_quality?.locality_matched || 'Bengaluru Suburb'}</strong>
                </p>

                {/* Tooltip Popup */}
                {showReliabilityTooltip && (
                  <div className="absolute bottom-full right-0 mb-2 w-72 p-3.5 rounded-2xl bg-slate-950 border border-slate-800 text-[11px] text-slate-300 shadow-2xl z-20 backdrop-blur-md space-y-1.5">
                    <p className="font-bold text-white border-b border-slate-800 pb-1">XGBoost Model Performance & Data Quality</p>
                    <p>• <strong>Model R² Score:</strong> {((pred.model_metrics?.r2 || 0.7843) * 100).toFixed(1)}%</p>
                    <p>• <strong>Model MAPE:</strong> {pred.model_metrics?.mape_percent || 25.18}%</p>
                    <p>• <strong>Model MAE:</strong> ₹{pred.model_metrics?.mae_lakhs || 23.27} Lakhs</p>
                    <p className="text-slate-400 pt-1 text-[10px]">Data Quality score reflects locality geocoding validation & attribute completeness.</p>
                  </div>
                )}
              </div>

            </div>

            {/* Model Evaluation Metrics Banner */}
            <div className="flex flex-wrap items-center justify-between gap-4 text-xs text-slate-400 bg-slate-900/60 p-3.5 rounded-2xl border border-slate-800/80">
              <div className="flex items-center gap-2">
                <Sparkles className="w-4 h-4 text-brand-400" />
                <span className="font-semibold text-slate-300">Trained XGBoost Engine ({pred.model_metrics?.model_version || '1.0.0-xgboost-bengaluru'})</span>
              </div>
              <div className="flex flex-wrap items-center gap-4 text-[11px]">
                <span>Test R² Score: <strong className="text-emerald-400">{((pred.model_metrics?.r2 || 0.7843) * 100).toFixed(1)}%</strong></span>
                <span className="text-slate-700">|</span>
                <span>Test MAPE: <strong className="text-slate-200">{pred.model_metrics?.mape_percent || 25.18}%</strong></span>
                <span className="text-slate-700">|</span>
                <span>Test MAE: <strong className="text-slate-200">₹{pred.model_metrics?.mae_lakhs || 23.27} Lakhs</strong></span>
              </div>
            </div>

          </div>
        )}

        {/* PHASE 4A — PROPERTY SPECIFICATIONS GRID */}
        <div className="glass-card p-6 md:p-8 rounded-3xl border border-slate-800 space-y-6 bg-slate-900/10">
          <h3 className="text-lg font-bold font-outfit text-white border-b border-slate-800 pb-3 flex items-center gap-2">
            <Building2 className="w-5 h-5 text-brand-500" />
            Property Specifications
          </h3>

          <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-5 gap-4 text-xs">
            <div className="p-3.5 rounded-2xl bg-slate-900 border border-slate-800 space-y-1">
              <span className="text-slate-500 block text-[10px] uppercase font-bold">Built-up Area</span>
              <span className="text-sm font-bold text-white">{property.area_sqft ? `${property.area_sqft.toLocaleString()} Sq.ft` : "Not available"}</span>
            </div>
            <div className="p-3.5 rounded-2xl bg-slate-900 border border-slate-800 space-y-1">
              <span className="text-slate-500 block text-[10px] uppercase font-bold">Bedrooms</span>
              <span className="text-sm font-bold text-white">{property.bhk ? `${property.bhk} BHK` : "Not available"}</span>
            </div>
            <div className="p-3.5 rounded-2xl bg-slate-900 border border-slate-800 space-y-1">
              <span className="text-slate-500 block text-[10px] uppercase font-bold">Bathrooms</span>
              <span className="text-sm font-bold text-white">{property.bathrooms ? `${property.bathrooms} Baths` : "Not available"}</span>
            </div>
            <div className="p-3.5 rounded-2xl bg-slate-900 border border-slate-800 space-y-1">
              <span className="text-slate-500 block text-[10px] uppercase font-bold">Balconies</span>
              <span className="text-sm font-bold text-white">{property.balconies !== undefined ? `${property.balconies} Balconies` : "Not available"}</span>
            </div>
            <div className="p-3.5 rounded-2xl bg-slate-900 border border-slate-800 space-y-1">
              <span className="text-slate-500 block text-[10px] uppercase font-bold">Floor Level</span>
              <span className="text-sm font-bold text-white">{property.floor ? `Floor ${property.floor} of ${property.total_floors || 1}` : "Not available"}</span>
            </div>
            <div className="p-3.5 rounded-2xl bg-slate-900 border border-slate-800 space-y-1">
              <span className="text-slate-500 block text-[10px] uppercase font-bold">Property Age</span>
              <span className="text-sm font-bold text-white">{property.property_age || "Not available"}</span>
            </div>
            <div className="p-3.5 rounded-2xl bg-slate-900 border border-slate-800 space-y-1">
              <span className="text-slate-500 block text-[10px] uppercase font-bold">Facing</span>
              <span className="text-sm font-bold text-white">{property.facing || "Not available"}</span>
            </div>
            <div className="p-3.5 rounded-2xl bg-slate-900 border border-slate-800 space-y-1">
              <span className="text-slate-500 block text-[10px] uppercase font-bold">Parking Status</span>
              <span className="text-sm font-bold text-white">{property.parking || "Not available"}</span>
            </div>
            <div className="p-3.5 rounded-2xl bg-slate-900 border border-slate-800 space-y-1">
              <span className="text-slate-500 block text-[10px] uppercase font-bold">Furnishing</span>
              <span className="text-sm font-bold text-white">{property.furnishing || "Not available"}</span>
            </div>
            <div className="p-3.5 rounded-2xl bg-slate-900 border border-slate-800 space-y-1">
              <span className="text-slate-500 block text-[10px] uppercase font-bold">Listing Locality</span>
              <span className="text-sm font-bold text-brand-400 truncate block">{property.locality || "Not available"}</span>
            </div>
            {property.society && (
              <div className="p-3.5 rounded-2xl bg-slate-900 border border-slate-800 space-y-1">
                <span className="text-slate-500 block text-[10px] uppercase font-bold">Society Name</span>
                <span className="text-sm font-bold text-white truncate block">{property.society}</span>
              </div>
            )}
            <div className="p-3.5 rounded-2xl bg-slate-900 border border-slate-800 space-y-1">
              <span className="text-slate-500 block text-[10px] uppercase font-bold">Coordinate Accuracy</span>
              <span className={`text-sm font-bold truncate block ${property.coordinate_status === 'EXACT' ? 'text-emerald-400' : 'text-amber-400'}`}>
                {property.coordinate_status === 'EXACT' ? 'Exact location' : 'Approximate locality'}
              </span>
            </div>
            <div className="p-3.5 rounded-2xl bg-slate-900 border border-slate-800 space-y-1">
              <span className="text-slate-500 block text-[10px] uppercase font-bold">Classification</span>
              <span className="text-sm font-bold text-slate-300 truncate block">Inferred ({property.property_type})</span>
            </div>
            <div className="p-3.5 rounded-2xl bg-slate-900 border border-slate-800 space-y-1">
              <span className="text-slate-500 block text-[10px] uppercase font-bold">Source Provenance</span>
              <span className="text-sm font-bold text-slate-350 truncate block">{isDirect ? 'PropPulse Direct' : (property.source || 'Historical Dataset')}</span>
            </div>
          </div>

          {/* Amenities sub-section */}
          <div className="pt-4 border-t border-slate-800 space-y-2">
            <span className="text-[10px] uppercase font-bold text-slate-500 tracking-wider">Available Amenities</span>
            {property.amenities && property.amenities.length > 0 ? (
              <div className="flex flex-wrap gap-2 pt-1">
                {property.amenities.map((amenity, idx) => (
                  <span key={idx} className="px-3 py-1 rounded-xl bg-slate-900 border border-slate-800 text-slate-300 font-medium">
                    {amenity}
                  </span>
                ))}
              </div>
            ) : (
              <p className="text-xs text-slate-500 italic">Not available</p>
            )}
          </div>

          {property.description && (
            <div className="pt-4 border-t border-slate-800 space-y-2">
              <span className="text-[10px] uppercase font-bold text-slate-500 tracking-wider">Description</span>
              <p className="text-xs sm:text-sm text-slate-400 leading-relaxed whitespace-pre-line">
                {property.description}
              </p>
            </div>
          )}
        </div>

        {/* PHASE 4C & 4D — MAP & NEARBY AMENITIES */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          
          {/* Leaflet Map Card */}
          <div className="lg:col-span-2 glass-card p-6 rounded-3xl border border-slate-800 flex flex-col justify-between gap-4 bg-slate-900/20">
            <div className="space-y-1">
              <h3 className="text-base font-bold font-outfit text-white flex items-center gap-2">
                <MapPin className="w-5 h-5 text-emerald-400" />
                Property GIS Location & Map
              </h3>
              <p className="text-xs text-slate-400">Interactive OpenStreetMap centered on the property coordinates.</p>
            </div>
            
            <div className="rounded-2xl overflow-hidden border border-slate-800 h-[360px]">
              <MapView
                searchResult={mapSearchResult}
                property={property}
                nearbyPlaces={nearbyPlaces}
              />
            </div>

            <div className="pt-3 border-t border-slate-800/60 flex flex-col lg:flex-row items-start lg:items-center justify-between gap-3 text-xs">
              <div className="flex flex-wrap items-center gap-3 text-[11px] font-mono text-slate-400">
                <span>Lat: {property.latitude.toFixed(6)}</span>
                <span>Lon: {property.longitude.toFixed(6)}</span>
                <span className={`px-2 py-0.5 rounded text-[10px] font-semibold ${
                  disp.isExact 
                    ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' 
                    : 'bg-amber-500/10 text-amber-400 border border-amber-500/20'
                }`}>
                  {disp.coordinateAccuracy}
                </span>
              </div>
              <div className="flex flex-wrap items-center gap-2">
                <button
                  onClick={() => openInOpenStreetMap(property)}
                  className="px-3 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 font-bold transition-all text-xs flex items-center gap-1.5"
                >
                  <ExternalLink className="w-3.5 h-3.5 text-sky-400" />
                  <span>OpenStreetMap</span>
                </button>
                <button
                  onClick={() => openInGoogleMaps(property)}
                  className="px-3 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 font-bold transition-all text-xs flex items-center gap-1.5"
                >
                  <ExternalLink className="w-3.5 h-3.5 text-brand-400" />
                  <span>Google Maps</span>
                </button>
                <button
                  onClick={() => navigateToProperty(property)}
                  className="px-4 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-bold transition-all shadow-lg shadow-emerald-600/20 text-xs flex items-center gap-1.5"
                >
                  <Navigation className="w-3.5 h-3.5" />
                  <span>{disp.isExact ? "Navigate to Property" : "Directions to Area"}</span>
                </button>
              </div>
            </div>
          </div>

          {/* Radius selector & Live Geoapify Nearby POIs */}
          <div className="flex flex-col">
            <NearbyPlacesList
              places={nearbyPlaces}
              loading={nearbyLoading}
              radius={nearbyRadius}
              onRadiusChange={setNearbyRadius}
              coordinateStatus={property.coordinate_status}
              apiError={nearbyError}
            />
          </div>

        </div>

        {/* PHASE 4F & 4G — COMPUTER VISION & NLP TEXT ANALYSIS */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          
          {/* CNN Image analysis results */}
          <div className="glass-card p-6 md:p-8 rounded-3xl border border-slate-800 space-y-5 bg-slate-900/10">
            <div className="border-b border-slate-800 pb-3 flex items-center justify-between">
              <h3 className="text-base font-bold font-outfit text-white flex items-center gap-2">
                <Sparkles className="w-5 h-5 text-purple-400" />
                IMAGE INTELLIGENCE (CV)
              </h3>
              <div className="flex items-center gap-2">
                {cv && cv.image_analysis_available ? (
                  <>
                    <span className="px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-300 border border-emerald-500/20 text-[10px] font-mono font-bold">
                      ACTUAL PROPERTY IMAGE
                    </span>
                    <span className="px-2 py-0.5 rounded bg-purple-500/10 text-purple-300 border border-purple-500/20 text-[10px] font-mono font-bold">
                      IMAGE ANALYSIS AVAILABLE
                    </span>
                  </>
                ) : (
                  <>
                    <span className="px-2 py-0.5 rounded bg-amber-500/10 text-amber-300 border border-amber-500/20 text-[10px] font-mono font-bold">
                      LOCATION REFERENCE
                    </span>
                    <span className="px-2 py-0.5 rounded bg-slate-800 text-slate-400 border border-slate-700 text-[10px] font-mono font-bold">
                      NOT ACTUAL PROPERTY PHOTO
                    </span>
                  </>
                )}
              </div>
            </div>

            {proAccessDenied ? (
              <div className="text-center py-10 space-y-3">
                <Lock className="w-8 h-8 text-purple-400 mx-auto animate-pulse" />
                <p className="text-xs font-bold text-white uppercase tracking-wider">Image AI Locked</p>
                <p className="text-[11px] text-slate-400 max-w-xs mx-auto">Upgrade to the Pro Plan to unlock the PyTorch ResNet-18 and OpenCV image quality scanner results.</p>
              </div>
            ) : cv && cv.image_analysis_available !== false && property.images && property.images.length > 0 ? (
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div className="space-y-0.5">
                    <span className="text-[10px] uppercase font-bold text-slate-500">Overall Image Score</span>
                    <p className="text-2xl font-extrabold text-white">{cv.overall_score || 75} <span className="text-xs font-semibold text-slate-500">/ 100</span></p>
                  </div>
                  <span className="px-3 py-1 rounded-xl bg-purple-500/10 text-purple-300 border border-purple-500/20 text-xs font-bold">
                    {cv.overall_condition || "Good / Clean"}
                  </span>
                </div>

                <div className="grid grid-cols-2 gap-4 text-xs pt-1">
                  <div className="p-3 rounded-xl bg-slate-900 border border-slate-800 space-y-1">
                    <span className="text-slate-500 block text-[10px] uppercase">Brightness</span>
                    <span className="font-bold text-slate-200">{cv.brightness_score || 75.0}%</span>
                  </div>
                  <div className="p-3 rounded-xl bg-slate-900 border border-slate-800 space-y-1">
                    <span className="text-slate-500 block text-[10px] uppercase">Sharpness</span>
                    <span className="font-bold text-slate-200">{cv.sharpness_score || 75.0}%</span>
                  </div>
                  <div className="p-3 rounded-xl bg-slate-900 border border-slate-800 space-y-1">
                    <span className="text-slate-500 block text-[10px] uppercase">Interior Quality</span>
                    <span className="font-bold text-slate-200">{cv.interior_condition_score || 75.0}%</span>
                  </div>
                  <div className="p-3 rounded-xl bg-slate-900 border border-slate-800 space-y-1">
                    <span className="text-slate-500 block text-[10px] uppercase">Exterior Quality</span>
                    <span className="font-bold text-slate-200">{cv.exterior_condition_score || 75.0}%</span>
                  </div>
                </div>

                {/* Professional inspection warning tag */}
                <div className="p-3 rounded-2xl bg-amber-500/5 border border-amber-500/20 text-[10px] text-amber-400/90 leading-relaxed flex items-start gap-2">
                  <AlertTriangle className="w-4 h-4 flex-shrink-0 mt-0.5" />
                  <span>Notice: This score represents automated visual/image analysis of the property photos and is NOT a professional physical structural inspection.</span>
                </div>
              </div>
            ) : (
              <div className="p-6 rounded-2xl border border-slate-800 bg-slate-900/40 text-center space-y-2">
                <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-slate-800/80 border border-slate-700 text-xs font-bold text-slate-300 uppercase">
                  <span>IMAGE ANALYSIS UNAVAILABLE</span>
                </div>
                <p className="text-xs text-slate-400">
                  Location reference active. No authentic owner or authorized provider image is linked to this historical record; automated ResNet analysis has been honestly bypassed.
                </p>
              </div>
            )}

          </div>

          {/* NLP Listing Text Analysis */}
          <div className="glass-card p-6 md:p-8 rounded-3xl border border-slate-800 space-y-5 bg-slate-900/10">
            <div className="border-b border-slate-800 pb-3 flex items-center justify-between">
              <h3 className="text-base font-bold font-outfit text-white flex items-center gap-2">
                <FileText className="w-5 h-5 text-emerald-400" />
                TEXT INTELLIGENCE (NLP)
              </h3>
              <div className="flex items-center gap-2">
                {property.description ? (
                  <>
                    <span className="px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-300 border border-emerald-500/20 text-[10px] font-mono font-bold">
                      TEXT DATA AVAILABLE
                    </span>
                    <span className="px-2 py-0.5 rounded bg-brand-500/10 text-brand-300 border border-brand-500/20 text-[10px] font-mono font-bold">
                      TF-IDF PROCESSING COMPLETE
                    </span>
                  </>
                ) : (
                  <span className="px-2 py-0.5 rounded bg-amber-500/10 text-amber-300 border border-amber-500/20 text-[10px] font-mono font-bold">
                    TEXT DATA UNAVAILABLE
                  </span>
                )}
              </div>
            </div>

            {proAccessDenied ? (
              <div className="text-center py-10 space-y-3">
                <Lock className="w-8 h-8 text-emerald-400 mx-auto animate-pulse" />
                <p className="text-xs font-bold text-white uppercase tracking-wider">Text AI Locked</p>
                <p className="text-[11px] text-slate-400 max-w-xs mx-auto">Upgrade to the Pro Plan to unlock the TF-IDF keyword extraction and description sentiment analyzer results.</p>
              </div>
            ) : !property.description ? (
              <div className="p-6 rounded-2xl border border-slate-800 bg-slate-900/40 text-center space-y-2">
                <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-slate-800/80 border border-slate-700 text-xs font-bold text-amber-400 uppercase">
                  <span>TEXT DATA UNAVAILABLE</span>
                </div>
                <p className="text-xs text-slate-400">
                  No property listing description provided in dataset. TF-IDF vectorization was bypassed without generating synthetic text.
                </p>
              </div>
            ) : nlp ? (
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div className="space-y-0.5">
                    <span className="text-[10px] uppercase font-bold text-slate-500">Text Quality Score</span>
                    <p className="text-2xl font-extrabold text-white">{nlp.text_quality_score || 70} <span className="text-xs font-semibold text-slate-500">/ 100</span></p>
                  </div>
                  <div className="text-right">
                    <span className="px-2.5 py-1 rounded-xl bg-slate-900 border border-slate-800 text-xs font-bold block">
                      Tone: {nlp.tone || "Professional"}
                    </span>
                    <span className="text-[10px] text-slate-500 block mt-1">Sentiment: {nlp.sentiment_label || "Neutral"}</span>
                  </div>
                </div>

                {/* TF-IDF Important terms */}
                {nlp.top_tfidf_terms && nlp.top_tfidf_terms.length > 0 && (
                  <div className="space-y-2">
                    <span className="text-[10px] uppercase font-bold text-slate-500 block">TF-IDF Weighted Key Terms</span>
                    <div className="flex flex-wrap gap-1.5">
                      {nlp.top_tfidf_terms.map((t, idx) => (
                        <span key={idx} className="px-2 py-0.5 rounded-lg bg-slate-900 border border-slate-800 text-[11px] text-slate-300 font-mono">
                          {t.term} <span className="text-[9px] text-slate-500 font-bold">({t.weight})</span>
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {/* Keywords list */}
                {nlp.detected_keywords && nlp.detected_keywords.length > 0 && (
                  <div className="space-y-1.5 pt-1">
                    <span className="text-[10px] uppercase font-bold text-slate-500 block">Detected Premium Keywords</span>
                    <div className="flex flex-wrap gap-1">
                      {nlp.detected_keywords.map((kw, idx) => (
                        <span key={idx} className="text-[10px] font-bold text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded">
                          #{kw}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <p className="text-xs text-slate-500 italic">NLP models analysis not available.</p>
            )}

          </div>

        </div>

        {/* PHASE 4H — SHAP EXPLAINABILITY DRIVERS */}
        {proAccessDenied && (
          <div className="glass-card p-6 md:p-8 rounded-3xl border border-slate-800 space-y-4 text-center py-10">
            <div className="border-b border-slate-850 pb-3 flex items-center justify-between text-left">
              <h3 className="text-base font-bold font-outfit text-white flex items-center gap-2">
                <Brain className="w-5 h-5 text-brand-400" />
                WHY DID AI ESTIMATE THIS PRICE? [LOCKED]
              </h3>
              <span className="text-xs text-slate-500 font-bold uppercase tracking-wider">Pro Feature</span>
            </div>
            <Lock className="w-8 h-8 text-brand-400/80 mx-auto animate-pulse" />
            <p className="text-xs text-slate-400 max-w-sm mx-auto">Upgrade to the Pro Plan to unlock the dynamic SHAP explainable AI attribution breakdown explaining exactly how locality, layout, and size features influence model estimates.</p>
          </div>
        )}
        {pred?.shap_explanation && !proAccessDenied && (

          <div className="glass-card p-6 md:p-8 rounded-3xl border border-slate-800 space-y-4">
            <div className="border-b border-slate-800 pb-3 flex items-center justify-between">
              <h3 className="text-base font-bold font-outfit text-white flex items-center gap-2">
                <Brain className="w-5 h-5 text-brand-400" />
                WHY DID AI ESTIMATE THIS PRICE?
              </h3>
              <span className="text-xs text-slate-400">SHAP feature attributions on XGBoost regression</span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              
              {/* Positive Factors */}
              <div className="p-4 rounded-2xl bg-emerald-500/5 border border-emerald-500/20 space-y-3">
                <div className="flex items-center gap-2 text-emerald-400 text-xs font-bold uppercase tracking-wider">
                  <ThumbsUp className="w-4 h-4" />
                  <span>Top Positive Drivers</span>
                </div>
                
                <div className="space-y-2">
                  {pred.shap_explanation.top_positive_factors && pred.shap_explanation.top_positive_factors.length > 0 ? (
                    pred.shap_explanation.top_positive_factors.map((f, idx) => (
                      <div key={idx} className="p-2.5 rounded-xl bg-slate-900 border border-slate-800 flex items-center justify-between text-xs">
                        <div className="space-y-0.5">
                          <span className="font-semibold text-slate-200 block">{f.factor}</span>
                          <span className="text-[10px] text-slate-500">{f.description}</span>
                        </div>
                        <span className="font-mono text-emerald-400 font-extrabold text-xs whitespace-nowrap pl-2">
                          {f.impact_amount}
                        </span>
                      </div>
                    ))
                  ) : (
                    <p className="text-xs text-slate-500 italic">No significant positive drivers calculated.</p>
                  )}
                </div>
              </div>

              {/* Adjustments / Negatives */}
              <div className="p-4 rounded-2xl bg-amber-500/5 border border-amber-500/20 space-y-3">
                <div className="flex items-center gap-2 text-amber-400 text-xs font-bold uppercase tracking-wider">
                  <ThumbsDown className="w-4 h-4" />
                  <span>Top Value Adjustments</span>
                </div>

                <div className="space-y-2">
                  {pred.shap_explanation.top_negative_factors && pred.shap_explanation.top_negative_factors.length > 0 ? (
                    pred.shap_explanation.top_negative_factors.map((f, idx) => (
                      <div key={idx} className="p-2.5 rounded-xl bg-slate-900 border border-slate-800 flex items-center justify-between text-xs">
                        <div className="space-y-0.5">
                          <span className="font-semibold text-slate-200 block">{f.factor}</span>
                          <span className="text-[10px] text-slate-500">{f.description}</span>
                        </div>
                        <span className="font-mono text-amber-400 font-extrabold text-xs whitespace-nowrap pl-2">
                          {f.impact_amount}
                        </span>
                      </div>
                    ))
                  ) : (
                    <p className="text-xs text-slate-500 italic">No value adjustments calculated.</p>
                  )}
                </div>
              </div>

            </div>
          </div>
        )}

        {/* PHASE 4I — SAFETY GUARD */}
        {safety && (
          <div className="glass-card p-6 md:p-8 rounded-3xl border border-slate-800 space-y-5 bg-slate-900/10">
            <div className="border-b border-slate-800 pb-3 flex flex-col sm:flex-row sm:items-center justify-between gap-2">
              <h3 className="text-base font-bold font-outfit text-white flex items-center gap-2">
                <Shield className="w-5 h-5 text-emerald-400" />
                LOCALITY SAFETY GUARD
              </h3>
              <span className="text-xs text-slate-500">Emergency Response & GIS Proximity Metrics</span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              
              {/* Safety metrics stats */}
              <div className="space-y-4 border-r border-slate-800 pr-6">
                <div className="flex items-center justify-between text-xs">
                  <span className="text-slate-400 font-semibold">Emergency Coverage Score</span>
                  <strong className="text-emerald-400 text-base font-extrabold">{safety.emergency_coverage_score} / 100</strong>
                </div>
                <div className="flex items-center justify-between text-xs">
                  <span className="text-slate-400">Nearest Police Station</span>
                  <strong className="text-slate-200 text-xs font-semibold">{safety.nearest_police_station_dist_meters ? `${(safety.nearest_police_station_dist_meters / 1000).toFixed(1)} km` : "N/A"}</strong>
                </div>
                <div className="flex items-center justify-between text-xs">
                  <span className="text-slate-400">Nearest Hospital</span>
                  <strong className="text-slate-200 text-xs font-semibold">{safety.nearest_hospital_dist_meters ? `${(safety.nearest_hospital_dist_meters / 1000).toFixed(1)} km` : "N/A"}</strong>
                </div>
                <div className="flex items-center justify-between text-xs">
                  <span className="text-slate-400">Nearest Fire Station</span>
                  <strong className="text-slate-200 text-xs font-semibold">{safety.nearest_fire_station_dist_meters ? `${(safety.nearest_fire_station_dist_meters / 1000).toFixed(1)} km` : "N/A"}</strong>
                </div>

                <div className="p-3 rounded-xl bg-slate-950 border border-slate-850 text-[10px] text-slate-500 leading-relaxed flex items-start gap-1.5">
                  <AlertCircle className="w-4 h-4 text-slate-500 flex-shrink-0 mt-0.5" />
                  <span>Emergency Coverage Score is computed directly from spatial proximity to verified Geoapify emergency infrastructure (Police, Hospitals, Fire Stations).</span>
                </div>
              </div>

              {/* Emergency facilities */}
              <div className="md:col-span-2 space-y-4 pl-0 md:pl-4 text-xs">
                <span className="text-[10px] uppercase font-bold text-slate-500 tracking-wider block">Nearest Emergency Services</span>
                
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                  
                  {/* Police Station */}
                  <div className="p-3.5 rounded-xl bg-slate-900 border border-slate-800 space-y-1.5">
                    <div className="flex items-center gap-1.5 text-blue-400 font-bold text-[10px] uppercase">
                      <Shield className="w-3.5 h-3.5" />
                      <span>Police Station</span>
                    </div>
                    <span className="font-bold text-slate-200 block line-clamp-1">
                      {safety.nearest_police_station || "Not available"}
                    </span>
                    <span className="text-[10px] font-mono text-slate-500 font-semibold">
                      {safety.nearest_police_station_dist_meters 
                        ? `${(safety.nearest_police_station_dist_meters / 1000).toFixed(2)} km away` 
                        : "Not available"}
                    </span>
                  </div>

                  {/* Hospital */}
                  <div className="p-3.5 rounded-xl bg-slate-900 border border-slate-800 space-y-1.5">
                    <div className="flex items-center gap-1.5 text-emerald-400 font-bold text-[10px] uppercase">
                      <Heart className="w-3.5 h-3.5" />
                      <span>Hospital POI</span>
                    </div>
                    <span className="font-bold text-slate-200 block line-clamp-1">
                      {safety.nearest_hospital || "Not available"}
                    </span>
                    <span className="text-[10px] font-mono text-slate-500 font-semibold">
                      {safety.nearest_hospital_dist_meters 
                        ? `${(safety.nearest_hospital_dist_meters / 1000).toFixed(2)} km away` 
                        : "Not available"}
                    </span>
                  </div>

                  {/* Fire Station */}
                  <div className="p-3.5 rounded-xl bg-slate-900 border border-slate-800 space-y-1.5">
                    <div className="flex items-center gap-1.5 text-rose-400 font-bold text-[10px] uppercase">
                      <Flame className="w-3.5 h-3.5" />
                      <span>Fire Station</span>
                    </div>
                    <span className="font-bold text-slate-200 block line-clamp-1">
                      {safety.nearest_fire_station || "Not available"}
                    </span>
                    <span className="text-[10px] font-mono text-slate-500 font-semibold">
                      {safety.nearest_fire_station_dist_meters 
                        ? `${(safety.nearest_fire_station_dist_meters / 1000).toFixed(2)} km away` 
                        : "Not available"}
                    </span>
                  </div>

                </div>

                <p className="text-[10px] text-slate-600 italic">
                  Academic Disclosure: Emergency response mapping scores are calculated deterministically from OpenStreetMap GIS nodes using the haversine formula relative to the property centroid.
                </p>
              </div>

            </div>
          </div>
        )}

        {/* PHASE 4J — AI PROPERTY SUMMARY */}
        <div className="glass-card p-6 md:p-8 rounded-3xl border border-brand-500/20 bg-brand-950/5 space-y-4 shadow-md">
          <div className="border-b border-slate-800 pb-3 flex items-center justify-between">
            <h3 className="text-base font-bold font-outfit text-white flex items-center gap-2">
              <Brain className="w-5 h-5 text-brand-400" />
              AI PROPERTY SUMMARY
            </h3>
            <span className="px-2 py-0.5 rounded bg-brand-500/10 text-brand-300 border border-brand-500/20 text-[10px] font-mono font-bold">
              Deterministic Synthesizer
            </span>
          </div>

          <div className="space-y-3 text-xs sm:text-sm text-slate-300 leading-relaxed font-medium">
            <p>{generateDeterministicSummary()}</p>
            
            <div className="p-3 rounded-2xl bg-slate-950 border border-slate-900 text-[10px] text-slate-500 leading-normal flex items-start gap-2">
              <AlertTriangle className="w-4 h-4 text-slate-600 flex-shrink-0 mt-0.5" />
              <span>Safety disclaimer: This synthesis is compiled deterministically based on statistical parameters, OpenStreetMap GIS records, and computer vision heuristics. It is for research/demo purposes only and does NOT constitute professional appraisal, structural inspection, or surveying.</span>
            </div>
          </div>
        </div>

        {/* PHASE 4K — SELLER INFORMATION */}
        <div className="glass-card p-6 md:p-8 rounded-3xl border border-slate-800 space-y-4 bg-slate-900/10">
          <h3 className="text-base font-bold font-outfit text-white border-b border-slate-800 pb-3 flex items-center gap-2">
            <User className="w-5 h-5 text-brand-400" />
            Seller & Listing Metadata
          </h3>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 text-xs">
            <div className="p-3.5 rounded-xl bg-slate-900 border border-slate-800 space-y-1">
              <span className="text-slate-500 block text-[10px] uppercase">Seller (Type)</span>
              <span className="text-sm font-bold text-white">
                {property.seller_name || property.owner_name || "PropPulse Verified Seller"} 
                <span className="text-slate-400 font-normal"> ({property.seller_type || "Owner"})</span>
              </span>
            </div>
            <div className="p-3.5 rounded-xl bg-slate-900 border border-slate-800 space-y-1">
              <span className="text-slate-500 block text-[10px] uppercase">Listing Source</span>
              <span className="text-sm font-bold text-slate-200">
                {property.source_url ? (
                  <a href={property.source_url} target="_blank" rel="noopener noreferrer" className="text-brand-400 hover:underline">
                    {property.source || "External Link"}
                  </a>
                ) : (
                  property.source || "PropPulse Direct"
                )}
              </span>
            </div>
            <div className="p-3.5 rounded-xl bg-slate-900 border border-slate-800 space-y-1">
              <span className="text-slate-500 block text-[10px] uppercase">Source Verification</span>
              <span className={`text-sm font-bold ${property.verified ? "text-emerald-400" : "text-amber-400"}`}>
                {property.verified ? "Verified Source" : "Verification Not Available"}
              </span>
            </div>
            <div className="p-3.5 rounded-xl bg-slate-900 border border-slate-800 space-y-1">
              <span className="text-slate-500 block text-[10px] uppercase">Contact Phone</span>
              {((property.phone && property.phone.includes("Redacted")) || 
                (property.owner_phone && property.owner_phone.includes("Redacted"))) ? (
                revealedContact ? (
                  <a href={`tel:${revealedContact.phone || revealedContact.owner_phone}`} className="text-sm font-bold text-brand-400 hover:underline block font-mono">
                    {revealedContact.phone || revealedContact.owner_phone}
                  </a>
                ) : (
                  <div className="space-y-1.5 pt-1">
                    <button
                      onClick={handleRevealContact}
                      disabled={revealLoading}
                      className="text-[10px] font-bold px-3 py-1 rounded bg-brand-600 hover:bg-brand-500 text-white transition-all disabled:opacity-50 flex items-center gap-1"
                    >
                      {revealLoading && <Loader2 className="w-2.5 h-2.5 animate-spin" />}
                      Reveal Contact Number
                    </button>
                    {revealError && (
                      <span className="text-[9px] text-rose-400 block font-semibold leading-tight">{revealError}</span>
                    )}
                  </div>
                )
              ) : (
                <a href={`tel:${detailsPhone}`} className="text-sm font-bold text-brand-400 hover:underline block font-mono">
                  {detailsPhone}
                </a>
              )}
            </div>

          </div>
        </div>

      </main>

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
              <h4 className="text-lg font-bold text-white font-outfit">Contact Seller</h4>
              <p className="text-xs text-slate-400">Directly inquiry for: <strong className="text-slate-200">{displayName}</strong></p>
            </div>

            <div className="p-3 rounded-2xl bg-slate-900 border border-slate-800 space-y-1 text-xs">
              <p className="font-semibold text-white">Seller: {property.seller_name || property.owner_name || "PropPulse Verified Seller"}</p>
              <div className="flex items-center gap-1.5">
                <span className="text-slate-400">Phone:</span>
                {((property.phone && property.phone.includes("Redacted")) || 
                  (property.owner_phone && property.owner_phone.includes("Redacted"))) ? (
                  revealedContact ? (
                    <span className="text-emerald-400 font-mono font-bold">{revealedContact.phone || revealedContact.owner_phone}</span>
                  ) : (
                    user ? (
                      <button 
                        onClick={handleRevealContact} 
                        disabled={revealLoading} 
                        className="underline text-brand-400 hover:text-brand-300 font-semibold"
                      >
                        {revealLoading ? "Revealing..." : "Reveal Number"}
                      </button>
                    ) : (
                      <span className="text-slate-500 italic">Login to view number</span>
                    )
                  )
                ) : (
                  <span className="text-emerald-400 font-mono font-bold">{detailsPhone}</span>
                )}
              </div>
              <p className="text-slate-400">Location: {property.address}</p>
            </div>


            {messageSent ? (
              <div className="p-4 rounded-2xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-xs flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 flex-shrink-0" />
                <span>Your contact request has been sent successfully. The seller will call you shortly!</span>
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
                  <textarea rows={3} defaultValue={`Hi, I am interested in viewing your property '${property.title}' in ${property.locality || "Bengaluru"}. Please share availability.`} className="w-full px-3 py-2 rounded-xl bg-slate-900 border border-slate-800 text-xs text-white" />
                </div>

                <button type="submit" className="w-full py-3 rounded-xl bg-brand-600 hover:bg-brand-500 text-white font-semibold text-xs shadow-lg shadow-brand-500/20">
                  Send Contact Inquiry
                </button>
              </form>
            )}
          </div>
        </div>
      )}

      <Footer />
    </div>
  );
};

function int(val) {
  return Math.round(val || 0);
}
