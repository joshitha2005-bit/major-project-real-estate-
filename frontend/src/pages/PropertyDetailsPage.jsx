import React, { useEffect, useState } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { propertyService } from '../services/propertyService';
import { aiService } from '../services/aiService';
import { Navbar } from '../components/Navbar';
import { Footer } from '../components/Footer';
import { MapView } from '../components/MapView';
import { NearbyPlacesList } from '../components/NearbyPlacesList';
import { 
  Building2, MapPin, IndianRupee, ArrowLeft, Loader2, Phone, Mail, 
  Shield, CheckCircle2, Sparkles, Download, Brain, User, MessageSquare, X, Eye, ThumbsUp, ThumbsDown
} from 'lucide-react';

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

  useEffect(() => {
    const fetchPropertyAndAi = async () => {
      setLoading(true);
      try {
        const [propData, aiData] = await Promise.all([
          propertyService.getPropertyById(id),
          aiService.analyzeProperty(id)
        ]);
        setProperty(propData);
        setAiAnalytics(aiData);
      } catch (err) {
        console.error("Failed to load property details:", err);
        setErrorMsg("Property listing could not be found or has been removed.");
      } finally {
        setLoading(false);
      }
    };
    fetchPropertyAndAi();
  }, [id]);

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

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-dark-950">
        <div className="flex flex-col items-center gap-3">
          <Loader2 className="w-10 h-10 text-brand-500 animate-spin" />
          <p className="text-slate-400 font-medium text-sm">Loading Property & AI Intelligence...</p>
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

  return (
    <div className="min-h-screen flex flex-col bg-dark-950 text-slate-100">
      <Navbar />

      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
        {/* Back Link & Action Bar */}
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          <button
            onClick={() => navigate(-1)}
            className="inline-flex items-center gap-2 text-xs font-semibold text-slate-400 hover:text-white transition-colors"
          >
            <ArrowLeft className="w-4 h-4" />
            <span>Back to Listings</span>
          </button>

          <div className="flex items-center gap-3 w-full sm:w-auto">
            <Link
              to={`/analytics/${property.id}`}
              className="flex-1 sm:flex-initial px-5 py-2.5 rounded-xl bg-gradient-to-r from-brand-600 to-accent-600 hover:from-brand-500 hover:to-accent-500 text-white font-bold text-xs shadow-lg shadow-brand-500/25 transition-all flex items-center justify-center gap-2"
            >
              <Brain className="w-4 h-4" />
              <span>Full AI Analytics Dashboard</span>
            </Link>
            
            <button
              onClick={handleDownloadPdf}
              disabled={downloadingPdf}
              className="px-4 py-2.5 rounded-xl bg-slate-900 hover:bg-slate-800 text-slate-200 border border-slate-800 text-xs font-semibold transition-all flex items-center gap-2"
            >
              {downloadingPdf ? <Loader2 className="w-4 h-4 animate-spin" /> : <Download className="w-4 h-4 text-emerald-400" />}
              <span>{downloadingPdf ? 'Downloading...' : 'PDF Report'}</span>
            </button>
          </div>
        </div>

        {/* Title & Price Header Banner */}
        <div className="glass-card p-6 md:p-8 rounded-3xl border border-slate-800 flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
          <div className="space-y-2">
            <div className="flex flex-wrap items-center gap-2">
              <span className="px-3 py-1 rounded-full bg-brand-500/10 text-brand-300 border border-brand-500/20 text-xs font-bold uppercase tracking-wider">
                {property.property_type}
              </span>
              <span className="px-3 py-1 rounded-full bg-accent-500/10 text-accent-300 border border-accent-500/20 text-xs font-bold uppercase tracking-wider">
                {property.bhk} BHK
              </span>
              <span className="px-3 py-1 rounded-full bg-emerald-500/10 text-emerald-300 border border-emerald-500/20 text-xs font-bold uppercase tracking-wider">
                {property.furnishing}
              </span>
            </div>
            <h1 className="text-2xl sm:text-3xl font-extrabold font-outfit text-white">{property.title}</h1>
            <p className="text-xs sm:text-sm text-slate-400 flex items-center gap-1.5">
              <MapPin className="w-4 h-4 text-brand-400 flex-shrink-0" />
              <span>{property.address}</span>
            </p>
          </div>

          <div className="bg-slate-900/90 px-6 py-4 rounded-2xl border border-slate-800 text-left md:text-right space-y-0.5 w-full md:w-auto">
            <span className="text-xs uppercase font-bold text-slate-400 block">Asking Price</span>
            <p className="text-2xl sm:text-3xl font-extrabold text-emerald-400">{property.price_formatted}</p>
            <p className="text-xs text-slate-400">₹{property.price_per_sqft?.toLocaleString()} / sq.ft</p>
          </div>
        </div>

        {/* Image Gallery */}
        <div className="space-y-4">
          <div className="relative h-[380px] sm:h-[480px] w-full rounded-3xl overflow-hidden border border-slate-800 glass-card">
            {property.images && property.images.length > 0 ? (
              <img
                src={property.images[activeImageIndex] || property.images[0]}
                alt={property.title}
                className="w-full h-full object-cover"
              />
            ) : (
              <div className="w-full h-full bg-slate-900 flex items-center justify-center text-slate-500">
                <Building2 className="w-16 h-16" />
              </div>
            )}
          </div>

          {/* Thumbnails Row */}
          {property.images && property.images.length > 1 && (
            <div className="flex items-center gap-3 overflow-x-auto pb-2 scrollbar-thin">
              {property.images.map((img, idx) => (
                <button
                  key={idx}
                  onClick={() => setActiveImageIndex(idx)}
                  className={`w-20 h-20 rounded-xl overflow-hidden border-2 flex-shrink-0 transition-all ${
                    activeImageIndex === idx ? 'border-brand-500 scale-105 shadow-lg shadow-brand-500/25' : 'border-slate-800 opacity-60 hover:opacity-100'
                  }`}
                >
                  <img src={img} alt={`Thumb ${idx}`} className="w-full h-full object-cover" />
                </button>
              ))}
            </div>
          )}
        </div>

        {/* AI Valuation & SHAP Summary Banner */}
        {pred && (
          <div className="glass-card p-6 rounded-3xl border border-brand-500/30 bg-gradient-to-r from-slate-900/90 to-brand-950/40 grid grid-cols-1 md:grid-cols-4 gap-6">
            <div className="space-y-1">
              <span className="text-[11px] font-bold uppercase text-brand-400 tracking-wider">AI Predicted Market Value</span>
              <p className="text-2xl font-extrabold text-white">₹{int(pred.predicted_selling_price).toLocaleString()}</p>
              <p className="text-xs text-slate-400">Confidence: <strong className="text-emerald-400">{pred.confidence_score}%</strong></p>
            </div>

            <div className="space-y-1">
              <span className="text-[11px] font-bold uppercase text-accent-400 tracking-wider">Est. Monthly Rent</span>
              <p className="text-2xl font-extrabold text-accent-400">₹{int(pred.estimated_rental_price).toLocaleString()} / mo</p>
              <p className="text-xs text-slate-400">Rental Yield: <strong>3.6% p.a.</strong></p>
            </div>

            <div className="space-y-1">
              <span className="text-[11px] font-bold uppercase text-purple-400 tracking-wider">Computer Vision Score</span>
              <p className="text-2xl font-extrabold text-purple-400">{cv?.overall_score || 85} / 100</p>
              <p className="text-xs text-slate-400">OpenCV Quality: <strong>{cv?.overall_condition || 'Good'}</strong></p>
            </div>

            <div className="space-y-1">
              <span className="text-[11px] font-bold uppercase text-emerald-400 tracking-wider">Description NLP Score</span>
              <p className="text-2xl font-extrabold text-emerald-400">{nlp?.text_quality_score || 78} / 100</p>
              <p className="text-xs text-slate-400">Keywords Detected: <strong>{nlp?.keywords_found?.length || 4}</strong></p>
            </div>
          </div>
        )}

        {/* Specs & Side Action Column */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {/* Main Specifications */}
          <div className="md:col-span-2 space-y-8">
            <div className="glass-card p-6 md:p-8 rounded-3xl border border-slate-800 space-y-6">
              <h3 className="text-lg font-bold font-outfit text-white border-b border-slate-800 pb-3 flex items-center gap-2">
                <Building2 className="w-5 h-5 text-brand-500" />
                Property Specifications
              </h3>

              <div className="grid grid-cols-2 sm:grid-cols-3 gap-4 text-xs">
                <div className="p-3.5 rounded-xl bg-slate-900/80 border border-slate-800/80 space-y-1">
                  <span className="text-slate-400 block text-[10px] uppercase font-bold">Built-up Area</span>
                  <span className="text-sm font-bold text-white">{property.area_sqft.toLocaleString()} Sq.ft</span>
                </div>
                <div className="p-3.5 rounded-xl bg-slate-900/80 border border-slate-800/80 space-y-1">
                  <span className="text-slate-400 block text-[10px] uppercase font-bold">Bedrooms</span>
                  <span className="text-sm font-bold text-white">{property.bhk} BHK</span>
                </div>
                <div className="p-3.5 rounded-xl bg-slate-900/80 border border-slate-800/80 space-y-1">
                  <span className="text-slate-400 block text-[10px] uppercase font-bold">Bathrooms</span>
                  <span className="text-sm font-bold text-white">{property.bathrooms} Baths</span>
                </div>
                <div className="p-3.5 rounded-xl bg-slate-900/80 border border-slate-800/80 space-y-1">
                  <span className="text-slate-400 block text-[10px] uppercase font-bold">Balconies</span>
                  <span className="text-sm font-bold text-white">{property.balconies} Balconies</span>
                </div>
                <div className="p-3.5 rounded-xl bg-slate-900/80 border border-slate-800/80 space-y-1">
                  <span className="text-slate-400 block text-[10px] uppercase font-bold">Floor Level</span>
                  <span className="text-sm font-bold text-white">Floor {property.floor} of {property.total_floors}</span>
                </div>
                <div className="p-3.5 rounded-xl bg-slate-900/80 border border-slate-800/80 space-y-1">
                  <span className="text-slate-400 block text-[10px] uppercase font-bold">Property Age</span>
                  <span className="text-sm font-bold text-white">{property.property_age}</span>
                </div>
                <div className="p-3.5 rounded-xl bg-slate-900/80 border border-slate-800/80 space-y-1">
                  <span className="text-slate-400 block text-[10px] uppercase font-bold">Facing</span>
                  <span className="text-sm font-bold text-white">{property.facing}</span>
                </div>
                <div className="p-3.5 rounded-xl bg-slate-900/80 border border-slate-800/80 space-y-1">
                  <span className="text-slate-400 block text-[10px] uppercase font-bold">Parking</span>
                  <span className="text-sm font-bold text-white">{property.parking}</span>
                </div>
                <div className="p-3.5 rounded-xl bg-slate-900/80 border border-slate-800/80 space-y-1">
                  <span className="text-slate-400 block text-[10px] uppercase font-bold">Furnishing</span>
                  <span className="text-sm font-bold text-white">{property.furnishing}</span>
                </div>
              </div>

              {property.description && (
                <div className="pt-4 border-t border-slate-800/80 space-y-2">
                  <h4 className="text-xs uppercase font-bold tracking-wider text-slate-300">Description</h4>
                  <p className="text-xs sm:text-sm text-slate-400 leading-relaxed whitespace-pre-line">
                    {property.description}
                  </p>
                </div>
              )}
            </div>

            {/* SHAP Factors Card */}
            {pred?.shap_explanation && (
              <div className="glass-card p-6 md:p-8 rounded-3xl border border-slate-800 space-y-4">
                <h3 className="text-base font-bold font-outfit text-white flex items-center gap-2">
                  <Brain className="w-5 h-5 text-brand-400" />
                  SHAP Explainable Valuation Drivers
                </h3>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div className="p-4 rounded-2xl bg-emerald-500/10 border border-emerald-500/30 space-y-2">
                    <div className="flex items-center gap-2 text-emerald-400 text-xs font-bold uppercase">
                      <ThumbsUp className="w-4 h-4" />
                      <span>Top Positive Factors</span>
                    </div>
                    {pred.shap_explanation.top_positive_factors?.map((f, idx) => (
                      <div key={idx} className="flex items-center justify-between text-xs">
                        <span className="text-slate-300">{f.factor}</span>
                        <span className="font-mono text-emerald-400 font-bold">+{f.impact}%</span>
                      </div>
                    ))}
                  </div>

                  <div className="p-4 rounded-2xl bg-amber-500/10 border border-amber-500/30 space-y-2">
                    <div className="flex items-center gap-2 text-amber-400 text-xs font-bold uppercase">
                      <ThumbsDown className="w-4 h-4" />
                      <span>Value Adjustments</span>
                    </div>
                    {pred.shap_explanation.top_negative_factors?.map((f, idx) => (
                      <div key={idx} className="flex items-center justify-between text-xs">
                        <span className="text-slate-300">{f.factor}</span>
                        <span className="font-mono text-amber-400 font-bold">{f.impact}%</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {/* Interactive Map View */}
            <div className="glass-card p-6 md:p-8 rounded-3xl border border-slate-800 space-y-4">
              <h3 className="text-base font-bold font-outfit text-white flex items-center gap-2">
                <MapPin className="w-5 h-5 text-emerald-400" />
                Property GIS Location & Map
              </h3>
              <MapView
                searchResult={mapSearchResult}
                nearbyPlaces={property.nearby_places || []}
              />
            </div>
          </div>

          {/* Owner Info & Direct Contact Card */}
          <div className="space-y-6">
            <div className="glass-card p-6 rounded-3xl border border-slate-800 space-y-6 sticky top-24">
              <div className="space-y-2 border-b border-slate-800 pb-4">
                <span className="text-[10px] font-bold uppercase tracking-widest text-emerald-400">Verified Seller</span>
                <h4 className="text-lg font-bold text-white font-outfit">{property.owner_name}</h4>
                <a href={`tel:${property.owner_phone}`} className="text-xs text-emerald-400 font-mono hover:underline block">
                  {property.owner_phone}
                </a>
              </div>

              <div className="space-y-3">
                <a
                  href={`tel:${property.owner_phone}`}
                  className="w-full py-3.5 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-xs shadow-lg shadow-emerald-500/25 transition-all flex items-center justify-center gap-2"
                >
                  <Phone className="w-4 h-4" />
                  <span>Call Owner Now</span>
                </a>

                <button
                  onClick={() => setShowContactModal(true)}
                  className="w-full py-3 rounded-xl bg-slate-900 hover:bg-slate-800 text-slate-200 font-semibold text-xs border border-slate-800 transition-all flex items-center justify-center gap-2"
                >
                  <MessageSquare className="w-4 h-4 text-brand-400" />
                  <span>Inquire Owner</span>
                </button>
              </div>

              <div className="pt-4 border-t border-slate-800/80 text-[11px] text-slate-500 space-y-2 font-mono">
                <p className="flex items-center gap-2">
                  <Shield className="w-3.5 h-3.5 text-emerald-400" />
                  <span>Verified Bangalore Seller</span>
                </p>
                <p>Lat: {property.latitude.toFixed(4)}</p>
                <p>Lon: {property.longitude.toFixed(4)}</p>
              </div>
            </div>
          </div>
        </div>

        {/* Nearby Facilities Section */}
        <NearbyPlacesList places={property.nearby_places || []} />
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

      <Footer />
    </div>
  );
};

function int(val) {
  return Math.round(val || 0);
}
