import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Navbar } from '../components/Navbar';
import { Footer } from '../components/Footer';
import { BangaloreLocationAutocomplete } from '../components/BangaloreLocationAutocomplete';
import { useAuth } from '../context/AuthContext';
import { 
  Building2, Image as ImageIcon, MapPin, Upload, CheckCircle2, 
  AlertCircle, Trash2, Star, ShieldCheck, Clock, Layers, ArrowLeft
} from 'lucide-react';

export const ListPropertyPage = () => {
  const { user } = useAuth();
  const navigate = useNavigate();

  const [formData, setFormData] = useState({
    title: '',
    property_type: 'Apartment',
    listing_type: 'Buy',
    bhk: 2,
    area_sqft: 1200,
    price: 7500000,
    locality: 'Whitefield',
    sub_locality: '',
    address: '',
    latitude: 12.9696,
    longitude: 77.7497,
    availability: 'Ready to Move',
    furnishing: 'Semi-Furnished',
    floor: 3,
    total_floors: 10,
    parking: 'Covered',
    description: '',
    owner_name: user?.full_name || '',
    owner_phone: '+91 98860 12345',
    seller_type: 'Owner'
  });

  const [selectedFiles, setSelectedFiles] = useState([]);
  const [primaryIdx, setPrimaryIdx] = useState(0);
  const [submitting, setSubmitting] = useState(false);
  const [submissionResult, setSubmissionResult] = useState(null);
  const [errorMsg, setErrorMsg] = useState('');

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleLocalitySelect = (locObj) => {
    setFormData(prev => ({
      ...prev,
      locality: locObj.name,
      latitude: locObj.lat || prev.latitude,
      longitude: locObj.lon || prev.longitude
    }));
  };

  const handleFileChange = (e) => {
    const files = Array.from(e.target.files);
    if (files.length > 0) {
      const newFiles = files.map(f => ({
        file: f,
        preview: URL.createObjectURL(f)
      }));
      setSelectedFiles(prev => [...prev, ...newFiles]);
    }
  };

  const removeFile = (index) => {
    setSelectedFiles(prev => prev.filter((_, i) => i !== index));
    if (primaryIdx >= selectedFiles.length - 1) {
      setPrimaryIdx(Math.max(0, selectedFiles.length - 2));
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    setErrorMsg('');
    setSubmissionResult(null);

    try {
      const token = localStorage.getItem('token');
      const headers = {
        'Content-Type': 'application/json',
        ...(token ? { 'Authorization': `Bearer ${token}` } : {})
      };

      // 1. Submit property payload
      const response = await fetch('/api/v1/listings/', {
        method: 'POST',
        headers,
        body: JSON.stringify({
          ...formData,
          bhk: parseInt(formData.bhk),
          area_sqft: parseFloat(formData.area_sqft),
          price: parseFloat(formData.price),
          floor: parseInt(formData.floor),
          total_floors: parseInt(formData.total_floors),
          latitude: parseFloat(formData.latitude),
          longitude: parseFloat(formData.longitude)
        })
      });

      if (!response.ok) {
        const errData = await response.json();
        throw new Error(errData.detail || 'Failed to submit property listing.');
      }

      const listingData = await response.json();
      const createdPropId = listingData.id;

      // 2. Upload images if selected
      if (selectedFiles.length > 0 && createdPropId) {
        const fileFormData = new FormData();
        fileFormData.append('property_id', createdPropId);
        fileFormData.append('primary_index', primaryIdx);
        selectedFiles.forEach(item => {
          fileFormData.append('files', item.file);
        });

        const uploadHeaders = token ? { 'Authorization': `Bearer ${token}` } : {};
        const uploadRes = await fetch('/api/v1/listings/upload-images', {
          method: 'POST',
          headers: uploadHeaders,
          body: fileFormData
        });

        if (uploadRes.ok) {
          const uploadResult = await uploadRes.json();
          listingData.uploaded_count = uploadResult.uploaded_count;
        }
      }

      setSubmissionResult(listingData);
    } catch (err) {
      console.error(err);
      setErrorMsg(err.message || 'Error occurred while listing property.');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen bg-dark-950 text-slate-100 flex flex-col font-sans">
      <Navbar />

      <main className="flex-grow max-w-5xl mx-auto px-4 py-8 sm:px-6 lg:px-8 w-full">
        {/* Header */}
        <div className="mb-8 flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800 pb-6">
          <div>
            <div className="flex items-center gap-2 text-emerald-400 text-sm font-bold uppercase tracking-wider mb-1">
              <Building2 className="w-4 h-4" />
              PropPulse Direct Inventory Engine
            </div>
            <h1 className="text-3xl font-extrabold text-white tracking-tight font-outfit">
              List Your Bengaluru Property
            </h1>
            <p className="text-sm text-slate-400 mt-1">
              Direct owner & agent submission with verified data provenance and authentic photo support.
            </p>
          </div>
          <button
            onClick={() => navigate('/properties')}
            className="flex items-center gap-2 px-4 py-2 rounded-xl bg-slate-900 border border-slate-800 text-slate-300 hover:text-white hover:border-slate-700 text-sm font-medium transition-all"
          >
            <ArrowLeft className="w-4 h-4" />
            Browse Listings
          </button>
        </div>

        {/* Submission Success View */}
        {submissionResult ? (
          <div className="glass-card border border-emerald-500/30 rounded-2xl p-8 text-center bg-emerald-950/20 max-w-2xl mx-auto my-12 shadow-2xl">
            <div className="w-16 h-16 rounded-full bg-emerald-500/20 text-emerald-400 flex items-center justify-center mx-auto mb-4">
              <CheckCircle2 className="w-10 h-10" />
            </div>
            <h2 className="text-2xl font-extrabold text-white mb-2">
              Property Submitted Successfully!
            </h2>
            <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-amber-500/20 border border-amber-500/30 text-amber-300 font-bold text-xs uppercase tracking-wider my-3">
              <Clock className="w-4 h-4" />
              Status: PENDING VERIFICATION
            </div>
            <p className="text-sm text-slate-300 max-w-md mx-auto mb-6">
              Your property listing <strong className="text-white">BLR-{submissionResult.id}</strong> in {submissionResult.locality} has been received and queued for admin verification.
            </p>

            <div className="bg-slate-900/80 rounded-xl p-4 border border-slate-800 text-left text-xs space-y-2 mb-6">
              <div className="flex justify-between">
                <span className="text-slate-400">Listing ID:</span>
                <span className="font-semibold text-white">BLR-{submissionResult.id}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Locality:</span>
                <span className="font-semibold text-white">{submissionResult.locality}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Price & Sq.Ft:</span>
                <span className="font-semibold text-emerald-400">₹{submissionResult.price_inr?.toLocaleString('en-IN')} (₹{submissionResult.price_per_sqft}/sqft)</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Images Uploaded:</span>
                <span className="font-semibold text-white">{submissionResult.uploaded_count || selectedFiles.length} Photos</span>
              </div>
            </div>

            <div className="flex justify-center gap-4">
              <button
                onClick={() => {
                  setSubmissionResult(null);
                  setSelectedFiles([]);
                }}
                className="px-5 py-2.5 rounded-xl bg-slate-800 text-slate-200 hover:bg-slate-700 text-sm font-semibold transition-all"
              >
                List Another Property
              </button>
              <button
                onClick={() => navigate('/properties')}
                className="px-5 py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white text-sm font-semibold transition-all shadow-lg shadow-emerald-600/30"
              >
                View Marketplace
              </button>
            </div>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="space-y-8">
            {errorMsg && (
              <div className="p-4 rounded-xl bg-red-900/30 border border-red-500/40 text-red-300 flex items-center gap-3 text-sm">
                <AlertCircle className="w-5 h-5 flex-shrink-0" />
                <span>{errorMsg}</span>
              </div>
            )}

            {/* 1. Basic Property Info */}
            <div className="glass-card rounded-2xl p-6 border border-slate-800 space-y-6">
              <h2 className="text-lg font-bold text-white flex items-center gap-2">
                <Building2 className="w-5 h-5 text-brand-400" />
                1. Basic Details
              </h2>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="md:col-span-2">
                  <label className="block text-xs font-semibold text-slate-300 mb-1">
                    Property Title *
                  </label>
                  <input
                    type="text"
                    name="title"
                    required
                    value={formData.title}
                    onChange={handleInputChange}
                    placeholder="e.g. Luxurious 3 BHK Apartment in Sobha City, Thanisandra"
                    className="w-full bg-slate-900 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-white focus:outline-none focus:border-brand-500"
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-300 mb-1">
                    Property Type *
                  </label>
                  <select
                    name="property_type"
                    value={formData.property_type}
                    onChange={handleInputChange}
                    className="w-full bg-slate-900 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-white focus:outline-none focus:border-brand-500"
                  >
                    <option value="Apartment">Apartment / Flat</option>
                    <option value="Villa">Villa / Independent House</option>
                    <option value="Independent House">Independent House</option>
                    <option value="Plot">Plot / Land</option>
                    <option value="Penthouse">Penthouse</option>
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-300 mb-1">
                    BHK Configuration *
                  </label>
                  <select
                    name="bhk"
                    value={formData.bhk}
                    onChange={handleInputChange}
                    className="w-full bg-slate-900 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-white focus:outline-none focus:border-brand-500"
                  >
                    <option value="1">1 BHK</option>
                    <option value="2">2 BHK</option>
                    <option value="3">3 BHK</option>
                    <option value="4">4 BHK</option>
                    <option value="5">5+ BHK</option>
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-300 mb-1">
                    Super Built-up Area (sq.ft) *
                  </label>
                  <input
                    type="number"
                    name="area_sqft"
                    required
                    min="100"
                    value={formData.area_sqft}
                    onChange={handleInputChange}
                    className="w-full bg-slate-900 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-white focus:outline-none focus:border-brand-500"
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-300 mb-1">
                    Expected Total Price (₹ INR) *
                  </label>
                  <input
                    type="number"
                    name="price"
                    required
                    min="100000"
                    value={formData.price}
                    onChange={handleInputChange}
                    className="w-full bg-slate-900 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-white focus:outline-none focus:border-brand-500"
                  />
                  <span className="text-[11px] text-emerald-400 mt-1 block">
                    Calculated Rate: ₹{Math.round(formData.price / (formData.area_sqft || 1))}/sq.ft
                  </span>
                </div>
              </div>
            </div>

            {/* 2. Location & Pin */}
            <div className="glass-card rounded-2xl p-6 border border-slate-800 space-y-6">
              <h2 className="text-lg font-bold text-white flex items-center gap-2">
                <MapPin className="w-5 h-5 text-emerald-400" />
                2. Location & Address
              </h2>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-slate-300 mb-1">
                    Bengaluru Locality *
                  </label>
                  <BangaloreLocationAutocomplete
                    value={formData.locality}
                    onChange={(val) => setFormData(p => ({ ...p, locality: val }))}
                    onSelectLocation={handleLocalitySelect}
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-300 mb-1">
                    Sub-locality / Sector (Optional)
                  </label>
                  <input
                    type="text"
                    name="sub_locality"
                    value={formData.sub_locality}
                    onChange={handleInputChange}
                    placeholder="e.g. Phase 2, EPIP Zone"
                    className="w-full bg-slate-900 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-white focus:outline-none focus:border-brand-500"
                  />
                </div>

                <div className="md:col-span-2">
                  <label className="block text-xs font-semibold text-slate-300 mb-1">
                    Full Address *
                  </label>
                  <input
                    type="text"
                    name="address"
                    required
                    value={formData.address}
                    onChange={handleInputChange}
                    placeholder="Door No, Street Name, Landmark, Bengaluru, Karnataka"
                    className="w-full bg-slate-900 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-white focus:outline-none focus:border-brand-500"
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-300 mb-1">Latitude</label>
                  <input
                    type="number"
                    step="0.0001"
                    name="latitude"
                    value={formData.latitude}
                    onChange={handleInputChange}
                    className="w-full bg-slate-900 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-white focus:outline-none focus:border-brand-500"
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-300 mb-1">Longitude</label>
                  <input
                    type="number"
                    step="0.0001"
                    name="longitude"
                    value={formData.longitude}
                    onChange={handleInputChange}
                    className="w-full bg-slate-900 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-white focus:outline-none focus:border-brand-500"
                  />
                </div>
              </div>
            </div>

            {/* 3. Additional Specifications */}
            <div className="glass-card rounded-2xl p-6 border border-slate-800 space-y-6">
              <h2 className="text-lg font-bold text-white flex items-center gap-2">
                <Layers className="w-5 h-5 text-purple-400" />
                3. Specifications & Furnishing
              </h2>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-slate-300 mb-1">Availability</label>
                  <select
                    name="availability"
                    value={formData.availability}
                    onChange={handleInputChange}
                    className="w-full bg-slate-900 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-white focus:outline-none focus:border-brand-500"
                  >
                    <option value="Ready to Move">Ready to Move</option>
                    <option value="Under Construction">Under Construction</option>
                    <option value="15-30 Days">15-30 Days</option>
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-300 mb-1">Furnishing</label>
                  <select
                    name="furnishing"
                    value={formData.furnishing}
                    onChange={handleInputChange}
                    className="w-full bg-slate-900 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-white focus:outline-none focus:border-brand-500"
                  >
                    <option value="Fully Furnished">Fully Furnished</option>
                    <option value="Semi-Furnished">Semi-Furnished</option>
                    <option value="Unfurnished">Unfurnished</option>
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-300 mb-1">Parking</label>
                  <select
                    name="parking"
                    value={formData.parking}
                    onChange={handleInputChange}
                    className="w-full bg-slate-900 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-white focus:outline-none focus:border-brand-500"
                  >
                    <option value="Covered">Covered Parking</option>
                    <option value="Open">Open Parking</option>
                    <option value="None">No Parking</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">Property Description</label>
                <textarea
                  name="description"
                  rows="3"
                  value={formData.description}
                  onChange={handleInputChange}
                  placeholder="Highlight key features, amenities, nearby schools/IT parks..."
                  className="w-full bg-slate-900 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-white focus:outline-none focus:border-brand-500"
                ></textarea>
              </div>
            </div>

            {/* 4. Owner / Agent Info */}
            <div className="glass-card rounded-2xl p-6 border border-slate-800 space-y-6">
              <h2 className="text-lg font-bold text-white flex items-center gap-2">
                <ShieldCheck className="w-5 h-5 text-amber-400" />
                4. Contact Information
              </h2>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-slate-300 mb-1">Poster Type</label>
                  <select
                    name="seller_type"
                    value={formData.seller_type}
                    onChange={handleInputChange}
                    className="w-full bg-slate-900 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-white focus:outline-none focus:border-brand-500"
                  >
                    <option value="Owner">Owner</option>
                    <option value="Agent">Agent / Broker</option>
                    <option value="Builder">Builder</option>
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-300 mb-1">Full Name *</label>
                  <input
                    type="text"
                    name="owner_name"
                    required
                    value={formData.owner_name}
                    onChange={handleInputChange}
                    className="w-full bg-slate-900 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-white focus:outline-none focus:border-brand-500"
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-300 mb-1">Contact Phone *</label>
                  <input
                    type="text"
                    name="owner_phone"
                    required
                    value={formData.owner_phone}
                    onChange={handleInputChange}
                    className="w-full bg-slate-900 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-white focus:outline-none focus:border-brand-500"
                  />
                </div>
              </div>
            </div>

            {/* 5. Authentic Image Upload */}
            <div className="glass-card rounded-2xl p-6 border border-slate-800 space-y-6">
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-lg font-bold text-white flex items-center gap-2">
                    <ImageIcon className="w-5 h-5 text-brand-400" />
                    5. Real Property Photos (OWNER_UPLOADED)
                  </h2>
                  <p className="text-xs text-slate-400 mt-0.5">
                    Requires at least 1 genuine property photo to be eligible for Verified Current Listing badge.
                  </p>
                </div>
              </div>

              {/* Upload Drop Zone */}
              <div className="border-2 border-dashed border-slate-800 hover:border-brand-500/50 rounded-2xl p-6 text-center transition-all bg-slate-900/40">
                <input
                  type="file"
                  id="image_upload_input"
                  multiple
                  accept="image/jpeg,image/png,image/webp"
                  onChange={handleFileChange}
                  className="hidden"
                />
                <label htmlFor="image_upload_input" className="cursor-pointer block">
                  <Upload className="w-10 h-10 text-brand-400 mx-auto mb-2" />
                  <span className="text-sm font-semibold text-white block">
                    Click to upload property photos
                  </span>
                  <span className="text-xs text-slate-400 block mt-1">
                    Supports JPG, PNG, WEBP (Min 400x300 resolution, Max 10MB per image)
                  </span>
                </label>
              </div>

              {/* Upload Previews */}
              {selectedFiles.length > 0 && (
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 pt-4">
                  {selectedFiles.map((item, idx) => (
                    <div
                      key={idx}
                      className={`relative rounded-xl overflow-hidden border ${
                        primaryIdx === idx ? 'border-brand-500 ring-2 ring-brand-500/40' : 'border-slate-800'
                      }`}
                    >
                      <img
                        src={item.preview}
                        alt={`Upload ${idx + 1}`}
                        className="w-full h-28 object-cover"
                      />
                      <div className="absolute top-1 right-1 flex gap-1">
                        <button
                          type="button"
                          onClick={() => removeFile(idx)}
                          className="p-1 rounded-lg bg-red-600/80 text-white hover:bg-red-600"
                        >
                          <Trash2 className="w-3.5 h-3.5" />
                        </button>
                      </div>

                      <button
                        type="button"
                        onClick={() => setPrimaryIdx(idx)}
                        className={`absolute bottom-1 left-1 px-2 py-0.5 rounded text-[10px] font-bold ${
                          primaryIdx === idx
                            ? 'bg-brand-500 text-white'
                            : 'bg-slate-900/80 text-slate-300 hover:bg-slate-900'
                        }`}
                      >
                        {primaryIdx === idx ? '★ Primary' : 'Make Primary'}
                      </button>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Submit Action */}
            <div className="flex justify-end gap-4 pt-4">
              <button
                type="button"
                onClick={() => navigate('/properties')}
                className="px-6 py-3 rounded-xl bg-slate-900 border border-slate-800 text-slate-300 hover:text-white text-sm font-semibold"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={submitting}
                className="px-8 py-3 rounded-xl bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white font-bold text-sm shadow-xl shadow-emerald-600/30 transition-all flex items-center gap-2"
              >
                {submitting ? 'Submitting Property...' : 'Submit Direct Listing'}
              </button>
            </div>
          </form>
        )}
      </main>

      <Footer />
    </div>
  );
};
